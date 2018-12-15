#!/usr/bin/env python3
# nsndswap/__main__.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import sys
import requests
import nsndswap.util
import nsndswap.makin_nsnd
import nsndswap.cookie_nsnd
import nsndswap.viko_nsnd
import nsndswap.web


def main():
    makin_nsnd = get_nsnd_page('https://recordcrash.com/nsnd.html')
    makin_nsnd = nsndswap.makin_nsnd.parse(makin_nsnd)
    makin_nsnd = postprocess(makin_nsnd)
    cookie_nsnd = get_nsnd_page('https://wheals.github.io/canwc/nsnd.html')
    cookie_nsnd = nsndswap.cookie_nsnd.parse(cookie_nsnd)
    cookie_nsnd = postprocess(cookie_nsnd)
    viko_nsnd = nsndswap.viko_nsnd.parse()
    viko_nsnd = postprocess(viko_nsnd)

    makin_web = nsndswap.web.Web()
    makin_web.append(makin_nsnd, skip_on_duplicate=['Requiem for Something Really Excellent (Demo)', 'Skaian Shuffle', 'Mother (Malcolm Brown)', 'Skaia Voyages', 'Clockwork Apocalypse', 'Double Midnight', 'Hawkeye', 'Homosuck Anthem', 'Jadesprite', 'Penumbra Phantasm', 'Mother (Malcolm Brown)'])
    dump(makin_web, 'homestuck')

    cookie_web = nsndswap.web.Web()
    cookie_web.append([nsndswap.util.Track('Showtime (Imp Strife Mix)', ['Showtime'])])
    cookie_web.append(cookie_nsnd, override_on_duplicate=['C R Y S T A L S'], skip_on_duplicate=['Showtime (Imp Strife Mix)'])
    dump(cookie_web, 'canwc')

    viko_web = nsndswap.web.Web()
    viko_web.append(viko_nsnd)
    dump(viko_web, 'viko')

    all_web = nsndswap.web.Web()
    all_web.append(makin_nsnd, skip_on_duplicate=['Requiem for Something Really Excellent (Demo)', 'Skaian Shuffle', 'Mother (Malcolm Brown)', 'Skaia Voyages', 'Clockwork Apocalypse', 'Double Midnight', 'Hawkeye', 'Homosuck Anthem', 'Jadesprite', 'Penumbra Phantasm', 'Mother (Malcolm Brown)'])
    all_web.append(cookie_nsnd, override_on_duplicate=['C R Y S T A L S', 'Tick', 'Rex Mille Geromius', 'Smackdown', 'Contra', 'CONTACT', 'Moshi Moshi?', 'Unintentional Touhou', 'Muse of Nanchos', 'Intro', 'daet with roze', 'Lord Spanish', 'Something Familiar', 'Stay in Touch', 'Midnight Suffer', 'The Gemoni Mustard Blood', 'Formation', 'hors', 'Jungle #3', 'Revisit/Rewind', 'Resend', 'Aura of Colour', 'Ringleader', 'Collision Course (Davepeta\'s Movement)', 'Horizontal Headshot', 'Raise of the Conductor\'s Baton'], skip_on_duplicate=['Showtime (Imp Strife Mix)', 'A History of Babies', 'Throguh Song', 'The Baby is You', 'bootes', 'rose pragnant', 'the rose rap', 'uh oh', 'vs bros', 'a baby is born', 'Old Secret', 'Conflict!', 'Apexhalation'])
    all_web.append(viko_nsnd, override_on_duplicate=['Cascadium Dioxide', 'Conflict!', 'Malediction', 'Taureg', 'Your Best Friend', 'Metal Crusher', 'CORE', 'Death by Glamour', 'Menu (Full)', 'Hopes and Dreams', 'Spider Dance', 'Reunited', 'Snowdin Town', 'Spooktune'])
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
    "3 in the Morning (Pianokind)": "Three in the Morning (Pianokind)",
    "7 GRAND END (Noisemaker's part)": "7 GRAND END",
    "AAAAAAAAAA": "AAAAAAAAAAAA",
    "Anbroids v2.0": "Anbroids V2.0",
    "At the Price of Oblivion": "At The Price of Oblivion",
    "BL1ND JUST1C3: 1NV3ST1G4T1ON!!": "BL1ND JUST1C3 : 1NV3ST1G4T1ON !!",
    "Baby Legend": "A Baby Legend - The Baby is 2",
    "Bad Apple!! (feat. Nomico)": "Bad Apple!!",
    "Bad Apple!! feat. Nomico": "Bad Apple!!",
    "Beatdown (Strider Style)": "Beatdown",
    "Brofessor Layton (EPHaB)": "Brofessor Layton (Every Problem Has a Brolution)",
    "Catchyegrabber": "Catchyegrabber (Skipper Plumbthroat's Song)",
    "Dave Fucking Owns At This Game": "Upward Movement (Dave Owns)",
    "Dersite": "Something Familiar",
    "Doct̸̀o̴̕r̵": "Doctor (Zalgo)",
    "Eternity Served Cold": "Eternity, Served Cold",
    "Even in Dance": "Even In Dance",
    "Fighter Kanaya (Album Cut)": "Fighter Kanaya",
    "Final Confrontation": "Something Familiar",
    "Foley": "Wind chime foley",
    "GameBro (Original 1990 Mix)": "GameBro",
    "GameGrl (Original 1993 Mix)": "GameGrl",
    "It Don't Mean A Thing": "It Don't Mean a Thing (If It Ain't Got That Swing)",
    "Jambox (by Noisemaker)": "Jambox",
    "Layton's Theme": "Professor Layton's Theme",
    "Let the Squiddles Sleep": "Let the Squiddles Sleep (End Theme)",
    "Lilith in Starlight": "Lilith In Starlight",
    "Love You (Feferi's Theme)": "Love You",
    "Love You": "Love You (Feferi's Theme)",
    "MACINTOSH PLUS": "MACINTOSH PLUS - リサフランク420 / 現代のコンピュー",
    "Overture": "I - Overture",
    "PPiSHWA": "Pumpkin Party in Sea Hitler's Water Apocalypse",
    "Problem Sleuth Title Screen": "Problem Sleuth Title Theme",
    "Sad Jhon :( (Album Cut)": "Sad Jhon :(",
    "Shop (Undertale)": "Shop",
    "Showdown (who were you expecting, the easter bunny?)": "Showdown",  # goddammit
    "Showtime (Original Mix)": "Showtime",
    "Skaian Dreams Remix": "Skaian Dreams (Remix)",
    "Softbit (Original Version)": "Softbit (Original GFD PStFMBRD Version)",
    "TBoSRE": "The Beginning of Something Really Excellent",
    "The Endless Black (aka Clockwork Negrocity)": "The Endless Black (Clockwork Negrocity)",
    "The Endless Black": "The Endless Black (Clockwork Negrocity)",
    "The Will to Fight": "The Will to Fight (Original Mix)",
    "Three in the Morning (Kali)": "Three in the Morning (Kali's 2 in the AM PM Edit)",
    "Three in the Morning (RJ)": "Three in the Morning (RJ's I Can Barely Sleep In This Casino Remix)",
    "Title Screen (Jailbreak)": "Title Screen",
    "Unintentional Anime": "Unintentional Anime (Piano Version)",
    "Upward Movement": "Upward Movement (Dave Owns)",
    "Walk-Stab-Walk": "Walk-Stab-Walk (R&E)",
    "Welcome to Flavortown (Greatest Hits 2)": "Welcome to Flavortown (Battle Against a Bodacious Foe) (Greatest Hits 2)",
    "Welcome to Flavortown (call and new 2: locomotif)": "Welcome to Flavortown (Battle Against a Bodacious Foe) (call and new 2: locomotif)",
    "Welcome to Flavortown": "Welcome to Flavortown (Battle Against a Bodacious Foe)",
    "You Killed My Father (Prepare to Die)": "You Killed My Father (Prepare To Die)",
    "cool and new Jungle": "cool and new Jungle (Beta Mix)",
    "i transcribed a pokemon song but...": "i transcribed a pokemon song but due to time constraints i fucked up the ending",
    "it's literally just XROM let's not pretend it isn't": "XROM",
    "the version we had of this was unusable...": "the version we had of this was unusable and we had like one day to replace it so yazshu whipped out his kazoo and here we are",
    "you have got to be SHITTONG me (9)": "you have got to be SHITTONG me (temp title) (9)",
    "you have got to be SHITTONG me (Greatest Hits 2)": "you have got to be SHITTONG me (temp title) (Greatest Hits 2)",

    # Discs!
    "~~~~DISC 1~~~~": "Disc 1 (SBURB OST)",
    "~~~~DISC 2~~~~": "Disc 2 (SBURB OST)",
    "~~~~BONUS~~~~": "Bonus (SBURB OST)",
    "• ~ DISC 1 ~ • (LOFAM 2)": "Disc 1 (Land of Fans and Music 2)",
    "•~DISC 1~•": "Disc 1 (Land of Fans and Music 2)",
    "•~DISC 2~•": "Disc 2 (Land of Fans and Music 2)",
    "~DISC 1~": "Disc 1 (Land of Fans and Music 2)",
    "~DISC 2~": "Disc 2 (Land of Fans and Music 2)",
    "˚Disc 1˚": "Disc 1 (Land of Fans and Music 3)",
    "˚Disc 2˚": "Disc 2 (Land of Fans and Music 3)",
    "♪ Disc 1 ♪": "Disc 1 (Beforus)",
    "♫ Disc 2 ♫": "Disc 2 (Beforus)",
    "♬ Disc 3 ♬": "Disc 3 (Beforus)",
    "• ~ 2 SKID~ •": "2 Skid (cool and new volume 7)",
    "• ~ DIKS 1 ~ •": "Diks 1 (cool and new volume 7)",
}

