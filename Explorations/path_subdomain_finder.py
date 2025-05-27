import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from retrying import retry

class Workset:
    def __init__(self, url, path_wordlist, subdomain_wordlist):
        self.url = url
        self.path_wordlist = path_wordlist
        self.subdomain_wordlist = subdomain_wordlist
        self.parsed_url = urlparse(url)
        self.base_domain = self.parsed_url.netloc
        self.scheme = self.parsed_url.scheme
        self.valid_urls = []

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def make_request(self, url):
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        return response

    def find_subdomains(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.make_request, f"{self.scheme}://{word}.{self.base_domain}"): word for word in self.subdomain_wordlist}
            for future in as_completed(futures):
                word = futures[future]
                try:
                    response = future.result()
                    if response.status_code == 200:
                        self.valid_urls.append(f"{self.scheme}://{word}.{self.base_domain}")
                        print(self.valid_urls)
                        print("+"*20)
                except requests.RequestException:
                    pass

    def find_directories(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.make_request, f"{self.url}/{word}"): word for word in self.path_wordlist}
            for future in as_completed(futures):
                word = futures[future]
                try:
                    response = future.result()
                    if response.status_code == 200:
                        self.valid_urls.append(f"{self.url}/{word}")
                        print(self.valid_urls)
                        print("+"*20)
                except requests.RequestException:
                    pass

    def generatePathsAndSubdomains(self):
        self.find_subdomains()
        self.find_directories()
        return self.valid_urls

# path_wordlist = ['admin', 'login', 'test']
# subdomain_wordlist = ['api', 'dev', 'staging']
# workset = Workset('https://httpbin.org', path_wordlist, subdomain_wordlist)
# valid_urls = workset.generatePathsAndSubdomains()
# print(valid_urls)