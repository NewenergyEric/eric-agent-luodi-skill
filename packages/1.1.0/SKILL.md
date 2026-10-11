---
name: safe-order-summary
description: Summarize the bundled synthetic order fixture locally when verifying this isolated customer setup. Never use this example with real customer data.
---

Run `python -I -S -B scripts/summarize.py assets/orders.csv` from this Skill folder.
Send a JSON object with `currency` and `minimum_total` on stdin.
Example: `{"currency":"USD","minimum_total":0}`.
Return the order count, total, and largest qualifying order. Package version: 1.1.0.
This fixture is synthetic; no network, credentials, or customer files are needed.
Running this script alone does not prove that an Agent has loaded this Skill.
