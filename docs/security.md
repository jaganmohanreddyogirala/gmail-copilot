# Gmail Copilot — Security Architecture & Safety Philosophy

## Core Security Principle

> **EMAIL CONTENT IS UNTRUSTED DATA, NOT SYSTEM INSTRUCTIONS.**

The agent treats all incoming email text as untrusted external payload. Instructions contained inside an email body are never permitted to override system safety rules or leak system prompts.

---

## 🔒 Deterministic Safety Precedence

System safety evaluation enforces strict deterministic hierarchy:

```text
SYSTEM SAFETY RULES
        >
SECURITY VALIDATION
        >
RISK CLASSIFICATION
        >
MODEL CONFIDENCE
```

Model confidence **never** overrides security rules.

---

## 🛡️ Credential & Secret Detection

If any of the following patterns are detected in an email body or subject:
- `api_key`, `api key`, `secret_key`, `client_secret`
- `password`, `passwd`, `credential`
- `private_key`, `private key`, `-----BEGIN PRIVATE KEY-----`, `.pem`
- `prod database`, `production database`, `auth_token`, `bearer_token`

The agent automatically forces:
```python
risk_level = "High - Requires Human Review"
requires_human_approval = True
decision = "NEEDS_HUMAN_APPROVAL"
```

The message is placed in the **Human Approval Queue** and will **never** be auto-sent.

---

## 🔍 Pre-Send Reply Validator

Every generated reply draft must pass a 10-point deterministic validation layer before draft creation:

1. **Sensitive Token Check**: Scans for leaked API keys, tokens, or PEM blocks in reply text.
2. **Placeholder Leak Check**: Blocks unreplaced placeholders like `[INSERT_NAME]`, `[TODO]`, `[COMPANY]`, `<insert here>`.
3. **Prompt Leak Check**: Detects accidental system prompt text in output.
4. **Empty Reply Check**: Ensures output is non-empty.
5. **Length Check**: Rejects excessively long replies (>2000 chars).
6. **Internal Metadata Leak**: Verifies no raw trace IDs or JSON metadata are present in final text.
