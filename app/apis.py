from app import app
import ssl
from urllib import request, parse
from urllib.error import URLError

# disable ssl check
ssl._create_default_https_context = ssl._create_unverified_context


def get_dota_open_api(path, base_url='https://api.opendota.com', params=None, r=request):
    url = base_url + '/' + path
    if params is not None:
        url += '?' + parse.urlencode(params)
    app.logger.info('API URL: {}'.format(url))
    try:
        req = r.urlopen(r.Request(url), timeout=30.0)
        if req.getcode() != 200:
            return None
        return req.read()
    except URLError as e:
        app.logger.warning(e)
        return None
