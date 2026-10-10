"""Daily price updater. Run locally (python scripts/update_prices.py) or from GitHub Actions."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from market_data import update_all  # noqa: E402

if __name__ == "__main__":
    report = update_all()
    for r in report:
        status = f"{r['source']:<7} {r['rows']:>3} rows  last close {r['last_close']:.2f}" if r["source"] else "NO DATA (check symbol in market_data.TICKERS)"
        print(f"{r['company']:<20} {status}")
    if not any(r["source"] for r in report):
        sys.exit(1)
