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

        # Send API parameters that work (minApy has API bug, apyInterval doesn't affect response)
        params = {
            'allowedAssets': 'USDC',
            'allowedNetworks': 'base',
            'minTvl': criteria.get('min_tvl', 100000),
            'onlyTransactional': 'true' if criteria.get('only_transactional', True) else 'false',
            # Note: minApy causes 400 error (API can't parse string as number)
            # Note: apyInterval doesn't seem to work (apy.1d always None)
        }

        response = self.client.make_request(endpoint, params=params)

        # Parse and filter opportunities client-side
        opportunities = []

        # Find USDC balance and its deposit options
        for user_balance in response.get('userBalances', []):
            asset = user_balance.get('asset', {})

            # Filter for USDC only
            if asset.get('symbol') != 'USDC':
                continue

            # Get deposit options for USDC
            for vault in user_balance.get('depositOptions', []):
                network = vault.get('network', {})
                apy_data = vault.get('apy', {})
                tvl_data = vault.get('tvl', {})

                # Apply filters
                network_name = network.get('name')
                if network_name != 'base':
                    continue

                # Check if transactional if required
                if criteria.get('only_transactional', True):
                    if not vault.get('isTransactional', False):
                        continue

                # Check TVL
                tvl = float(tvl_data.get('usd', 0))
                if tvl < criteria.get('min_tvl', 0):
                    continue

                # Check APY
                apy_total = float(apy_data.get('total', 0))
                if apy_total < criteria.get('min_apy', 0):
                    continue

                opportunities.append({
                    'vault_address': vault.get('address'),
                    'vault_name': vault.get('name'),
                    'apy': apy_total,
                    'tvl': tvl,
                    'network': network_name,
                    'asset': asset.get('symbol'),
                })

        # Sort by APY descending
        opportunities.sort(key=lambda x: x['apy'], reverse=True)

        return opportunities
