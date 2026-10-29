# WealthOS AI — Database Schema & Data Modeling

## 1. Relational Entity Overview

All tables utilize UUID primary keys (`String(36)`) and enforce foreign-key relationships referencing `users.id` with `ondelete="CASCADE"` to prevent orphan records upon account deletion.

```
+---------------------------------------------------------------------------------+
|                                    users                                        |
| id (PK), email (UQ), hashed_password, full_name, preferred_currency, etc.      |
+--------+--------------+---------------+--------------+------------+-------------+
         |              |               |              |            |
         v              v               v              v            v
  +--------------+ +----------+ +---------------+ +----------+ +------------------+
  | transactions | | budgets  | | savings_goals | |  debts   | |   portfolios     |
  +--------------+ +----------+ +-------+-------+ +----------+ +--------+---------+
                                        |                               |
                                        v                               v
                              +--------------------+        +---------------------+
                              |savings_contribut'ns|        | portfolio_holdings  |
                              +--------------------+        +---------------------+
```

## 2. Table Specifications

### 2.1 `users`
- `id`: `String(36)`, Primary Key.
- `email`: `String(255)`, Unique, Not Null, Indexed.
- `hashed_password`: `String(255)`, Bcrypt hash with per-user salt.
- `full_name`: `String(255)`, Nullable.
- `preferred_currency`: `String(3)`, Default `"USD"`.
- `locale`: `String(10)`, Default `"en_US"`.
- `timezone`: `String(50)`, Default `"UTC"`.
- `monthly_income`: `String(20)`, Default `"0.00"`.
- `custom_settings`: `JSON`, Structured preferences.
- `created_at`, `updated_at`: `DateTime(timezone=True)`.

### 2.2 `transactions`
- `id`: `String(36)`, Primary Key.
- `user_id`: `String(36)`, Foreign Key (`users.id`).
- `date`: `Date`, Not Null.
- `description`: `String(255)`, Not Null.
- `amount`: `Numeric(14, 2)`, Not Null (Always positive; sign governed by `type`).
- `type`: `String(10)`, Not Null (`"income"` or `"expense"`).
- `category`: `String(100)`, Not Null.
- `currency`: `String(3)`, Default `"USD"`.
- `is_recurring`: `Boolean`, Default `False`.
- `classification_source`: `String(20)` (`"manual"`, `"rule"`, `"ml"`).
- `classification_confidence`: `Numeric(4, 3)`.
- Indexes: `idx_tx_user_date` (`user_id`, `date`), `idx_tx_user_category` (`user_id`, `category`).

### 2.3 `budgets`
- `id`: `String(36)`, Primary Key.
- `user_id`: `String(36)`, Foreign Key (`users.id`).
- `category`: `String(100)`, Not Null.
- `monthly_limit`: `Numeric(14, 2)`, Not Null.
- `period`: `String(7)`, Not Null (Format `"YYYY-MM"`).
- `alert_threshold_percentage`: `Numeric(5, 2)`, Default `80.0`.
- Constraint: Unique index on `("user_id", "period", "category")`.

### 2.4 `savings_goals` & `savings_contributions`
- `savings_goals`: Target amount, current amount, target date, monthly contribution, annual return %, priority, status (`"active"`, `"completed"`, `"paused"`), category (`"emergency_fund"`, `"house"`, `"car"`, etc.).
- `savings_contributions`: Contribution amount, date, source (`"manual"`, `"roundup"`, `"surplus"`).

### 2.5 `debts`
- `id`: `String(36)`, Primary Key.
- `user_id`: `String(36)`, Foreign Key (`users.id`).
- `name`: `String(150)`, Not Null.
- `debt_type`: `String(50)` (`"credit_card"`, `"student_loan"`, `"mortgage"`, `"auto_loan"`, `"personal_loan"`).
- `principal_amount`: `Numeric(14, 2)`, Not Null.
- `current_balance`: `Numeric(14, 2)`, Not Null.
- `interest_rate_apr`: `Numeric(6, 3)`, Not Null (Annual Percentage Rate).
- `minimum_monthly_payment`: `Numeric(14, 2)`, Not Null.

### 2.6 `portfolios` & `portfolio_holdings`
- `portfolios`: Name, description, is_default, currency.
- `portfolio_holdings`: `user_id` (Mandatory for isolation), `portfolio_id`, `symbol`, `name`, `asset_class` (`"equity"`, `"fixed_income"`, `"cash"`, `"commodities"`, `"crypto"`, `"real_estate"`), `quantity`, `average_buy_price`, `current_price`, `last_price_updated_at`.

### 2.7 `learning_progress`
- `user_id`: Foreign Key (`users.id`).
- `topic_id`: `String(50)`, Not Null.
- `completed`: `Boolean`, Default `False`.
- `quiz_score`: `Integer` (0-100%).
- `quiz_attempts`: `Integer`, Default `0`.
- `last_studied_at`: `DateTime(timezone=True)`.
- Unique Index: `("user_id", "topic_id")`.

### 2.8 `assistant_sessions` & `assistant_messages`
- `assistant_sessions`: `id`, `user_id`, `title`, `created_at`.
- `assistant_messages`: `session_id`, `role` (`"user"`, `"assistant"`, `"system"`), `content`, `tool_calls` (`JSON`), `knowledge_sources` (`JSON`).

### 2.9 `audit_logs`
- Append-only security audit log recording event timestamp, event type, IP address, user agent, and payload summary for sensitive security actions (logins, settings changes, data exports, deletions).
