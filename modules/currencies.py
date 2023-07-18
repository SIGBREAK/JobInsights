from requests import get


def get_rates():
    with get('https://api.hh.ru/dictionaries') as r:
        return {curr['code']: curr['rate'] for curr in r.json()['currency']}
