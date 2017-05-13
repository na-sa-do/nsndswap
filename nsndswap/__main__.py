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
    cookie_web.append(cookie_nsnd, override_on_duplicate=['C R Y S T A L S'])
    dump(cookie_web, 'canwc')

    all_web = nsndswap.web.Web()
    all_web.append(xzaz_nsnd)
    all_web.append(cookie_nsnd, override_on_duplicate=['C R Y S T A L S', 'Tick', 'Rex Mille Geromius', 'Smackdown', 'Contra', 'CONTACT', 'Moshi Moshi?', 'Unintentional Touhou', 'Muse of Nanchos', 'Intro',])
    dump(all_web, 'almost_everything')
    all_web.append(viko_nsnd, override_on_duplicate=['daet with roze (Strife 2)'])
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
        track.title = postprocess_title(track.title, "")
        track.references = [postprocess_title(title, track.title) for title in track.references if title != ""]
    return nsnd


postprocess_title_table = {
    "Beatdown": "Beatdown (Strider Style)",
    "Catchyegrabber": "Catchyegrabber (Skipper Plumbthroat's Song)",
    "Dave Fucking Owns At This Game": "Upward Movement (Dave Owns)",
    "Eternity Served Cold": "Eternity, Served Cold",
    "GameBro": "GameBro (Original 1990 Mix)",
    "GameGrl": "GameGrl (Original 1993 Mix)",
    "IaMotMC": "I'm a Member of the Midnight Crew",
    "Overture": "I - Overture",
    "PPiSHWA": "Pumpkin Party in Sea Hitler's Water Apocalypse",
    "Showdown (who were you expecting, the easter bunny?)": "Showdown",  # goddammit cookie
    "Showtime": "Showtime (Original Mix)",
    "Softbit (Original Version)": "Softbit (Original GFD PStFMBRD Version)",
    "TBoSRE": "The Beginning of Something Really Excellent",
    "Three in the Morning (Kali)": "Three in the Morning (Kali's 2 in the AM PM Edit)",
    "Three in the Morning (RJ)": "Three in the Morning (RJ's I Can Barely Sleep In This Casino Remix)",
    "Upward Movement": "Upward Movement (Dave Owns)",
    "Walk-Stab-Walk": "Walk-Stab-Walk (R&E)",
}

forbidden_names = [
    # Things that need manual disambiguation
    'Light', 'Frost', '~~SIDE 1~~', '~~SIDE 2~~', '~~ADDITIONAL MAYHEM~~', 'Game Over', 'Under the Hat', 'Red Miles', '==>', 'Checkmate', 'Premonition', 'Moondoctor', '==>', 'Checkmate', 'Dentist', 'Anticipation', 'Three in the Morning (4 1/3 Hours Late Remix)', 'Fake Fruit Fiesta', 'Showup', 'Stress', 'Contention',
    # Artist names (might be caught by cookie_nsnd if things aren't doing well)
    'HadronKalido', 'Hadron Kalido', 'ostrichlittledungeon', 'Sir Felix (Jaspy)', 'ost', 'cookiefonster', 'Makin', 'wheals', 'Difarem',
]

special_cases = {
    # (title, reference): new_reference
    ('Trollcops', 'Under the Hat'): 'Under the Hat (Land of Fans and Music)',
    ('~~SIDE 2~~ (coloUrs and mayhem: Universe A)', '~~SIDE 1~~'): '~~SIDE 1~~ (coloUrs and mayhem: Universe A)',
    ('~~SIDE 2~~ (coloUrs and mayhem: Universe B)', '~~SIDE 1~~'): '~~SIDE 1~~ (coloUrs and mayhem: Universe B)',
    ('Under the Hat (One Year Older)', 'Under the Hat'): 'Under the Hat (Land of Fans and Music)',
    ('Dance-Stab-Dance', 'Under the Hat'): 'Under the Hat (One Year Older)',
    ('Emissary of Dance', 'Checkmate'): 'Checkmate (coloUrs and mayhem: Universe B)',
    ('Premonition Overdrive', 'Premonition'): 'Premonition (Stuckhome Syndrome)',
    ('You Killed My Father (Prepare To Die)', 'Checkmate'): 'Checkmate (coloUrs and mayhem: Universe B)',
    ('Detective Cherry Inspector', 'Under the Hat'): 'Trollcops',
    ('Explored', 'Under the Hat'): 'Under the Hat (Land of Fans and Music)',
    ('go down (cool and new Mix)', 'Under the Hat'): 'Under the Hat (One Year Older)',
    ('Something Familiar', 'Under the Hat'): 'Under the Hat (Land of Fans and Music)',
    ('Something Familiar', 'Game Over'): 'Game Over (One Year Older)',
    ('[reverie vaporwave]', 'Game Over'): 'Game Over (One Year Older)',
    ('Three in the Morning (4 1/3 Hours Late Remix; CaNon edit)', 'Three in the Morning (4 1/3 Hours Late Remix)'): 'Three in the Morning (4 1/3 Hours Late Remix) (voulem. 1)',
    ('Three in the morning (Dif\'s JUST GO THE FUCK TO SLEEP ALREADY mix)', 'Three in the Morning (4 1/3 Hours Late Remix)'): 'Three in the Morning (4 1/3 Hours Late Remix) (voulem. 1)',
    ('Final Confrontation', 'Game Over'): 'Game Over (One Year Older)',
    ('Stress (Vol. 9)', 'Stress'): 'Stress (George Buzinkai)',
}

def postprocess_title(title, context):
    title = (title.replace('RCT', 'Rollercoaster Tycoon')
                  .replace('ICBSITC', 'I Can Barely Sleep in This Casino')
                  .replace(' (unreleased)', '')
                  .replace('\n', '')
                  .replace('  ', ' ')
                  .strip())
    if title in postprocess_title_table.keys():
        title = postprocess_title_table[title]
    if (context, title) in special_cases.keys():
        title = special_cases[(context, title)]
    if title in forbidden_names:
        print(f'Got a forbidden name "{title}", aborting (context: "{context}")')
        raise Exception()
    return title


def dump(web, name):
    with open(f'output/{name}.gexf', 'w') as f:
        web.dump_gexf(f)
    with open(f'output/{name}.titles.txt', 'w') as f:
        web.dump_titles(f)
    with open(f'output/{name}.txt', 'w') as f:
        web.dump_plaintext(f)
    with open(f'output/{name}.reverse.txt', 'w') as f:
        web.dump_plaintext(f, reverse=True)


if __name__ == '__main__':
    main()
