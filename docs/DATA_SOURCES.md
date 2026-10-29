# WealthOS AI — External Data Sources & Provenance Policy

## 1. Principles of Data Provenance

In strict compliance with non-negotiable rule 2.1:
- WealthOS AI **never fabricates market prices**, synthetic ticker histories, or fictitious financial reports.
- All live quotes, historical closing prices, and dividend yields are fetched through verified data providers.
- Data observations are persisted with exact fetch timestamps and provider attribution (`data_source`).

## 2. Integrated Providers

### 2.1 Live Market Data Adapter (`YahooFinanceAdapter`)
- **Primary Source:** Public Yahoo Finance Chart API (`query1.finance.yahoo.com/v8/finance/chart/{symbol}`).
- **Supported Instruments:**
  - Equities: `SPY`, `VTI`, `AAPL`, `MSFT`, `GOOGL`, etc.
  - Fixed Income ETFs: `BND`, `AGG`, `TLT`, `SHY`.
  - Commodities: `GLD`, `SLV`, `USO`.
  - Cryptocurrencies: `BTC-USD`, `ETH-USD`, `SOL-USD`.
- **Payload Extraction:**
  - `regularMarketPrice`: Current real-time transaction price.
  - `fiftyTwoWeekHigh`, `fiftyTwoWeekLow`: 52-week price extremes.
  - `historical_prices`: Timestamped daily closing prices and volumes used for historical volatility and drawdown calculations.
- **Failover & Caching:**
  - Market quotes are cached in `market_observations` table with timestamped snapshots.
  - If network or external rate-limiting interrupts live calls, the adapter retrieves the most recent verified observation from the database and flags `"data_source": "cached_observation"`.

## 3. Regulatory Knowledge Documents

The internal Retrieval-Augmented Generation (RAG) system indexes verified documents stored in `data/knowledge/`:
1. `sip_and_compounding.md`: Mechanics of Dollar-Cost Averaging, mathematical compounding, and market timing hazards.
2. `budgeting_and_emergency_funds.md`: 50/30/20 budget framework, emergency cushion sizing (3-6 months), and liquid cash yields.
3. `asset_allocation_and_risk.md`: Modern Portfolio Theory, uncorrelated assets, diversification, bond duration, and crypto volatility risks.

All knowledge chunks are tagged with unique identifiers, source titles, and categories, allowing the AI Assistant to output clickable citations with every grounded answer.
