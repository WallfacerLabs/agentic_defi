"""
Vault filtering criteria
Client-side filtering for vault whitelist and diversification
"""

from typing import List


class VaultCriteria:
    """Handles client-side vault filtering"""

    def __init__(self, config: dict):
        """Initialize with configuration"""
        self.vault_whitelist = config.get('vault_whitelist', [])

    def apply_vault_whitelist(self, vaults: List[dict]) -> List[dict]:
        """
        Filter vaults by whitelist
        If whitelist is empty, return all vaults
        """
        if not self.vault_whitelist:
            return vaults

        filtered = []
        for vault in vaults:
            if vault['vault_address'] in self.vault_whitelist:
                filtered.append(vault)

        return filtered

    def exclude_existing_positions(
        self,
        vaults: List[dict],
        positions: List[dict]
    ) -> List[dict]:
        """
        Exclude vaults where user already has positions
        Enables automatic diversification
        """
        existing_vault_addresses = {p['vault_address'] for p in positions}

        filtered = []
        for vault in vaults:
            if vault['vault_address'] not in existing_vault_addresses:
                filtered.append(vault)

        return filtered
