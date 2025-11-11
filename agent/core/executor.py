"""
Transaction execution module
Handles gas estimation, transaction signing, broadcasting, and confirmation
"""

import os
from typing import List, Tuple
from web3 import Web3
from dotenv import load_dotenv
from .wallet import Wallet


class TransactionExecutor:
    """Executes blockchain transactions"""

    def __init__(self, wallet: Wallet, rpc_url: str = None):
        """Initialize executor with wallet and RPC connection"""
        self.wallet = wallet

        # Load RPC URL from env if not provided
        if rpc_url is None:
            load_dotenv()
            rpc_url = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')

        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to RPC: {rpc_url}")

    def check_gas_balance(self) -> dict:
        """
        Check ETH balance for gas (requirement Q1)
        Returns dict with balance info and sufficiency check
        """
        balance_wei = self.w3.eth.get_balance(self.wallet.address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')

        # Rough estimate: need at least 0.001 ETH for gas
        min_gas_eth = 0.001
        sufficient = balance_eth >= min_gas_eth

        return {
            'balance_wei': balance_wei,
            'balance_eth': float(balance_eth),
            'sufficient': sufficient,
            'min_required_eth': min_gas_eth
        }

    def validate_gas_balance(self) -> Tuple[bool, str]:
        """
        Validate sufficient gas balance
        Returns (is_sufficient, error_message)
        """
        gas_info = self.check_gas_balance()

        if not gas_info['sufficient']:
            error = (
                f"Insufficient ETH for gas. "
                f"Have {gas_info['balance_eth']:.6f} ETH, "
                f"need at least {gas_info['min_required_eth']:.6f} ETH."
            )
            return False, error

        return True, ""

    def execute(self, tx_payload: dict, wait_for_confirmation: bool = True, use_pending_nonce: bool = False) -> str:
        """
        Execute a single transaction
        Returns transaction hash

        Args:
            tx_payload: Transaction data (to, data, value)
            wait_for_confirmation: Wait for transaction to be mined
            use_pending_nonce: Use 'pending' block for nonce (for sequential transactions)
        """
        # Build transaction
        # Use 'pending' nonce to include pending transactions in the count
        nonce_block = 'pending' if use_pending_nonce else 'latest'
        nonce = self.w3.eth.get_transaction_count(self.wallet.address, nonce_block)

        transaction = {
            'from': self.wallet.address,
            'to': tx_payload['to'],
            'data': tx_payload['data'],
            'value': int(tx_payload.get('value', 0)),
            'nonce': nonce,
            'chainId': self.w3.eth.chain_id,
        }

        # Estimate gas
        try:
            gas_estimate = self.w3.eth.estimate_gas(transaction)
            # Use 50% buffer for complex vault interactions (10% was too low)
            transaction['gas'] = int(gas_estimate * 1.5)
        except Exception as e:
            raise Exception(f"Gas estimation failed: {str(e)}")

        # Get gas price
        transaction['gasPrice'] = self.w3.eth.gas_price

        # Sign transaction
        signed_tx = self.wallet.sign_transaction(transaction)

        # Broadcast transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx)
        tx_hash_hex = tx_hash.hex()

        # Wait for confirmation if requested
        if wait_for_confirmation:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            if receipt['status'] != 1:
                raise Exception(f"Transaction failed: {tx_hash_hex}")

        return tx_hash_hex

    def execute_multiple(self, tx_payloads: List[dict]) -> List[str]:
        """
        Execute multiple transactions sequentially (requirement Q23)
        Returns list of transaction hashes
        Never revokes approvals on failure (requirement Q24)
        """
        tx_hashes = []

        for i, tx_payload in enumerate(tx_payloads):
            try:
                # For second+ transactions, use pending nonce to account for previous txs
                use_pending = i > 0
                tx_hash = self.execute(tx_payload, wait_for_confirmation=True, use_pending_nonce=use_pending)
                tx_hashes.append(tx_hash)
            except Exception as e:
                # If approval succeeded but deposit failed, DO NOT revoke (Q24)
                if i > 0:
                    raise Exception(
                        f"Transaction {i+1} failed after {i} successful transaction(s). "
                        f"Previous transactions: {tx_hashes}. "
                        f"Error: {str(e)}"
                    )
                else:
                    raise Exception(f"Transaction {i+1} failed: {str(e)}")

        return tx_hashes
