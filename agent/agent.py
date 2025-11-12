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
        from .display import format_state_summary

        # Get data
        gas_info = self.executor.check_gas_balance()
        idle_info = self.position_api.get_idle_assets(self.wallet.address)
        positions = self.position_api.get_positions(self.wallet.address)

        # Display with enhanced formatting
        print(format_state_summary(
            gas_info['balance_eth'],
            idle_info['usdc_balance'],
            len(positions)
        ))
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
        from .display import format_positions_table

        positions = self.position_api.get_positions(self.wallet.address)

        if not positions:
            if retry:
                print("  No positions found yet (may be indexing delay)...")
            else:
                print("  No active positions")
            return

        # Use enhanced table formatting
        print(format_positions_table(positions, self.display_decimals))
        print()

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

        # Increase approval amount by 10% buffer to handle vault fees/slippage
        from .utils import increase_approval_buffer
        transactions = increase_approval_buffer(transactions, buffer_percent=10.0)

        print(f"Generated {len(transactions)} transaction(s)")

        # 9. Execute transactions (Q23, Q24)
        print("Executing transaction(s)...")
        try:
            tx_hashes = self.executor.execute_multiple(transactions)

        except Exception as e:
            from .display import format_error
            print(format_error(f"Transaction failed: {str(e)}"))
            return

        # Display success
        from .display import format_deploy_success
        print(format_deploy_success(deploy_amount_usd, selected_vault['vault_name'], tx_hashes, self.display_decimals))

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

        # For 100% redemptions, pass a flag to handle precision issues
        is_full_redemption = (percentage >= 99.99)

        transactions = self.transaction_api.generate_redeem_tx(
            self.wallet.address,
            position['vault_address'],
            redeem_lp_tokens,
            position['lp_decimals'],
            self.asset_address,
            self.network,
            is_full_redemption=is_full_redemption
        )

        # 5. Execute transaction(s)
        print("Executing transaction(s)...")
        try:
            if len(transactions) == 1:
                tx_hash = self.executor.execute(transactions[0])
                tx_hashes = [tx_hash]
            else:
                tx_hashes = self.executor.execute_multiple(transactions)

            # Display success
            from .display import format_redeem_success
            if len(tx_hashes) == 1:
                print(format_redeem_success(redeem_amount_usd, position['vault_name'], tx_hashes[0], self.display_decimals))
            else:
                print(format_redeem_success(redeem_amount_usd, position['vault_name'], tx_hashes[0], self.display_decimals))
                for i in range(1, len(tx_hashes)):
                    print(f"  Transaction {i+1}: {tx_hashes[i]}")

        except Exception as e:
            from .display import format_error
            print(format_error(f"Transaction failed: {str(e)}"))
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

    def help(self):
        """Display help information with available commands"""
        from .display import section_header, subsection_header, command_list, tip_box

        print(section_header("DeFi Agent Help"))

        # Available commands
        commands = [
            ('agent.show_state()', 'Display gas balance, USDC balance, and position count'),
            ('agent.show_positions()', 'Show detailed position table with APY and balances'),
            ('agent.show_idle_assets()', 'Show idle USDC available for deployment'),
            ('agent.deploy_capital(percentage)', 'Deploy % of idle USDC to highest yield vault'),
            ('agent.redeem(nickname, percentage)', 'Redeem % from specific position by nickname'),
            ('agent.redeem_all()', 'Redeem 100% from all active positions'),
            ('agent.help()', 'Show this help message'),
        ]

        print(command_list(commands))

        # Examples
        print("\n" + subsection_header("Examples"))

        examples = [
            "agent.deploy_capital(10)        # Deploy 10% of idle USDC",
            "agent.redeem('SparkUSDCV', 50)  # Redeem 50% from SparkUSDCV",
            "agent.show_positions()          # Refresh position view",
        ]

        for example in examples:
            print(f"  {example}")

        print()

        # Tips
        tips = [
            "Nicknames are first 10 chars of vault name (spaces removed)",
            "Minimum deposit: $0.10 USDC",
            "All transactions require gas (ETH)",
            "Positions may take 5-10 seconds to update after transactions",
        ]

        print(tip_box(tips))
        print()
