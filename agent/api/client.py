"""
x402 Payment Protocol Client
Handles pay-per-use API access with USDC payments
"""

import json
import requests
from x402.clients.base import x402Client
from x402.types import x402PaymentRequiredResponse
from x402.encoding import safe_base64_decode


class X402Client:
    """Client for making x402 authenticated API requests"""

    def __init__(self, wallet, base_url: str = "https://api.vaults.fyi"):
        """Initialize x402 client"""
        self.wallet = wallet
        self.base_url = base_url.rstrip('/')
        self.x402_client = x402Client(account=wallet.account)

    def make_request(self, endpoint: str, params: dict = None, timeout: int = 60) -> dict:
        """
        Make x402 authenticated request

        Flow:
        1. Send GET with x-402-auth: true header
        2. Receive 402 with payment requirements
        3. Execute blockchain payment (Base/USDC)
        4. Resend GET with X-Payment proof header
        5. Receive 200 with data
        """
        url = f"{self.base_url}{endpoint}"

        # Step 1: Initial request to trigger 402 (MUST include x-402-auth header)
        headers = {
            'x-402-auth': 'true',
            'Accept': 'application/json'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        # If 402, handle payment
        if response.status_code == 402:
            return self._handle_payment_and_retry(response, url, params, timeout)

        # If 200, return data (no payment required)
        if response.status_code == 200:
            return response.json()

        # Handle errors
        raise Exception(f"API request failed: {response.status_code} {response.text}")

    def _handle_payment_and_retry(self, initial_response, url: str, params: dict, timeout: int) -> dict:
        """Handle x402 payment flow using x402 library"""

        # Step 2-3: Parse payment requirements and make payment
        payment_data = initial_response.json()
        payment_response = x402PaymentRequiredResponse(**payment_data)

        # Select payment requirements (Base/USDC)
        selected_req = self.x402_client.select_payment_requirements(payment_response.accepts)

        # Step 4: Create payment proof header
        payment_header = self.x402_client.create_payment_header(
            selected_req,
            payment_response.x402_version
        )

        # Step 5: Retry with payment proof
        headers = {
            'x-402-auth': 'true',
            'Accept': 'application/json',
            'X-Payment': payment_header
        }

        paid_response = requests.get(url, params=params, headers=headers, timeout=timeout)

        # Handle edge case: API may return 500 error even after successful payment
        if paid_response.status_code == 500 and 'x-payment-response' in paid_response.headers:
            try:
                payment_resp_data = json.loads(
                    safe_base64_decode(paid_response.headers['x-payment-response'])
                )
                if payment_resp_data.get('success'):
                    # Payment succeeded despite 500 error - API bug
                    # Try to return data if available
                    if paid_response.text:
                        try:
                            return paid_response.json()
                        except:
                            pass
            except Exception:
                pass

        # Standard success case
        if paid_response.status_code == 200:
            return paid_response.json()

        # Payment verification failed
        raise Exception(f"Payment verification failed: {paid_response.status_code} {paid_response.text}")
