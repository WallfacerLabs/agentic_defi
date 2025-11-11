# DeFi Agent Implementation Plan

## Overview
This document outlines a systematic approach to implementing the DeFi Capital Management Agent, addressing all requirements from questions.md and following software engineering best practices.

## Engineering Approach

### Core Principles
1. **Bottom-Up Implementation** - Build foundational layers first (Core → API → Strategy → Orchestration)
2. **Test-As-You-Go** - Validate each component independently before integration
3. **Fail-Fast Philosophy** - Check preconditions early, fail with clear error messages
4. **Incremental Delivery** - Each phase produces working, testable functionality
5. **Stateless Design** - Always query fresh state, no persistent storage

---

## Phase 1: Project Foundation & Core Infrastructure

### 1.1 Project Setup
**Goal**: Establish project structure and dependencies

**Tasks**:
- [ ] Create directory structure matching architecture.md
  ```
  defi_agent/
  ├── agent/
  │   ├── __init__.py
  │   ├── agent.py
  │   ├── api/
  │   │   ├── __init__.py
  │   │   ├── client.py
  │   │   ├── positions.py
  │   │   ├── opportunities.py
  │   │   └── transactions.py
  │   ├── strategy/
  │   │   ├── __init__.py
  │   │   ├── selector.py
  │   │   └── criteria.py
  │   └── core/
  │       ├── __init__.py
  │       ├── executor.py
  │       └── wallet.py
  ├── examples/
  │   ├── basic_usage.py
  │   └── interactive.py
  ├── config.yaml
  ├── .env.example
  └── requirements.txt
  ```
- [ ] Create requirements.txt with dependencies:
  - web3
  - eth-account
  - requests
  - pyyaml
  - python-dotenv
  - tabulate
- [ ] Create .env.example template
- [ ] Create initial config.yaml with defaults

**Testing**: Verify imports work, directory structure is correct

**Requirements Addressed**: Setup foundation for all features

---

### 1.2 Core Layer - Wallet Management
**Goal**: Manage private keys and wallet address

**File**: `agent/core/wallet.py`

**Implementation**:
```python
class Wallet:
    def __init__(self, private_key: str):
        # Load private key
        # Derive address

    def get_address(self) -> str:
        # Return wallet address

    def sign_transaction(self, tx_dict: dict) -> SignedTransaction:
        # Sign transaction with private key
```

**Tasks**:
- [ ] Implement Wallet class
- [ ] Load private key from environment variable
- [ ] Validate private key format
- [ ] Derive Ethereum address
- [ ] Implement transaction signing

**Testing**:
- Create test wallet
- Verify address derivation
- Sign a dummy transaction

**Requirements Addressed**: Foundation for all transaction signing

---

### 1.3 Core Layer - Gas Management
**Goal**: Check gas balance, estimate gas, ensure sufficient ETH

**File**: `agent/core/executor.py`

**Implementation**:
```python
class TransactionExecutor:
    def __init__(self, wallet: Wallet, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.wallet = wallet

    def check_gas_balance(self) -> dict:
        # Get ETH balance
        # Return {'balance_eth': float, 'balance_wei': int, 'sufficient': bool}

    def estimate_gas_cost(self, tx_dict: dict) -> dict:
        # Estimate gas needed
        # Get current gas price
        # Calculate total cost in ETH
        # Return {'gas_limit': int, 'gas_price': int, 'total_eth': float}

    def validate_sufficient_gas(self, tx_dict: dict) -> tuple[bool, str]:
        # Check if user has enough ETH for gas
        # Return (is_sufficient, error_message)
```

**Tasks**:
- [ ] Implement Web3 connection to Base RPC
- [ ] Implement ETH balance check
- [ ] Implement gas estimation for transactions
- [ ] **Requirement Q1**: Add upfront gas validation before any transaction
- [ ] Return clear error messages: "Insufficient ETH for gas. Need 0.0023 ETH, have 0.0010 ETH"

**Testing**:
- Query ETH balance on Base testnet
- Estimate gas for a sample transaction
- Test insufficient gas scenario

**Requirements Addressed**: Q1 (gas check upfront)

---

## Phase 2: API Layer - vaults.fyi Integration

