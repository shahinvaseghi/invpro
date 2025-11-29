#!/usr/bin/env python3
"""
Script to check and compare modification dates of README files and their source files.
This script extracts the last modification date from Git for each file pair and compares them.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def get_git_date(filepath):
    """Get the last modification date of a file from Git."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ai', '--', filepath],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0 and result.stdout.strip():
            date_str = result.stdout.strip()
            # Extract just date and time (without timezone)
            parts = date_str.split()
            return f"{parts[0]} {parts[1]}"
    except Exception as e:
        print(f"Error getting date for {filepath}: {e}", file=sys.stderr)
    return "N/A"

def compare_dates(source_date, readme_date):
    """Compare two dates and return status."""
    if source_date == "N/A" or readme_date == "N/A":
        return "⚠️ Unknown"
    try:
        source_dt = datetime.strptime(source_date.split()[0], "%Y-%m-%d")
        readme_dt = datetime.strptime(readme_date.split()[0], "%Y-%m-%d")
        if source_dt > readme_dt:
            return "⚠️ Source newer"
        elif readme_dt > source_dt:
            return "✅ README newer"
        else:
            return "✅ Same date"
    except Exception as e:
        return f"⚠️ Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python check_readme_dates.py <readme_file> <source_file>")
        sys.exit(1)
    
    readme_file = sys.argv[1]
    source_file = sys.argv[2]
    
    readme_date = get_git_date(readme_file)
    source_date = get_git_date(source_file)
    comparison = compare_dates(source_date, readme_date)
    
    print(f"README: {readme_date}")
    print(f"Source: {source_date}")
    print(f"Check: {comparison}")

