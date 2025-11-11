"""
Interactive guide for using the DeFi Agent

This file demonstrates all available commands with explanations.

Run this from the project root:
    python examples/interactive.py
"""

import sys
sys.path.insert(0, '.')

from agent import Agent


def main():
    print("=== DeFi Agent Interactive Guide ===\n")

    # Initialize agent
    print("1. Initialize the agent:")
    print("   agent = Agent()\n")
    agent = Agent()

    # Show state
    print("2. Check your current state (gas, USDC, positions):")
    print("   agent.show_state()\n")
    agent.show_state()

    # Show positions
    print("3. View your positions:")
    print("   agent.show_positions()\n")
    agent.show_positions()

    # Deploy capital (commented - uncomment to actually deploy)
    print("4. Deploy 10% of idle USDC to best vault:")
    print("   agent.deploy_capital(10)")
    print("   [Command commented - uncomment to execute]\n")
    # agent.deploy_capital(10)

    # Redeem (commented - uncomment to actually redeem)
    print("5. Redeem 50% from a position by nickname:")
    print("   agent.redeem('SparkUSDCV', 50)")
    print("   [Command commented - uncomment to execute]\n")
    # agent.redeem('SparkUSDCV', 50)

    # Redeem all (commented - uncomment to actually redeem all)
    print("6. Redeem all positions:")
    print("   agent.redeem_all()")
    print("   [Command commented - uncomment to execute]\n")
    # agent.redeem_all()

    print("=== End of Guide ===\n")
    print("Dropping into interactive Python REPL...")
    print("The 'agent' variable is available for you to use.\n")
    print("Try commands like:")
    print("  agent.show_state()")
    print("  agent.deploy_capital(10)")
    print("  agent.show_positions()")
    print("\nPress Ctrl+D (or Ctrl+Z on Windows) to exit.\n")

    # Drop into interactive mode with agent available
    import code
    code.interact(local=locals(), banner="")


if __name__ == "__main__":
    main()
