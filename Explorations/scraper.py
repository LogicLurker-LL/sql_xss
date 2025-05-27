from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from retrying import retry
import requests
from urllib.parse import urljoin, urlparse


class Scraper:
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.injection_points = []

    @retry(stop_max_attempt_number=3, wait_fixed=100)
    def scrape_static(self, url):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract form details
            forms = []
            all_parameters = set()  # Use a set to avoid duplicate parameters
            for form in soup.find_all("form"):
                form_details = {
                    "action": form.get("action"),
                    "method": form.get("method"),
                    "inputs": []
                }
                for input_tag in form.find_all("input"):
                    input_details = {
                        "name": input_tag.get("name"),
                        "type": input_tag.get("type"),
                        "value": input_tag.get("value")
                    }
                    form_details["inputs"].append(input_details)
                    if input_tag.get("name"):
                        all_parameters.add(input_tag.get("name"))
                        self.injection_points.append({
                            "url": url,
                            "parameter": input_tag.get("name"),
                            "type": input_tag.get("type")
                        })
                forms.append(form_details)

            return soup
        except requests.RequestException as e:
            print(f"Failed to scrape {url}: {e}")
            return None

    def crawl_and_extract(self, url):
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)

        soup = self.scrape_static(url)
        if not soup:
            return

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for link in soup.find_all("a", href=True):
                href = link.get("href")
                full_url = urljoin(url, href)
                parsed_url = urlparse(full_url)
                if parsed_url.scheme in ['http', 'https'] and self.is_related_domain(full_url) and full_url not in self.visited_urls:
                    futures.append(executor.submit(self.crawl_and_extract, full_url))

            for future in as_completed(futures):
                future.result()

                
    def is_related_domain(self, url):
        base_domain = urlparse(self.base_url).netloc
        target_domain = urlparse(url).netloc
        return target_domain.endswith(base_domain) or base_domain.endswith(target_domain)

    def extract_injection_points(self):
        return self.injection_points

# Example usage:
scraper = Scraper("http://eu.httpbin.org/")
scraper.crawl_and_extract(scraper.base_url)
injection_points = scraper.extract_injection_points()
print(injection_points)