### 2.1 x402 Payment Client
**Goal**: Implement pay-per-use API access

**File**: `agent/api/client.py`

**Implementation**:
```python
class X402Client:
    def __init__(self, wallet: Wallet, base_url: str):
        self.wallet = wallet
        self.base_url = base_url
        self.usdc_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

    def make_request(self, endpoint: str, params: dict = None) -> dict:
        # Make x402 authenticated request
        # Handle payment
        # Return response JSON

    def check_usdc_balance(self) -> float:
        # Query USDC balance from blockchain
        # Return balance in human-readable format (dollars)
```

**Tasks**:
- [ ] Implement x402 payment protocol
- [ ] Handle API authentication
- [ ] Parse response JSON
- [ ] Handle API errors (payment failures, rate limits, etc.)
- [ ] **Requirement Q2**: Don't worry about API payment costs, just execute

**Testing**:
- Make test request to vaults.fyi
- Verify payment goes through
- Check response format

**Requirements Addressed**: Foundation for all API calls, Q2 (accept API costs)

---

### 2.2 Position Queries
**Goal**: Query user's current DeFi positions

**File**: `agent/api/positions.py`

**Implementation**:
```python
class PositionAPI:
    def __init__(self, client: X402Client):
        self.client = client

    def get_positions(self, wallet_address: str) -> list[dict]:
        # Call /users/positions endpoint
        # Parse response
        # Return list of positions with:
        #   - vault address
        #   - vault name
        #   - amount deposited
        #   - current value
        #   - APY
        #   - generated nickname (Q10)

    def get_idle_assets(self, wallet_address: str) -> dict:
        # Call /users/idle-assets endpoint
        # Filter for USDC on Base
        # Return {'usdc_balance': float, 'balance_wei': int}
```

**Tasks**:
- [ ] Implement get_positions()
- [ ] Implement get_idle_assets()
- [ ] Filter for USDC on Base network only
- [ ] **Requirement Q10**: Generate nickname for each position (hash of vault address → memorable name)
- [ ] **Requirement Q12**: Filter out zero-balance positions from display
- [ ] Parse decimal amounts correctly (USDC has 6 decimals)

**Testing**:
- Query positions for a test wallet
- Verify idle assets detection
- Test nickname generation uniqueness

**Requirements Addressed**: Q10 (position nicknames), Q12 (hide zero positions)

---

### 2.3 Opportunity Discovery
**Goal**: Find best yield opportunities

**File**: `agent/api/opportunities.py`

**Implementation**:
```python
class OpportunityAPI:
    def __init__(self, client: X402Client):
        self.client = client

    def get_best_vaults(
        self,
        asset: str = "USDC",
        network: str = "base",
        apy_interval: str = "1day",
        limit: int = 20
    ) -> list[dict]:
        # Call /best-deposit-options endpoint
        # Filter by network and asset
        # Return sorted by APY (descending)
```

**Tasks**:
- [ ] Implement vault discovery
- [ ] **Requirement Q27**: Always use 1-day APY interval
- [ ] Sort by APY descending
- [ ] **Requirement Q7**: Handle empty response gracefully
- [ ] Return clear message: "No deposit options available for USDC on Base. Try adjusting criteria."

**Testing**:
- Query best vaults for USDC on Base
- Verify sorting
- Test empty results scenario

**Requirements Addressed**: Q7 (empty options), Q27 (1-day APY)

---

### 2.4 Transaction Generation
**Goal**: Generate deposit/redeem transaction payloads

**File**: `agent/api/transactions.py`

**Implementation**:
```python
class TransactionAPI:
    def __init__(self, client: X402Client):
        self.client = client

    def generate_deposit_tx(
        self,
        vault_address: str,
        amount_wei: int,
        wallet_address: str
    ) -> list[dict]:
        # Call /transactions/deposit endpoint
        # Parse response actions array
        # Return list of transaction dicts (approve + deposit)

    def generate_redeem_tx(
        self,
        vault_address: str,
        amount_wei: int,
        wallet_address: str
    ) -> list[dict]:
        # Call /transactions/redeem endpoint
        # **Requirement Q11**: Use default step only (no multi-step)
        # Return list of transaction dicts
```

