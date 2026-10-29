"""Transaction management and CSV import/export API routes."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Response, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.transaction_service import TransactionService
from backend.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionFilter,
    TransactionSummaryResponse,
    CSVPreviewResponse,
    CSVCommitRequest
)
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/transactions", tags=["Transactions & Money Manager"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new income or expense transaction."""
    service = TransactionService(db)
    return service.create_transaction(current_user, payload)


@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_recurring: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    max_amount: Optional[Decimal] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List transactions with rich filters and pagination."""
    filters = TransactionFilter(
        start_date=start_date,
        end_date=end_date,
        type=type,
        category=category,
        is_recurring=is_recurring,
        search=search,
        min_amount=min_amount,
        max_amount=max_amount,
        limit=limit,
        offset=offset
    )
    service = TransactionService(db)
    items, _ = service.list_transactions(current_user, filters)
    return items


@router.get("/summary", response_model=TransactionSummaryResponse)
def get_transaction_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve financial summary: income, expenses, net savings, and category breakdown."""
    service = TransactionService(db)
    return service.get_summary(current_user, start_date=start_date, end_date=end_date)


@router.post("/csv-preview", response_model=CSVPreviewResponse)
async def preview_csv_import(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and preview a CSV file: validates headers, rows, duplicates, and suggests categories."""
    content = await file.read()
    csv_text = content.decode("utf-8-sig", errors="replace")
    service = TransactionService(db)
    return service.parse_and_preview_csv(current_user, csv_text)


@router.post("/csv-commit", response_model=List[TransactionResponse], status_code=status.HTTP_201_CREATED)
def commit_csv_import(
    payload: CSVCommitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Commit verified previewed CSV rows into user's database."""
    service = TransactionService(db)
    return service.commit_csv_import(current_user, payload.rows)


@router.get("/export-csv")
def export_transactions_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user transactions to standard CSV format."""
    service = TransactionService(db)
    csv_data = service.export_transactions_csv(current_user)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve a single transaction by ID."""
    service = TransactionService(db)
    return service.get_transaction(current_user, transaction_id)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: str,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update transaction details."""
    service = TransactionService(db)
    return service.update_transaction(current_user, transaction_id, payload)


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction."""
    service = TransactionService(db)
    service.delete_transaction(current_user, transaction_id)
    return {"message": "Transaction deleted successfully."}
