# WealthOS AI — Mathematical & Financial Formulations

WealthOS AI executes all monetary calculations deterministically using `decimal.Decimal` to eliminate binary floating-point roundoff errors. Below are the exact formulations implemented across the platform.

## 1. Cash Flow & Budgeting Formulas

- **Net Cash Flow / Surplus:**
  $$S = \sum \text{Income} - \sum \text{Expenses}$$

- **Savings Rate Percentage:**
  $$\text{Savings Rate} = \frac{S}{\sum \text{Income}} \times 100\%$$

- **50/30/20 Framework:**
  - Needs $\le 50\%$ of Net Income (Rent, essential groceries, utilities, debt minimums).
  - Wants $\le 30\%$ of Net Income (Dining out, streaming, travel, discretionary hobbies).
  - Savings & Debt Acceleration $\ge 20\%$ of Net Income.

## 2. Savings & Future Wealth Accumulation

- **Compound Interest with Recurring Monthly Contributions (SIP):**
  $$FV = P \left(1 + \frac{r}{n}\right)^{nt} + PMT \left[ \frac{\left(1 + \frac{r}{n}\right)^{nt} - 1}{\frac{r}{n}} \right]$$
  Where:
  - $P$ = Starting principal
  - $PMT$ = Recurring monthly contribution
  - $r$ = Nominal annual interest rate
  - $n$ = Compounding periods per year ($12$ for monthly)
  - $t$ = Investment horizon in years

- **Inflation Purchasing-Power Discount (Real Wealth):**
  $$\text{Real } FV = \frac{FV}{(1 + i)^t}$$
  Where $i$ is the annual inflation rate.

- **Required Monthly Contribution for Fixed Goal Deadline:**
  $$PMT = \frac{FV - P(1 + r/n)^{nt}}{\left[ \frac{(1 + r/n)^{nt} - 1}{r/n} \right]}$$

## 3. Loan Financing & Installment Payments

- **Fixed-Rate Equal Monthly Installment (EMI):**
  $$PMT = P \times \left[ \frac{r(1 + r)^n}{(1 + r)^n - 1} \right]$$
  Where:
  - $P$ = Financed loan principal (Purchase price minus down payment)
  - $r$ = Monthly interest rate ($\frac{\text{APR}}{12 \times 100}$)
  - $n$ = Total tenure in months

- **Total Interest Paid Over Loan Term:**
  $$\text{Total Interest} = (PMT \times n) - P$$

## 4. Portfolio Risk & Concentration Analytics

- **Asset Holding Weight:**
  $$w_i = \frac{V_i}{\sum_{j=1}^k V_j}$$

- **Herfindahl-Hirschman Concentration Index (HHI):**
  $$HHI = \sum_{i=1}^k w_i^2$$
  - $HHI < 0.15$: Highly Diversified.
  - $0.15 \le HHI \le 0.25$: Moderately Concentrated.
  - $HHI > 0.25$: Highly Concentrated (Warning issued).

- **Annualized Historical Volatility:**
  $$\sigma_{\text{ann}} = \sqrt{252} \times \text{std}(R_{\text{daily}})$$

- **Maximum Drawdown (MDD):**
  $$MDD = \max_{\tau \in (0, T)} \left[ \frac{\max_{t \in (0, \tau)} P_t - P_\tau}{\max_{t \in (0, \tau)} P_t} \right] \times 100\%$$

- **Sharpe Ratio:**
  $$\text{Sharpe} = \frac{R_p - R_f}{\sigma_p}$$
  Where $R_p$ is portfolio return, $R_f$ is the risk-free rate ($4.0\%$ benchmark), and $\sigma_p$ is annualized portfolio volatility.

## 5. Stochastic Monte Carlo Engine (Geometric Brownian Motion)

Wealth paths are modeled in discrete monthly increments ($\Delta t = 1/12$) using Geometric Brownian Motion with drift and continuous compounding:

$$S_{t+\Delta t} = \left( S_t + PMT \right) \times \exp\left( \left(\mu - \frac{1}{2}\sigma^2\right)\Delta t + \sigma \sqrt{\Delta t} Z \right)$$

Where:
- $S_t$ = Portfolio balance at step $t$
- $PMT$ = Periodic inflow
- $\mu$ = Expected annualized return (drift)
- $\sigma$ = Expected annualized volatility (diffusion)
- $Z \sim \mathcal{N}(0, 1)$ = Standard normal random variate
- Percentiles ($P_{10}, P_{25}, P_{50}, P_{75}, P_{90}$) are evaluated across $1,000$ simulated paths sorted at horizon $T$.
- Probability of reaching target:
  $$\mathbb{P}(\text{Goal}) = \frac{1}{M} \sum_{m=1}^M \mathbf{1}_{\{S_T^{(m)} \ge \text{Target}\}}$$

## 6. Financial Health Score (0-100 Points)

The overall financial health score synthesizes seven weighted indicators:

| Dimension | Max Points | Benchmark Target | Score Criteria |
|---|---|---|---|
| Savings Rate | 20 | $\ge 20\%$ of net income | $\ge 20\% \to 20$, $\ge 10\% \to 14$, $> 0\% \to 8$, $\le 0\% \to 0$ |
| Emergency Liquidity | 20 | 3 to 6 months living costs | $\ge 6 \text{ mos} \to 20$, $\ge 3 \text{ mos} \to 14$, $\ge 1 \text{ mo} \to 8$, $< 1 \text{ mo} \to 2$ |
| Budget Adherence | 15 | 0 categories over budget | $0 \text{ over} \to 15$, $1 \text{ over} \to 8$, $\ge 2 \text{ over} \to 2$ |
| Debt-to-Income (DTI) | 15 | Debt service $< 15\%$ income | Debt-free/$\le 15\% \to 15$, $\le 30\% \to 10$, $> 30\% \to 4$ |
| Savings Goal Adherence | 10 | $\ge 80\%$ active goals on track | $\ge 80\% \to 10$, $\ge 50\% \to 7$, $< 50\% \to 3$ |
| Expense Stability | 10 | MoM variance $< 15\%$ | Stable burn rate $\to 8$ to $10$ |
| Multi-Asset Diversification | 10 | Allocation across $\ge 3$ classes | $\ge 3 \text{ classes} \to 10$, $1\text{-}2 \text{ classes} \to 6$ |
| **Total Composite Score** | **100** | **Excellent: 85-100, Good: 70-84, Fair: 55-69, Needs Attention: < 55** |
