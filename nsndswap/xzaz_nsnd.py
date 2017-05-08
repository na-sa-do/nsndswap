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
    DONE = enum.auto()
    

@enum.unique
class Benchmarks(enum.IntEnum):
    # This is used to manage some songs with duplicated names.
    NONE = 0
    ALTERNIABOUND = 1  # Light and Frost are Medium
    MAYHEM_B = 2  # ~~SIDE 1~~, ~~SIDE 2~~, ~~ADDITIONAL MAYHEM~~ are Universe B


class XzazParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.mode = ParseStates.SEEKING_SONG
        self.active_song = None
        self.all_songs = []
        self.benchmark = Benchmarks.NONE

    def handle_starttag(self, tag, attrs):
        attrs = nsndswap.util.split_attrs(attrs)
        if tag == "hr":
            self.mode = ParseStates.DONE
        elif self.mode == ParseStates.SEEKING_SONG and tag == "td":
            if 'class' not in attrs.keys():
                self.active_song = self.all_songs.pop()
                self.mode = ParseStates.FOUND_SONG
                print(f'Resuming "{self.active_song.title}"')
            elif 'original' in attrs['class']:
                self.mode = ParseStates.SKIPPING_ORIGINAL_SONG
            elif 'hasquotes' in attrs['class']:
                self.mode = ParseStates.FOUND_SONG
        elif self.mode == ParseStates.SEEKING_REFERENCE and tag == "td":
            self.mode = ParseStates.EATING_REFERENCE

    def handle_data(self, data):
        data = nsndswap.util.reencode(data)
        data = self._check_duplicate_title(data)
        if self.mode != ParseStates.DONE and data == "?" * len(data):
            if self.mode in (ParseStates.SKIPPING_ORIGINAL_SONG, ParseStates.SEEKING_SONG):
                print('Scanning a song with ??? (GODDAMMIT RJ)')
                self.active_song = nsndswap.util.Track(data)
            else:
                print('Caught a question marks zone, ending now')
                self.mode = ParseStates.DONE
        elif self.mode == ParseStates.SKIPPING_ORIGINAL_SONG:
            self.all_songs.append(nsndswap.util.Track(data))
            print(f'Skipping "{self.all_songs[-1].title}" (flagged as original)')
        elif self.mode == ParseStates.FOUND_SONG:
            self.active_song = nsndswap.util.Track(data)
            print(f'Scanning song "{self.active_song.title}"')
        elif self.mode == ParseStates.EATING_REFERENCE:
            data = nsndswap.util.reencode(data)
            if data == "":
                return
            print(f'Got "{self.active_song.title}" referencing "{data}"')
            self.mode = ParseStates.SEEKING_REFERENCE
            self.active_song.references.append(data)

    def handle_endtag(self, tag):
        if self.mode == ParseStates.FOUND_SONG and tag == "td":
            self.mode = ParseStates.SEEKING_REFERENCE
        elif self.mode in (ParseStates.SEEKING_REFERENCE, ParseStates.SKIPPING_ORIGINAL_SONG) \
                and tag == "tr":
            self.mode = ParseStates.SEEKING_SONG
            self.all_songs.append(self.active_song)
            self.active_song = None

    def _check_duplicate_title(self, title, update_benchmark=True):
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

        # Update benchmark
        if update_benchmark:
            if title == 'Rest a While' and self.benchmark < Benchmarks.ALTERNIABOUND:
                print('Reached benchmark: ALTERNIABOUND')
                self.benchmark = Benchmarks.ALTERNIABOUND
            elif title == 'Temporal Shenanigans' and self.benchmark < Benchmarks.MAYHEM_B:
                print('Reached benchmark: MAYHEM_B')
                self.benchmark = Benchmarks.MAYHEM_B

        return title


def parse(nsnd):
    parser = XzazParser()
    parser.feed(nsnd)
    return parser.all_songs
