import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unittest
import datetime
from main import audit

AS_OF = datetime.date(2026, 11, 15)

def row(ssid, guest, expiry, sponsor="ayesha"):
    return {"ssid": ssid, "guest_name": guest, "expiry_date": expiry,
            "sponsor": sponsor}

class TestGuestWifiAuditor(unittest.TestCase):
    def test_expired(self):
        r, _ = audit([row("Guest-WiFi", "Visitor A", "2026-11-01")], AS_OF)
        self.assertEqual(r[0][3], "EXPIRED")
        self.assertIn("14 day(s) ago", r[0][4])

    def test_expiring_soon(self):
        r, _ = audit([row("Guest-WiFi", "Visitor B", "2026-11-20")], AS_OF)
        self.assertEqual(r[0][3], "EXPIRING SOON")

    def test_active(self):
        r, _ = audit([row("Guest-WiFi", "Visitor C", "2026-12-15")], AS_OF)
        self.assertEqual(r[0][3], "ACTIVE")

    def test_exactly_seven_days_is_expiring_soon(self):
        r, _ = audit([row("Guest-WiFi", "Visitor D", "2026-11-22")], AS_OF)
        self.assertEqual(r[0][3], "EXPIRING SOON")

    def test_eight_days_is_active(self):
        r, _ = audit([row("Guest-WiFi", "Visitor E", "2026-11-23")], AS_OF)
        self.assertEqual(r[0][3], "ACTIVE")

    def test_expiry_today_is_expiring_soon(self):
        r, _ = audit([row("Guest-WiFi", "Visitor F", "2026-11-15")], AS_OF)
        self.assertEqual((r[0][3], r[0][5]), ("EXPIRING SOON", 0))

    def test_longest_expired_first(self):
        r, _ = audit([row("Guest-WiFi", "A", "2026-11-10"),
                      row("Guest-WiFi", "B", "2026-10-20")], AS_OF)
        self.assertEqual(r[0][1], "B")

    def test_invalid_date_is_skipped(self):
        r, skipped = audit([row("Guest-WiFi", "Bad", "soon"),
                            row("Guest-WiFi", "Good", "2026-12-01")], AS_OF)
        self.assertEqual((len(r), skipped), (1, 1))

    def test_empty_input(self):
        self.assertEqual(audit([], AS_OF), ([], 0))