**Tasks**:
- [ ] Implement deposit transaction generation
- [ ] Implement redeem transaction generation
- [ ] **Requirement Q11**: Filter to default step only, ignore multi-step redemption
- [ ] **Requirement Q23**: Handle multi-transaction responses (approve + deposit)
- [ ] Parse actions array correctly

**Testing**:
- Generate deposit transaction for test vault
- Verify transaction format
- Test multi-transaction response (approval + deposit)

**Requirements Addressed**: Q11 (single-step redemption), Q23 (multi-tx)

---

## Phase 3: Strategy Layer - Vault Selection

### 3.1 Vault Filtering
**Goal**: Apply user criteria to filter vaults

**File**: `agent/strategy/criteria.py`

**Implementation**:
```python
class VaultCriteria:
    def __init__(self, config: dict):
        self.min_apy = config.get('min_apy', 0.0)
        self.min_tvl = config.get('min_tvl', 0.0)
        self.max_tvl = config.get('max_tvl', float('inf'))
        self.vault_whitelist = config.get('vault_whitelist', [])

    def filter_vaults(self, vaults: list[dict]) -> list[dict]:
        # Filter by APY
        # Filter by TVL
        # Filter by whitelist
        # Return filtered vaults

    def apply_diversification(
        self,
        vaults: list[dict],
        existing_positions: list[dict]
    ) -> list[dict]:
        # Exclude vaults user already has positions in
        # Return diversified vault list
```

**Tasks**:
- [ ] Implement criteria filtering
- [ ] Apply vault whitelist
- [ ] Implement diversification logic (never deploy to existing positions)
- [ ] **Requirement Q13**: If no vaults pass filters, return detailed reason:
  - "All vaults filtered: 5 below APY threshold, 3 in whitelist, 2 existing positions"

**Testing**:
- Filter test vault list
- Verify diversification works
- Test edge case: all vaults filtered

**Requirements Addressed**: Q13 (impossible criteria feedback), Q25 (actionable errors)

---

### 3.2 Vault Selection
**Goal**: Select the best vault from filtered options

**File**: `agent/strategy/selector.py`

**Implementation**:
```python
class VaultSelector:
    def __init__(self, criteria: VaultCriteria):
        self.criteria = criteria

    def select_best_vault(
        self,
        opportunities: list[dict],
        positions: list[dict]
    ) -> tuple[dict | None, str]:
        # Filter by criteria
        # Apply diversification
        # Select highest APY
        # Return (vault, reason) or (None, error_message)
```

**Tasks**:
- [ ] Implement vault selection logic
- [ ] Return detailed selection reason
- [ ] Handle case where no vault is suitable

**Testing**:
- Select from test vault list
- Verify highest APY is chosen
- Test all-filtered scenario

**Requirements Addressed**: Architecture requirement for vault selection

---

## Phase 4: Orchestration Layer - Agent Interface

### 4.1 Core Agent Class
**Goal**: High-level interface for user interaction

**File**: `agent/agent.py`

**Implementation**:
```python
class Agent:
    def __init__(self, config_path: str = "config.yaml"):
        # Load config
        # Initialize wallet
        # Initialize executor
        # Initialize API clients
        # Initialize strategy

    def show_state(self):
        # **Requirement Q1**: Display gas balance (ETH)
        # Display USDC balance
        # Display active positions summary
        # Format with 2 decimals for USD amounts (Q26)

    def show_idle_assets(self):
        # Query idle USDC
        # Display in table format
        # Show balance with 2 decimal places (Q26)

    def show_positions(self, retry: bool = True):
        # Query positions
        # **Requirement Q17**: If retry=True and empty, wait and retry
        # Display positions with nicknames (Q10)
        # Filter out zero-balance positions (Q12)
        # Show APY (1-day), amount, value
        # Format USD with 2 decimals (Q26)

    def deploy_capital(self, percentage: float):
        # **Requirement Q1**: Check gas balance FIRST
        # Calculate deployment amount from idle USDC
        # **Requirement Q5**: Validate minimum deposit ($0.10)
        # Get positions (for diversification)
        # Get vault opportunities
        # Select best vault
        # **Requirement Q7**: Handle no suitable vaults
        # Generate deposit transaction(s)
        # **Requirement Q23**: Execute all transactions (approve + deposit)
        # **Requirement Q17**: Show positions after with retry

    def redeem(self, position_nickname: str, percentage: float = 100.0):
        # **Requirement Q1**: Check gas balance
        # Find position by nickname
        # Calculate redemption amount
        # Generate redeem transaction (single-step only, Q11)
        # **Requirement Q24**: Do NOT revoke approvals
        # Execute transaction
        # Show updated positions

    def redeem_all(self):
        # Redeem 100% from all positions
        # Execute sequentially (not parallel)
```

