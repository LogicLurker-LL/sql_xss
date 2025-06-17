from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, parse_qsl
import aiohttp
import asyncio

class Fuzzer:
    def __init__(self, fuzzing_wordlist):
        self.fuzzing_wordlist = fuzzing_wordlist
        self.requests_responses = []

    async def fuzz(self, injection_points):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for req in injection_points:
                for payload in self.fuzzing_wordlist:
                    tasks.extend([
                        self.fuzz_url(session, req, payload),
                        self.fuzz_headers(session, req, payload),
                        self.fuzz_body(session, req, payload)
                    ])
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.requests_responses.extend([r for r in results if r])

    async def fuzz_url(self, session, req, payload):
        mutated = req.copy()
        parsed_url = urlparse(mutated['url'])
        query = parse_qsl(parsed_url.query)
        if not query:
            return None
        fuzzed_query = [(k, payload) for k, _ in query]
        new_query = urlencode(fuzzed_query)
        mutated['url'] = urlunparse(parsed_url._replace(query=new_query))
        return await self.send(session, mutated, 'url', payload)

    async def fuzz_headers(self, session, req, payload):
        mutated = req.copy()
        mutated['headers'] = mutated.get('headers', {}).copy()
        changed = False
        for h in ['Referer', 'Origin', 'X-Forwarded-For', 'Cookie']:
            if h in mutated['headers']:
                mutated['headers'][h] = payload
                changed = True
        if not changed:
            return None
        return await self.send(session, mutated, 'header', payload)

    async def fuzz_body(self, session, req, payload):
        mutated = req.copy()
        body = mutated.get('body', '')
        if body and isinstance(body, str) and '=' in body:
            try:
                parsed_body = parse_qsl(body)
                fuzzed_body = urlencode([(k, payload) for k, _ in parsed_body])
                mutated['body'] = fuzzed_body
                return await self.send(session, mutated, 'body', payload)
            except:
                return None
        return None

    async def send(self, session, req, mutation_type, payload):
        try:
            async with session.request(
                method=req['method'],
                url=req['url'],
                headers=req.get('headers', {}),
                data=req.get('body', None),
                timeout=5
            ) as resp:
                content = await resp.text()
                return {
                    'mutation_type': mutation_type,
                    'request_method': req['method'],
                    'payload': payload,
                    'response_header': dict(resp.headers),
                    'response_status': resp.status,
                    'response_body': content[:5000]  # trim to avoid huge output 
                }
        except:
            return None