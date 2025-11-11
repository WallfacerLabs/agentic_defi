# Interactive Interface Improvement Plan

## Problem Statement

Current `interactive.py` has several UX issues:
- ❌ Inconsistent numbering (numbered steps vs bullet points vs no markers)
- ❌ Confusing "[Command commented - uncomment to execute]" messages
- ❌ No visual separation between sections
- ❌ Hard to distinguish between:
  - Guide instructions
  - Actual data output
  - Helper tips
  - Available commands
- ❌ Important numbers (balances, APY) not visually prominent
- ❌ Formatting logic mixed into interactive.py (reduces readability)

## Goals

1. **Clear Visual Hierarchy** - Obvious separation between sections
2. **No Confusion** - Auto-run safe commands, list dangerous ones (don't fake-execute)
3. **Highlight Important Data** - Balances, APY, addresses stand out
4. **Clean Code** - Move formatting to `display.py`, keep `interactive.py` simple
5. **Add Help Function** - `agent.help()` shows available commands
6. **Professional Polish** - Looks impressive but code stays readable

## Design Decisions

### What Gets Auto-Executed
✅ **Safe to auto-run:**
- `agent.show_state()` - Read-only
- `agent.show_positions()` - Read-only
- `agent.show_idle_assets()` - Read-only (maybe skip since show_state covers it)

❌ **Never auto-run:**
- `agent.deploy_capital()` - Costs money, modifies state
- `agent.redeem()` - Costs money, modifies state
- `agent.redeem_all()` - Costs money, modifies state

### Information Architecture

```
┌─────────────────────────────────────────────┐
│ 1. WELCOME BANNER                           │
│    - Agent name                             │
│    - Version/network info                   │
│    - Wallet address                         │
└─────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────┐
│ 2. CURRENT STATE (auto-executed)            │
│    - Gas balance                            │
│    - USDC balance                           │
│    - Active positions count                 │
│    - Position details (if any)              │
└─────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────┐
│ 3. AVAILABLE COMMANDS                       │
│    - List of commands with descriptions     │
│    - No execution, just reference           │
└─────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────┐
│ 4. TIPS & HELP                              │
│    - How to get help: agent.help()          │
│    - How to exit: Ctrl+D                    │
└─────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────┐
│ 5. INTERACTIVE REPL                         │
│    - User types commands here               │
│    - agent variable available               │
└─────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Create Display Utilities

**File:** `agent/display.py`

**Purpose:** Centralize all formatting logic, keep it out of interactive.py and agent.py

**Functions to create:**

```python
# Section headers
def section_header(title: str) -> str
    """Create a formatted section header"""
    # Example:
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #   CURRENT STATE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def subsection_header(title: str) -> str
    """Create a subsection header"""
    # Example: ── Positions ──────────

# Value formatters (with optional colors)
def highlight_currency(amount: float) -> str
    """Format USD with color/emphasis"""
    # Example: $1.97 (in green/cyan)

def highlight_percentage(value: float) -> str
    """Format percentages with color"""
    # Example: 6.10% (in green if positive)

def highlight_address(address: str, nickname: str = None) -> str
    """Format address with optional nickname"""
    # Example: 0x34bf...82F7 or SparkUSDCV

# Info boxes
def info_box(lines: list[str]) -> str
    """Create an info box with border"""

def command_list(commands: list[tuple]) -> str
    """Format a list of commands"""
    # Input: [('agent.deploy_capital(10)', 'Deploy 10% to best vault'), ...]
    # Output: Formatted command reference

def tip_box(tips: list[str]) -> str
    """Create a tips/help box"""

# State display (reusable)
def format_state_summary(gas_eth: float, usdc_balance: float, position_count: int) -> str
    """Format state in compact, highlighted way"""

def format_positions_table(positions: list[dict], decimals: int = 2) -> str
    """Enhanced position table with highlighting"""
```

**Color Scheme (using standard terminal colors):**
- **Cyan**: Section headers, command names
- **Green**: Currency amounts, positive values
- **Yellow**: Important numbers (APY, balances)
- **White/Default**: Regular text
- **Dim/Gray**: Helper text, tips

**Constraint:** Must work without color library (use ANSI codes or detect if terminal supports colors)

---

### Phase 2: Add agent.help() Method

**File:** `agent/agent.py`

**Add method:**

```python
def help(self):
    """
    Display available commands and usage information
    """
    from .display import command_list, tip_box, section_header

    print(section_header("AVAILABLE COMMANDS"))

    commands = [
        ('agent.show_state()', 'Display gas balance, USDC, and positions'),
        ('agent.show_positions()', 'Show detailed position information'),
        ('agent.show_idle_assets()', 'Show idle USDC balance'),
        ('agent.deploy_capital(percentage)', 'Deploy % of idle USDC to best vault'),
        ('agent.redeem(nickname, percentage)', 'Redeem % from position by nickname'),
        ('agent.redeem_all()', 'Redeem 100% from all positions'),
        ('agent.help()', 'Show this help message'),
    ]

    print(command_list(commands))

    tips = [
        "Commands cost gas - check agent.show_state() before transacting",
        "Nicknames are first 10 chars of vault name (no spaces)",
        "Minimum deposit: $0.10 USDC",
    ]

    print(tip_box(tips))
```

**Testing:** Add to `examples/interactive.py` - call `agent.help()` to verify it works

---

### Phase 3: Redesign interactive.py Flow

**File:** `examples/interactive.py`

**New Structure:**

```python
"""
Interactive DeFi Agent - Clean, guided experience
"""

import sys
sys.path.insert(0, '.')

from agent import Agent
from agent.display import (
    section_header,
    subsection_header,
    highlight_currency,
    format_state_summary,
    format_positions_table,
    command_list,
    tip_box,
    info_box
)


def main():
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. WELCOME BANNER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print(section_header("DeFi Agent Interactive Session"))

    # Initialize agent
    agent = Agent()

    # Show wallet info
    info = [
        f"Wallet:  {agent.wallet.address}",
        f"Network: {agent.network.upper()}",
        f"Asset:   {agent.config['asset']}",
    ]
    print(info_box(info))
    print()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. CURRENT STATE (auto-executed)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print(section_header("Current State"))
    agent.show_state()  # Uses enhanced formatting from display.py

    print(subsection_header("Positions"))
    agent.show_positions()  # Uses enhanced formatting
    print()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. AVAILABLE COMMANDS (reference only, not executed)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print(section_header("Available Commands"))

    commands = [
        ('agent.deploy_capital(10)', 'Deploy 10% of idle USDC'),
        ('agent.redeem("SparkUSDCV", 50)', 'Redeem 50% from position'),
        ('agent.redeem_all()', 'Redeem all positions'),
        ('agent.help()', 'Show detailed help'),
    ]

    print(command_list(commands))
    print()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4. TIPS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    tips = [
        "Type 'agent.help()' for full command reference",
        "Minimum deposit: $0.10 USDC",
        "Press Ctrl+D to exit",
    ]

    print(tip_box(tips))
    print()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 5. INTERACTIVE REPL
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print(section_header("Interactive Mode"))
    print("The 'agent' variable is ready. Try the commands above!\n")

    import code
    code.interact(local=locals(), banner="")


if __name__ == "__main__":
    main()
```

**Key changes:**
- ✅ Auto-run safe commands (no fake demos)
- ✅ Show available commands (without fake executing them)
- ✅ Clean sections with clear separators
- ✅ All formatting in display.py
- ✅ No more "[Command commented]" confusion

---

### Phase 4: Update Agent Class Methods

**Files:** `agent/agent.py`

**Changes to existing methods:**

Use the new display utilities:

```python
def show_state(self):
    """Display current state with enhanced formatting"""
    from .display import section_header, highlight_currency, format_state_summary

    # Get data
    gas_info = self.executor.check_gas_balance()
    idle_info = self.position_api.get_idle_assets(self.wallet.address)
    positions = self.position_api.get_positions(self.wallet.address)

    # Format and display using display.py utilities
    print(format_state_summary(
        gas_info['balance_eth'],
        idle_info['usdc_balance'],
        len(positions)
    ))

def show_positions(self, retry: bool = False):
    """Display positions with enhanced formatting"""
    from .display import format_positions_table, subsection_header

    positions = self.position_api.get_positions(self.wallet.address)

    if not positions:
        print("  No active positions")
        return

    # Use enhanced table formatting
    print(format_positions_table(positions, self.display_decimals))
```

**Add new method:**

```python
def help(self):
    """Display help information"""
    from .display import section_header, command_list, tip_box

    print(section_header("DEFI AGENT HELP"))

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

    print("\n" + subsection_header("Examples"))

    examples = [
        "agent.deploy_capital(10)      # Deploy 10% of idle USDC",
        "agent.redeem('SparkUSDCV', 50) # Redeem 50% from SparkUSDCV",
        "agent.show_positions()         # Refresh position view",
    ]

    for example in examples:
        print(f"  {example}")

    print()

    tips = [
        "Nicknames are first 10 chars of vault name (spaces removed)",
        "Minimum deposit: $0.10 USDC",
        "All transactions require gas (ETH)",
        "Positions update may take 5-10 seconds after transactions",
    ]

    print(tip_box(tips))
```

---

### Phase 5: Create display.py Module

**File:** `agent/display.py`

**Implementation Plan:**

#### 5.1 Color Support

```python
"""
Display utilities for formatted output
Provides colors, boxes, separators, and highlighting
"""

import sys
from typing import List, Tuple

# ANSI color codes
class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright variants
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_CYAN = '\033[96m'

# Detect if terminal supports colors
def supports_color() -> bool:
    """Check if terminal supports ANSI colors"""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

# Safe color wrapper
def colorize(text: str, color: str) -> str:
    """Apply color if terminal supports it"""
    if supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text
```

#### 5.2 Section Headers

```python
def section_header(title: str) -> str:
    """
    Create a major section header

    Example:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      CURRENT STATE
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    width = 60
    line = "━" * width
    title_formatted = colorize(title.upper(), Colors.CYAN + Colors.BOLD)

    return f"\n{line}\n  {title_formatted}\n{line}\n"

def subsection_header(title: str) -> str:
    """
    Create a subsection header

    Example:
    ── Positions ──────────────────────
    """
    width = 40
    title_with_space = f" {title} "
    remaining = width - len(title_with_space)
    line = "─" * remaining

    title_formatted = colorize(title, Colors.BRIGHT_CYAN)

    return f"── {title_formatted} {line}"
```

#### 5.3 Value Highlighting

```python
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
```

#### 5.4 Info Boxes

```python
def info_box(lines: List[str]) -> str:
    """
    Create an info box

    Example:
    ┌────────────────────────────────┐
    │ Wallet:  0x34bf...82F7         │
    │ Network: BASE                  │
    │ Asset:   USDC                  │
    └────────────────────────────────┘
    """
    if not lines:
        return ""

    # Calculate width
    max_len = max(len(line) for line in lines)
    width = max_len + 4  # Padding

    # Build box
    top = f"┌{'─' * (width - 2)}┐"
    bottom = f"└{'─' * (width - 2)}┘"

    result = [top]
    for line in lines:
        padded = line.ljust(max_len)
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

    lines = [colorize("💡 Tips", Colors.BRIGHT_YELLOW + Colors.BOLD)]
    for tip in tips:
        lines.append(f"  • {tip}")

    return '\n'.join(lines)
```

#### 5.5 Command List

```python
def command_list(commands: List[Tuple[str, str]]) -> str:
    """
    Format a list of commands with descriptions

    Example:
    agent.deploy_capital(10)         Deploy 10% to best vault
    agent.redeem('SparkUSDCV', 50)   Redeem 50% from position
    """
    if not commands:
        return ""

    # Calculate max command length for alignment
    max_cmd_len = max(len(cmd) for cmd, _ in commands)

    lines = []
    for cmd, description in commands:
        cmd_formatted = colorize(cmd, Colors.BRIGHT_CYAN)
        padded_cmd = cmd.ljust(max_cmd_len)

        # Re-apply color after padding (padding removes color codes)
        lines.append(f"  {cmd_formatted}{' ' * (max_cmd_len - len(cmd))}  {description}")

    return '\n'.join(lines)
```

#### 5.6 Enhanced State Formatting

```python
def format_state_summary(gas_eth: float, usdc_balance: float, position_count: int) -> str:
    """
    Format state summary with highlighting

    Example:
      Gas Balance:   0.004994 ETH
      USDC Balance:  $1.97
      Positions:     2 active
    """
    lines = [
        f"  {highlight_label('Gas Balance:'):<20} {gas_eth:.6f} ETH",
        f"  {highlight_label('USDC Balance:'):<20} {highlight_currency(usdc_balance)}",
        f"  {highlight_label('Positions:'):<20} {position_count} active",
    ]

    return '\n'.join(lines)

def format_positions_table(positions: List[dict], decimals: int = 2) -> str:
    """
    Enhanced positions table with color highlighting
    """
    if not positions:
        return "  No active positions"

    from tabulate import tabulate

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

    total_line = f"\n  Total: {highlight_currency(total_balance, decimals)}"

    return f"{table}{total_line}"
```

---

### Phase 6: Update Agent Methods to Use Display

**File:** `agent/agent.py`

**Changes:**

1. Import display utilities at top of file
2. Update `show_state()` to use `format_state_summary()`
3. Update `show_positions()` to use `format_positions_table()`
4. Update `deploy_capital()` to use section headers and highlights
5. Update `redeem()` to use section headers and highlights
6. Add `help()` method

**Example refactor for show_state():**

```python
def show_state(self):
    """Display current state with enhanced formatting"""
    from .display import section_header, format_state_summary

    # Don't print section header here (let caller do it if needed)
    # Just format and display the data

    gas_info = self.executor.check_gas_balance()
    idle_info = self.position_api.get_idle_assets(self.wallet.address)
    positions = self.position_api.get_positions(self.wallet.address)

    print(format_state_summary(
        gas_info['balance_eth'],
        idle_info['usdc_balance'],
        len(positions)
    ))
    print()
```

---

### Phase 7: Testing & Validation

**Test Cases:**

1. **Color Support**
   - Test in terminal with color support
   - Test in environment without color (should gracefully degrade)

2. **Readability**
   - Open `interactive.py` - should be easy to understand
   - Open `display.py` - should be well-documented

3. **Functionality**
   - All commands still work exactly the same
   - No behavior changes, only presentation

4. **Help Function**
   - `agent.help()` displays correctly
   - Shows all available commands
   - Tips are useful

**Manual Test:**
```bash
python examples/interactive.py
# Should show:
# - Clean welcome banner
# - Current state (auto-executed)
# - Positions (auto-executed)
# - Available commands (not executed)
# - Tips section
# - Drop into REPL

# In REPL:
>>> agent.help()  # Should display help
>>> agent.deploy_capital(10)  # Should work normally
```

---

## Visual Design Preview

### Before (Current):
```
=== DeFi Agent Interactive Guide ===

1. Initialize the agent:
   agent = Agent()

2. Check your current state (gas, USDC, positions):
   agent.show_state()


=== Current State ===

Gas Balance: 0.004994 ETH
USDC Balance: $1.97
Active Positions: 2

3. View your positions:
   agent.show_positions()


=== Current Positions ===

Nickname    Vault Name        Asset    APY         Balance
----------  ----------------  -------  ----------  ---------
SparkUSDCV  Spark USDC Vault  USDC     6.10% (1d)  $0.14
...
```

### After (Proposed):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DEFI AGENT INTERACTIVE SESSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────────────────────────────────────────────┐
│ Wallet:  0x34bf...82F7                                   │
│ Network: BASE                                            │
│ Asset:   USDC                                            │
└──────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CURRENT STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Gas Balance:      0.004994 ETH
  USDC Balance:     $1.97       [green]
  Positions:        2 active

── Positions ─────────────────────────────────────────────

Nickname    Vault Name        Asset    APY           Balance
----------  ----------------  -------  ------------  ---------
SparkUSDCV  Spark USDC Vault  USDC     6.10% (1d)    $0.14     [green/yellow]
Steakhouse  Steakhouse USDC   USDC     5.07% (1d)    $0.25     [green/yellow]

  Total: $0.39 [green]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AVAILABLE COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  agent.deploy_capital(10)           Deploy 10% of idle USDC
  agent.redeem('SparkUSDCV', 50)     Redeem 50% from position
  agent.redeem_all()                 Redeem all positions
  agent.help()                       Show detailed help

💡 Tips
  • Type 'agent.help()' for full command reference
  • Minimum deposit: $0.10 USDC
  • Press Ctrl+D to exit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  INTERACTIVE MODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The 'agent' variable is ready. Try the commands above!

>>>
```

**Note:** `[green]`, `[yellow]` annotations show where colors would appear

---

## Implementation Order

### Day 1: Foundation
1. Create `agent/display.py` with basic utilities
   - Color support detection
   - Basic colorize function
   - section_header()
   - subsection_header()

2. Test color support in terminal
   - Verify ANSI codes work
   - Test graceful degradation without color

### Day 2: Display Utilities
3. Implement value highlighters
   - highlight_currency()
   - highlight_percentage()
   - highlight_address()

4. Implement box functions
   - info_box()
   - tip_box()
   - command_list()

### Day 3: Enhanced Formatters
5. Implement state and table formatters
   - format_state_summary()
   - format_positions_table()

6. Test all formatters independently

### Day 4: Integration
7. Add agent.help() method to Agent class

8. Update agent methods to use display utilities
   - show_state()
   - show_positions()
   - Deploy/redeem success messages

### Day 5: Interactive.py Redesign
9. Rewrite interactive.py with new structure
   - Clean sections
   - Auto-run safe commands
   - List dangerous commands
   - Drop to REPL

10. Update basic_usage.py if needed

### Day 6: Testing & Polish
11. Test in different terminals
    - macOS Terminal
    - iTerm2
    - VSCode integrated terminal
    - Without color support

12. Verify code readability
    - interactive.py should be <100 lines
    - display.py should be well-documented
    - No behavior changes to agent methods

---

## Success Criteria

✅ **Clear Structure:** Obvious visual hierarchy, no confusion between sections
✅ **Highlighted Data:** Currency, APY, addresses stand out
✅ **No Fake Execution:** Safe commands run, dangerous ones listed only
✅ **Clean Code:** interactive.py <100 lines, easy to understand
✅ **Help Function:** `agent.help()` works and is useful
✅ **Terminal Compatibility:** Works with and without color support
✅ **No Behavior Changes:** All agent methods work exactly the same
✅ **Professional Look:** Looks polished and impressive

---

## Risk Mitigation

**Risks:**
1. Colors might not work in all terminals → Add color detection
2. Display.py might get too complex → Keep functions simple and focused
3. Changing agent.py methods might break existing code → Only change formatting, not logic
4. Unicode box chars might not render → Provide fallback to ASCII

**Mitigation:**
- Test in multiple environments
- Keep display.py optional (agent methods work without it)
- Maintain backward compatibility
- Add graceful fallbacks

---

## Non-Goals

❌ Don't add any new agent functionality
❌ Don't change API behavior
❌ Don't modify configuration
❌ Don't add external dependencies (work with stdlib + existing deps)
❌ Don't make interactive.py complex (keep it simple showcase)

---

## Next Steps

Once this plan is approved:
1. Create `agent/display.py` with all utilities
2. Add `agent.help()` method
3. Rewrite `interactive.py` with new structure
4. Test in terminal
5. Commit changes

Ready to proceed when you approve this plan!
