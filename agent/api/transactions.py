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

        # Parse transaction actions (tx data is nested under action['tx'])
        transactions = []
        for action in response.get('actions', []):
            tx = action.get('tx', {})
            transactions.append({
                'to': tx.get('to'),
                'data': tx.get('data'),
                'value': tx.get('value', '0'),
            })

        return transactions

    def generate_redeem_tx(
        self,
        user_address: str,
        vault_address: str,
        lp_token_amount: float,
        lp_decimals: int,
        asset_address: str,
        network: str = 'base',
        is_full_redemption: bool = False
    ) -> List[dict]:
        """
        Generate redeem transaction
        Only uses default step (requirement Q11 - no multi-step redemption)

        Args:
            lp_token_amount: Amount of LP tokens to redeem (e.g., 0.5 LP tokens)
            lp_decimals: Decimals of the LP token (usually 18)
            is_full_redemption: If True, subtracts 1 wei to avoid rounding errors
        """
        endpoint = f"/v2/transactions/redeem/{user_address}/{network}/{vault_address}"

        # Convert LP token amount to wei using LP token decimals
        amount_wei = int(lp_token_amount * (10 ** lp_decimals))

        # For 100% redemptions, subtract 1 wei to avoid floating-point precision issues
        # This ensures we never try to redeem more than we actually have
        if is_full_redemption and amount_wei > 0:
            amount_wei -= 1

        params = {
            'amount': amount_wei,
            'assetAddress': asset_address,
        }

        response = self.client.make_request(endpoint, params)

        # Parse transaction actions (use only default step, tx data nested under action['tx'])
        transactions = []
        actions = response.get('actions', [])

        # If multiple steps exist, only use the first/default one (Q11)
        if actions:
            for action in actions:
                tx = action.get('tx', {})
                transactions.append({
                    'to': tx.get('to'),
                    'data': tx.get('data'),
                    'value': tx.get('value', '0'),
                })

        return transactions
