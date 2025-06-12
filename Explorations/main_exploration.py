import asyncio
import os
import requests
from Explorations.fuzzer import Fuzzer
from Explorations.scraper import Scraper
from Explorations.target import Target
from Explorations.path_subdomain_finder import Workset


class MainExploration:
    def __init__(self, target, username=None, password=None, cookie=None, token=None, output='html'):
        self.target = target
        self.username = username
        self.password = password
        self.cookie = cookie
        self.token = token
        self.output = output

    async def run(self):
        return await self.operation(self.target, self.username, self.password, self.cookie, self.token, self.output)

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


    async def operation(self, target, username=None, password=None, cookie=None, token=None, output='html'):
        # create a new target object
        target = Target(target)
        # initialize a workset object with wordlists from /wordlists directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        wordlists_dir = os.path.join(base_dir, 'wordlists')


        path_wordlist = open(os.path.join(wordlists_dir, 'directory-list-2.3-small.txt')).read().splitlines()
        subdomain_wordlist = open(os.path.join(wordlists_dir, 'test.txt')).read().splitlines()
        sqli_wordlist = open(os.path.join(wordlists_dir,'refined_sqli_fuzzer.txt')).read().splitlines()
        xss_wordlist = open(os.path.join(wordlists_dir, 'xss_fuzzer_refined.txt')).read().splitlines()
        fuzzing_wordlist = sqli_wordlist + xss_wordlist
        
        workset = Workset(target.url, path_wordlist, subdomain_wordlist)
        print("FINDING SUBDOMAINS AND DIRECTORIES") 
        target.subSites = await workset.generate_paths_and_subdomains()

        # initialize scraper object
        print(target.subSites)
        print("SCRAPING PAGES")
        scraper = Scraper(target.subSites)
        # injection points
        
        await scraper.crawl_and_extract()
        target.injectionPoints = scraper.injection_points

        print(target.injectionPoints)

        print("FUZZING INJECTION POINTS")
        fuzzer = Fuzzer(fuzzing_wordlist)
        # fuzzer.fuzz(injection_points)
        await fuzzer.fuzz(target.injectionPoints)
        target.responseSpace = fuzzer.requests_responses


        ##### use requests_responses to identify vulnerabilities
        
        # LNN
        
        ##### based on the LNN's result generate report
        
        # report generation

        return ...
    

# async def main():
#     target = "https://httpbin.org/forms/post"
#     exp = MainExploration(target)
#     result = await exp.run()
#     print(result)

# if __name__ == "__main__":
#     asyncio.run(main())