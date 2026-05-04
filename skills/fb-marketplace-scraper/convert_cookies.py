#!/usr/bin/env python3
"""
Convert EditThisCookie export format to Playwright cookie format.

Usage:
    python3 convert_cookies.py cookies.txt fb_cookies.json

Input format (tab-separated from EditThisCookie):
    name    value    domain    path    expires    size    httpOnly    secure    sameSite    description

Output: Playwright-compatible JSON array.
"""
import argparse, json, sys
from datetime import datetime


def parse_line(line):
    """Parse a single tab-separated cookie line."""
    parts = line.strip().split('\t')
    if len(parts) < 9:
        return None
    
    name = parts[0]
    value = parts[1]
    domain = parts[2]
    path = parts[3]
    expires_str = parts[4]
    http_only = '✓' in parts[6] if len(parts) > 6 else False
    secure = '✓' in parts[7] if len(parts) > 7 else True
    same_site = parts[8] if len(parts) > 8 else 'None'
    
    # Parse expiry
    if expires_str == 'Session':
        expires = -1
    else:
        try:
            dt = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            expires = dt.timestamp()
        except:
            expires = -1
    
    # Normalize sameSite
    if same_site in ('✓', 'None', ''):
        same_site = 'None'
    elif same_site not in ('Lax', 'Strict'):
        same_site = 'None'
    
    return {
        "name": name,
        "value": value,
        "domain": domain,
        "path": path,
        "expires": expires,
        "httpOnly": http_only,
        "secure": secure,
        "sameSite": same_site
    }


def main():
    import os
    
    if len(sys.argv) < 3:
        print("Usage: convert_cookies.py <input.txt> <output.json>")
        print()
        print("Input: EditThisCookie tab-separated export")
        print("Output: Playwright-compatible JSON cookie array")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    cookies = []
    skipped = 0
    
    with open(input_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            cookie = parse_line(line)
            if cookie:
                cookies.append(cookie)
            else:
                skipped += 1
    
    # Write output
    with open(output_file, 'w') as f:
        json.dump(cookies, f, indent=2)
    
    print(f"[+] Converted {len(cookies)} cookies -> {output_file}")
    if skipped:
        print(f"    ({skipped} lines skipped)")
    
    # Verify c_user
    c_user = next((c for c in cookies if c['name'] == 'c_user'), None)
    if c_user:
        print(f"    c_user = {c_user['value']}")
    
    # Check expiry
    import time
    now = time.time()
    expired = [c for c in cookies if c['expires'] > 0 and c['expires'] < now]
    if expired:
        print(f"    [!] {len(expired)} cookies EXPIRED")


if __name__ == "__main__":
    main()
