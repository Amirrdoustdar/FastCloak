#!/usr/bin/env python3
"""Generate cryptographically secure SECRET_KEY"""

import secrets
import sys


def generate_secret_key(length: int = 32) -> str:
    """Generate URL-safe secret key"""
    return secrets.token_urlsafe(length)


if __name__ == "__main__":
    key = generate_secret_key()
    print(f"\n🔑 Generated SECRET_KEY:\n")
    print(key)
    print(f"\n📋 Add this to your .env file:")
    print(f"SECRET_KEY={key}\n")