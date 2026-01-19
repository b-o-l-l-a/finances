"""Teller API integration for bank account linking and transaction sync."""

import os
from datetime import datetime
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

# Teller API configuration
TELLER_API_URL = "https://api.teller.io"
TELLER_APPLICATION_ID = os.getenv("TELLER_APPLICATION_ID")
TELLER_CERTIFICATE = os.getenv("TELLER_CERTIFICATE")
TELLER_PRIVATE_KEY = os.getenv("TELLER_PRIVATE_KEY")
TELLER_ENV = os.getenv("TELLER_ENV", "sandbox")


class TellerClient:
    """Client for interacting with the Teller API."""

    def __init__(self, access_token: Optional[str] = None):
        """Initialize the Teller client.

        Args:
            access_token: The access token from Teller Connect enrollment.
                         Required for account/transaction operations.
        """
        self.access_token = access_token
        self.cert = (TELLER_CERTIFICATE, TELLER_PRIVATE_KEY)

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make an authenticated request to the Teller API."""
        url = f"{TELLER_API_URL}{endpoint}"

        # Use access token for authentication (HTTP Basic with token as username)
        auth = (self.access_token, "") if self.access_token else None

        response = requests.request(
            method,
            url,
            cert=self.cert,
            auth=auth,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    def list_accounts(self) -> list[dict]:
        """List all accounts associated with the access token."""
        return self._request("GET", "/accounts")

    def get_account(self, account_id: str) -> dict:
        """Get details for a specific account."""
        return self._request("GET", f"/accounts/{account_id}")

    def get_account_balances(self, account_id: str) -> dict:
        """Get balance information for an account."""
        return self._request("GET", f"/accounts/{account_id}/balances")

    def list_transactions(self, account_id: str, count: int = 100) -> list[dict]:
        """List transactions for an account.

        Args:
            account_id: The Teller account ID
            count: Maximum number of transactions to fetch (default 100)
        """
        return self._request("GET", f"/accounts/{account_id}/transactions", params={"count": count})

    def delete_account(self, account_id: str) -> None:
        """Disconnect an account (revoke access)."""
        self._request("DELETE", f"/accounts/{account_id}")


def get_teller_connect_url() -> str:
    """Get the Teller Connect URL for account enrollment."""
    return f"https://teller.io/connect/{TELLER_APPLICATION_ID}"


def parse_teller_date(date_str: str) -> datetime:
    """Parse a date string from Teller API (YYYY-MM-DD format)."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def map_teller_account_type(teller_type: str, teller_subtype: str) -> str:
    """Map Teller account type/subtype to our AccountType enum."""
    # Teller types: depository, credit
    # Teller subtypes: checking, savings, money_market, credit_card, etc.
    if teller_subtype in ("checking", "money_market"):
        return "checking"
    elif teller_subtype == "savings":
        return "savings"
    elif teller_type == "credit" or teller_subtype == "credit_card":
        return "credit"
    return "checking"  # default


def map_teller_institution(institution_id: str, institution_name: str) -> str:
    """Map Teller institution to our Institution enum code."""
    # Map known institutions
    institution_map = {
        "usaa": "usaa",
        "us_bank": "us_bank",
    }

    # Try to match by ID first
    lower_id = institution_id.lower()
    for key, value in institution_map.items():
        if key in lower_id:
            return value

    # Try to match by name
    lower_name = institution_name.lower()
    for key, value in institution_map.items():
        if key.replace("_", " ") in lower_name:
            return value

    # Return the ID as-is if no match (will need to add to enum)
    return institution_id
