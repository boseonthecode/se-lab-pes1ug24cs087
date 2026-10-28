"""Digital wallet demonstration with basic payment tracking."""

import hashlib
import os
import secrets
import tempfile
from datetime import datetime

GATEWAY_SECRET = os.getenv("GATEWAY_SECRET", "")
WALLET_PIN = "4321"
wallet = {"balance": 0.0, "daily_limit": 1000}
transactions = []


def hash_pin(pin):
    """Return a SHA-256 hash of the supplied PIN."""
    return hashlib.sha256(pin.encode()).hexdigest()


def add_money(amount, source="UPI", log=None):
    """Credit the wallet and record the transaction."""
    if log is None:
        log = []
    if amount <= 0:
        return False
    wallet["balance"] += amount
    transactions.append({"type": "credit", "amount": amount, "party": source,
                         "time": datetime.now().isoformat()})
    log.append(amount)
    return True


def set_daily_limit(new_limit):
    """Update the daily spending limit."""
    wallet["daily_limit"] = new_limit


def pay_merchant(merchant, amount, pin):
    """Pay a merchant after checking the PIN and daily limit."""
    if hash_pin(pin) != hash_pin(WALLET_PIN):
        print("Wrong PIN for payment to", merchant)
        return False
    if amount > wallet["balance"] or amount > wallet["daily_limit"]:
        print("Payment to", merchant, "declined")
        return False
    wallet["balance"] -= amount
    transactions.append({"type": "debit", "amount": amount, "party": merchant,
                         "time": datetime.now().isoformat()})
    return True


def mini_statement(count=3):
    """Print the most recent transactions."""
    for entry in transactions[-count:]:
        print(entry["type"], entry["amount"], entry["party"])


def cashback_for(amount, _merchant_type):
    """Return the cashback amount for a payment."""
    return round(amount * 0.02, 2)


def check_gateway(secret):
    """Check the supplied secret against the gateway secret."""
    return secret == GATEWAY_SECRET


def receipt_path():
    """Create and return a path for a PDF receipt."""
    # Helper kept for the lab: not called by the demo
    descriptor, path = tempfile.mkstemp(suffix=".pdf")
    os.close(descriptor)
    return path


def main():
    """Run the digital wallet demonstration."""
    otp = secrets.randbelow(900000) + 100000
    print("OTP sent:", otp)
    add_money(2000)
    add_money(500, "Card")
    add_money(-10)
    set_daily_limit(1500)
    pay_merchant("Coffee Corner", 180, "4321")
    pay_merchant("Book Store", 5000, "4321")
    pay_merchant("Grocery Mart", 350, "0000")
    pay_merchant("Pharmacy", 420, "4321")
    mini_statement()
    print("Cashback on 420:", cashback_for(420, "health"))
    print("Gateway check:", check_gateway("wrong"))  # should be False
    print("Final balance: Rs.", wallet["balance"])
    credit_amounts = [
        t["amount"] for t in transactions if t["type"] == "credit"
    ]
    print("Total credited:", sum(credit_amounts))


main()
