"""
Opportunity discovery API
Find best yield opportunities using API-side filtering
"""

from typing import List


class OpportunityAPI:
    """API for discovering yield opportunities"""

    def __init__(self, client):
        """Initialize with x402 client"""
        self.client = client

    def get_best_deposit_options(
        self,
        wallet_address: str,
        criteria: dict
    ) -> List[dict]:
        """
        Get best deposit options with API-side filtering
        Uses 1-day APY (requirement Q27)
        """
        endpoint = f"/v2/portfolio/best-deposit-options/{wallet_address}"

        # Build query parameters from criteria
        params = {
            'allowedAssets': 'USDC',
            'allowedNetworks': 'base',
            'minTvl': criteria.get('min_tvl', 1000000),
            'minApy': criteria.get('min_apy', 0.01),
            'onlyTransactional': 'true',
            'apyInterval': '1day',  # Always 1-day APY (Q27)
            'minUsdAssetValueThreshold': 1,
        }

        response = self.client.make_request(endpoint, params)

        # Parse opportunities
        opportunities = []
        for vault in response.get('vaults', []):
            opportunities.append({
                'vault_address': vault.get('vaultAddress'),
                'vault_name': vault.get('vaultName'),
                'apy': float(vault.get('apy1d', 0)),  # 1-day APY (Q27)
                'tvl': float(vault.get('tvl', 0)),
                'network': vault.get('network'),
                'asset': vault.get('asset'),
            })

        # Sort by APY descending
        opportunities.sort(key=lambda x: x['apy'], reverse=True)

        return opportunities
