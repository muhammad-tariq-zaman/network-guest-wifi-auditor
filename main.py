"""Audit guest Wi-Fi accounts for expiry.

Usage: python3 main.py guests.csv [--as-of 2026-11-15]
CSV columns: ssid,guest_name,expiry_date,sponsor.
expiry_date is YYYY-MM-DD. Verdicts, against --as-of
(default: today):
- EXPIRED: the expiry date has passed — the account should
  already be removed.
- EXPIRING SOON: expiry is within the next 7 days.
- ACTIVE: expiry is more than 7 days away.
EXPIRED first (longest expired first), then EXPIRING SOON
(soonest first), then ACTIVE. Rows with an unparseable
expiry date are reported as skipped, not silently dropped.
"""
import argparse, csv, sys
from datetime import date

SOON_DAYS = 7

def audit(rows, as_of=None):
    as_of = as_of or date.today()
    out = []
    skipped = 0
    for row in rows:
        try:
            ssid = row["ssid"].strip()
            guest = row["guest_name"].strip()
            expiry = date.fromisoformat(row["expiry_date"].strip())
            sponsor = row["sponsor"].strip()
            if not ssid or not guest or not sponsor:
                raise ValueError("missing value")
        except (KeyError, AttributeError, ValueError, TypeError):
            skipped += 1
            continue
        days = (expiry - as_of).days
        if days < 0:
            verdict = "EXPIRED"
            detail = f"expired {-days} day(s) ago ({expiry}), sponsor {sponsor}"
        elif days <= SOON_DAYS:
            verdict = "EXPIRING SOON"
            detail = f"expires in {days} day(s) ({expiry}), sponsor {sponsor}"
        else:
            verdict = "ACTIVE"
            detail = f"expires in {days} day(s) ({expiry}), sponsor {sponsor}"
        out.append((ssid, guest, expiry, verdict, detail, days))
    order = {"EXPIRED": 0, "EXPIRING SOON": 1, "ACTIVE": 2}
    out.sort(key=lambda r: (order[r[3]], r[5], r[0], r[1]))
    return out, skipped

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    parser.add_argument("--as-of", default=None, help="reference date YYYY-MM-DD (default: today)")
    args = parser.parse_args(argv)
    as_of = date.fromisoformat(args.as_of) if args.as_of else None
    with open(args.path, newline="", encoding="utf-8") as f:
        results, skipped = audit(list(csv.DictReader(f)), as_of)
    for ssid, guest, _, verdict, detail, _ in results:
        print(f"{ssid} {guest}: {verdict} - {detail}")
    counts = {v: sum(1 for *_, verdict, _, _ in results if verdict == v)
              for v in ("EXPIRED", "EXPIRING SOON", "ACTIVE")}
    print(f"{counts['EXPIRED']} expired, {counts['EXPIRING SOON']} expiring soon, "
          f"{counts['ACTIVE']} active out of {len(results)} guest account(s).")
    if skipped:
        print(f"Skipped {skipped} invalid row(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
