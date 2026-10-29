"""Yahoo Finance Market Data Adapter implementation."""

from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
import httpx

from backend.integrations.market_data.base import (
    MarketDataProviderBase,
    InstrumentQuote,
    HistoricalPriceBar,
    HistoricalDataSeries,
    MarketDataError
)


def _classify_asset_class(symbol: str) -> str:
    s = symbol.upper()
    if s in ("BTC-USD", "ETH-USD", "SOL-USD") or s.endswith("-USD"):
        return "crypto"
    if s in ("GLD", "IAU", "GOLD"):
        return "gold"
    if s in ("BND", "TLT", "AGG", "SHY", "IEF", "VCIT"):
        return "bond"
    if s in ("VTSAX", "VFIAX", "FXAIX", "SWPPX"):
        return "mutual_fund"
    return "equity"


class YahooFinanceAdapter(MarketDataProviderBase):
    """Real HTTP client connecting to Yahoo Finance Chart API."""

    def __init__(self, timeout: float = 6.0):
        self._timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    @property
    def provider_name(self) -> str:
        return "yahoo_finance"

    def get_quote(self, symbol: str) -> InstrumentQuote:
        """Fetch latest quote from chart API."""
        clean_symbol = symbol.strip().upper()
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}?range=5d&interval=1d"

        try:
            with httpx.Client(timeout=self._timeout, headers=self.headers) as client:
                resp = client.get(url)
                if resp.status_code == 404:
                    raise MarketDataError(f"Instrument '{clean_symbol}' not found on Yahoo Finance.", self.provider_name, clean_symbol)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            raise MarketDataError(f"Failed to fetch quote for '{clean_symbol}': {str(e)}", self.provider_name, clean_symbol)

        try:
            chart = data["chart"]["result"][0]
            meta = chart["meta"]
            current_price = Decimal(str(round(meta.get("regularMarketPrice", 0.0), 4)))
            prev_close = Decimal(str(round(meta.get("chartPreviousClose", meta.get("previousClose", current_price)), 4)))
            change = current_price - prev_close
            change_pct = float((change / prev_close) * 100.0) if prev_close > 0 else 0.0
            
            instrument_name = meta.get("shortName") or meta.get("longName") or clean_symbol
            currency = meta.get("currency", "USD").upper()

            return InstrumentQuote(
                symbol=clean_symbol,
                name=instrument_name,
                price=current_price,
                change=change,
                change_pct=round(change_pct, 2),
                currency=currency,
                asset_class=_classify_asset_class(clean_symbol),
                timestamp=datetime.now(timezone.utc),
                source=self.provider_name,
                is_delayed=True
            )
        except (KeyError, IndexError, Exception) as e:
            raise MarketDataError(f"Malformed quote payload for '{clean_symbol}': {str(e)}", self.provider_name, clean_symbol)

    def get_historical_series(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> HistoricalDataSeries:
        """Fetch historical daily bars."""
        clean_symbol = symbol.strip().upper()
        p1 = int(datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc).timestamp())
        # add 1 day to end_date to ensure inclusive query
        p2 = int(datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc).timestamp())
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}?period1={p1}&period2={p2}&interval=1d"

        try:
            with httpx.Client(timeout=self._timeout, headers=self.headers) as client:
                resp = client.get(url)
                if resp.status_code == 404:
                    raise MarketDataError(f"Instrument '{clean_symbol}' not found.", self.provider_name, clean_symbol)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            raise MarketDataError(f"Failed to fetch historical series for '{clean_symbol}': {str(e)}", self.provider_name, clean_symbol)

        try:
            chart = data["chart"]["result"][0]
            meta = chart["meta"]
            currency = meta.get("currency", "USD").upper()
            timestamps = chart.get("timestamp", [])
            indicators = chart["indicators"]["quote"][0]
            
            opens = indicators.get("open", [])
            highs = indicators.get("high", [])
            lows = indicators.get("low", [])
            closes = indicators.get("close", [])
            volumes = indicators.get("volume", [])

            bars: List[HistoricalPriceBar] = []
            for i, ts in enumerate(timestamps):
                c = closes[i] if i < len(closes) else None
                if c is None:
                    continue # skip market holidays / null bars
                bar_date = datetime.fromtimestamp(ts, tz=timezone.utc).date()
                if bar_date < start_date or bar_date > end_date:
                    continue

                bars.append(
                    HistoricalPriceBar(
                        date=bar_date,
                        open=Decimal(str(round(opens[i], 4))) if i < len(opens) and opens[i] is not None else None,
                        high=Decimal(str(round(highs[i], 4))) if i < len(highs) and highs[i] is not None else None,
                        low=Decimal(str(round(lows[i], 4))) if i < len(lows) and lows[i] is not None else None,
                        close=Decimal(str(round(c, 4))),
                        volume=int(volumes[i]) if i < len(volumes) and volumes[i] is not None else None
                    )
                )

            return HistoricalDataSeries(
                symbol=clean_symbol,
                currency=currency,
                source=self.provider_name,
                bars=bars,
                start_date=start_date,
                end_date=end_date,
                data_freshness=datetime.now(timezone.utc)
            )
        except (KeyError, IndexError, Exception) as e:
            raise MarketDataError(f"Error parsing historical series for '{clean_symbol}': {str(e)}", self.provider_name, clean_symbol)

    def search_instruments(self, query: str) -> List[Dict[str, Any]]:
        """Search instruments using Yahoo Finance search API."""
        clean_q = query.strip()
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={clean_q}&quotesCount=6&newsCount=0"

        try:
            with httpx.Client(timeout=self._timeout, headers=self.headers) as client:
                resp = client.get(url)
                resp.raise_for_status()
                data = resp.json()
                quotes = data.get("quotes", [])
                results = []
                for q in quotes:
                    sym = q.get("symbol")
                    if sym:
                        results.append({
                            "symbol": sym,
                            "name": q.get("shortname") or q.get("longname") or sym,
                            "exchange": q.get("exchange", ""),
                            "asset_class": _classify_asset_class(sym),
                            "currency": "USD"
                        })
                return results
        except Exception:
            return []
