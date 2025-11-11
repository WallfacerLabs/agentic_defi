"""
Basic usage example: Deploy capital to highest yield vault

Run this from the project root:
    python examples/basic_usage.py
"""

import sys
sys.path.insert(0, '.')

from agent import Agent


def main():
    print("=== DeFi Agent - Basic Usage Example ===\n")

    # Initialize agent
    agent = Agent()

    # Show current state
    agent.show_state()

    # Show idle USDC
    agent.show_idle_assets()

    # Deploy 10% of idle USDC to best vault
    agent.deploy_capital(10)


if __name__ == "__main__":
    main()
