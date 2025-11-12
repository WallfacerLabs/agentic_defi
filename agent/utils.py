"""
Utility functions for transaction manipulation
"""

from typing import Dict


def modify_erc20_approve_amount(tx_data: str, new_amount: int) -> str:
    """
    Modify the amount in an ERC20 approve transaction

    ERC20 approve function signature: approve(address spender, uint256 amount)
    Transaction data format:
    - Bytes 0-4: Function selector (0x095ea7b3)
    - Bytes 4-36: Spender address (32 bytes, left-padded)
    - Bytes 36-68: Amount (32 bytes, uint256)

    Args:
        tx_data: Original transaction data hex string
        new_amount: New amount to approve (in wei)

    Returns:
        Modified transaction data hex string
    """
    # Parse original data
    if not tx_data.startswith('0x'):
        tx_data = '0x' + tx_data

    # Extract parts
    function_selector = tx_data[:10]  # 0x + 8 chars (4 bytes)
    spender_address = tx_data[10:74]  # 64 chars (32 bytes)

    # Encode new amount as 32-byte hex (left-padded with zeros)
    new_amount_hex = f"{new_amount:064x}"  # 64 hex chars = 32 bytes

    # Reconstruct transaction data
    modified_data = f"{function_selector}{spender_address}{new_amount_hex}"

    return modified_data


def increase_approval_buffer(transactions: list[Dict], buffer_percent: float = 10.0) -> list[Dict]:
    """
    Increase the approval amount in a multi-transaction deposit flow

    Args:
        transactions: List of transaction dicts (typically [approve, deposit])
        buffer_percent: Percentage to increase approval (default 10%)

    Returns:
        Modified transaction list with increased approval amount
    """
    if len(transactions) < 2:
        # No approve transaction, return as-is
        return transactions

    # Assume first transaction is approve (standard pattern)
    approve_tx = transactions[0]
    approve_data = approve_tx['data']

    # Check if it's actually an approve transaction (function selector 0x095ea7b3)
    if not approve_data.startswith('0x095ea7b3'):
        # Not an approve, return as-is
        return transactions

    # Extract current approval amount
    amount_hex = approve_data[74:138]  # Bytes 36-68 in hex = chars 74-138
    current_amount = int(amount_hex, 16)

    # Calculate new amount with buffer
    new_amount = int(current_amount * (1 + buffer_percent / 100))

    # Modify approve transaction
    modified_approve_data = modify_erc20_approve_amount(approve_data, new_amount)

    # Create modified transaction list
    modified_transactions = transactions.copy()
    modified_transactions[0] = {
        **approve_tx,
        'data': modified_approve_data
    }

    return modified_transactions
