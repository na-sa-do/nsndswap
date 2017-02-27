#!/usr/bin/env python3 -ttb
# nsndswap/__main__.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import sys
import requests
import re
import nsndswap.util
import nsndswap.xzaz_nsnd

def main():
    nsnd = get_nsnd_page()
    xzaz_nsnd = nsndswap.xzaz_nsnd.parse(nsnd)

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
    for track in nsnd:
        track.title = postprocess_title(track.title)
        track.references = [postprocess_title(title) for title in track.references]
        for i in range(0, len(track.references)): # separately because this screws with indexes
            if ref == track.title:
                # no, just no
                track.references = [r for r in track.references if r is not ref]

postprocess_title_table = {
        "Beatdown (Strider Style)": "Beatdown",
        "Showtime (Original Mix)": "Showtime",
        }
def postprocess_title(title):
    title = title.replace('TBoSRE', 'The Beginning of Something Really Excellent')\
                 .replace('IaMotMC', 'I\'m a Member of the Midnight Crew')\
                 .replace('PPiSHWA', 'Pumpkin Party in Sea Hitler\'s Water Apocalypse')\
                 .replace('RCT', 'Rollercoaster Tycoon')
    if title in postprocess_title_table.keys():
        title = postprocess_title_table[title]
    return title

if __name__ == '__main__':
    main()