**Tasks**:
- [ ] Implement Agent class initialization
- [ ] **Requirement Q1**: Implement show_state() function
- [ ] Implement show_idle_assets()
- [ ] **Requirement Q17**: Implement show_positions() with retry logic (wait 5s, retry up to 3 times)
- [ ] **Requirement Q5**: Implement deploy_capital() with $0.10 minimum validation
- [ ] **Requirement Q23 & Q24**: Execute approve + deposit, never revoke
- [ ] Implement redeem() with nickname-based position lookup
- [ ] Implement redeem_all()
- [ ] **Requirement Q26**: Format all USD amounts to 2 decimal places
- [ ] Add verbose error messages for all failure modes

**Testing**:
- Test show_state() with test wallet
- Test deploy_capital() flow end-to-end
- Test position display with retry
- Test redemption flow
- Test minimum deposit validation

**Requirements Addressed**: Q1 (gas check), Q5 (min deposit), Q10 (nicknames), Q11 (single-step), Q12 (hide zero), Q17 (retry display), Q23 (multi-tx), Q24 (no revoke), Q26 (2 decimals)

---

## Phase 5: Configuration & Error Handling

### 5.1 Configuration Management
**Goal**: Load and validate user configuration

**File**: `config.yaml`

**Default Configuration**:
```yaml
# Network Configuration
network: base
rpc_url: https://mainnet.base.org

# Asset Configuration
asset: USDC
asset_address: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# API Configuration
vaults_api_url: https://api.vaults.fyi

# Strategy Configuration
vault_selection:
  min_apy: 0.01          # 1% minimum APY
  apy_interval: "1day"    # Q27: Always use 1-day APY
  min_tvl: 10000          # $10k minimum TVL
  max_tvl: null           # No maximum
  vault_whitelist: []     # Empty = all vaults allowed

# Operational Configuration
min_deposit_usd: 0.10     # Q5: $0.10 minimum deposit
display_decimals: 2       # Q26: 2 decimal places for USD
gas_buffer_multiplier: 1.1  # 10% buffer on gas estimates
position_retry_attempts: 3  # Q17: Retry display 3 times
position_retry_delay: 5     # Q17: Wait 5 seconds between retries
```

**Tasks**:
- [ ] Create default config.yaml
- [ ] Load configuration in Agent.__init__()
- [ ] Validate required fields
- [ ] **Requirement Q27**: Ensure apy_interval is always "1day"
- [ ] **Requirement Q5**: Ensure min_deposit_usd is $0.10
- [ ] **Requirement Q26**: Use display_decimals = 2

**Testing**:
- Load config successfully
- Test with missing fields
- Validate defaults

**Requirements Addressed**: Q5, Q26, Q27 (config defaults)

---

### 5.2 Environment Variables
**Goal**: Secure handling of private keys

**File**: `.env.example`

**Content**:
```bash
# Private Key (DO NOT COMMIT .env FILE)
WALLET_PRIVATE_KEY=your_private_key_here

# RPC URL (optional override)
BASE_RPC_URL=https://mainnet.base.org

# RPC API Key (if using paid RPC)
# BASE_RPC_API_KEY=your_key_here
```

**Tasks**:
- [ ] Create .env.example
- [ ] Load private key in Wallet class
- [ ] Validate private key exists and is valid format
- [ ] Add .env to .gitignore

**Testing**:
- Load environment variables
- Test missing private key error

**Requirements Addressed**: Secure key management

---

### 5.3 Error Handling & Messaging
**Goal**: Clear, actionable error messages

