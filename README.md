# Return_routing_engine
Automated return authorization engine that evaluates e-commerce return requests in real time — applying category return-window rules and multi-factor risk scoring (return history, account age, order value, linked-account fraud detection) to auto-approve, flag for review, or reject.

## Requirements

- Python 3.8 or newer (works fine on plain Windows, no WSL needed)

Check your version:
```bash
python --version
```
(On some systems the command is `python3` instead of `python`.)

## Quick start

```bash
python main.py
```

This reads `data/returns.jsonl` and prints one JSON decision per line:
```
{"request_id": "r101", "risk_score": 3, "decision": "AUTO_APPROVE"}
{"request_id": "r103", "risk_score": 60, "decision": "MANUAL_REVIEW", "reason": "MEDIUM_RISK_SCORE"}
{"request_id": "r104", "risk_score": 95, "decision": "REJECT", "reason": "HIGH_RISK_SCORE"}
{"request_id": "r105", "risk_score": null, "decision": "REJECT", "reason": "RETURN_WINDOW_EXPIRED"}
```

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## How it works

1. **Return window check** — if `days_since_purchase` exceeds the category's
   allowed window (`data/category_rules.json`), the request is rejected
   immediately with `RETURN_WINDOW_EXPIRED` and no risk score (`null`).
2. **Risk scoring** — otherwise, three factors are scored and summed using
   `data/scoring_rules.json`:
   - total return history (own + linked accounts, via `data/account_links.jsonl`
     and `data/account_profiles.jsonl`)
   - account age
   - order value
3. **Decision band** — the total score (0–100) is mapped to
   `AUTO_APPROVE` / `MANUAL_REVIEW` / `REJECT` via `data/decision_bands.json`.

## Project structure

```
main.py                    # CLI entry point
returns/
  models.py                 # dataclasses (CategoryRule, ScoringRules, ReturnRequest...)
  parser.py                 # JSON/JSONL parsing
  engine.py                 # Core decisioning logic
  file_io.py                # File read/write helpers
tests/
  test_engine.py             # Unit tests reproducing the README examples
data/
  category_rules.json       # Category return window policies
  scoring_rules.json        # Risk scoring threshold rules
  decision_bands.json       # Score-to-decision mappings
  account_profiles.jsonl    # Account return histories
  account_links.jsonl       # Linked account groups
  returns.jsonl             # Batch of return requests to evaluate
```

## Customizing

All thresholds live in `data/*.json` — edit them without touching any Python
code to tune category windows, scoring bands, or decision cutoffs.

Use your own batch of requests, and optionally write results to a file:
```bash
python main.py --data-dir data --out results.jsonl
```
