# AI Tools & Provider Architecture

## Overview
Veridian IT Copilot abstracts the AI inference layer behind a provider interface (`BaseLLMProvider`), ensuring zero vendor lock-in and allowing switching between providers via a single environment variable: `LLM_PROVIDER`.

---

### Supported Providers

1. **Deterministic Mock Provider (`LLM_PROVIDER=mock`) [Default]**:
   - Zero external API requirements.
   - Grounded directly in `knowledge_base.json` and `seed_tickets.json`.
   - Guaranteed, reproducible responses for all 15 Data Pack scenarios.
   - Ideal for local evaluation, CI/CD automated testing, and offline demonstrations.

2. **OpenAI Provider (`LLM_PROVIDER=openai`)**:
   - Compatible with GPT-4o, GPT-4o-mini, and OpenAI-compatible API proxies.
   - Requires `OPENAI_API_KEY`.
   - Configurable model via `OPENAI_MODEL` (default: `gpt-4o`).

3. **Gemini Provider (`LLM_PROVIDER=gemini`)**:
   - Compatible with Google Gemini 1.5/2.0 API.
   - Requires `GEMINI_API_KEY`.
   - Configurable model via `GEMINI_MODEL` (default: `gemini-1.5-pro`).

---

### Strict Guardrail Rules for Any LLM
Regardless of which LLM provider is active, the following **system constraints** are enforced:
1. **Policy Primacy**: The LLM prompt injection explicitly prohibits overriding company policy or making exceptions not documented in the provided KB.
2. **Deterministic Pre-flight**: Critical decisions (such as P1 phishing warnings, admin privilege denials, or lockout unlock thresholds) are verified by the outer Python rule engine before or alongside LLM synthesis.
3. **Structured Citation**: The agent must output citations in structured JSON containing `policy_id`, `policy_title`, and the exact quote from the Data Pack.
