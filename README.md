# network-guest-wifi-auditor

Audit guest Wi-Fi accounts for expiry: the input CSV lists ssid, guest_name, expiry_date (YYYY-MM-DD) and sponsor — EXPIRED when the expiry date has passed (the account should already be removed), EXPIRING SOON when expiry is within the next 7 days, ACTIVE when expiry is more than 7 days away, all judged against --as-of (default today) — EXPIRED first (longest expired first), then EXPIRING SOON (soonest first), then ACTIVE. Rows with an unparseable expiry date are reported as skipped, not silently dropped.

Sample input is included (sample.csv with six guests, one invalid row).

## How to run

```sh
python3 main.py sample.csv --as-of 2026-11-15
```

## Example output

```
Guest-WiFi Visitor D: EXPIRED - expired 26 day(s) ago (2026-10-20), sponsor omar
Guest-WiFi Visitor A: EXPIRED - expired 14 day(s) ago (2026-11-01), sponsor ayesha
Guest-WiFi Visitor B: EXPIRING SOON - expires in 5 day(s) (2026-11-20), sponsor bilal
Guest-WiFi Visitor E: EXPIRING SOON - expires in 7 day(s) (2026-11-22), sponsor hina
Guest-WiFi Visitor C: ACTIVE - expires in 30 day(s) (2026-12-15), sponsor sara
2 expired, 2 expiring soon, 1 active out of 5 guest account(s).
Skipped 1 invalid row(s).
```

Standard library only. Run the tests with `python3 -m unittest discover`.
