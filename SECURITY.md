# Security Policy — WealthOS AI

WealthOS AI is designed with defense-in-depth principles to protect sensitive personal financial records and prevent unauthorized cross-tenant data leakage.

## 1. Security Architecture

### 1.1 Authentication & Session Management
- Passwords are encrypted using **Bcrypt** with unique per-user salts and a work factor of 12. Plaintext passwords are never logged, cached, or persisted.
- Sessions are authenticated via signed **JSON Web Tokens (JWT)** using the HS256 algorithm with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- Tokens must be transmitted via the `Authorization: Bearer <token>` header over TLS/HTTPS.

### 1.2 Multi-Tenant Data Isolation
- Strict database-level isolation is enforced across all tables (`transactions`, `budgets`, `savings_goals`, `debts`, `portfolios`, `portfolio_holdings`, `learning_progress`, `assistant_sessions`, `audit_logs`).
- Every query filters by `user_id == current_user.id`.
- Automated security integration tests (`tests/security/test_user_isolation.py`, `tests/security/test_transaction_isolation.py`) systematically verify that unauthorized cross-user access attempts result in 404 or 403 status codes.

### 1.3 Rate Limiting & Denial-of-Service Protection
- Sensitive endpoints (such as `/api/v1/auth/login` and `/api/v1/auth/register`) are rate-limited per IP address using in-memory token-bucket tracking to mitigate brute-force password guessing.

### 1.4 Input Sanitization & Error Handling
- All incoming payloads are strictly validated against Pydantic models with type bounds, regex checks, and decimal precision enforcement.
- Global exception handlers catch unhandled server errors and output standardized, opaque error JSON, preventing internal database stack traces or system environment variables from leaking to clients.

### 1.5 Prompt Injection & LLM Guardrails
- Assistant input and retrieved knowledge chunks are sanitized to neutralize instruction override sequences and markdown escaping.
- The AI Assistant is constrained to deterministic tool execution (`ai/tools/registry.py`) with whitelisted functions and Pydantic argument validation.

## 2. Reporting a Vulnerability

If you identify a security vulnerability in WealthOS AI, please report it responsibly:
- Email: `security@wealthos.ai`
- Include detailed reproduction steps, request payloads, and affected versions.
- Do not disclose security vulnerabilities publicly until an official remediation patch has been released.
