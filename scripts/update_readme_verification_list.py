#!/usr/bin/env python3
"""
Script to update README_VERIFICATION_LIST.md with current Git modification dates.
This script extracts the last modification date from Git for each file pair and updates the markdown file.
"""

import subprocess
import re
from pathlib import Path
from datetime import datetime

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
            # Extract date and time (format: YYYY-MM-DD HH:MM:SS)
            parts = date_str.split()
            if len(parts) >= 2:
                return f"{parts[0]} {parts[1]}"
    except Exception:
        pass
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
            # Check time if dates are same
            try:
                source_time = datetime.strptime(source_date, "%Y-%m-%d %H:%M:%S")
                readme_time = datetime.strptime(readme_date, "%Y-%m-%d %H:%M:%S")
                if source_time > readme_time:
                    return "⚠️ Source newer"
                elif readme_time > source_time:
                    return "✅ README newer"
            except:
                pass
            return "✅ Same date"
    except Exception:
        return "⚠️ Unknown"

def update_table_row(line, readme_file, source_file):
    """Update a table row with Git dates."""
    # Extract current values
    pattern = r'\| `([^`]+)` \| `([^`]+)` \| ([✅⏳⚠️❌]+ [\w\s]+) \| ([^\|]+) \| ([^\|]+) \| ([^\|]+) \| ([^\|]+) \|'
    match = re.match(pattern, line)
    if not match:
        return line
    
    readme_path = match.group(1)
    source_path = match.group(2)
    status = match.group(3)
    source_date_old = match.group(4).strip()
    readme_date_old = match.group(5).strip()
    git_check_old = match.group(6).strip()
    notes = match.group(7).strip()
    
    # Get new dates from Git
    source_date_new = get_git_date(source_path)
    readme_date_new = get_git_date(readme_path)
    git_check_new = compare_dates(source_date_new, readme_date_new)
    
    # Update the row
    new_line = f"| `{readme_path}` | `{source_path}` | {status} | {source_date_new} | {readme_date_new} | {git_check_new} | {notes} |"
    return new_line

def main():
    """Main function to update README_VERIFICATION_LIST.md"""
    project_root = Path(__file__).parent.parent
    readme_file = project_root / "README_VERIFICATION_LIST.md"
    
    if not readme_file.exists():
        print(f"Error: {readme_file} not found")
        return
    
    content = readme_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a table row with file paths
        if re.match(r'^\| `[^`]+` \| `[^`]+` \|', line) and 'README' in line and '.py' in line:
            # This is a table row we need to update
            new_line = update_table_row(line, None, None)
            new_lines.append(new_line)
        else:
            new_lines.append(line)
        
        i += 1
    
    # Write updated content
    readme_file.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"Updated {readme_file}")

if __name__ == "__main__":
    main()

