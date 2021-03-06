from datetime import datetime
import dateutil.parser
from typing import Text
import requests
import cl_spider


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


def seconds2humanView(seconds: int) -> Text:
    result = []
    append = result.append
    if seconds >= 24 * 60 * 60:
        days = seconds // (24 * 60 * 60)
        seconds -= days * (24 * 60 * 60)
        append(f'{days} DAY ')
    if seconds >= 60 * 60:
        hours = seconds // (60 * 60)
        seconds -= hours * (60 * 60)
        append(f'{hours}h')
    if seconds >= 60:
        minus = seconds // 60
        seconds -= minus * 60
        append(f'{minus}m')
    if seconds != 0:
        append(f'{seconds}s')
    return ''.join(result)


def request_source_url():
    url = 'https://user.xunfss.com/app/listapp.php'
    data = {'a': 'get18', 'system': 'pc'}
    r = requests.post(url, data)
    resp = r.json()
    if 'url1' not in resp or 'update' not in resp:
        raise KeyError('request source url failed')
    return resp['url1'], resp['update']


def get_source_url():
    start_time = datetime.now()
    end_time = dateutil.parser.parse(cl_spider.source_url_update)
    if (end_time - start_time).days < 7:
        return request_source_url()
    else:
        return cl_spider.source_url_cache, cl_spider.source_url_update
