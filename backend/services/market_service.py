"""Market Data caching and asset-class intelligence service."""

from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.integrations.market_data.base import (
    MarketDataProviderBase,
    InstrumentQuote,
    HistoricalDataSeries,
    MarketDataError
)
from backend.integrations.market_data.yahoo_finance import YahooFinanceAdapter
from backend.models.market import SupportedInstrument, MarketObservation
from backend.schemas.market import (
    QuoteResponse,
    HistoricalSeriesResponse,
    HistoricalBarItem,
    InstrumentSearchItem,
    AssetClassEducation
)
from backend.core.exceptions import NotFoundException, BadRequestException
from finance_engine.budgeting.engine import to_decimal

# Primary market adapter
_yahoo_adapter = YahooFinanceAdapter()

# Educational asset class knowledge
ASSET_CLASSES_INFO = [
    AssetClassEducation(
        key="equity",
        name="Stocks & Equities",
        description="Ownership shares in publicly traded companies offering potential capital appreciation and dividend income.",
        typical_risk_profile="Moderate to High",
        expected_volatility="15% - 22% annualized",
        role_in_portfolio="Primary long-term capital growth engine and inflation hedge.",
        liquidity="Very High (T+1 settlement during market hours)",
        common_benchmarks=["S&P 500 (SPY)", "Total US Stock Market (VTI)", "Nasdaq 100 (QQQ)"]
    ),
    AssetClassEducation(
        key="mutual_fund",
        name="Mutual Funds & SIPs",
        description="Pooled investment vehicles offering broad diversification across equities or bonds. SIP (Systematic Investment Plan) is a disciplined dollar-cost-averaging contribution method.",
        typical_risk_profile="Low to High depending on fund objective",
        expected_volatility="10% - 18% annualized",
        role_in_portfolio="Core diversified holdings with automated periodic contributions.",
        liquidity="High (end-of-day NAV pricing)",
        common_benchmarks=["Vanguard Total Stock Index (VTSAX)", "Fidelity 500 Index (FXAIX)"]
    ),
    AssetClassEducation(
        key="bond",
        name="Bonds & Fixed Income",
        description="Debt securities issued by governments or corporations paying regular coupon interest until principal maturity.",
        typical_risk_profile="Low to Moderate",
        expected_volatility="4% - 8% annualized",
        role_in_portfolio="Capital preservation, predictable income generation, and deflation dampener.",
        liquidity="High (major government & corporate ETFs)",
        common_benchmarks=["Vanguard Total Bond Market (BND)", "iShares Core US Aggregate Bond (AGG)"]
    ),
    AssetClassEducation(
        key="gold",
        name="Gold & Precious Metals",
        description="Physical commodity historically recognized as a store of value and monetary reserve.",
        typical_risk_profile="Moderate",
        expected_volatility="12% - 16% annualized",
        role_in_portfolio="Crisis hedge, tail-risk protector, and currency debasement defense.",
        liquidity="High (physically-backed ETFs like GLD)",
        common_benchmarks=["SPDR Gold Shares (GLD)", "iShares Gold Trust (IAU)"]
    ),
    AssetClassEducation(
        key="crypto",
        name="Cryptocurrency & Digital Assets",
        description="Decentralized digital currencies using cryptographic consensus protocols. Highly speculative.",
        typical_risk_profile="Very High / Speculative",
        expected_volatility="50% - 85% annualized",
        role_in_portfolio="High-risk, asymmetric capital growth allocation (recommended 1% - 5% max of portfolio).",
        liquidity="Continuous 24/7 global trading",
        common_benchmarks=["Bitcoin (BTC-USD)", "Ethereum (ETH-USD)"]
    ),
    AssetClassEducation(
        key="cash_equivalent",
        name="Cash & Deposit Products",
        description="High-yield savings accounts (HYSA), certificates of deposit (CDs), and money market funds offering principal stability.",
        typical_risk_profile="Very Low",
        expected_volatility="0.1% - 0.5% annualized",
        role_in_portfolio="Emergency fund reserve, immediate liquidity, and short-term capital parking.",
        liquidity="Immediate to T+0",
        common_benchmarks=["US 3-Month Treasury Bill (BIL)", "Federal Funds Rate"]
    )
]