forbidden_names = [
    # Things that need manual disambiguation
    'Light', 'Frost', '~~SIDE 1~~', '~~SIDE 2~~', '~~ADDITIONAL MAYHEM~~', 'Game Over', 'Under the Hat', 'Red Miles', '==>', 'Checkmate', 'Premonition', 'Moondoctor', '==>', 'Checkmate', 'Anticipation', 'Three in the Morning (4 1/3 Hours Late Remix)', 'Fake Fruit Fiesta', 'Showup', 'Stress', 'Contention', 'Mother', 'Fanfare', "Don't Hug Me I'm Scared", 'Let It Snow', "I Don't Want to Miss a Thing", 'Sunrise', 'Mutiny', 'Swan Song', 'Downwards', 'Midnight', 'Meme Voyage', 'Vegetal Colina', 'Enter with Caliborn: Destruction Adventure', '"Libera me" from Bowman', 'Fighting Spirit ~Double Ascended Form~', '1 Through 15', '72.0x SHOWDOWN COMBO', 'Welcome to Flavortown (Battle Against a Bodacious Foe)', 'Welcome to Flavortown', 'you have got to be SHITTONG me (temp title)', 'you have got to be SHITTONG me', 'The End of Something Really Excellent', 'Strife Mayhem', 'Null', 'Aggress', 'Meldey', 'Explored', 'Rain', 'Sunset',
    # Artist names (might be caught by cookie_nsnd if things aren't doing well)
    'HadronKalido', 'Hadron Kalido', 'ostrichlittledungeon', 'Sir Felix (Jaspy)', 'ost', 'cookiefonster', 'Makin', 'wheals', 'Difarem',
    # Typos
    'Horscatska',
]

