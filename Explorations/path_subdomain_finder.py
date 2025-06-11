# dir_subdomain_bruteforce.py

import asyncio
from datetime import datetime 
import os
import aiohttp
import socket
from aiohttp import ClientSession
from typing import List
from urllib.parse import urlparse

TIMEOUT = 5
CONCURRENCY = 100
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

class Workset:
    def __init__(self, url: str, path_wordlist: List[str], subdomain_wordlist: List[str]):
        self.url = url.rstrip('/')
        self.parsed_url =  urlparse(self.url)
        self.base_domain = self.parsed_url.netloc
        self.scheme = self.parsed_url.scheme
        self.path_wordlist = path_wordlist
        self.subdomain_wordlist = subdomain_wordlist
        self.valid_urls = []

    async def check_directory(self, session: ClientSession, word: str):
        url = f"{self.url}/{word}/"
        try:
            async with session.get(url, timeout=TIMEOUT) as resp:
                if resp.status in [200, 301, 302, 403]:
                    print(f"[+] Found directory: {url} ({resp.status})")
                    self.valid_urls.append(url)
        except Exception:
            pass

    async def check_subdomain(self, word: str):
        subdomain = f"{word}.{self.base_domain}"
        url = f"{self.scheme}://{subdomain}"
        try:
            await asyncio.get_event_loop().getaddrinfo(subdomain, None)
            print(f"[+] Found subdomain: {url}")
            self.valid_urls.append(url)
        except socket.gaierror:
            pass

    async def directory_bruteforce(self):
        connector = aiohttp.TCPConnector(limit=CONCURRENCY)
        async with aiohttp.ClientSession(connector=connector, headers=HEADERS) as session:
            tasks = [self.check_directory(session, word) for word in self.path_wordlist]
            await asyncio.gather(*tasks)

    async def subdomain_bruteforce(self):
        tasks = [self.check_subdomain(word) for word in self.subdomain_wordlist]
        await asyncio.gather(*tasks)

    async def generate_paths_and_subdomains(self):
        await self.subdomain_bruteforce()
        await self.directory_bruteforce()
        return self.valid_urls

# Example usage:
# ...existing code...

# Example usage:
# async def main():
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     wordlists_dir = os.path.join(base_dir, 'wordlists')
#     path_wordlist = open(os.path.join(wordlists_dir, 'directory-list-2.3-small.txt')).read().splitlines()
#     subdomain_wordlist = open(os.path.join(wordlists_dir, 'subdomains-top1million-5000.txt')).read().splitlines()
#     # scanner = Workset('http://portswigger-labs.net/', path_wordlist, subdomain_wordlist)
#     print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#     scanner = Workset('https://httpbin.org/forms/post', path_wordlist, subdomain_wordlist)
#     result = await scanner.generate_paths_and_subdomains()
#     print(result)
#     print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
# if __name__ == "__main__":
#     asyncio.run(main())