**Implementation Strategy**:
```python
class AgentError(Exception):
    """Base class for agent errors"""
    pass

class InsufficientGasError(AgentError):
    """Raised when ETH balance too low for gas"""
    pass

class InsufficientBalanceError(AgentError):
    """Raised when USDC balance too low"""
    pass

class NoSuitableVaultsError(AgentError):
    """Raised when no vaults pass filters"""
    pass

class MinimumDepositError(AgentError):
    """Raised when deposit amount below minimum"""
    pass
```

**Error Message Templates**:
- **Insufficient Gas**: "❌ Insufficient ETH for gas. Need {needed} ETH, have {have} ETH. Please add ETH to your wallet."
- **No Suitable Vaults**: "❌ No suitable vaults found. Filters: {filtered_count} below APY threshold, {whitelist_count} not in whitelist, {existing_count} already invested."
- **Minimum Deposit**: "❌ Deposit amount ${amount} below minimum $0.10. Either deposit more or increase percentage."
- **Empty API Response**: "❌ No deposit options available for USDC on Base. The API returned no vaults."

**Tasks**:
- [ ] Define custom exception classes
- [ ] Implement error message formatting
- [ ] **Requirement Q25**: Ensure all errors are actionable
- [ ] Wrap all API calls in try/except with clear messages
- [ ] Wrap all transactions in try/except with clear messages

**Testing**:
- Trigger each error type
- Verify messages are clear

**Requirements Addressed**: Q25 (actionable errors), Q7 (empty options)

---

## Phase 6: Display & Formatting

### 6.1 Display Utilities
**Goal**: Consistent, readable output formatting

**Implementation**:
```python
def format_usd(amount: float, decimals: int = 2) -> str:
    """Format USD amount with specified decimals (Q26)"""
    return f"${amount:.{decimals}f}"

def format_apy(apy: float) -> str:
    """Format APY as percentage"""
    return f"{apy * 100:.2f}%"

def format_eth(amount_wei: int) -> str:
    """Format ETH amount"""
    from web3 import Web3
    return f"{Web3.from_wei(amount_wei, 'ether'):.6f} ETH"

def generate_nickname(vault_name: str) -> str:
    """Generate 10-char nickname from vault name (Q10)"""
    # Remove spaces and take first 10 characters
    # Examples: "Yearn USDC Vault" → "YearnUSDCV"
    #           "Gauntlet Aave USDC" → "GauntletAa"
    return vault_name.replace(" ", "")[:10]

def display_positions_table(positions: list[dict]):
    """Display positions in formatted table"""
    from tabulate import tabulate
    # Format with 2 decimal USD amounts (Q26)
    # Show nickname, vault name, amount, value, APY (1day)
    pass
```

**Tasks**:
- [ ] **Requirement Q26**: Implement format_usd() with 2 decimal places
- [ ] **Requirement Q10**: Implement generate_nickname() - first 10 chars of vault name (spaces removed)
- [ ] **Requirement Q27**: Display 1-day APY in all tables
- [ ] Implement display_positions_table() using tabulate
- [ ] Implement display_state_table() for show_state()

**Testing**:
- Test USD formatting with various amounts
- Test nickname generation: "Yearn USDC Vault" → "YearnUSDCV"
- Test table display

**Requirements Addressed**: Q10, Q26, Q27 (display formatting)

---

## Phase 7: Examples & Documentation

### 7.1 Interactive Example
**Goal**: Guide users through typical workflows

**File**: `examples/interactive.py`

**Content**:
```python
"""
Interactive guide for using the DeFi Agent

Run this file to see example commands and outputs.
"""

from agent import Agent

def main():
    print("=== DeFi Agent Interactive Guide ===\n")

    # Initialize agent
    agent = Agent()

    # Show current state (Q1: gas + positions)
    print("1. Check your current state:")
    print("   agent.show_state()")
    agent.show_state()

    # Show idle assets
    print("\n2. Check idle USDC:")
    print("   agent.show_idle_assets()")
    agent.show_idle_assets()

    # Deploy capital
    print("\n3. Deploy 10% of idle USDC:")
    print("   agent.deploy_capital(10)")
    # agent.deploy_capital(10)  # Commented - user can uncomment

    # Show positions
    print("\n4. View your positions:")
    print("   agent.show_positions()")
    agent.show_positions()

    # Redeem
    print("\n5. Redeem 50% from a position:")
    print("   agent.redeem('alpine-fox', 50)")
    # agent.redeem('alpine-fox', 50)  # Commented

    print("\n=== End of Guide ===")

if __name__ == "__main__":
    main()
```

