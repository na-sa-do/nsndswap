#!/usr/bin/env python3 -ttb
# nsndswap/__main__.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import sys
import requests
import nsndswap.util
import nsndswap.xzaz_nsnd

def main():
    nsnd = get_nsnd_page()
    print(repr(nsndswap.xzaz_nsnd.parse(nsnd)))

def get_nsnd_page():
    try:
        req = requests.get('http://xzazupsilon.webs.com/nsnd.html')
        if req.status_code != 200:
            sys.stderr.write(f'Request for nsnd returned {req.status_code}, aborting\n')
            raise SystemExit(1)
        nsndtext = req.text
        if len(nsndtext) == 0:
            sys.stderr.write(f'Got a blank page instead of nsnd, aborting\n')
            raise SystemExit(1)
        return nsndtext
    except Exception as e:
        sys.stderr.write(f'Caught an exception while fetching nsnd\n')
        raise

if __name__ == '__main__':
    main()
