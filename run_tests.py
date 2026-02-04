#!/usr/bin/env python
"""
Test runner with coverage reporting.
Generates coverage reports and screenshots.
"""

import sys
import os
import subprocess
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))


def run_tests_with_coverage():
    """Run tests with coverage."""
    print("=" * 80)
    print("Running tests with coverage...")
    print("=" * 80)
    
    # Create reports directory
    reports_dir = os.path.join(os.path.dirname(__file__), 'test_reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Run pytest with coverage
    cmd = [
        'python', '-m', 'pytest',
        'tests/',
        '--cov=app',
        '--cov-report=html:test_reports/htmlcov',
        '--cov-report=term-missing',
        '--cov-report=xml:test_reports/coverage.xml',
        '-v'
    ]
    
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    
    print("\n" + "=" * 80)
    print("Test Results Summary")
    print("=" * 80)
    
    if result.returncode == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    
    print(f"\nCoverage reports generated in: {reports_dir}/htmlcov/")
    print(f"Open {reports_dir}/htmlcov/index.html to view detailed coverage")
    
    return result.returncode


def main():
    """Main entry point."""
    exit_code = run_tests_with_coverage()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
