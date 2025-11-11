"""
Wallet management module
Handles private key management and account operations
"""

import os
from eth_account import Account
from web3 import Web3
from dotenv import load_dotenv


class Wallet:
    """Manages wallet account and private key"""

    def __init__(self):
        """Initialize wallet from private key in environment"""
        load_dotenv()

        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            raise ValueError("PRIVATE_KEY not found in environment variables")

        # Create account from private key
        self.account = Account.from_key(private_key)
        self.address = self.account.address

    def get_address(self) -> str:
        """Get wallet address"""
        return self.address

    def sign_transaction(self, transaction_dict: dict) -> bytes:
        """Sign a transaction"""
        signed = self.account.sign_transaction(transaction_dict)
        # In newer eth-account versions, it's raw_transaction (with underscore)
        return signed.raw_transaction if hasattr(signed, 'raw_transaction') else signed.rawTransaction

    def __repr__(self):
        return f"Wallet(address={self.address})"
