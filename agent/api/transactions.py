"""
Transaction generation API
Generate transaction payloads for deposit and redeem operations
"""

from typing import List


class TransactionAPI:
    """API for generating transaction payloads"""

    def __init__(self, client):
        """Initialize with x402 client"""
        self.client = client

    def generate_deposit_tx(
        self,
        user_address: str,
        vault_address: str,
        amount_tokens: float,
        asset_address: str,
        network: str = 'base'
    ) -> List[dict]:
        """
        Generate deposit transaction(s)
        Returns list of transactions (e.g., approve + deposit)
        """
        endpoint = f"/v2/transactions/deposit/{user_address}/{network}/{vault_address}"

        # Convert amount to wei (USDC has 6 decimals)
        amount_wei = int(amount_tokens * 1e6)

        params = {
            'amount': amount_wei,
            'assetAddress': asset_address,
        }

        response = self.client.make_request(endpoint, params)

        # Parse transaction actions
        transactions = []
        for action in response.get('actions', []):
            transactions.append({
                'to': action.get('to'),
                'data': action.get('data'),
                'value': action.get('value', '0'),
            })

        return transactions

    def generate_redeem_tx(
        self,
        user_address: str,
        vault_address: str,
        amount_tokens: float,
        asset_address: str,
        network: str = 'base'
    ) -> List[dict]:
        """
        Generate redeem transaction
        Only uses default step (requirement Q11 - no multi-step redemption)
        """
        endpoint = f"/v2/transactions/redeem/{user_address}/{network}/{vault_address}"

        # Convert amount to wei (USDC has 6 decimals)
        amount_wei = int(amount_tokens * 1e6)

        params = {
            'amount': amount_wei,
            'assetAddress': asset_address,
            'step': 'default',  # Only use default step (Q11)
        }

        response = self.client.make_request(endpoint, params)

        # Parse transaction actions (use only default step)
        transactions = []
        actions = response.get('actions', [])

        # If multiple steps exist, only use the first/default one (Q11)
        if actions:
            for action in actions:
                transactions.append({
                    'to': action.get('to'),
                    'data': action.get('data'),
                    'value': action.get('value', '0'),
                })

        return transactions
