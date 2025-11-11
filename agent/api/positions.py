"""
Position management API
Query user's current positions and idle assets
"""

from typing import List


def generate_nickname(vault_name: str) -> str:
    """Generate 10-char nickname from vault name (requirement Q10)"""
    return vault_name.replace(" ", "")[:10]


class PositionAPI:
    """API for querying positions and idle assets"""

    def __init__(self, client):
        """Initialize with x402 client"""
        self.client = client

    def get_positions(self, wallet_address: str) -> List[dict]:
        """
        Get user's vault positions
        Filters out zero-balance positions (requirement Q12)
        Generates nicknames (requirement Q10)
        """
        endpoint = f"/v2/portfolio/positions/{wallet_address}"
        params = {
            'network': 'base',
            'asset': 'USDC'
        }

        response = self.client.make_request(endpoint, params)

        # Parse positions
        positions = []
        for position in response.get('positions', []):
            # Filter out zero-balance positions (Q12)
            balance_usd = float(position.get('balanceUsd', 0))
            if balance_usd <= 0:
                continue

            # Generate nickname (Q10)
            vault_name = position.get('vaultName', '')
            nickname = generate_nickname(vault_name)

            positions.append({
                'vault_address': position.get('vaultAddress'),
                'vault_name': vault_name,
                'nickname': nickname,
                'asset': position.get('asset'),
                'apy': float(position.get('apy1d', 0)),  # 1-day APY (Q27)
                'balance_usd': balance_usd,
                'balance_tokens': float(position.get('balanceTokens', 0)),
                'network': position.get('network'),
            })

        return positions

    def get_idle_assets(self, wallet_address: str) -> dict:
        """Get user's idle USDC balance"""
        endpoint = f"/v2/portfolio/idle-assets/{wallet_address}"
        params = {
            'network': 'base',
            'asset': 'USDC'
        }

        response = self.client.make_request(endpoint, params)

        # Find USDC balance
        for asset in response.get('assets', []):
            if asset.get('symbol') == 'USDC' and asset.get('network') == 'base':
                return {
                    'usdc_balance': float(asset.get('balanceUsd', 0)),
                    'balance_tokens': float(asset.get('balanceTokens', 0)),
                }

        # No USDC found
        return {
            'usdc_balance': 0.0,
            'balance_tokens': 0.0,
        }
