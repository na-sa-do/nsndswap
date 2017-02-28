#!/usr/bin/env python3 -ttb
# nsndswap/__main__.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import sys
import requests
import re
import nsndswap.util
import nsndswap.xzaz_nsnd
import nsndswap.web

def main():
    xzaz_nsnd = get_nsnd_page()
    xzaz_nsnd = nsndswap.xzaz_nsnd.parse(xzaz_nsnd)
    xzaz_nsnd = postprocess(xzaz_nsnd)

    web = nsndswap.web.Web()
    web.append(xzaz_nsnd)
    with open('everything.gexf', 'w') as outf:
        web.dump_gexf(outf)

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

def postprocess(nsnd):
    nsnd = [x for x in nsnd if x]
    for track in nsnd:
        track.title = postprocess_title(track.title)
        track.references = [postprocess_title(title) for title in track.references]
    return nsnd

postprocess_title_table = {
        "Beatdown (Strider Style)": "Beatdown",
        "Showtime (Original Mix)": "Showtime",
        "TBoSRE": "The Beginning of Something Really Excellent",
        "IaMotMC": "I'm a Member of the Midnight Crew",
        "PPiSHWA": "Pumpkin Party in Sea Hitler's Water Apocalypse",
        }
def postprocess_title(title):
    title = title.replace('RCT', 'Rollercoaster Tycoon')\
                 .replace('ICBSITC', 'I Can Barely Sleep in This Casino')
    if title in postprocess_title_table.keys():
        title = postprocess_title_table[title]
    return title

if __name__ == '__main__':
    main()
