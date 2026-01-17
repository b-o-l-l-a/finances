"""Plaid API integration service."""

from datetime import date, timedelta

import plaid
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

from finances.config import config


def get_plaid_client() -> plaid_api.PlaidApi:
    """Create and return a Plaid API client."""
    env_map = {
        "sandbox": plaid.Environment.Sandbox,
        "production": plaid.Environment.Production,
    }

    configuration = plaid.Configuration(
        host=env_map.get(config.PLAID_ENV, plaid.Environment.Sandbox),
        api_key={
            "clientId": config.PLAID_CLIENT_ID,
            "secret": config.PLAID_SECRET,
        },
    )

    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def create_link_token(user_id: str = "user-1") -> str:
    """
    Create a Link token for initializing Plaid Link.

    Args:
        user_id: Unique identifier for the user (can be any string for personal use)

    Returns:
        The link token string to pass to Plaid Link
    """
    client = get_plaid_client()

    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(client_user_id=user_id),
        client_name="Personal Finance Tracker",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language="en",
    )

    response = client.link_token_create(request)
    return response.link_token


def exchange_public_token(public_token: str) -> tuple[str, str]:
    """
    Exchange a public token from Plaid Link for an access token.

    Args:
        public_token: The public token received from Plaid Link

    Returns:
        Tuple of (access_token, item_id)
    """
    client = get_plaid_client()

    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)

    return response.access_token, response.item_id


def get_transactions(
    access_token: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict]:
    """
    Fetch transactions for an account.

    Args:
        access_token: The Plaid access token for the account
        start_date: Start of date range (default: 30 days ago)
        end_date: End of date range (default: today)

    Returns:
        List of transaction dictionaries
    """
    client = get_plaid_client()

    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    transactions = []
    total_transactions = None
    offset = 0

    # Paginate through all transactions
    while total_transactions is None or offset < total_transactions:
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(
                offset=offset,
                count=500,  # Max per request
            ),
        )

        response = client.transactions_get(request)
        transactions.extend(response.transactions)

        total_transactions = response.total_transactions
        offset = len(transactions)

    return transactions


def get_accounts(access_token: str) -> list[dict]:
    """
    Fetch accounts for an item.

    Args:
        access_token: The Plaid access token

    Returns:
        List of account dictionaries
    """
    client = get_plaid_client()

    # Use transactions_get to also get accounts (included in response)
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=date.today() - timedelta(days=1),
        end_date=date.today(),
    )

    response = client.transactions_get(request)
    return response.accounts
