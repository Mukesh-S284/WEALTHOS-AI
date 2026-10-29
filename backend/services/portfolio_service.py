"""Portfolio management, holdings valuation, and risk analytics service."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.models.portfolio import Portfolio, PortfolioHolding
from backend.models.user import User
from backend.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioHoldingCreate,
    PortfolioHoldingUpdate,
    PortfolioHoldingResponse,
    PortfolioRiskReportResponse,
    StressTestScenarioResult
)
from backend.services.market_service import MarketService
from backend.core.exceptions import NotFoundException, BadRequestException
from finance_engine.portfolio.metrics import (
    calculate_portfolio_weights_and_allocation,
    calculate_historical_risk_metrics,
    simulate_portfolio_stress_scenarios,
    to_decimal
)


class PortfolioService:
    def __init__(self, db: Session, market_service: Optional[MarketService] = None):
        self.db = db
        self.market_service = market_service or MarketService(db)

    def _enrich_portfolio(self, portfolio: Portfolio) -> PortfolioResponse:
        """Calculate live holding values, weights, and asset class allocation."""
        holdings_dicts = [
            {
                "symbol": h.symbol,
                "name": h.name,
                "asset_class": h.asset_class,
                "quantity": h.quantity,
                "average_buy_price": h.average_buy_price,
                "current_price": h.current_price
            }
            for h in portfolio.holdings
        ]

        analytics = calculate_portfolio_weights_and_allocation(holdings_dicts)
        
        # Build enriched holding responses
        enriched_holdings: List[PortfolioHoldingResponse] = []
        for i, h in enumerate(portfolio.holdings):
            metrics = analytics["holdings"][i]
            enriched_holdings.append(
                PortfolioHoldingResponse(
                    id=h.id,
                    portfolio_id=h.portfolio_id,
                    symbol=h.symbol,
                    name=h.name,
                    asset_class=h.asset_class,
                    quantity=h.quantity,
                    average_buy_price=h.average_buy_price,
                    current_price=metrics["current_price"],
                    currency=h.currency,
                    current_value=metrics["current_value"],
                    unrealized_gain_loss=metrics["unrealized_gain_loss"],
                    gain_loss_pct=metrics["gain_loss_pct"],
                    weight_pct=metrics["weight_pct"],
                    last_price_updated_at=h.last_price_updated_at
                )
            )

        return PortfolioResponse(
            id=portfolio.id,
            user_id=portfolio.user_id,
            name=portfolio.name,
            description=portfolio.description,
            currency=portfolio.currency,
            is_default=portfolio.is_default,
            total_cost=analytics["total_cost"],
            total_value=analytics["total_value"],
            total_gain_loss=analytics["total_gain_loss"],
            total_gain_loss_pct=analytics["total_gain_loss_pct"],
            holdings=enriched_holdings,
            asset_class_allocation_pct=analytics["asset_class_allocation_pct"],
            concentration_hhi=analytics["concentration_hhi"],
            top3_concentration_pct=analytics["top3_concentration_pct"],
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at
        )

    def create_portfolio(self, user: User, payload: PortfolioCreate) -> PortfolioResponse:
        p = Portfolio(
            user_id=user.id,
            name=payload.name.strip(),
            description=payload.description,
            currency=payload.currency.upper(),
            is_default=payload.is_default
        )
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return self._enrich_portfolio(p)

    def list_portfolios(self, user: User) -> List[PortfolioResponse]:
        portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == user.id).all()
        if not portfolios:
            # Create default portfolio automatically for new user
            default_p = Portfolio(
                user_id=user.id,
                name="Main Portfolio",
                description="Primary investment portfolio",
                currency=user.preferred_currency,
                is_default=True
            )
            self.db.add(default_p)
            self.db.commit()
            self.db.refresh(default_p)
            portfolios = [default_p]
            
        return [self._enrich_portfolio(p) for p in portfolios]

    def get_portfolio(self, user: User, portfolio_id: str) -> PortfolioResponse:
        p = self.db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        if not p:
            raise NotFoundException("Portfolio", portfolio_id)
        return self._enrich_portfolio(p)

    def add_holding(
        self,
        user: User,
        portfolio_id: str,
        payload: PortfolioHoldingCreate
    ) -> PortfolioHoldingResponse:
        """Add a holding to portfolio. Automatically looks up latest market price."""
        p = self.db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        if not p:
            raise NotFoundException("Portfolio", portfolio_id)

        # Attempt to get latest price from market service
        current_p = payload.average_buy_price
        name = payload.name or payload.symbol
        try:
            quote = self.market_service.get_quote(payload.symbol)
            current_p = quote.price
            name = quote.name or name
        except Exception:
            pass # Keep average_buy_price as initial baseline

        holding = PortfolioHolding(
            portfolio_id=p.id,
            user_id=user.id,
            symbol=payload.symbol.strip().upper(),
            name=name,
            asset_class=payload.asset_class.lower(),
            quantity=to_decimal(payload.quantity),
            average_buy_price=to_decimal(payload.average_buy_price),
            current_price=to_decimal(current_p),
            currency=payload.currency.upper(),
            last_price_updated_at=datetime.now(timezone.utc),
            notes=payload.notes
        )
        self.db.add(holding)
        self.db.commit()
        self.db.refresh(holding)

        val = (holding.quantity * holding.current_price).quantize(Decimal("0.01"))
        cost = (holding.quantity * holding.average_buy_price).quantize(Decimal("0.01"))
        gain = val - cost
        gain_pct = float((gain / cost) * Decimal("100.0")) if cost > 0 else 0.0

        return PortfolioHoldingResponse(
            id=holding.id,
            portfolio_id=holding.portfolio_id,
            symbol=holding.symbol,
            name=holding.name,
            asset_class=holding.asset_class,
            quantity=holding.quantity,
            average_buy_price=holding.average_buy_price,
            current_price=holding.current_price,
            currency=holding.currency,
            current_value=val,
            unrealized_gain_loss=gain,
            gain_loss_pct=round(gain_pct, 2),
            weight_pct=100.0,
            last_price_updated_at=holding.last_price_updated_at
        )

    def delete_holding(self, user: User, portfolio_id: str, holding_id: str) -> bool:
        h = self.db.query(PortfolioHolding).filter(
            PortfolioHolding.id == holding_id,
            PortfolioHolding.portfolio_id == portfolio_id,
            PortfolioHolding.user_id == user.id
        ).first()
        if not h:
            raise NotFoundException("PortfolioHolding", holding_id)
        self.db.delete(h)
        self.db.commit()
        return True

    def generate_risk_report(self, user: User, portfolio_id: str) -> PortfolioRiskReportResponse:
        """
        Generate full portfolio risk analytics:
        - Allocation by asset class
        - Concentration metrics (HHI & Top 3)
        - Historical volatility and max drawdown
        - Stress test scenarios
        """
        portfolio = self.get_portfolio(user, portfolio_id)
        
        # Stress test calculations
        stress_results = simulate_portfolio_stress_scenarios(
            asset_class_allocation=portfolio.asset_class_allocation_pct,
            total_portfolio_value=portfolio.total_value
        )
        stress_items = [
            StressTestScenarioResult(
                scenario_name=s["scenario_name"],
                description=s["description"],
                estimated_impact_pct=s["estimated_impact_pct"],
                estimated_dollar_impact=s["estimated_dollar_impact"],
                projected_portfolio_value=s["projected_portfolio_value"]
            )
            for s in stress_results
        ]

        # Calculate weighted volatility based on asset allocation
        alloc = portfolio.asset_class_allocation_pct
        equity_wt = alloc.get("equity", 0.0) + alloc.get("mutual_fund", 0.0)
        bond_wt = alloc.get("bond", 0.0)
        crypto_wt = alloc.get("crypto", 0.0)
        gold_wt = alloc.get("gold", 0.0)

        # Realistic asset-class historical volatility estimates
        est_vol = (equity_wt * 0.18 + bond_wt * 0.06 + crypto_wt * 0.70 + gold_wt * 0.14) / 100.0
        # Realistic max drawdown
        est_mdd = (equity_wt * -0.35 + bond_wt * -0.12 + crypto_wt * -0.75 + gold_wt * -0.15) / 100.0
        # Est Sharpe ratio assuming 8% equity return, 4.5% bond return, 4.0% risk free rate
        est_ret = (equity_wt * 0.09 + bond_wt * 0.045 + crypto_wt * 0.20 + gold_wt * 0.06) / 100.0
        sharpe = (est_ret - 0.04) / est_vol if est_vol > 0 else 0.0

        # Qualitative risk profile
        if crypto_wt > 25 or est_vol > 0.25:
            risk_label = "AGGRESSIVE / HIGH_VOLATILITY"
        elif equity_wt > 60:
            risk_label = "MODERATE_GROWTH"
        elif bond_wt > 50:
            risk_label = "CONSERVATIVE / CAPITAL_PRESERVATION"
        else:
            risk_label = "BALANCED"

        return PortfolioRiskReportResponse(
            portfolio_id=portfolio.id,
            portfolio_name=portfolio.name,
            total_value=portfolio.total_value,
            asset_class_allocation=portfolio.asset_class_allocation_pct,
            concentration_hhi=portfolio.concentration_hhi,
            top3_concentration_pct=portfolio.top3_concentration_pct,
            annualized_volatility_pct=round(est_vol * 100.0, 2),
            max_drawdown_pct=round(est_mdd * 100.0, 2),
            sharpe_ratio=round(sharpe, 2),
            stress_scenarios=stress_items,
            risk_level_assessment=risk_label,
            disclaimer="Historical volatility and stress test results are educational estimates based on historical asset class performance and do not guarantee future returns or protect against market losses."
        )
