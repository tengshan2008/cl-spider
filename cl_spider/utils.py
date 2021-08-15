from typing import Text
import requests


def bit2humanView(bit_val: int) -> Text:
    kb = bit_val / 1024
    mb = bit_val / 1024 / 1024
    gb = bit_val / 1024 / 1024 / 1024
    if int(gb) is not 0:
        return f'{gb:.2f} GB'
    if int(mb) is not 0:
        return f'{mb:.2f} MB'
    if int(kb) is not 0:
        return f'{kb:.2f} KB'
    return f'{bit_val} bit'


def get_source_url():
    url = 'https://user.xunfss.com/app/listapp.php'
    data = {'a': 'get18', 'system': 'pc'}
    r = requests.post(url, data)
    resp = r.json()
    if 'url1' not in resp or 'update' not in resp:
        raise KeyError('request source url failed')
    return resp['url1'], resp['update']
