#!/usr/bin/env python3
# nsndswap/viko_nsnd.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

nsnd = {
    # A Shade of Two
    'criticalErr0r': ['Taureg'],
    'Exploreation': ['Explore', 'Upward Movement (Dave Owns)'],
    'Taureg': ['Sburban Jungle', 'Beatdown'],
    'HammertimeVsThatBlackDoggo': ['Beatdown', 'Doctor', 'Sburban Jungle', 'Liquid Negrocity', 'BeatVale', 'Penumbra Phantasm'],
    'Saviour of the Dancing Demon': ['Doctor', 'Penumbra Phantasm', 'Beatdown', 'Sburban Jungle'],
    'Player 2': ['Sburban Jungle', 'Beatdown', 'Liquid Negrocity', 'Doctor', 'Dance of Thorns'],
    'Cascadium Dioxide': ['Cascade (Beta)', 'Flare', 'Doctor', 'Penumbra Phantasm', 'Black Rose / Green Sun', 'Black Hole / Green Sun', 'Sburban Jungle'],
    'Unnamed Jungle Club Remix (Extra)': ['Sburban Jungle'],
    'Tales of an Unknown Universe': [],
}


def parse():
    from nsndswap.util import Track
    return [Track(x, y) for x, y in nsnd.items() if y is not NotImplementedError]
