#!/usr/bin/env python3
# nsndswap/xzaz_nsnd.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import html.parser
import enum
import nsndswap.util


@enum.unique
class ParseStates(enum.Enum):
    SEEKING_SONG = enum.auto()
    FOUND_SONG = enum.auto()
    SKIPPING_ORIGINAL_SONG = enum.auto()
    SEEKING_REFERENCE = enum.auto()
    EATING_REFERENCE = enum.auto()
    SEEKING_UNRELEASED = enum.auto()
    UNRELEASED_SKIP = enum.auto()
    DONE = enum.auto()


@enum.unique
class Benchmarks(enum.IntEnum):
    # This is used to manage some songs with duplicated names.
    NONE = 0
    ALTERNIABOUND = 1  # Light and Frost are Medium
    MAYHEM_B = 2  # ~~SIDE 1~~, ~~SIDE 2~~, ~~ADDITIONAL MAYHEM~~ are Universe B
    ONE_YEAR_OLDER = 3  # Game Over is OYO
    COLLIDE = 4  # Game Over and ==> are Stuckhome


class XzazParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.state = ParseStates.SEEKING_SONG
        self.active_song = None
        self.all_songs = []
        self.benchmark = Benchmarks.NONE
        self.song_class = None
        self.am_in_unreleased = False

    def handle_starttag(self, tag, attrs):
        if self.state == ParseStates.DONE:
            return
        attrs = nsndswap.util.split_attrs(attrs)
        if tag == "hr":
            print('Reached unreleased!')
            self.state = ParseStates.UNRELEASED_SKIP
            self.am_in_unreleased = True
        elif self.state == ParseStates.UNRELEASED_SKIP and tag == "td":
            self.state = ParseStates.SEEKING_SONG
        elif self.state == ParseStates.SEEKING_SONG and tag == "td":
            if 'class' not in attrs.keys():
                self.active_song = self.all_songs.pop()
                self.state = ParseStates.SEEKING_REFERENCE
                print(f'Resuming "{self.active_song.title}"')
            else:
                self.song_class = attrs['class']
                if 'original' in attrs['class']:
                    self.state = ParseStates.SKIPPING_ORIGINAL_SONG
                if 'hasquotes' in attrs['class']:
                    self.state = ParseStates.FOUND_SONG
        elif self.state == ParseStates.SEEKING_REFERENCE and tag == "td":
            self.song_class = attrs['class']
            self.state = ParseStates.EATING_REFERENCE

    def handle_data(self, data):
        if self.state == ParseStates.DONE:
            return
        if data == 'Non-Homestuck songs':
            print('Reached non-Homestuck songs, ending')
            self.state = ParseStates.DONE
        elif data == '????':
            print('Ignoring a ????')
            self.state = ParseStates.SEEKING_UNRELEASED
        elif self.state == ParseStates.SKIPPING_ORIGINAL_SONG:
            data = self._check_duplicate_title(data)
            self.all_songs.append(nsndswap.util.Track(data))
            print(f'Skipping "{self.all_songs[-1].title}" (flagged as original)')
            self.state = ParseStates.SEEKING_SONG
        elif self.state == ParseStates.FOUND_SONG:
            data = self._check_duplicate_title(data)
            self.active_song = nsndswap.util.Track(data)
            self.state = ParseStates.SEEKING_REFERENCE
            print(f'Scanning song "{self.active_song.title}"')
        elif self.state == ParseStates.EATING_REFERENCE:
            if data == "":
                return
            print(f'Got "{self.active_song.title}" referencing "{data}"')
            self.state = ParseStates.SEEKING_REFERENCE
            self.active_song.references.append(data)

    def handle_endtag(self, tag):
        if self.state == ParseStates.DONE:
            return
        if self.state == ParseStates.FOUND_SONG and tag == "td":
            self.state = ParseStates.SEEKING_REFERENCE if not self.am_in_unreleased else ParseStates.UNRELEASED_SKIP
        elif self.state in (ParseStates.SEEKING_REFERENCE, ParseStates.SKIPPING_ORIGINAL_SONG) \
                and tag == "tr":
            self.state = ParseStates.SEEKING_SONG if not self.am_in_unreleased else ParseStates.UNRELEASED_SKIP
            self.all_songs.append(self.active_song)
            self.active_song = None

    def _check_duplicate_title(self, title, *, update_benchmark=True):
        val = self._check_duplicate_title_inner(title, update_benchmark=update_benchmark)
        if val != title:
            print(f'[W] Disambiguated "{title}" to "{val}", class is "{self.song_class}"')
        return val

    def _check_duplicate_title_inner(self, title, *, update_benchmark=True):
        # Check duplicates relative to benchmark
        if title == 'Light':
            if self.benchmark < Benchmarks.ALTERNIABOUND:
                return 'Light (Vol. 5)'
            else:
                return 'Light (Medium)'
        elif title == 'Frost':
            if self.benchmark < Benchmarks.ALTERNIABOUND:
                return 'Frost (Vol. 6)'
            else:
                return 'Frost (Medium)'
        elif title == '~~SIDE 1~~':
            if self.benchmark < Benchmarks.MAYHEM_B:
                return '~~SIDE 1~~ (coloUrs and mayhem: Universe A)'
            else:
                return '~~SIDE 1~~ (coloUrs and mayhem: Universe B)'
        elif title == '~~SIDE 2~~':
            if self.benchmark < Benchmarks.MAYHEM_B:
                return '~~SIDE 2~~ (coloUrs and mayhem: Universe A)'
            else:
                return '~~SIDE 2~~ (coloUrs and mayhem: Universe B)'
        elif title == '~~ADDITIONAL MAYHEM~~':
            if self.benchmark < Benchmarks.MAYHEM_B:
                return '~~ADDITIONAL MAYHEM~~ (coloUrs and mayhem: Universe A)'
            else:
                return '~~ADDITIONAL MAYHEM~~ (coloUrs and mayhem: Universe B)'
        elif title == 'Game Over':
            if self.benchmark < Benchmarks.ONE_YEAR_OLDER or 'unofficial' in self.song_class:
                return 'Game Over (Jailbreak Vol. 1)'
            elif self.benchmark < Benchmarks.COLLIDE:
                return 'Game Over (One Year Older)'
            else:
                return 'Game Over (Stuckhome Syndrome)'
        elif title == 'Under the Hat':
            if self.benchmark < Benchmarks.ONE_YEAR_OLDER or 'unofficial' in self.song_class:
                return 'Under the Hat (Land of Fans and Music)'
            else:
                return 'Under the Hat (One Year Older)'
        elif title == 'Red Miles':
            if self.benchmark < Benchmarks.ONE_YEAR_OLDER:
                return 'Red Miles (Vol. 9)'
            else:
                return 'Red Miles (Land of Fans and Music 2)'
        elif title == 'Disc 1':
            if self.benchmark < Benchmarks.COLLIDE:
                return '˚Disc 1˚'  # LOFAM3
            else:
                return '♪ Disc 1 ♪'  # Beforus
        elif title == '==>':
            # There's one of these in canmt and one here
            return '==> (Stuckhome Syndrome)'
        elif title == 'Checkmate':
            # as above
            return 'Checkmate (coloUrs and mayhem: Universe B)'
        elif title == 'Premonition':
            # as above, but in viko_nsnd
            return 'Premonition (Stuckhome Syndrome)'
        elif title == 'Stress':
            # one is under unreleased, one is Vol. 9
            if self.am_in_unreleased:
                return 'Stress (George Buzinkai)'
            else:
                return 'Stress (Vol. 9)'
        elif title == 'Contention':
            # as above
            if self.am_in_unreleased:
                return 'Contention (Toby Fox & Bill Bolin)'
            else:
                return 'Contention (Land of Fans and Music 3)'

        # Update benchmark
        if update_benchmark:
            if title == 'Rest a While' and self.benchmark < Benchmarks.ALTERNIABOUND:
                print('Reached benchmark: ALTERNIABOUND')
                self.benchmark = Benchmarks.ALTERNIABOUND
            elif title == 'Temporal Shenanigans' and self.benchmark < Benchmarks.MAYHEM_B:
                print('Reached benchmark: MAYHEM_B')
                self.benchmark = Benchmarks.MAYHEM_B
            elif title == 'Cancerous Core' and self.benchmark < Benchmarks.ONE_YEAR_OLDER:
                print('Reached benchmark: ONE_YEAR_OLDER')
                self.benchmark = Benchmarks.ONE_YEAR_OLDER
            elif title == 'Creata (Canon Edit)' and self.benchmark < Benchmarks.COLLIDE:
                print('Reached benchmark: COLLIDE')
                self.benchmark = Benchmarks.COLLIDE

        return title


def parse(nsnd):
    parser = XzazParser()
    parser.feed(nsnd)
    return parser.all_songs
