"""
Vault selection logic
Chooses best vault from filtered opportunities
"""

from typing import Optional, Tuple, List
from .criteria import VaultCriteria


class VaultSelector:
    """Selects best vault for deployment"""

    def __init__(self, criteria: VaultCriteria):
        """Initialize with criteria"""
        self.criteria = criteria

    def select_vault(
        self,
        opportunities: List[dict],
        positions: List[dict]
    ) -> Tuple[Optional[dict], str]:
        """
        Select best vault from opportunities
        Returns (vault, reason) or (None, error_message)

        Provides detailed feedback for failures (requirement Q25)
        """
        if not opportunities:
            return None, "No deposit options available from API (requirement Q7)"

        # Apply vault whitelist
        filtered_by_whitelist = self.criteria.apply_vault_whitelist(opportunities)
        whitelist_filtered_count = len(opportunities) - len(filtered_by_whitelist)

        if not filtered_by_whitelist:
            return None, f"All {len(opportunities)} vaults filtered by whitelist"

        # Exclude existing positions (diversification)
        filtered_final = self.criteria.exclude_existing_positions(
            filtered_by_whitelist,
            positions
        )
        existing_position_count = len(filtered_by_whitelist) - len(filtered_final)

        if not filtered_final:
            details = []
            if whitelist_filtered_count > 0:
                details.append(f"{whitelist_filtered_count} not in whitelist")
            if existing_position_count > 0:
                details.append(f"{existing_position_count} already have positions")

            error_msg = "No suitable vaults found. "
            if details:
                error_msg += "Filters: " + ", ".join(details)

            return None, error_msg

        # Select first vault (already sorted by APY descending)
        selected = filtered_final[0]
        reason = f"Selected {selected['vault_name']} with {selected['apy']*100:.2f}% APY"

        return selected, reason
