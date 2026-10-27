#!/usr/bin/env python3
"""Restaurant Tip Calculator.

Asks for a bill amount and a tip percentage, then prints the tip and the
total rounded to 2 decimal places. Bad input never crashes the program:
the user gets a friendly message and is asked again.

Design notes
------------
* Uses ``decimal.Decimal`` instead of ``float`` so money maths is exact
  (e.g. 15% of 19.99 is never off by a fraction of a cent).
* Calculation logic (pure functions) is separate from input/output so it
  can be unit-tested.
* Optional extras: split the bill between several people, repeat runs.

Run:      python tip_calculator.py
Test:     python -m unittest -v
"""

from __future__ import annotations

import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

NUMBER_RE = re.compile(r"[+-]?(\d+\.?\d*|\.\d+)")
CENT = Decimal("0.01")
MAX_BILL = Decimal("1000000")
MAX_TIP_PERCENT = Decimal("100")
MAX_PEOPLE = 100
QUICK_TIPS = (Decimal("10"), Decimal("15"), Decimal("20"))


# --------------------------------------------------------------------------
# Pure logic (no input/print) -> easy to test
# --------------------------------------------------------------------------
def parse_decimal(text: str) -> Decimal:
    """Convert user text to a finite Decimal.

    Accepts things people really type: ' 1,250.50 ', '$40', '15%'.
    Raises ValueError for anything that is not an ordinary number
    (including 'nan', 'inf' and '1e999', which Decimal would accept).
    """
    cleaned = text.strip().replace(",", "").replace("$", "").rstrip("%").strip()
    if not cleaned:
        raise ValueError("empty input")
    if not NUMBER_RE.fullmatch(cleaned):  # blocks 'nan', 'inf', '1e999'
        raise ValueError(f"{text!r} is not a number")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"{text!r} is not a number") from None


def money(value: Decimal) -> Decimal:
    """Round to 2 decimal places the way a cashier would (half up)."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_tip(bill: Decimal, percent: Decimal, people: int = 1) -> dict:
    """Return tip, total and per-person figures, all rounded to 2 dp."""
    if bill < 0:
        raise ValueError("bill cannot be negative")
    if percent < 0:
        raise ValueError("tip percentage cannot be negative")
    if people < 1:
        raise ValueError("people must be at least 1")

    tip = money(bill * percent / 100)
    total = money(bill + tip)
    return {
        "bill": money(bill),
        "percent": percent,
        "tip": tip,
        "total": total,
        "people": people,
        "tip_each": money(tip / people),
        "total_each": money(total / people),
    }


# --------------------------------------------------------------------------
# Input helpers
# --------------------------------------------------------------------------
def ask(prompt: str, lower: Decimal, upper: Decimal, what: str,
        integer: bool = False) -> Decimal:
    """Keep asking until the user gives a valid number in range.

    Typing 'q' quits the program cleanly.
    """
    while True:
        raw = input(prompt)
        if raw.strip().lower() in {"q", "quit", "exit"}:
            raise SystemExit("Goodbye!")
        try:
            value = parse_decimal(raw)
        except ValueError:
            print(f"  ! That is not a number. Please type digits only, "
                  f"e.g. {'3' if integer else '45.50'}.")
            continue
        if integer and value != value.to_integral_value():
            print(f"  ! {what} must be a whole number.")
            continue
        if not lower <= value <= upper:
            print(f"  ! {what} must be between {lower} and {upper}.")
            continue
        return value


def show(result: dict) -> None:
    """Print the receipt-style summary."""
    line = "-" * 34
    print(f"\n{line}")
    print(f"  Bill           : {result['bill']:>12,.2f}")
    print(f"  Tip ({result['percent']:g}%)".ljust(17) + f": {result['tip']:>12,.2f}")
    print(f"  Total          : {result['total']:>12,.2f}")
    if result["people"] > 1:
        print(f"  Split {result['people']} ways:")
        print(f"    Tip each     : {result['tip_each']:>12,.2f}")
        print(f"    Pay each     : {result['total_each']:>12,.2f}")
    print(line)


def main() -> int:
    print("=== Restaurant Tip Calculator ===")
    print("(type q at any prompt to quit)\n")
    while True:
        bill = ask("Bill amount: ", Decimal("0"), MAX_BILL, "The bill")
        percent = ask(
            f"Tip percentage (common: {', '.join(f'{t:g}' for t in QUICK_TIPS)}): ",
            Decimal("0"), MAX_TIP_PERCENT, "The tip percentage",
        )
        people = int(ask("Split between how many people? ",
                         Decimal("1"), Decimal(MAX_PEOPLE),
                         "The number of people", integer=True))
        show(calculate_tip(bill, percent, people))
        again = input("\nAnother calculation? (y/n): ").strip().lower()
        if again not in {"y", "yes"}:
            print("Thank you for using the Tip Calculator!")
            return 0
        print()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        sys.exit(0)
