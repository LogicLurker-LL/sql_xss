import asyncio
from retrying import retry
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError



class Scraper:
    def __init__(self, pages:list):
        self.pages = pages
        self.injection_points = list()

    async def crawl_page(self, page):
        collected_requests = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page_obj = await context.new_page()

            async def log_request(route, request):
                req_data = {
                    'method': request.method,
                    'url': request.url,
                    'headers': dict(request.headers),
                    'body': request.post_data or ""
                }
                collected_requests.append(req_data)
                await route.continue_()

            await context.route("**/*", log_request)
            try:
                await page_obj.goto(page, timeout=60000)
                await page_obj.wait_for_load_state("load")
            except PlaywrightTimeoutError:
                print(f"[!] Timeout loading page: {page}")
                await browser.close()
                return collected_requests

            clickables = await page_obj.query_selector_all(
                'a, button, input[type=button], input[type=submit], [role=button], [onclick]'
            )
            for elem in clickables:
                try:
                    await elem.click(timeout=2000)
                    await page_obj.wait_for_timeout(1000)
                except Exception:
                    continue

            await browser.close()
        return collected_requests

    def extract(self, requests):
        sound_requests = []
        interesting_headers = ['Referer', 'Origin', 'X-Forwarded-For', 'Cookie']
        for req in requests:
            has_url_params = bool(parse_qs(urlparse(req['url']).query))
            has_headers = any(h in req.get('headers', {}) for h in interesting_headers)
            has_body = bool(req.get('body'))
            if has_url_params or has_headers or has_body:
                sound_requests.append(req)
        return sound_requests

    async def crawl_and_extract(self):
        tasks = [self.crawl_page(page) for page in self.pages]
        results = await asyncio.gather(*tasks)
        for requests in results:
            sound_requests = self.extract(requests)
            self.injection_points.extend(sound_requests)


# async def main():
#     pages = ['https://www.httpbin.org']
#     scraper = Scraper(pages)
#     await scraper.crawl_and_extract()
#     for point in scraper.injection_points:
#         print(point)
#         print("----")
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())