special_cases = {
    # (title, reference): new_reference
    ("Andrew Hussie's Wild Ride", 'Under the Hat'): 'Under the Hat (Land of Fans and Music)',
    ("Bolin's Cereal Journey", 'Mutiny'): 'Mutiny (Bill Bolin)',
    ("Don't want to hit those notes", "I Don't Want to Miss a Thing"): "I Don't Want to Miss a Thing (Bowman cover)",
    ("I Don't Want to Miss a Thing (Bowman cover)", "I Don't Want to Miss a Thing"): "I Don't Want to Miss a Thing (original)",
    ("I don't wanna smoke an e-cig", "I Don't Want to Miss a Thing"): "I Don't Want to Miss a Thing (original)",
    ("There's a Balcony", 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('24x SHOWDOWN COMBO', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('AAAAAAAAAAAAAAAAAAAAA: A Single', 'Under the Hat'): 'Under the Hat (One Year Older)',
    ('Amabecqueterasurel', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Cascade2 (Freefall Beta)', 'Frost'): 'Frost (Vol. 6)',
    ('Dance-Stab-Dance', 'Under the Hat'): 'Under the Hat (One Year Older)',
    ('Descend', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Detective Cherry Inspector', 'Under the Hat'): 'Trollcops',
    ('Downwards (9)', '1 Through 15'): '1 Through 15 (Intermishin)',
    ('Downwards (9)', 'Fighting Spirit ~Double Ascended Form~'): 'Fighting Spirit ~Double Ascended Form~ (V8lume)',
    ('Emissary of Dance', 'Checkmate'): 'Checkmate (coloUrs and mayhem: Universe B)',
    ('Explored (CANWC)', 'Under the Hat'): 'Under the Hat (One Year Older)',
    ('Explored', 'Under the Hat'): 'Under the Hat (Land of Fans and Music)',
    ('Greifstrife', '1 Through 15'): '1 Through 15 (Intermishin)',
    ('HOMOSUCK. DIRECTOR\'S CUT, OF THE YEAR EDITION.', 'Frost'): 'Frost (Vol. 6)',
    ('Last Chance [Bonus]', '1 Through 15'): '1 Through 15 (Intermishin)',
    ('Let It Snow (Homestuck for the Holidays)', 'Let It Snow'): 'Let It Snow (original)',
    ('Lilith In Starlight', 'Mother'): 'Mother (Malcolm Brown)',
    ('Mother (Bass Prelude)', 'Mother'): 'Mother (One Year Older)',
    ('Mother (Davekind)', 'Mother'): 'Mother (One Year Older)',
    ('Mutention', 'Contention'): 'Contention (Toby Fox & Bill Bolin)',
    ('Mutention', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Mutiny (Piano)', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Mutiny (crapapella)', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Nouveau Babylonica', 'Rain'): 'Rain (Medium)',
    ('Of Bork and Yifs', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Over the hat', 'Under the Hat'): 'Under the Hat (One Year Older)',
    ('Premonition Overdrive', 'Premonition'): 'Premonition (Stuckhome Syndrome)',
    ('S*x (Feat. Femorafreak)', 'Witch Doctor'): 'Witch Doctor (Ross Bagdasarian Sr.)',
    ('SOME UNINSPIRED JADE IDEAS', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Semisepulchritude', 'Aggress'): 'Aggress (Weird Puzzle Tunes)',
    ('Showtime (End Strife Remix)', "I Don't Want to Miss a Thing"): "I Don't Want to Miss a Thing (original)",
    ('Silenced', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Skaian Dreams (Remix)', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Something Familiar', 'Game Over'): 'Game Over (One Year Older)',
    ('Something Familiar', 'Rain'): 'Rain (Medium)',
    ('Something Familiar', 'Under the Hat'): 'Under the Hat (Land of Fans and Music)',
    ('Spacetime Starstriker', '==>'): '==> (CANWC)',
    ('Stab - Stab - Stab', 'Rain'): 'Rain (Medium)',
    ('Step Back, Doors Closing; Step Back To Allow The Doors To Close', 'Welcome to Flavortown (Battle Against a Bodacious Foe)'): 'Welcome to Flavortown (Battle Against a Bodacious Foe) (call and new 2: locomotif)',
    ('Stress (Vol. 9)', 'Stress'): 'Stress (George Buzinkai)',
    ('Strife Synthonic Medley', 'Contention'): 'Contention (Toby Fox & Bill Bolin)',
    ('Strife Synthonic Medley', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Strife! Under the Hat', 'Under the Hat'): 'Under the Hat (One Year Older)',
    ('Sunslammer is my music waifu', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Swan Song (Ancestral)', 'Swan Song'): 'Swan Song (Set It Off)',
    ('The Dance of Oblivion', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('The End of Something Really Excellent (Land of Fans and Music 4)', 'Frost'): 'Frost (Vol. 6)',
    ('Three in the Morning (4 1/3 Hours Late Remix; CaNon edit)', 'Three in the Morning (4 1/3 Hours Late Remix)'): 'Three in the Morning (4 1/3 Hours Late Remix) (voulem. 1)',
    ('Three in the morning (Dif\'s JUST GO THE FUCK TO SLEEP ALREADY mix)', 'Three in the Morning (4 1/3 Hours Late Remix)'): 'Three in the Morning (4 1/3 Hours Late Remix) (voulem. 1)',
    ('Trollcops', 'Under the Hat'): 'Under the Hat (Land of Fans and Music)',
    ('Unbreakable Unity', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('Under the Hat (One Year Older)', 'Under the Hat'): 'Under the Hat (Land of Fans and Music)',
    ('Variating Sides', '1 Through 15'): '1 Through 15 (Intermishin)',
    ('Variating Sides', 'Midnight'): 'Midnight (Intermishin)',
    ('You Killed My Father (Prepare To Die)', 'Checkmate'): 'Checkmate (coloUrs and mayhem: Universe B)',
    ('[S] Ascend, Descend', 'Fanfare'): 'Showtime (Imp Strife Mix)',
    ('[reverie vaporwave]', 'Game Over'): 'Game Over (One Year Older)',
    ('ceru_altwave', 'Sunset'): 'Sunset (Cerulean)',
    ('go down (cool and new Mix)', 'Under the Hat'): 'Under the Hat (One Year Older)',
    ('missathing.midi', "I Don't Want to Miss a Thing"): "I Don't Want to Miss a Thing (Bowman cover)",  # pending composer's word as of 2017-06-23
    ('the march of jaed', 'Mutiny'): 'Mutiny (Bill Bolin)',
    ('the version we had of this was unusable and we had like one day to replace it so yazshu whipped out his kazoo and here we are', "I Don't Want to Miss a Thing"): "I Don't Want to Miss a Thing (Bowman cover)",
    ('~~ GARBAGE ~~ 「 総たわごと 」 ~~ultimate fakeout~~', 'Meme Voyage'): 'Meme Voyage (vol. s*x)',
    ('~~SIDE 2~~ (coloUrs and mayhem: Universe A)', '~~SIDE 1~~'): '~~SIDE 1~~ (coloUrs and mayhem: Universe A)',
    ('~~SIDE 2~~ (coloUrs and mayhem: Universe B)', '~~SIDE 1~~'): '~~SIDE 1~~ (coloUrs and mayhem: Universe B)',
}


def postprocess_title(title, context):
    title = (title.replace('\u200b', ' ')
                  .replace('ICBSITC', 'I Can Barely Sleep In This Casino')
                  .replace('IaMotMC', "I'm a Member of the Midnight Crew")
                  .replace(' (unreleased)', '')
                  .replace(' (??)', '')
                  .replace('\n', '')
                  .replace('  ', ' ')
                  .replace('’', "'")
                  .replace('…', '...')
                  .replace('vol. s*x', 'cool and new volume s*x: hair transplant')
                  .replace('CANH2', 'Cool and New Homestuck 2')
                  .replace('vol. 8', 'V8lume')
                  .replace('(locomotif)', '(call and new 2: locomotif)')  # replacement string includes original so we have to avoid hitting already-correct titles if there are any
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
    with open(f'output/{name}.reverse.gexf', 'w') as f:
        web.dump_gexf(f, reverse_size=True)
    with open(f'output/{name}.titles.txt', 'w') as f:
        web.dump_titles(f)
    with open(f'output/{name}.txt', 'w') as f:
        web.dump_plaintext(f)
    with open(f'output/{name}.reverse.txt', 'w') as f:
        web.dump_plaintext(f, reverse=True)
    with open(f'output/{name}.unknown.txt', 'w') as f:
        web.dump_unknown_references(f)
    with open(f'output/{name}.unicode.txt', 'w') as f:
        web.dump_unicode_titles(f)
    with open(f'output/{name}.pkl', 'wb') as f:
        web.dump_pickle(f)


if __name__ == '__main__':
    main()
