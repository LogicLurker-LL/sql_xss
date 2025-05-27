import argparse
import requests
import sys
import os
from pyfiglet import Figlet


def display_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner = Figlet(font='slant')
    print(banner.renderText('LogicLurker'))
    print("Web Application's Vulnerability Identifier\n")


def parse_args():
    parser = argparse.ArgumentParser(description='LogicLurker Web Application Scanner')
    parser.add_argument('target', nargs='?', help='Website domain name or IP address to scan')
    parser.add_argument('--output', help='Output file format (default: html)', default='html')
    parser.add_argument('--username', help='Username for automatic login')
    parser.add_argument('--password', help='Password for automatic login')
    parser.add_argument('--cookie', help='Session cookie for manual authentication')
    parser.add_argument('--token', help='Token for manual authentication')
    parser.add_argument('--target-file', help='File with list of targets')
    return parser.parse_args()


def call_api(target, params):
    endpoint = "https://api.logiclurker.local/scan"  # Placeholder
    payload = {"target": target, **params}
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        print("[+] Scan started successfully.")
        print(response.json())
    except requests.RequestException as e:
        print("[-] Failed to start scan:", e)


def main():
    display_banner()
    args = parse_args()

    if not args.target and not args.target_file:
        print("[-] You must provide a target \n")
        print("Run with --help for usage.")
        sys.exit(1)

    targets = []
    if args.target:
        targets.append(args.target)
    elif args.target_file:
        if not os.path.isfile(args.target_file):
            print(f"[-] Target file not found: {args.target_file}")
            sys.exit(1)
        with open(args.target_file, 'r') as f:
            targets.extend([line.strip() for line in f if line.strip()])

    param_dict = {
        "output": args.output,
        "username": args.username,
        "password": args.password,
        "cookie": args.cookie,
        "token": args.token
    }

    for target in targets:
        print(f"[>] Launching scan on {target}...")
        call_api(target, param_dict)


if __name__ == '__main__':
    main()
