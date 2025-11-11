"""
x402 Payment Protocol Client
Handles pay-per-use API access with USDC payments
"""

import requests
from web3 import Web3
from eth_account.messages import encode_defunct


class X402Client:
    """Client for making x402 authenticated API requests"""

    def __init__(self, wallet, base_url: str = "https://api.vaults.fyi"):
        """Initialize x402 client"""
        self.wallet = wallet
        self.base_url = base_url.rstrip('/')
        self.w3 = Web3()  # For signing messages

    def make_request(self, endpoint: str, params: dict = None) -> dict:
        """
        Make x402 authenticated request
        Handles the 402 payment flow automatically
        """
        url = f"{self.base_url}{endpoint}"

        # Make initial request
        response = requests.get(url, params=params)

        # If 402, handle payment
        if response.status_code == 402:
            return self._handle_payment_and_retry(response, url, params)

        # If successful, return data
        if response.status_code == 200:
            return response.json()

        # Handle errors
        raise Exception(f"API request failed: {response.status_code} {response.text}")

    def _handle_payment_and_retry(self, initial_response, url: str, params: dict) -> dict:
        """Handle x402 payment flow"""
        # Get payment details from 402 response headers
        payment_address = initial_response.headers.get('X-Payment-Address')
        payment_amount = initial_response.headers.get('X-Payment-Amount')
        payment_message = initial_response.headers.get('X-Payment-Message')

        if not all([payment_address, payment_amount, payment_message]):
            raise Exception("Missing x402 payment headers")

        # Sign the payment message
        message = encode_defunct(text=payment_message)
        signed_message = self.wallet.account.sign_message(message)
        signature = signed_message.signature.hex()

        # Retry request with payment proof
        headers = {
            'X-Payment-Signature': signature,
            'X-Payment-Address': self.wallet.address,
        }

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            return response.json()

        raise Exception(f"Payment verification failed: {response.status_code} {response.text}")
