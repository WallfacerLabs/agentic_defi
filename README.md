# DeFi Agent

A DeFi capital management agent that demonstrates the mechanics of autonomous DeFi interactions. Manages USDC on Base network, discovers idle capital, analyzes yield opportunities, and deploys capital to the best available vaults.

## Features

- **Gas Validation**: Checks ETH balance upfront before any transaction
- **Idle Asset Detection**: Discovers USDC sitting idle in your wallet
- **Opportunity Discovery**: Finds best yield opportunities with API-side filtering
- **Smart Diversification**: Automatically avoids vaults with existing positions
- **Position Management**: Track positions with human-readable nicknames
- **Full Redemption Flow**: Redeem partial or full amounts from positions
- **x402 Payment Protocol**: Pay-per-use API access with USDC

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd defi_agent
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your private key
# PRIVATE_KEY=0x...
```

4. **Configure settings** (optional):
```bash
# Edit config.yaml to adjust:
# - Minimum APY threshold
# - Minimum TVL threshold
# - Vault whitelist
# - Display settings
```

## Quick Start

### Basic Usage

```python
from agent import Agent

# Initialize agent
agent = Agent()

# Check current state (gas, USDC, positions)
agent.show_state()

# Check idle USDC
agent.show_idle_assets()

# Deploy 10% of idle USDC to best vault
agent.deploy_capital(10)

# View positions
agent.show_positions()

# Redeem 50% from a position (by nickname)
agent.redeem('YearnUSDCV', 50)

# Redeem everything
agent.redeem_all()
```

### Run Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Interactive guide
python examples/interactive.py
```

## Architecture

The agent uses a clean 4-layer architecture:

1. **Orchestration Layer** (`agent.py`)
   - High-level user interface
   - Coordinates between all layers
   - Handles error messages and display

2. **API Layer** (`api/`)
   - x402 payment client
   - Position queries
   - Opportunity discovery
   - Transaction generation

3. **Strategy Layer** (`strategy/`)
   - Vault filtering and selection
   - Diversification logic
   - Whitelist management

4. **Core Layer** (`core/`)
   - Wallet management
   - Transaction signing
   - Gas estimation and validation
   - Transaction broadcasting

## Configuration

### config.yaml

```yaml
# Network Configuration
network: base
asset: USDC
asset_address: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Investment Rules
investment:
  min_deposit_usd: 0.10  # $0.10 minimum

# Vault Selection Criteria
criteria:
  min_apy: 0.01         # 1% minimum APY
  min_tvl: 1000000      # $1M minimum TVL
  apy_interval: "1day"  # Use 1-day APY

# Display Configuration
display:
  decimals: 2                    # USD decimals
  position_retry_attempts: 3     # Retry after deploy
  position_retry_delay: 5        # Wait 5s between retries

# Vault Whitelist (optional)
vault_whitelist: []  # Empty = allow all vaults
```

### Environment Variables (.env)

```bash
PRIVATE_KEY=0x...                              # Your private key
BASE_RPC_URL=https://mainnet.base.org          # Base RPC endpoint
```

## Requirements Addressed

This implementation addresses all 27 requirements from questions.md:

- **Q1**: Check gas (ETH) upfront before transactions
- **Q5**: Minimum deposit amount of $0.10
- **Q7**: Clear error messages for empty deposit options
- **Q10**: Position nicknames (first 10 chars of vault name)
- **Q11**: Single-step redemption only (no multi-step)
- **Q12**: Filter zero-balance positions from display
- **Q17**: Retry position display after deployment (3x, 5s delay)
- **Q23**: Execute multiple transactions (approve + deposit)
- **Q24**: Never revoke approvals on failure
- **Q26**: Display 2 decimal places for USD amounts
- **Q27**: Display 1-day APY everywhere

See [questions.md](questions.md) for full list and detailed discussion.

## API Costs

The agent uses x402 payment protocol for API access. Typical costs:

- `get_idle_assets()`: ~$0.01 USDC
- `get_positions()`: ~$0.01 USDC
- `get_best_deposit_options()`: ~$0.01 USDC
- `generate_deposit_tx()`: ~$0.01 USDC

A full `deploy_capital()` operation costs approximately **$0.04 USDC** in API payments.

## Safety Features

1. **Gas validation**: Checks ETH balance before any transaction
2. **Minimum deposit**: Prevents dust deployments ($0.10 minimum)
3. **Vault whitelist**: Optional restriction to trusted vaults
4. **Automatic diversification**: Never deploys to existing positions
5. **No approval revocation**: If deposit fails, approval stays (user must manually revoke if desired)

## Examples

### Deploy 10% of idle USDC

```python
agent = Agent()
agent.deploy_capital(10)
```

**Output**:
```
=== Deploying 10% of idle capital ===

Checking idle USDC...
Idle USDC: $100.00
Deploy amount: $10.00
Checking existing positions...
Found 0 existing position(s)
Finding best vaults...
Found 15 vault(s)
✓ Selected Yearn USDC Vault with 5.23% APY
Generating transaction(s)...
Generated 2 transaction(s)
Executing transaction(s)...

✓ Deployed $10.00 to Yearn USDC Vault
Transaction 1 (approve): 0x1234...
Transaction 2 (deposit): 0x5678...

Refreshing positions...

=== Current Positions ===

Nickname    Vault Name         Asset  APY        Balance
----------  -----------------  -----  ---------  --------
YearnUSDCV  Yearn USDC Vault   USDC   5.23% (1d) $10.00

Total: $10.00
```

### View Positions

```python
agent = Agent()
agent.show_positions()
```

### Redeem by Nickname

```python
agent = Agent()
agent.redeem('YearnUSDCV', 50)  # Redeem 50%
```

## Documentation

- [architecture.md](architecture.md) - Detailed architecture documentation
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Implementation strategy
- [questions.md](questions.md) - 27 requirements and design decisions

## Notes

- This is a **demonstrative tool**, not an autonomous agent
- User explicitly calls each method
- No background operation or scheduling
- Designed for Base network and USDC only
- Stateless design (queries fresh state each time)

## License

MIT

## Contributing

This is a showcase project. For production use, consider:
- Adding comprehensive test suite
- Implementing multi-chain support
- Adding historical tracking
- Implementing advanced strategies
- Adding position rebalancing

---

**Built with Claude Code** 🤖
