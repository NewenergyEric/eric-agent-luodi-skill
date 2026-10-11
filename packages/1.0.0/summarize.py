"""Sum the bundled synthetic orders. No network, secrets, or file writes."""
import csv
from decimal import Decimal
import json
from pathlib import Path
import sys


def main():
    config = json.load(sys.stdin)
    with Path(sys.argv[1]).open(encoding="utf-8", newline="") as stream:
        amounts = [Decimal(row["amount"]) for row in csv.DictReader(stream)]
    selected = [amount for amount in amounts if amount >= config["minimum_total"]]
    result = {"currency": config["currency"], "order_count": len(selected),
              "total": format(sum(selected, Decimal(0)), ".2f"), "version": "1.0.0"}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
