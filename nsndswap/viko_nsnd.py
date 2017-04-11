#!/usr/bin/env python3
# nsndswap/viko_nsnd.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

nsnd = {
    # A Shade of Two
    "criticalErr0r": ["Taureg"],
    "Exploreation": ["Explore", "Upward Movement (Dave Owns)"],
    "Taureg": ["Sburban Jungle", "Beatdown"],
    "HammertimeVsThatBlackDoggo": ["Beatdown", "Doctor", "Sburban Jungle", "Liquid Negrocity", "BeatVale", "Penumbra Phantasm"],
    "Saviour of the Dancing Demon": ["Doctor", "Penumbra Phantasm", "Beatdown", "Sburban Jungle"],
    "Player 2": ["Sburban Jungle", "Beatdown", "Liquid Negrocity", "Doctor", "Dance of Thorns"],
    "Cascadium Dioxide": ["Cascade (Beta)", "Flare", "Doctor", "Penumbra Phantasm", "Black Rose / Green Sun", "Black Hole / Green Sun", "Sburban Jungle"],
    "Unnamed Jungle Club Remix (Extra)": ["Sburban Jungle"],
    "Tales of an Unknown Universe": [],
    # M3l0m4ni4c soundcloud
    "At Shadow's Edge": ["Penumbra Phantasm", "Amen Break"],
    "Whirlwind (L8 for D8 Version)": ["Patient", "Penumbra Phantasm", "Doctor", "Showtime", "Crystalanthemums", "Crystamanthequins", "Spider's Claw", "Vriska's Theme"],
    "Wishful Thinking": ["Skies of Skaia", "Skaian Summoning", "Theme", "Rex Duodecim Angelus", "Penumbra Phantasm", "Upward Movement (Dave Owns)", "Lotus", "Homestuck Anthem", "Ruins", "Explore", "Skaian Skuffle", "Sburban Jungle", "Cascade (Beta)", "Overture (Canon Edit)", "Even in Death"],
    "\N{Dingbat Circled Sans-Serif Digit Eight}": ["Spider's Claw", "Vriska's Theme", "Rex Duodecim Angelus", "Amen Break"],
    "Blacker Than Licorice": ["Three in the Morning", "Liquid Negrocity", "Descend", "Umbral Ultimatum", "Walk-Stab-Walk", "Cascade (Beta)", "The Ballad of Jack Noir", "Lotus", "Non Compos Mentis", "Three's a Crowd", "Calamity", "Explore", "Flight of the White Wolf", "Amen Break", "Harlequin"],
}


def parse():
    from nsndswap.util import Track
    return [Track(x, y) for x, y in nsnd.items() if y is not NotImplementedError]
