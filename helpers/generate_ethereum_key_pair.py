#!/usr/bin/env python3
"""
Generate Ethereum key pair and add to .env file

Only generates if PRIVATE_KEY doesn't exist in .env
Outputs both private and public keys when generated
"""

import os
from pathlib import Path
from eth_account import Account


def has_existing_private_key(env_path: Path) -> bool:
    """Check if .env file exists and contains a non-empty PRIVATE_KEY"""
    if not env_path.exists():
        return False

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('PRIVATE_KEY='):
                value = line.split('=', 1)[1].strip()
                # Check if value exists and is not a placeholder
                if value and value != 'your_private_key_here':
                    return True
    return False


def add_private_key_to_env(env_path: Path, private_key: str):
    """Add or update PRIVATE_KEY in .env file"""

    # Read existing content
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []

    # Check if PRIVATE_KEY line exists
    key_line_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith('PRIVATE_KEY='):
            key_line_index = i
            break

    # Update or append
    new_line = f'PRIVATE_KEY={private_key}\n'
    if key_line_index is not None:
        lines[key_line_index] = new_line
    else:
        # Add at the beginning with comment
        lines.insert(0, '# Private Key\n')
        lines.insert(1, new_line)
        lines.insert(2, '\n')

    # Write back
    with open(env_path, 'w') as f:
        f.writelines(lines)


def main():
    env_path = Path('.env')

    # Check if private key already exists
    if has_existing_private_key(env_path):
        print("✓ Private key already exists in .env file. Skipping generation.")
        return

    # Generate new account
    print("Generating new Ethereum key pair...\n")
    account = Account.create()

    # Extract keys
    private_key = account.key.hex()
    public_key = account.address

    # Add to .env file
    add_private_key_to_env(env_path, private_key)

    # Output to console
    print("=" * 70)
    print("NEW ETHEREUM KEY PAIR GENERATED")
    print("=" * 70)
    print(f"\nPrivate Key: {private_key}")
    print(f"Public Key (Address): {public_key}")
    print("\n" + "=" * 70)
    print("✓ Private key has been added to .env file")
    print("=" * 70)
    print("\n⚠️  IMPORTANT: Keep your private key secure and never share it!")
    print("⚠️  Make sure .env is in your .gitignore file")


if __name__ == "__main__":
    main()
