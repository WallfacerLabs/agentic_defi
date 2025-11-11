"""
Basic test to verify implementation
"""

import sys
sys.path.insert(0, '.')

print("Testing DeFi Agent implementation...\n")

# Test imports
print("1. Testing imports...")
try:
    from agent import Agent
    from agent.core import Wallet, TransactionExecutor
    from agent.api import X402Client, PositionAPI, OpportunityAPI, TransactionAPI
    from agent.strategy import VaultCriteria, VaultSelector
    print("   ✓ All imports successful\n")
except Exception as e:
    print(f"   ✗ Import failed: {e}\n")
    sys.exit(1)

# Test wallet initialization
print("2. Testing wallet initialization...")
try:
    wallet = Wallet()
    print(f"   ✓ Wallet initialized: {wallet.address}\n")
except Exception as e:
    print(f"   ✗ Wallet initialization failed: {e}\n")
    sys.exit(1)

# Test agent initialization
print("3. Testing Agent initialization...")
try:
    agent = Agent()
    print(f"   ✓ Agent initialized\n")
    print(f"   - Wallet address: {agent.wallet.address}")
    print(f"   - Network: {agent.network}")
    print(f"   - Asset: {agent.config['asset']}")
    print(f"   - Min deposit: ${agent.min_deposit_usd}")
    print()
except Exception as e:
    print(f"   ✗ Agent initialization failed: {e}\n")
    sys.exit(1)

# Test gas balance check
print("4. Testing gas balance check...")
try:
    gas_info = agent.executor.check_gas_balance()
    print(f"   ✓ Gas balance: {gas_info['balance_eth']:.6f} ETH")
    print(f"   - Sufficient: {gas_info['sufficient']}")
    print()
except Exception as e:
    print(f"   ✗ Gas check failed: {e}\n")
    sys.exit(1)

print("=" * 50)
print("✓ All basic tests passed!")
print("=" * 50)
print("\nReady to use! Try:")
print("  python examples/interactive.py")
print("  python examples/basic_usage.py")
print("\nOr use in Python REPL:")
print("  from agent import Agent")
print("  agent = Agent()")
print("  agent.show_state()")
