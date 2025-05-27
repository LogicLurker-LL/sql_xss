# given api endpoint and parameters fuzz the endpoint with the given parameters with fuzzing wordlist and return the responses 

import requests


class Fuzzer:
    def __init__(self, fuzzing_wordlist):
        self.fuzzing_wordlist = fuzzing_wordlist
        self.requests_responses = []

    def fuzz(self, injection_points):
        for point in injection_points:
            url = point['url']
            parameter = point['parameter']
            for word in self.fuzzing_wordlist:
                payload = {parameter: word}
                try:
                    response = requests.post(url, data=payload)
                    self.requests_responses.append({
                      "request": {
                            "endpoint": url,
                            "body": payload
                            },
                        "response": {
                            "status": response.status_code,
                            "content": response.text
                            },
                    })
                    print(f"Fuzzed {url} with {payload} - Status Code: {response.status_code}")
                except requests.RequestException as e:
                    print(f"Failed to fuzz {url} with {payload}: {e}")

    def get_requests_responses(self):
        return self.requests_responses


# injection_points = [{'url': 'http://eu.httpbin.org/forms/post', 'parameter': 'custname', 'type': None}]
# sqli_wordlist = open('wordlists/Generic-SQLi.txt').read().splitlines()
# xss_wordlist = open('wordlists/XSS-Fuzzing.txt').read().splitlines()
# fuzzing_wordlist = sqli_wordlist + xss_wordlist
# fuzzing_wordlist = ['or 0=0 #"', '"><script>alert(1)</script>', '"><img src=x onerror=alert(1)>', '"><svg/onload=alert(1)>', '"><iframe src=x onerror=alert(1)>', '"><body onload=alert(1)>']
# fuzzer = Fuzzer(fuzzing_wordlist)
# fuzzer.fuzz(injection_points)
# print(fuzzer.get_requests_responses())