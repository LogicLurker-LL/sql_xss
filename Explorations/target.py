from urllib.parse import urlparse


class Target:
    def __init__(self, url):
        if not self._is_valid_url(url):
            raise ValueError("Invalid URL")
        self.url = url
        self.subSites = set()
        self.injectionPoints = set()
        self.responseSpace = set()

    def _is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False 