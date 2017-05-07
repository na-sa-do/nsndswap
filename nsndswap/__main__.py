#!/usr/bin/env python3
# nsndswap/__main__.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import sys
import requests
import nsndswap.util
import nsndswap.xzaz_nsnd
import nsndswap.cookie_nsnd
import nsndswap.viko_nsnd
import nsndswap.web


def main():
    xzaz_nsnd = get_nsnd_page('http://xzazupsilon.webs.com/nsnd.html')
    xzaz_nsnd = nsndswap.xzaz_nsnd.parse(xzaz_nsnd)
    xzaz_nsnd = postprocess(xzaz_nsnd)
    cookie_nsnd = get_nsnd_page('https://wheals.github.io/canwc/nsnd.html')
    cookie_nsnd = nsndswap.cookie_nsnd.parse(cookie_nsnd)
    cookie_nsnd = postprocess(cookie_nsnd)
    viko_nsnd = nsndswap.viko_nsnd.parse()
    viko_nsnd = postprocess(viko_nsnd)

    xzaz_web = nsndswap.web.Web()
    xzaz_web.append(xzaz_nsnd)
    dump(xzaz_web, 'homestuck')

    cookie_web = nsndswap.web.Web()
    cookie_web.append(cookie_nsnd)
    dump(cookie_web, 'canwc')

    all_web = nsndswap.web.Web()
    all_web.append(xzaz_nsnd)
    all_web.append(cookie_nsnd)
    dump(all_web, 'almost_everything')
    all_web.append(viko_nsnd)
    dump(all_web, 'everything')


def get_nsnd_page(url):
    print(f'Fetching {url}')
    try:
        req = requests.get(url)
        if req.status_code != 200:
            sys.stderr.write(f'Request for nsnd returned {req.status_code}, aborting\n')
            raise SystemExit(1)
        nsndtext = req.text
        if len(nsndtext) == 0:
            sys.stderr.write(f'Got a blank page instead of nsnd, aborting\n')
            raise SystemExit(1)
        return nsndtext.strip().replace('\n', '')
    except Exception as e:
        sys.stderr.write(f'Caught an exception while fetching nsnd\n')
        raise


def postprocess(nsnd):
    nsnd = [x for x in nsnd if x and x.title != ""]
    for track in nsnd:
        track.title = postprocess_title(track.title)
        track.references = [postprocess_title(title) for title in track.references if title != ""]
    return nsnd


postprocess_title_table = {
    "Beatdown": "Beatdown (Strider Style)",
    "Showtime": "Showtime (Original Mix)",
    "TBoSRE": "The Beginning of Something Really Excellent",
    "IaMotMC": "I'm a Member of the Midnight Crew",
    "PPiSHWA": "Pumpkin Party in Sea Hitler's Water Apocalypse",
    "Upward Movement": "Upward Movement (Dave Owns)",
    "Dave Fucking Owns At This Game": "Upward Movement (Dave Owns)",
    "Catchyegrabber": "Catchyegrabber (Skipper Plumbthroat's Song)",
    "Three in the Morning (Kali)": "Three in the Morning (Kali's 2 in the AM PM Edit)",
    "Three in the Morning (RJ)": "Three in the Morning (RJ's I Can Barely Sleep In This Casino Remix)",
    "Overture": "I - Overture",
    "Softbit (Original Version)": "Softbit (Original GFD PStFMBRD Version)",
    "GameBro": "GameBro (Original 1990 Mix)",
    "GameGrl": "GameGrl (Original 1993 Mix)",
    "Eternity Served Cold": "Eternity, Served Cold",
    "Walk-Stab-Walk": "Walk-Stab-Walk (R&E)",
    # a note to wheals + cookie: i can't believe you've done this
    "Showdown (who were you expecting, the easter bunny?)": "Showdown",
}


def postprocess_title(title):
    title = (title.replace('RCT', 'Rollercoaster Tycoon')
                  .replace('ICBSITC', 'I Can Barely Sleep in This Casino')
                  .replace(' (unreleased)', '')
                  .replace('\n', '')
                  .replace('  ', ' ')
                  .strip())
    if title in postprocess_title_table.keys():
        title = postprocess_title_table[title]
    return title


def dump(web, name):
    with open(f'output/{name}.gexf', 'w') as f:
        web.dump_gexf(f)
    with open(f'output/{name}.titles.txt', 'w') as f:
        web.dump_titles(f)


if __name__ == '__main__':
    main()
