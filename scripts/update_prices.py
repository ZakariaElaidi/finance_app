"""Daily price updater. Run locally (python scripts/update_prices.py) or from GitHub Actions."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import market_data  # noqa: E402

if __name__ == "__main__":
    report = market_data.update_all()
    for r in report:
        if r["source"]:
            status = f"{r['source']:<8} {r['rows']:>3} rows  last close {r['last_close']:.2f}"
        else:
            status = "NO DATA"
        print(f"{r['company']:<20} {status}")

    if market_data.ERRORS:
        print("\n--- provider errors (paste this log if something shows NO DATA) ---")
        for e in market_data.ERRORS:
            print(" *", e)

    if not any(r["source"] for r in report):
        sys.exit(1)
