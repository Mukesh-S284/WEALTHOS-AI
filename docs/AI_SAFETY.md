# WealthOS AI — AI Safety, Governance & Guardrails

## 1. Grounded Financial AI Principles

AI assistant responses in WealthOS AI are bound by three foundational safety principles:

1. **Deterministic Financial Computations (No Hallucinated Math):**
   The LLM is strictly prohibited from performing mental arithmetic or fabricating financial metrics. When a user asks about their spending, purchase affordability, or goal deadlines, the agent is forced to invoke verified deterministic tools from `ai/tools/registry.py` (`get_financial_summary`, `evaluate_purchase`, `calculate_required_monthly_savings`, etc.) which execute python financial engine functions.

2. **Grounded Source Attribution:**
   Educational responses must cite chunks retrieved from the verified knowledge vector store (`data/knowledge/`). The UI renders transparent citation cards detailing the source title and relevant excerpts.

3. **Mandatory Regulatory Disclaimers (Module M):**
   Every assistant response and health report is appended with standard regulatory notices clarifying that WealthOS AI provides educational analysis and scenario simulation, not licensed fiduciary advice or guaranteed returns.

## 2. Prompt Injection Defense

Retrieved documents and external user inputs are passed through `sanitize_retrieved_text` (`ai/retrieval/vector_store.py`) before insertion into prompt templates.

The sanitizer filters:
- Instruction override delimiters (e.g., `IGNORE PREVIOUS INSTRUCTIONS`, `SYSTEM PROMPT OVERRIDE`).
- Markdown and XML injection tags (e.g., `<system>`, `</user>`, `[INST]`).
- Unicode direction override characters and invisible zero-width spaces.

## 3. Controlled Tool Registry

Tool execution is constrained by strict Pydantic argument validation:
- `ToolRegistry` maintains a whitelist of 8 approved deterministic tools.
- Arbitrary code execution (`eval`, `exec`) is completely banned.
- Database access during tool execution is restricted to the authenticated user's tenant scope.

## 4. Scam & Fraud Heuristics

The scam detection engine (`backend/services/scam_service.py`) analyzes user-submitted claims against documented fraud patterns:
- Guaranteed returns without risk (Ponzi schemes).
- Manufactured urgency and FOMO pressure.
- Credential and OTP harvesting.
- Untraceable cryptocurrency and gift card payment demands.
- Multi-level pyramid recruitment matrices.

Every analysis outputs a clear threat score (0-100), risk level, and official verification steps linking to regulatory authorities (FINRA BrokerCheck, SEC Action Lookup, and CFTC RED List).