**Tasks**:
- [ ] Create interactive.py guide
- [ ] Document each command with example
- [ ] Show expected outputs

**Requirements Addressed**: User education

---

### 7.2 Basic Usage Example
**Goal**: Simple end-to-end example

**File**: `examples/basic_usage.py`

**Content**:
```python
"""
Basic usage example: Deploy capital to highest yield vault
"""

from agent import Agent

def main():
    # Initialize agent
    agent = Agent()

    # Deploy 10% of idle USDC to best vault
    agent.deploy_capital(10)

    # View positions
    agent.show_positions()

if __name__ == "__main__":
    main()
```

**Tasks**:
- [ ] Create basic_usage.py
- [ ] Test end-to-end flow

**Requirements Addressed**: Quick start guide

---

### 7.3 README Documentation
**Goal**: Comprehensive user documentation

**File**: `README.md`

**Content**:
- Project overview
- Installation instructions
- Configuration guide
- Usage examples
- Troubleshooting
- Requirements addressed (link to questions.md)

**Tasks**:
- [ ] Create README.md
- [ ] Document all features
- [ ] Document all requirements implemented
- [ ] Add troubleshooting section

**Requirements Addressed**: Project documentation

---

## Phase 8: Testing & Validation

### 8.1 Component Testing
**Goal**: Validate each component independently

**Test Plan**:
1. **Wallet & Core**
   - Load private key
   - Sign transaction
   - Check ETH balance
   - Estimate gas

2. **API Layer**
   - Make x402 payment
   - Query positions
   - Query idle assets
   - Get vault opportunities
   - Generate transactions

3. **Strategy Layer**
   - Filter vaults by criteria
   - Apply diversification
   - Select best vault

4. **Orchestration**
   - show_state()
   - show_idle_assets()
   - show_positions()
   - deploy_capital()
   - redeem()

**Testing Approach**:
- Use Base testnet initially
- Test with small amounts
- Verify each step manually
- Check error cases

**Tasks**:
- [ ] Test all core functions
- [ ] Test all API calls
- [ ] Test vault selection
- [ ] Test full deployment flow
- [ ] Test redemption flow
- [ ] Test all error scenarios

---

### 8.2 Integration Testing
**Goal**: End-to-end workflow validation

**Test Scenarios**:
1. **Happy Path**
   - Fresh wallet with USDC and ETH
   - Deploy 10% to vault
   - Show positions (with retry)
   - Redeem 100%

2. **Error Cases**
   - Insufficient gas (should fail with clear message)
   - Insufficient USDC (should fail with clear message)
   - Below minimum deposit (should fail with clear message)
   - No suitable vaults (should fail with clear message)
   - Empty API response (should fail with clear message)

3. **Edge Cases**
   - Deploy when already have position (should diversify)
   - Show positions immediately after deploy (should retry)
   - Multiple approve + deposit transactions
   - Zero-balance positions (should be hidden)

**Tasks**:
- [ ] Run full deployment flow
- [ ] Test all error scenarios
- [ ] Verify error messages are actionable
- [ ] Test edge cases

---

## Phase 9: Requirements Verification

### 9.1 Requirements Checklist

Go through each requirement from questions.md and verify implementation:

**Gas Management**:
- [x] **Q1**: Check gas upfront, show clear error if insufficient
- [x] **Q2**: Accept API payment costs, don't warn about them
- [x] **Q3**: Don't care about gas price volatility (let it fail and user retries)

**Decimals & Amounts**:
- [x] **Q4**: USDC has 6 decimals (handled in API response parsing)
- [x] **Q5**: Minimum deposit $0.10, validate before attempting
- [x] **Q6**: Don't worry about dust, minimum deposit handles it

**API Responses**:
- [x] **Q7**: Handle empty deposit options with clear message
- [x] **Q8**: Don't care about API data staleness
- [x] **Q9**: Don't care about vaults becoming unavailable (let tx fail)

