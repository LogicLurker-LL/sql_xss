import argparse

import requests
from fuzzer import Fuzzer
from scraper import Scraper
from target import Target
from path_subdomain_finder import Workset


def parse_arguments():
    parser = argparse.ArgumentParser(description='LogicLurker Web Application Scanner')
    parser.add_argument('target', help='Website domain name or IP address to scan')
    parser.add_argument('--output', help='Output file format (default: html)', default='html')
    parser.add_argument('--username', help='Username for automatic login')
    parser.add_argument('--password', help='Password for automatic login')
    parser.add_argument('--cookie', help='Session cookie for manual authentication')
    parser.add_argument('--token', help='Token for manual authentication')
    parser.add_argument('--target-file', help='File with list of targets')

    return parser.parse_args()

def check_web_service(target):
    for scheme in ['http', 'https']:
        url = f'{scheme}://{target}'
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return url
        except requests.RequestException:
            continue
    return None


def operation(target, output, username, password, cookie, token):
    # create a new target object
    target = Target(target)
    # initialize a workset object with wordlists from /wordlists directory

    path_wordlist = open('wordlists/directory-list-2.3-small.txt').read().splitlines()
    subdomain_wordlist = open('wordlists/subdomains-top1million-5000.txt').read().splitlines()
    sqli_wordlist = open('wordlists/Generic-SQLi.txt').read().splitlines()
    xss_wordlist = open('wordlists/XSS-Fuzzing.txt').read().splitlines()
    fuzzing_wordlist = sqli_wordlist + xss_wordlist
    
    workset = Workset(target.url, path_wordlist, subdomain_wordlist)
    # print("FINDING SUBDOMAINS AND DIRECTORIES") 
    target.valid_url = workset.generatePathsAndSubdomains()
    # initialize scraper object
    scraper = Scraper(target)
    for valid_url in target.valid_url:
        scraper.crawl_and_extract(valid_url)
    # injection points
    injection_points = scraper.injection_points
    fuzzer = Fuzzer(fuzzing_wordlist)
    fuzzer.fuzz(injection_points)
    requests_responses = fuzzer.get_requests_responses()

    ##### use requests_responses to identify vulnerabilities
    
    # LNN
    
    ##### based on the LNN's result generate report
    
    # report generation

    return ...
    


def main():
    args = parse_arguments()

    if args.target_file:
        with open(args.target_file, 'r') as file:
            targets = file.read().splitlines()
    else:
        targets = [args.target]
    
    valid_targets = []
    # print(valid_targets)
    for target in targets:
        valid_url = check_web_service(target)
        if valid_url:
            valid_targets.append(valid_url)
        else:
            print(f"No web service found at {target}")

    # print(valid_targets)

    results = []

    for target in valid_targets:
        results.append(operation(target, args.output, args.username, args.password, args.cookie, args.token))