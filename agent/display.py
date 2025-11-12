"""
Display utilities for formatted output
Provides colors, boxes, separators, and highlighting
"""

import sys
from typing import List, Tuple
from tabulate import tabulate


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COLOR SUPPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'

    # Bright variants
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_CYAN = '\033[96m'


def supports_color() -> bool:
    """Check if terminal supports ANSI colors"""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def colorize(text: str, color: str) -> str:
    """Apply color if terminal supports it"""
    if supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION HEADERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def section_header(title: str, width: int = 70) -> str:
    """
    Create a major section header

    Example:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      CURRENT STATE
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    line = "━" * width
    title_formatted = colorize(title.upper(), Colors.CYAN + Colors.BOLD)
    return f"\n{line}\n  {title_formatted}\n{line}\n"


def subsection_header(title: str, width: int = 60) -> str:
    """
    Create a subsection header

    Example:
    ── Positions ──────────────────────
    """
    title_with_space = f" {title} "
    remaining = width - len(title_with_space) - 3  # Account for "── "
    line = "─" * max(remaining, 0)

    title_formatted = colorize(title, Colors.BRIGHT_CYAN)
    return f"── {title_formatted} {line}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VALUE HIGHLIGHTING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def highlight_currency(amount: float, decimals: int = 2) -> str:
    """Format currency with color"""
    formatted = f"${amount:.{decimals}f}"
    return colorize(formatted, Colors.BRIGHT_GREEN)


def highlight_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage with color"""
    formatted = f"{value:.{decimals}f}%"
    return colorize(formatted, Colors.BRIGHT_YELLOW)


def highlight_address(address: str, truncate: bool = True) -> str:
    """Format address (optionally truncated)"""
    if truncate and len(address) > 10:
        display = f"{address[:6]}...{address[-4:]}"
    else:
        display = address

    return colorize(display, Colors.BRIGHT_CYAN)


def highlight_label(text: str) -> str:
    """Format field labels"""
    return colorize(text, Colors.DIM)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOXES & CONTAINERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def info_box(lines: List[str], width: int = 70) -> str:
    """
    Create an info box

    Example:
    ┌────────────────────────────────┐
    │ Wallet:  0x34bf...82F7         │
    │ Network: BASE                  │
    └────────────────────────────────┘
    """
    if not lines:
        return ""

    # Calculate content width
    max_len = max(len(line) for line in lines) if lines else 0
    content_width = min(max_len + 2, width - 4)  # Account for │ padding │

    # Build box
    top = f"┌{'─' * (content_width + 2)}┐"
    bottom = f"└{'─' * (content_width + 2)}┘"

    result = [top]
    for line in lines:
        padded = line.ljust(content_width)
        result.append(f"│ {padded} │")
    result.append(bottom)

    return '\n'.join(result)


def tip_box(tips: List[str]) -> str:
    """
    Create a tips box

    Example:
    💡 Tips
      • Minimum deposit: $0.10 USDC
      • Press Ctrl+D to exit
    """
    if not tips:
        return ""

    header = colorize("💡 Tips", Colors.BRIGHT_YELLOW + Colors.BOLD)
    lines = [header]
    for tip in tips:
        lines.append(f"  • {tip}")

    return '\n'.join(lines)


def command_list(commands: List[Tuple[str, str]]) -> str:
    """
    Format a list of commands with descriptions

    Example:
    agent.deploy_capital(10)         Deploy 10% to best vault
    agent.redeem('SparkUSDCV', 50)   Redeem 50% from position

    Args:
        commands: List of (command, description) tuples
    """
    if not commands:
        return ""

    # Calculate max command length for alignment
    max_cmd_len = max(len(cmd) for cmd, _ in commands)

    lines = []
    for cmd, description in commands:
        # Color the command
        cmd_colored = colorize(cmd, Colors.BRIGHT_CYAN)

        # Calculate padding (need to account for color codes not being visible)
        padding = ' ' * (max_cmd_len - len(cmd) + 3)

        lines.append(f"  {cmd_colored}{padding}{description}")

    return '\n'.join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENHANCED FORMATTERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def format_state_summary(gas_eth: float, usdc_balance: float, position_count: int) -> str:
    """
    Format state summary with highlighting

    Example:
      Gas Balance:      0.004994 ETH
      USDC Balance:     $1.97
      Positions:        2 active
    """
    lines = [
        f"  Gas Balance:      {gas_eth:.6f} ETH",
        f"  USDC Balance:     {highlight_currency(usdc_balance)}",
        f"  Positions:        {position_count} active",
    ]

    return '\n'.join(lines)


def format_positions_table(positions: List[dict], decimals: int = 2) -> str:
    """
    Enhanced positions table with color highlighting

    Args:
        positions: List of position dicts
        decimals: Number of decimal places for USD amounts
    """
    if not positions:
        return "  No active positions"

    # Prepare table data with highlighting
    table_data = []
    total_balance = 0

    for position in positions:
        nickname = colorize(position['nickname'], Colors.BRIGHT_CYAN)
        vault_name = position['vault_name']
        asset = position['asset']
        apy_str = highlight_percentage(position['apy'] * 100) + " (1d)"
        balance_str = highlight_currency(position['balance_usd'], decimals)

        table_data.append([nickname, vault_name, asset, apy_str, balance_str])
        total_balance += position['balance_usd']

    headers = ['Nickname', 'Vault Name', 'Asset', 'APY', 'Balance']
    table = tabulate(table_data, headers=headers, tablefmt='simple')

    # Add blank line and align Total with table
    total_line = f"\nTotal: {highlight_currency(total_balance, decimals)}"

    return f"{table}\n{total_line}"


def format_deploy_success(amount_usd: float, vault_name: str, tx_hashes: List[str], decimals: int = 2) -> str:
    """
    Format deployment success message

    Args:
        amount_usd: Amount deployed in USD
        vault_name: Name of the vault
        tx_hashes: List of transaction hashes
        decimals: Decimal places for USD
    """
    checkmark = colorize("✓", Colors.BRIGHT_GREEN)
    amount = highlight_currency(amount_usd, decimals)

    lines = [
        f"\n{checkmark} Deployed {amount} to {vault_name}"
    ]

    if len(tx_hashes) == 1:
        lines.append(f"  Transaction: {tx_hashes[0]}")
    else:
        for i, tx_hash in enumerate(tx_hashes):
            action_name = "approve" if i == 0 else "deposit"
            lines.append(f"  Transaction {i+1} ({action_name}): {tx_hash}")

    return '\n'.join(lines)


def format_redeem_success(amount_usd: float, vault_name: str, tx_hash: str, decimals: int = 2) -> str:
    """Format redemption success message"""
    checkmark = colorize("✓", Colors.BRIGHT_GREEN)
    amount = highlight_currency(amount_usd, decimals)

    return f"\n{checkmark} Redeemed {amount} from {vault_name}\n  Transaction: {tx_hash}"


def format_error(message: str) -> str:
    """Format error message"""
    cross = colorize("❌", Colors.RED)
    return f"\n{cross} {message}\n"
