#!/usr/bin/env python3
"""
Display wallet address derived from private key in .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from eth_account import Account


def main():
    # Load .env file
    env_path = Path('.env')

    if not env_path.exists():
        print("✗ .env file not found")
        print("Run generate_ethereum_key_pair.py to create a key pair first")
        return

    load_dotenv(env_path)
    private_key = os.getenv('PRIVATE_KEY')

    if not private_key:
        print("✗ PRIVATE_KEY not found in .env file")
        print("Run generate_ethereum_key_pair.py to create a key pair first")
        return

    if private_key == 'your_private_key_here':
        print("✗ PRIVATE_KEY is still a placeholder")
        print("Run generate_ethereum_key_pair.py to create a key pair first")
        return

    try:
        # Derive account from private key
        account = Account.from_key(private_key)

        print("=" * 70)
        print("WALLET INFORMATION")
        print("=" * 70)
        print(f"\nWallet Address: {account.address}")
        print(f"Private Key: {private_key}")
        print("\n" + "=" * 70)
        print("⚠️  Keep your private key secure and never share it!")
        print("=" * 70)

    except Exception as e:
        print(f"✗ Error deriving wallet address: {e}")
        print("Make sure your PRIVATE_KEY in .env is valid")


if __name__ == "__main__":
    main()
