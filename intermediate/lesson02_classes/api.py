from dataclasses import dataclass

from faker import Faker

fake = Faker()

class API:
    def get(url, kwargs={}, debug=False):
        if url not in ENDPOINTS:
            return KeyError(f'{url} endpoint does not exist')
        if debug:
            print('---', url, kwargs, ENDPOINTS[url])
        yield from ENDPOINTS[url](**kwargs)
        while True:
            yield None
        
    def get_customer(cid):
        yield fake.email()
    
    def get_all_customers():
        for _ in range(0, 5):
            yield fake.pyint()

    def get_transactions(ts, te):
        for _ in range(int(te-ts)):
            yield fake.uuid4()

ENDPOINTS = {
    'customer':     API.get_customer,
    'transactions': API.get_transactions,
    'customers':    API.get_all_customers,
}