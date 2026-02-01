#!/usr/bin/env python3
"""
WRDS Connection Setup and Validation
====================================

Configure WRDS credentials, test database access, and validate connection.

Usage:
    python setup_wrds.py --username your_username
    python setup_wrds.py --test  # Test existing connection
"""

import argparse
import sys
import os
from pathlib import Path


def validate_wrds_connection(username=None):
    """Test WRDS connection and list available libraries."""
    try:
        import wrds
    except ImportError:
        print("ERROR: wrds package not installed.")
        print("Install with: pip install wrds")
        return False

    try:
        # Use provided username or get from environment
        conn_kwargs = {}
        if username:
            conn_kwargs['wrds_username'] = username
        elif os.getenv('WRDS_USERNAME'):
            conn_kwargs['wrds_username'] = os.getenv('WRDS_USERNAME')
            print(f"Using WRDS_USERNAME from environment: {conn_kwargs['wrds_username']}")

        # Test connection
        print("Testing WRDS connection...")
        conn = wrds.Connection(**conn_kwargs)

        # List libraries
        print("\n✓ Connection successful!")
        print("\nAvailable WRDS libraries:")
        libraries = conn.list_libraries()

        # Check for key databases
        key_dbs = ['comp', 'crsp', 'ibes', 'taqm', 'tfn', 'boardex']
        available = {db: db in libraries for db in key_dbs}

        for db, avail in available.items():
            status = "✓" if avail else "✗"
            print(f"  {status} {db}")

        # Test a simple query
        print("\nTesting query access...")
        try:
            test_query = "SELECT * FROM comp.funda LIMIT 1"
            test_df = conn.raw_sql(test_query)
            print(f"✓ Query successful: Retrieved {len(test_df)} row(s)")
        except Exception as e:
            print(f"✗ Query failed: {str(e)}")

        conn.close()
        return True

    except Exception as e:
        print(f"\n✗ Connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify your WRDS credentials are correct")
        print("2. Check if you have active WRDS subscription")
        print("3. Ensure your institution has access to required databases")
        print("4. Try running: pgpass.sh (creates .pgpass file)")
        return False


def setup_environment_file(username):
    """Create or update .env file with WRDS credentials."""
    env_path = Path.cwd() / '.env'

    # Read existing .env if it exists
    existing_lines = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing_lines = [line for line in f.readlines()
                            if not line.startswith('WRDS_USERNAME=')]

    # Add WRDS_USERNAME
    with open(env_path, 'w') as f:
        f.writelines(existing_lines)
        f.write(f"WRDS_USERNAME={username}\n")

    print(f"✓ Created/updated .env file at: {env_path}")
    print("  Added: WRDS_USERNAME")
    print("\nIMPORTANT: Add .env to your .gitignore to protect credentials!")


def check_dependencies():
    """Check if required Python packages are installed."""
    required = {
        'wrds': 'wrds',
        'pandas': 'pandas',
        'numpy': 'numpy',
    }

    missing = []
    for package, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)

    if missing:
        print("Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False

    print("✓ All required packages installed")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Setup and validate WRDS connection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup with username
  python setup_wrds.py --username your_username

  # Test existing connection
  python setup_wrds.py --test

  # Setup and test
  python setup_wrds.py --username your_username --test
        """
    )
    parser.add_argument('--username', help='WRDS username')
    parser.add_argument('--test', action='store_true',
                       help='Test WRDS connection')
    parser.add_argument('--env', action='store_true',
                       help='Create .env file with credentials')

    args = parser.parse_args()

    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)

    # Setup .env file if requested
    if args.env and args.username:
        setup_environment_file(args.username)

    # Test connection if requested or if username provided
    if args.test or args.username:
        success = validate_wrds_connection(args.username)
        sys.exit(0 if success else 1)

    # If no arguments, show help
    parser.print_help()


if __name__ == '__main__':
    main()
