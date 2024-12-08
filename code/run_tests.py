#!/usr/bin/env python3
import unittest
import sys
import argparse

def run_tests(verbosity=2, pattern="test_*.py", failfast=False):
    """
    Run all tests in the current directory.

    Args:
        verbosity (int): Detail level of test output (1=minimal, 2=normal, 3=detailed)
        pattern (str): Pattern to match test files
        failfast (bool): Stop on first failure if True
    """
    # Initialize the test loader
    loader = unittest.TestLoader()

    # Discover and load all tests in current directory
    suite = loader.discover(
        start_dir='.',
        pattern=pattern
    )

    # Initialize the test runner
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast
    )

    # Run the tests
    result = runner.run(suite)

    # Return 0 if tests passed, 1 if any failed
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run all unit tests in the current directory')
    parser.add_argument('-v', '--verbosity', type=int, choices=[1, 2, 3], default=2,
                        help='Verbosity level (1=minimal, 2=normal, 3=detailed)')
    parser.add_argument('-p', '--pattern', type=str, default='test_*.py',
                        help='Pattern to match test files (default: test_*.py)')
    parser.add_argument('-f', '--failfast', action='store_true',
                        help='Stop on first failure')

    args = parser.parse_args()
    sys.exit(run_tests(args.verbosity, args.pattern, args.failfast))