class MarketService:
    def __init__(self, db: Session, adapter: Optional[MarketDataProviderBase] = None):
        self.db = db
        self.adapter = adapter or _yahoo_adapter

    def get_asset_classes(self) -> List[AssetClassEducation]:
        return ASSET_CLASSES_INFO

    def get_quote(self, symbol: str) -> QuoteResponse:
        """Fetch quote from provider with caching in market_observations."""
        clean_symbol = symbol.strip().upper()
        
        # Check if we have an observation from today cached
        today = date.today()
        obs = self.db.query(MarketObservation).filter(
            MarketObservation.symbol == clean_symbol,
            MarketObservation.observation_date == today
        ).first()

        if obs and (datetime.now(timezone.utc) - obs.fetched_at).total_seconds() < 900: # 15 min cache
            return QuoteResponse(
                symbol=clean_symbol,
                name=clean_symbol,
                price=obs.close_price,
                change=Decimal("0.00"),
                change_pct=0.0,
                currency="USD",
                asset_class="equity",
                timestamp=obs.fetched_at,
                source=obs.source,
                is_delayed=True
            )

        # Fetch live quote from adapter
        try:
            quote = self.adapter.get_quote(clean_symbol)
            # Cache in db
            if not obs:
                obs = MarketObservation(
                    symbol=clean_symbol,
                    observation_date=today,
                    open_price=quote.price,
                    high_price=quote.price,
                    low_price=quote.price,
                    close_price=quote.price,
                    source=quote.source,
                    fetched_at=quote.timestamp
                )
                self.db.add(obs)
            else:
                obs.close_price = quote.price
                obs.fetched_at = quote.timestamp
            self.db.commit()

            return QuoteResponse(
                symbol=quote.symbol,
                name=quote.name,
                price=quote.price,
                change=quote.change,
                change_pct=quote.change_pct,
                currency=quote.currency,
                asset_class=quote.asset_class,
                timestamp=quote.timestamp,
                source=quote.source,
                is_delayed=quote.is_delayed
            )
        except MarketDataError as e:
            # Fallback to cached observation if available
            cached_recent = self.db.query(MarketObservation).filter(
                MarketObservation.symbol == clean_symbol
            ).order_by(MarketObservation.observation_date.desc()).first()

            if cached_recent:
                return QuoteResponse(
                    symbol=clean_symbol,
                    name=clean_symbol,
                    price=cached_recent.close_price,
                    change=Decimal("0.00"),
                    change_pct=0.0,
                    currency="USD",
                    asset_class="equity",
                    timestamp=cached_recent.fetched_at,
                    source=f"cached_{cached_recent.source}",
                    is_delayed=True
                )
            raise NotFoundException(f"Market quote for symbol '{clean_symbol}'", e)

    def get_historical_series(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> HistoricalSeriesResponse:
        """Fetch historical daily bars from provider."""
        clean_symbol = symbol.strip().upper()
        try:
            series = self.adapter.get_historical_series(clean_symbol, start_date, end_date)
            return HistoricalSeriesResponse(
                symbol=series.symbol,
                currency=series.currency,
                source=series.source,
                start_date=series.start_date,
                end_date=series.end_date,
                data_freshness=series.data_freshness,
                bars=[
                    HistoricalBarItem(
                        date=b.date,
                        open=b.open,
                        high=b.high,
                        low=b.low,
                        close=b.close,
                        volume=b.volume
                    )
                    for b in series.bars
                ]
            )
        except MarketDataError as e:
            raise BadRequestException(f"Unable to retrieve historical market data for '{clean_symbol}': {str(e)}")

    def search_instruments(self, query: str) -> List[InstrumentSearchItem]:
        """Search instruments using provider."""
        items = self.adapter.search_instruments(query)
        return [
            InstrumentSearchItem(
                symbol=it["symbol"],
                name=it["name"],
                exchange=it.get("exchange"),
                asset_class=it.get("asset_class", "equity"),
                currency=it.get("currency", "USD")
            )
            for it in items
        ]