**Positions**:
- [x] **Q10**: Position nicknames (10 chars max) instead of indices
- [x] **Q11**: Only use default redemption step (no multi-step)
- [x] **Q12**: Filter zero-balance positions from display

**Configuration**:
- [x] **Q13**: Provide detailed error when no vaults pass criteria
- [x] **Q14**: Don't validate whitelist upfront
- [x] **Q15**: USDC address hardcoded in config

**State**:
- [x] **Q16**: Don't prevent rapid repeated calls (user responsibility)
- [x] **Q17**: Retry position display after deposit (3 attempts, 5s delay)

**x402**:
- [x] **Q18**: Don't warn about x402 payment accumulation
- [x] **Q19**: Don't care about partial x402 failures (standard API error handling)

**RPC**:
- [x] **Q20**: Single RPC endpoint, don't implement fallbacks
- [x] **Q21**: Wait for transaction confirmation (reasonable timeout)
- [x] **Q22**: Don't care about chain reorgs

**Transactions**:
- [x] **Q23**: Execute all transactions (approve + deposit) sequentially
- [x] **Q24**: NEVER revoke approvals, even on failure

**Display**:
- [x] **Q25**: All errors are actionable (tell user what to do)
- [x] **Q26**: Show 2 decimals for USD amounts
- [x] **Q27**: Display 1-day APY everywhere

---

## Implementation Order Summary

### Day 1: Foundation
1. Project structure
2. requirements.txt
3. Config and .env setup
4. Wallet class
5. TransactionExecutor with gas checking

### Day 2: API Integration
6. X402Client
7. PositionAPI
8. OpportunityAPI
9. TransactionAPI

### Day 3: Strategy & Selection
10. VaultCriteria
11. VaultSelector
12. Nickname generation

### Day 4: Agent Orchestration
13. Agent class initialization
14. show_state() (Q1)
15. show_idle_assets()
16. show_positions() with retry (Q17)

### Day 5: Deployment Flow
17. deploy_capital() with all validations
18. Multi-transaction execution (Q23, Q24)
19. Minimum deposit validation (Q5)

### Day 6: Redemption & Display
20. redeem() with nickname lookup (first 10 chars of vault name)
21. redeem_all()
22. Display formatting (Q26, Q27, Q10 - simple string slicing)

### Day 7: Error Handling & Examples
23. All error cases (Q7, Q13, Q25)
24. Interactive examples
25. README documentation

### Day 8: Testing & Validation
26. Component testing
27. Integration testing
28. Requirements verification

---

## Risk Mitigation

### High-Risk Areas
1. **Private Key Security**: Never log or expose private key
2. **Transaction Signing**: Validate all transaction data before signing
3. **Amount Calculations**: USDC has 6 decimals, be precise
4. **Multi-Transaction Flow**: Approve must succeed before deposit
5. **Gas Estimation**: Must check before attempting transaction

### Mitigation Strategies
- Extensive validation before any blockchain interaction
- Clear error messages at every failure point
- Test with small amounts first
- Never auto-retry failed transactions (user must decide)

---

## Success Criteria

The implementation is complete when:
1. ✅ User can run `agent.show_state()` and see gas + positions
2. ✅ User can run `agent.deploy_capital(10)` successfully
3. ✅ User can see positions with nicknames immediately after
4. ✅ All 27 requirements from questions.md are addressed
5. ✅ All error cases have actionable messages
6. ✅ Examples run without errors
7. ✅ README is complete and accurate

---

## Notes for Implementation

- **Start small**: Get basic wallet and gas checking working first
- **Test frequently**: After each component, test in isolation
- **Real API calls**: Use actual vaults.fyi API from day 1 (with test amounts)
- **User feedback**: All operations should print status messages
- **No surprises**: Validate everything upfront, fail early with clear messages
- **Simplicity**: Resist adding features not in requirements

---

## Next Steps

Once this plan is approved:
1. Create project structure
2. Start with Phase 1.1 (Project Setup)
3. Progress through phases sequentially
4. Test each component before moving to next
5. Document as you go

Ready to begin implementation when you are.
