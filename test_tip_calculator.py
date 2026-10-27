import unittest
from decimal import Decimal as D

from tip_calculator import calculate_tip, money, parse_decimal


class ParseTests(unittest.TestCase):
    def test_plain_and_messy_numbers(self):
        self.assertEqual(parse_decimal("45.5"), D("45.5"))
        self.assertEqual(parse_decimal(" $1,250.50 "), D("1250.50"))
        self.assertEqual(parse_decimal("15%"), D("15"))

    def test_rejects_non_numbers(self):
        for bad in ["", "   ", "abc", "12abc", "nan", "inf", "-inf", "1e999999"]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    parse_decimal(bad)


class CalcTests(unittest.TestCase):
    def test_basic(self):
        r = calculate_tip(D("100"), D("15"))
        self.assertEqual((r["tip"], r["total"]), (D("15.00"), D("115.00")))

    def test_rounding_half_up(self):
        self.assertEqual(money(D("0.125")), D("0.13"))
        self.assertEqual(calculate_tip(D("19.99"), D("15"))["tip"], D("3.00"))

    def test_zero_tip_and_zero_bill(self):
        self.assertEqual(calculate_tip(D("50"), D("0"))["total"], D("50.00"))
        self.assertEqual(calculate_tip(D("0"), D("20"))["total"], D("0.00"))

    def test_split(self):
        r = calculate_tip(D("90"), D("10"), people=3)
        self.assertEqual((r["tip_each"], r["total_each"]), (D("3.00"), D("33.00")))

    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            calculate_tip(D("-1"), D("10"))
        with self.assertRaises(ValueError):
            calculate_tip(D("10"), D("-5"))
        with self.assertRaises(ValueError):
            calculate_tip(D("10"), D("10"), people=0)


if __name__ == "__main__":
    unittest.main()
