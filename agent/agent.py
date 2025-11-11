"""
Main Agent class - Orchestration layer
Coordinates all operations and provides user interface
"""

import yaml
import time
from tabulate import tabulate
from typing import List

from .core import Wallet, TransactionExecutor
from .api import X402Client, PositionAPI, OpportunityAPI, TransactionAPI
from .strategy import VaultCriteria, VaultSelector


def format_usd(amount: float, decimals: int = 2) -> str:
    """Format USD amount (requirement Q26)"""
    return f"${amount:.{decimals}f}"


def format_apy(apy: float) -> str:
    """Format APY as percentage"""
    return f"{apy * 100:.2f}%"


class Agent:
    """DeFi Capital Management Agent"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize agent with configuration"""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize core components
        self.wallet = Wallet()
        self.executor = TransactionExecutor(self.wallet)

        # Initialize API clients
        api_url = self.config.get('vaults_api_url', 'https://api.vaults.fyi')
        self.x402_client = X402Client(self.wallet, api_url)
        self.position_api = PositionAPI(self.x402_client)
        self.opportunity_api = OpportunityAPI(self.x402_client)
        self.transaction_api = TransactionAPI(self.x402_client)

        # Initialize strategy
        self.criteria = VaultCriteria(self.config)
        self.selector = VaultSelector(self.criteria)

        # Configuration shortcuts
        self.asset_address = self.config['asset_address']
        self.network = self.config['network']
        self.min_deposit_usd = self.config['investment']['min_deposit_usd']
        self.display_decimals = self.config['display']['decimals']
        self.retry_attempts = self.config['display']['position_retry_attempts']
        self.retry_delay = self.config['display']['position_retry_delay']

    def show_state(self):
        """
        Display current state: gas, USDC balance, positions (requirement Q1)
        """
        print("\n=== Current State ===\n")

        # Check gas balance
        gas_info = self.executor.check_gas_balance()
        print(f"Gas Balance: {gas_info['balance_eth']:.6f} ETH")

        # Check USDC balance
        idle_info = self.position_api.get_idle_assets(self.wallet.address)
        print(f"USDC Balance: {format_usd(idle_info['usdc_balance'], self.display_decimals)}")

        # Check positions
        positions = self.position_api.get_positions(self.wallet.address)
        print(f"Active Positions: {len(positions)}")

        print()

    def show_idle_assets(self):
        """Display idle USDC balance"""
        print("\n=== Idle Assets ===\n")

        idle_info = self.position_api.get_idle_assets(self.wallet.address)
        usdc_balance = idle_info['usdc_balance']

        print(f"Idle USDC: {format_usd(usdc_balance, self.display_decimals)}")
        print()

    def show_positions(self, retry: bool = False):
        """
        Display current positions (requirement Q17 - retry logic)
        Filters zero-balance positions (requirement Q12)
        Shows 1-day APY (requirement Q27)
        2 decimal places for USD (requirement Q26)
        """
        positions = self.position_api.get_positions(self.wallet.address)

        if not positions:
            if retry:
                print("No positions found yet (may be indexing delay)...")
            else:
                print("\nNo active positions\n")
            return

        print("\n=== Current Positions ===\n")

        # Prepare table data
        table_data = []
        total_balance = 0

        for position in positions:
            table_data.append([
                position['nickname'],
                position['vault_name'],
                position['asset'],
                format_apy(position['apy']) + " (1d)",  # Q27: 1-day APY
                format_usd(position['balance_usd'], self.display_decimals),  # Q26: 2 decimals
            ])
            total_balance += position['balance_usd']

        # Print table
        headers = ['Nickname', 'Vault Name', 'Asset', 'APY', 'Balance']
        print(tabulate(table_data, headers=headers, tablefmt='simple'))
        print(f"\nTotal: {format_usd(total_balance, self.display_decimals)}\n")

    def deploy_capital(self, percentage: float):
        """
        Deploy X% of idle capital to best vault
        Implements all requirements: Q1, Q5, Q7, Q17, Q23, Q24, Q26
        """
        print(f"\n=== Deploying {percentage}% of idle capital ===\n")

        # 1. Check gas balance upfront (Q1)
        is_sufficient, error_msg = self.executor.validate_gas_balance()
        if not is_sufficient:
            print(f"❌ {error_msg}\n")
            return

        # 2. Get idle assets
        print("Checking idle USDC...")
        idle_info = self.position_api.get_idle_assets(self.wallet.address)
        idle_usdc = idle_info['usdc_balance']
        idle_tokens = idle_info['balance_tokens']

        print(f"Idle USDC: {format_usd(idle_usdc, self.display_decimals)}")

        # 3. Calculate deploy amount
        deploy_amount_usd = idle_usdc * (percentage / 100)
        deploy_amount_tokens = idle_tokens * (percentage / 100)

        print(f"Deploy amount: {format_usd(deploy_amount_usd, self.display_decimals)}")

        # 4. Validate minimum deposit (Q5)
        if deploy_amount_usd < self.min_deposit_usd:
            print(f"❌ Deposit amount {format_usd(deploy_amount_usd, self.display_decimals)} "
                  f"below minimum {format_usd(self.min_deposit_usd, self.display_decimals)}\n")
            return

        # 5. Get existing positions
        print("Checking existing positions...")
        positions = self.position_api.get_positions(self.wallet.address)
        print(f"Found {len(positions)} existing position(s)")

        # 6. Get opportunities
        print("Finding best vaults...")
        opportunities = self.opportunity_api.get_best_deposit_options(
            self.wallet.address,
            self.config['criteria']
        )
        print(f"Found {len(opportunities)} vault(s)")

        # 7. Select vault
        selected_vault, reason = self.selector.select_vault(opportunities, positions)

        if selected_vault is None:
            print(f"❌ {reason}\n")
            return

        print(f"✓ {reason}")

        # 8. Generate transaction(s)
        print("Generating transaction(s)...")
        transactions = self.transaction_api.generate_deposit_tx(
            self.wallet.address,
            selected_vault['vault_address'],
            deploy_amount_tokens,
            self.asset_address,
            self.network
        )
        print(f"Generated {len(transactions)} transaction(s)")

        # 9. Execute transactions (Q23, Q24)
        print("Executing transaction(s)...")
        try:
            tx_hashes = self.executor.execute_multiple(transactions)

            # Display success
            print(f"\n✓ Deployed {format_usd(deploy_amount_usd, self.display_decimals)} "
                  f"to {selected_vault['vault_name']}")

            # Show transaction hashes
            if len(tx_hashes) == 1:
                print(f"Transaction: {tx_hashes[0]}")
            else:
                for i, tx_hash in enumerate(tx_hashes):
                    action_name = "approve" if i == 0 else "deposit"
                    print(f"Transaction {i+1} ({action_name}): {tx_hash}")

        except Exception as e:
            print(f"\n❌ Transaction failed: {str(e)}\n")
            return

        # 10. Display positions with retry (Q17)
        print("\nRefreshing positions...")
        self._show_positions_with_retry()

    def _show_positions_with_retry(self):
        """
        Show positions with retry logic (requirement Q17)
        Retry up to 3 times with 5 second delays
        """
        for attempt in range(1, self.retry_attempts + 1):
            positions = self.position_api.get_positions(self.wallet.address)

            if positions:
                self.show_positions()
                return

            if attempt < self.retry_attempts:
                print(f"Attempt {attempt}/{self.retry_attempts}: No positions yet, retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)
            else:
                print(f"Position not showing after {self.retry_attempts} attempts (may take longer to index)\n")

    def redeem(self, position_nickname: str, percentage: float = 100.0):
        """
        Redeem from position by nickname (requirement Q10)
        Single-step redemption only (requirement Q11)
        """
        print(f"\n=== Redeeming {percentage}% from {position_nickname} ===\n")

        # 1. Check gas balance upfront (Q1)
        is_sufficient, error_msg = self.executor.validate_gas_balance()
        if not is_sufficient:
            print(f"❌ {error_msg}\n")
            return

        # 2. Get positions and find by nickname
        print("Finding position...")
        positions = self.position_api.get_positions(self.wallet.address)

        position = None
        for p in positions:
            if p['nickname'] == position_nickname:
                position = p
                break

        if position is None:
            print(f"❌ Position '{position_nickname}' not found\n")
            print("Available positions:")
            for p in positions:
                print(f"  - {p['nickname']}: {p['vault_name']}")
            print()
            return

        print(f"Found: {position['vault_name']}")

        # 3. Calculate redeem amount (in LP tokens, not asset tokens!)
        redeem_lp_tokens = position['balance_lp_tokens'] * (percentage / 100)
        redeem_amount_usd = position['balance_usd'] * (percentage / 100)

        print(f"Redeem amount: {format_usd(redeem_amount_usd, self.display_decimals)} ({redeem_lp_tokens:.6f} LP tokens)")

        # 4. Generate transaction (Q11 - single step only)
        print("Generating redemption transaction...")
        transactions = self.transaction_api.generate_redeem_tx(
            self.wallet.address,
            position['vault_address'],
            redeem_lp_tokens,
            position['lp_decimals'],
            self.asset_address,
            self.network
        )

        # 5. Execute transaction(s)
        print("Executing transaction(s)...")
        try:
            if len(transactions) == 1:
                tx_hash = self.executor.execute(transactions[0])
                print(f"\n✓ Redeemed {format_usd(redeem_amount_usd, self.display_decimals)} "
                      f"from {position['vault_name']}")
                print(f"Transaction: {tx_hash}")
            else:
                tx_hashes = self.executor.execute_multiple(transactions)
                print(f"\n✓ Redeemed {format_usd(redeem_amount_usd, self.display_decimals)} "
                      f"from {position['vault_name']}")
                for i, tx_hash in enumerate(tx_hashes):
                    print(f"Transaction {i+1}: {tx_hash}")

        except Exception as e:
            print(f"\n❌ Transaction failed: {str(e)}\n")
            return

        # Show updated positions
        print()
        self.show_positions()

    def redeem_all(self):
        """Redeem 100% from all positions"""
        print("\n=== Redeeming all positions ===\n")

        positions = self.position_api.get_positions(self.wallet.address)

        if not positions:
            print("No positions to redeem\n")
            return

        print(f"Found {len(positions)} position(s) to redeem\n")

        for i, position in enumerate(positions, 1):
            print(f"[{i}/{len(positions)}] Redeeming from {position['vault_name']}...")
            self.redeem(position['nickname'], 100.0)
            print()

        print("✓ All positions redeemed\n")
