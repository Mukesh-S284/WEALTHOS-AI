"""Transaction management, CSV processing, and categorization service."""

import csv
import io
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from backend.models.transaction import Transaction, Category
from backend.models.audit import AuditLog
from backend.models.user import User
from backend.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionFilter,
    TransactionSummaryResponse,
    CSVRowValidation,
    CSVPreviewResponse
)
from backend.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from finance_engine.budgeting.engine import to_decimal, calculate_cashflow_summary
from ml.expense_classifier.model import ExpenseClassifier

# Global classifier instance
_classifier = ExpenseClassifier()


class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(
        self,
        user: User,
        payload: TransactionCreate,
        source: str = "manual"
    ) -> Transaction:
        """Create a new transaction with automatic categorization if not provided or verified."""
        cat = payload.category.strip()
        conf = 1.0
        c_source = "manual"

        # If user left category as default or generic, run classifier
        if not cat or cat.lower() in ("unassigned", "uncategorized", "general", "other"):
            predicted_cat, predicted_conf, pred_source = _classifier.predict(payload.description)
            cat = predicted_cat
            conf = predicted_conf
            c_source = pred_source

        tx = Transaction(
            user_id=user.id,
            date=payload.date,
            description=payload.description.strip(),
            amount=to_decimal(payload.amount),
            type=payload.type.lower(),
            category=cat,
            currency=payload.currency.upper(),
            is_recurring=payload.is_recurring,
            recurrence_interval=payload.recurrence_interval,
            classification_source=c_source,
            classification_confidence=to_decimal(conf),
            is_user_corrected=False,
            notes=payload.notes,
            source=source
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def get_transaction(self, user: User, transaction_id: str) -> Transaction:
        tx = self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user.id
        ).first()
        if not tx:
            raise NotFoundException("Transaction", transaction_id)
        return tx

    def update_transaction(
        self,
        user: User,
        transaction_id: str,
        payload: TransactionUpdate
    ) -> Transaction:
        tx = self.get_transaction(user, transaction_id)
        
        if payload.date is not None:
            tx.date = payload.date
        if payload.description is not None:
            tx.description = payload.description.strip()
        if payload.amount is not None:
            tx.amount = to_decimal(payload.amount)
        if payload.type is not None:
            tx.type = payload.type.lower()
        if payload.category is not None:
            old_cat = tx.category
            tx.category = payload.category.strip()
            if old_cat != tx.category:
                tx.is_user_corrected = True
                tx.classification_source = "manual"
        if payload.currency is not None:
            tx.currency = payload.currency.upper()
        if payload.is_recurring is not None:
            tx.is_recurring = payload.is_recurring
        if payload.recurrence_interval is not None:
            tx.recurrence_interval = payload.recurrence_interval
        if payload.notes is not None:
            tx.notes = payload.notes
        
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def delete_transaction(self, user: User, transaction_id: str) -> bool:
        tx = self.get_transaction(user, transaction_id)
        self.db.delete(tx)
        self.db.commit()
        return True

    def list_transactions(
        self,
        user: User,
        filters: TransactionFilter
    ) -> Tuple[List[Transaction], int]:
        """List user's transactions with flexible filtering and pagination."""
        query = self.db.query(Transaction).filter(Transaction.user_id == user.id)

        if filters.start_date:
            query = query.filter(Transaction.date >= filters.start_date)
        if filters.end_date:
            query = query.filter(Transaction.date <= filters.end_date)
        if filters.type:
            query = query.filter(Transaction.type == filters.type.lower())
        if filters.category:
            query = query.filter(Transaction.category == filters.category)
        if filters.is_recurring is not None:
            query = query.filter(Transaction.is_recurring == filters.is_recurring)
        if filters.min_amount:
            query = query.filter(Transaction.amount >= to_decimal(filters.min_amount))
        if filters.max_amount:
            query = query.filter(Transaction.amount <= to_decimal(filters.max_amount))
        if filters.search:
            search_pat = f"%{filters.search.strip()}%"
            query = query.filter(
                or_(
                    Transaction.description.ilike(search_pat),
                    Transaction.notes.ilike(search_pat),
                    Transaction.category.ilike(search_pat)
                )
            )

        total_count = query.count()
        items = query.order_by(desc(Transaction.date), desc(Transaction.created_at))\
                     .offset(filters.offset)\
                     .limit(filters.limit)\
                     .all()

        return items, total_count

    def get_summary(
        self,
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> TransactionSummaryResponse:
        """Calculate income, expenses, net savings, and category breakdown."""
        query = self.db.query(Transaction).filter(Transaction.user_id == user.id)
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        txs = query.all()
        incomes = [t.amount for t in txs if t.type == "income"]
        expenses = [t.amount for t in txs if t.type == "expense"]
        
        summary = calculate_cashflow_summary(incomes, expenses)

        cat_breakdown: Dict[str, Decimal] = {}
        for t in txs:
            if t.type == "expense":
                cat = t.category
                cat_breakdown[cat] = cat_breakdown.get(cat, Decimal("0.00")) + t.amount

        return TransactionSummaryResponse(
            total_income=summary["total_income"],
            total_expenses=summary["total_expenses"],
            net_savings=summary["net_savings"],
            savings_rate_pct=summary["savings_rate_pct"],
            currency=user.preferred_currency,
            transaction_count=len(txs),
            categories_breakdown=cat_breakdown
        )

    def parse_and_preview_csv(self, user: User, csv_content: str) -> CSVPreviewResponse:
        """
        Validate CSV content, parse rows, detect duplicates against existing records,
        suggest categories using ML classifier, and report invalid rows without discarding them.
        """
        reader = csv.DictReader(io.StringIO(csv_content))
        if not reader.fieldnames:
            raise BadRequestException("CSV file contains no headers or is empty.")

        # Header normalization
        field_map = {}
        for fn in reader.fieldnames:
            clean = fn.strip().lower().replace(" ", "_")
            if clean in ("date", "transaction_date", "tx_date"):
                field_map["date"] = fn
            elif clean in ("description", "desc", "memo", "name", "payee"):
                field_map["description"] = fn
            elif clean in ("amount", "value", "price", "total"):
                field_map["amount"] = fn
            elif clean in ("type", "transaction_type"):
                field_map["type"] = fn
            elif clean in ("category", "cat"):
                field_map["category"] = fn
            elif clean in ("notes", "note", "comment"):
                field_map["notes"] = fn

        if "date" not in field_map or "description" not in field_map or "amount" not in field_map:
            raise BadRequestException(
                f"Missing required CSV columns. Found headers: {list(reader.fieldnames)}. "
                "Required columns: Date, Description, Amount."
            )

        results: List[CSVRowValidation] = []
        row_num = 1
        valid_count = 0
        invalid_count = 0
        duplicate_count = 0

        # Existing user transactions for duplicate detection
        existing_txs = self.db.query(Transaction).filter(Transaction.user_id == user.id).all()

        for row in reader:
            row_num += 1
            errors = []
            parsed_tx = None
            is_duplicate = False

            # 1. Parse Date
            raw_date = row.get(field_map["date"], "").strip()
            parsed_date = None
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%m-%d-%Y"):
                try:
                    parsed_date = datetime.strptime(raw_date, fmt).date()
                    break
                except ValueError:
                    continue
            if not parsed_date:
                errors.append(f"Invalid date format '{raw_date}'. Expected YYYY-MM-DD or MM/DD/YYYY.")

            # 2. Parse Description
            raw_desc = row.get(field_map["description"], "").strip()
            if not raw_desc:
                errors.append("Description cannot be empty.")

            # 3. Parse Amount
            raw_amount = row.get(field_map["amount"], "").strip()
            parsed_amount = None
            try:
                # Remove currency symbols or commas
                clean_amt = raw_amount.replace("$", "").replace("€", "").replace("£", "").replace(",", "")
                val = Decimal(clean_amt)
                if val <= Decimal("0.00"):
                    errors.append(f"Amount '{raw_amount}' must be greater than zero.")
                else:
                    parsed_amount = val.quantize(Decimal("0.01"))
            except (InvalidOperation, Exception):
                errors.append(f"Invalid numeric amount '{raw_amount}'.")

            # 4. Parse Type
            raw_type = row.get(field_map.get("type", ""), "").strip().lower() if "type" in field_map else None
            if not raw_type:
                # Infer from amount sign or description if not provided
                raw_type = "expense"
            elif raw_type not in ("income", "expense"):
                raw_type = "income" if "credit" in raw_type or "deposit" in raw_type else "expense"

            # 5. Suggested Category via ML/Rule Classifier
            pred_cat, pred_conf, _ = _classifier.predict(raw_desc or "")
            raw_cat = row.get(field_map.get("category", ""), "").strip() if "category" in field_map else None
            final_cat = raw_cat if raw_cat else pred_cat

            # 6. Duplicate Detection
            if parsed_date and raw_desc and parsed_amount:
                for ext in existing_txs:
                    if (
                        abs((ext.date - parsed_date).days) <= 1
                        and ext.description.strip().lower() == raw_desc.lower()
                        and ext.amount == parsed_amount
                    ):
                        is_duplicate = True
                        duplicate_count += 1
                        break

            if not errors and parsed_date and raw_desc and parsed_amount:
                parsed_tx = TransactionCreate(
                    date=parsed_date,
                    description=raw_desc,
                    amount=parsed_amount,
                    type=raw_type,
                    category=final_cat,
                    currency=user.preferred_currency,
                    notes=row.get(field_map.get("notes", ""), "").strip() if "notes" in field_map else None
                )
                valid_count += 1
            else:
                invalid_count += 1

            results.append(
                CSVRowValidation(
                    row_number=row_num,
                    raw_data=dict(row),
                    parsed_transaction=parsed_tx,
                    is_valid=len(errors) == 0,
                    is_duplicate=is_duplicate,
                    errors=errors,
                    suggested_category=pred_cat,
                    category_confidence=pred_conf
                )
            )

        return CSVPreviewResponse(
            total_rows=len(results),
            valid_rows=valid_count,
            invalid_rows=invalid_count,
            duplicate_rows=duplicate_count,
            rows=results
        )

    def commit_csv_import(
        self,
        user: User,
        transactions: List[TransactionCreate]
    ) -> List[Transaction]:
        """Commit a batch of validated transactions in a single transaction."""
        if not transactions:
            raise BadRequestException("No valid transactions provided to commit.")

        created_records = []
        for t in transactions:
            tx = Transaction(
                user_id=user.id,
                date=t.date,
                description=t.description.strip(),
                amount=to_decimal(t.amount),
                type=t.type.lower(),
                category=t.category.strip(),
                currency=t.currency.upper(),
                is_recurring=t.is_recurring,
                recurrence_interval=t.recurrence_interval,
                classification_source="csv_import",
                classification_confidence=Decimal("1.0"),
                notes=t.notes,
                source="csv_import"
            )
            self.db.add(tx)
            created_records.append(tx)

        # Audit log for CSV import
        audit = AuditLog(
            user_id=user.id,
            action="csv_import",
            status="success",
            details={"imported_count": len(created_records)}
        )
        self.db.add(audit)
        self.db.commit()
        return created_records

    def export_transactions_csv(self, user: User) -> str:
        """Export user transactions to standard CSV string."""
        txs = self.db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).order_by(Transaction.date.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Description", "Amount", "Type", "Category", "Currency", "Recurring", "Notes"])
        for t in txs:
            writer.writerow([
                t.date.isoformat(),
                t.description,
                str(t.amount),
                t.type,
                t.category,
                t.currency,
                "Yes" if t.is_recurring else "No",
                t.notes or ""
            ])
        return output.getvalue()
