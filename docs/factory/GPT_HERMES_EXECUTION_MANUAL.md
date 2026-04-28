# GPT Hermes Execution Manual (No Experimentation)

## Purpose
Force deterministic setup and operation of Hermes Gateway (Telegram) without improvisation.

## Rules
- No new architecture
- No runners
- No assumptions
- Always verify against system state
- One command per step

## Verified Environment
- Hermes installed
- venv: ~/.hermes/venv
- repo: /opt/smartpyme-factory

## Setup Procedure (STRICT)

### 1. Ensure correct binary
cd ~
~/.hermes/venv/bin/hermes --version

### 2. Run gateway setup
cd ~
~/.hermes/venv/bin/hermes gateway setup

MANDATORY:
- Select Telegram (never skip)
- Enter BOT TOKEN
- Choose polling

### 3. Start gateway
cd ~
~/.hermes/venv/bin/hermes gateway start

### 4. Check status
cd ~
~/.hermes/venv/bin/hermes gateway status

Expected:
- running
- telegram active

### 5. Real test
Send message from Telegram → Hermes must receive

## If Telegram NOT visible

Check code:
cd /opt/smartpyme-factory/repos/hermes-agent
search gateway platform list

Conclusion:
Build missing adapter OR conditional hidden

## Stop Conditions
- If step fails → stop and show error
- Do not retry blindly

## Success Criteria
- Hermes receives Telegram messages
- No legacy scripts involved

## Final Rule
If not confirmed in system → does not exist
