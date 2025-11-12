"""
Interactive DeFi Agent Session

This script demonstrates the DeFi Agent with a clean, guided interface.
It auto-executes safe read-only commands and provides a reference for
transactional commands you can try in the interactive REPL.
"""

import sys
sys.path.insert(0, '.')

from agent import Agent
from agent.display import (
    section_header,
    subsection_header,
    info_box,
    command_list,
    tip_box,
)


def main():
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. WELCOME & INITIALIZATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print(section_header("DeFi Agent Interactive Session"))

    # Initialize agent
    agent = Agent()

    # Show wallet info
    info_lines = [
        f"Wallet:  {agent.wallet.address}",
        f"Network: {agent.network.upper()}",
        f"Asset:   {agent.config['asset']}",
    ]
    print(info_box(info_lines))
    print()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. CURRENT STATE (auto-executed)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print(section_header("Current State"))
    agent.show_state()

    print(subsection_header("Positions"))
    agent.show_positions()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. AVAILABLE COMMANDS (reference only)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print(section_header("Available Commands"))

    commands = [
        ('agent.deploy_capital(10)', 'Deploy 10% of idle USDC to best vault'),
        ('agent.redeem("SparkUSDCV", 50)', 'Redeem 50% from a position'),
        ('agent.redeem_all()', 'Redeem all positions'),
        ('agent.show_state()', 'Refresh state display'),
        ('agent.show_positions()', 'Refresh positions'),
        ('agent.help()', 'Show detailed help'),
    ]

    print(command_list(commands))
    print()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4. TIPS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    tips = [
        "Type 'agent.help()' for detailed command reference and examples",
        "Minimum deposit: $0.10 USDC",
        "Press Ctrl+D (or Ctrl+Z on Windows) to exit",
    ]

    print(tip_box(tips))
    print()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 5. INTERACTIVE REPL
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print(section_header("Interactive Mode"))
    print("The 'agent' variable is ready. Try the commands above!\n")

    # Drop into interactive mode with agent available
    import code
    code.interact(local=locals(), banner="")


if __name__ == "__main__":
    main()
