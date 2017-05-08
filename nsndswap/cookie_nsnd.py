#!/usr/bin/env python3
# nsndswap/cookie_nsnd.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

# Okay, a quick overview of how cookie's nsnd is structured:
# The first row is a header, which Word (wtf cookie) neglects to mark,
# so we'll just skip it automatically. Then, the next row is the first song!
# First cell in the row is the track number, skip that. Then the title,
# then the musician and album artist, then the references. If there is more than
# one row to the same song, we need to skip the first _four_ slots rather than
# Lambda's _one_ slot. We can safely ignore the <span>s and <b>s and <i>s
# scattered everywhere, but we _do_ need to watch for cell end tags, unlike
# in Lambda's. That's because occasionally Word decides to split one contiguous
# phrase into two (or more!) separate data regions, probably an artifact of the
# formatting being applied badly. Anyway, that's... relatively straightforward.

import html.parser
import enum
import nsndswap.util


@enum.unique
class ParseStates(enum.Enum):
    SEEKING_ALBUM = enum.auto()
    SKIPPING_ALBUM_HEADER = enum.auto()
    SEEKING_SONG = enum.auto()
    SKIPPING_TRACK_NUM = enum.auto()
    EATING_TITLE = enum.auto()
    SKIPPING_ARTIST = enum.auto()
    SKIPPING_ALBUM_ARTIST = enum.auto()
    SEEKING_REFERENCE = enum.auto()
    EATING_REFERENCE = enum.auto()
    RESUMING = enum.auto()
    DONE = enum.auto()


@enum.unique
class Benchmarks(enum.IntEnum):
    NONE = 0
    PARTWAY_THROUGH_CANV5 = 1  # there are two tracks ON THE SAME DAMN ALBUM WITH THE SAME DAMN NAME


class CookieParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.state = ParseStates.SEEKING_ALBUM
        self.active_song = None
        self.all_songs = []
        self.got_new_this_round = False
        self.benchmark = Benchmarks.NONE

    def _finish_song(self):
        if self.active_song is not None:
            if self.active_song.title != "":
                self.active_song.title = self._check_benchmarks(self.active_song.title.strip())
                print(f'Finished "{self.active_song.title}"')
                self.all_songs.append(self.active_song)
                self.active_song = None

    def _check_benchmarks(self, title, *, is_ref=False, update_benchmark=True):
        val = self._check_benchmarks_inner(title, is_ref=is_ref, update_benchmark=update_benchmark)
        if val != title:
            print(f'[W] Disambiguated "{title}" to "{val}"')
        return val

    def _check_benchmarks_inner(self, title, *, is_ref=False, update_benchmark=True):
        # Check
        if title == 'Moondoctor':
            if self.benchmark < Benchmarks.PARTWAY_THROUGH_CANV5:
                return 'Moondoctor (Difarem)'
            else:
                return 'Moondoctor (Shwan)'
        elif title == '==>':
            # There's one of these in xzaz_nsnd and one here
            return '==> (CANWC)'
        elif title == 'daet with roze':
            # as above
            return 'daet with roze (CANWC)'
        elif title == 'Checkmate' and not is_ref:
            # as above
            return 'Checkmate (CANWC)'
        elif title == 'Dentist':
            # as above, but viko_nsnd
            return 'Dentist (Double Hats Eyewear)'
        elif title == 'Doctor' and not is_ref:
            # fucking hell
            return 'Doctor (Zalgo)'

        # Update
        if update_benchmark:
            if title == 'Dogtor (get it?)' and self.benchmark < Benchmarks.PARTWAY_THROUGH_CANV5:
                print('Reached benchmark: PARTWAY_THROUGH_CANV5')
                self.benchmark = Benchmarks.PARTWAY_THROUGH_CANV5
        
        return title

    def handle_starttag(self, tag, attrs):
        if self.state == ParseStates.DONE:
            return
        attrs = nsndswap.util.split_attrs(attrs)
        if tag == "table" and "class" in attrs.keys() and "no-artist" in attrs["class"]:
            print('Reached unreleased?, ending')
            self.state = ParseStates.DONE
        elif self.state == ParseStates.SEEKING_ALBUM and tag == "tr":
            self.state = ParseStates.SKIPPING_ALBUM_HEADER
        elif self.state == ParseStates.SEEKING_SONG and tag == "tr" and 'class' in attrs.keys() and 'no-sep' in attrs['class']:
            self.state = ParseStates.RESUMING
        elif self.state != ParseStates.SKIPPING_ALBUM_HEADER and tag == "td":
            self.state = {
                ParseStates.SEEKING_SONG: ParseStates.SKIPPING_TRACK_NUM,
                ParseStates.SKIPPING_TRACK_NUM: ParseStates.EATING_TITLE,
                ParseStates.EATING_TITLE: ParseStates.SKIPPING_ARTIST,
                ParseStates.RESUMING: ParseStates.SKIPPING_ARTIST,
                ParseStates.SKIPPING_ARTIST: ParseStates.SKIPPING_ALBUM_ARTIST,
                ParseStates.SKIPPING_ALBUM_ARTIST: ParseStates.SEEKING_REFERENCE,
                ParseStates.SEEKING_REFERENCE: ParseStates.EATING_REFERENCE,
                ParseStates.EATING_REFERENCE: ParseStates.EATING_REFERENCE,
            }[self.state]
            if self.state in (ParseStates.EATING_TITLE, ParseStates.SKIPPING_TRACK_NUM):  # ???
                self._finish_song()
                self.active_song = nsndswap.util.Track("")

    def handle_endtag(self, tag):
        if self.state == ParseStates.DONE:
            return
        if self.state in (ParseStates.SKIPPING_ALBUM_HEADER, ParseStates.SEEKING_REFERENCE) and tag == "tr":
            self.state = ParseStates.SEEKING_SONG
        elif tag == "td":
            if self.state == ParseStates.EATING_REFERENCE:
                self.state = ParseStates.SEEKING_REFERENCE
                if self.active_song.references[-1] != "":
                    print(f'Got a reference from "{self.active_song.title}" to "{self.active_song.references[-1]}"')
                self.got_new_this_round = False
            elif self.state == ParseStates.EATING_TITLE:
                self.state = ParseStates.SKIPPING_ARTIST
                if self.active_song.title == "":
                    self.active_song = self.all_songs.pop()
                    print(f'Resuming "{self.active_song.title}"')
                else:
                    print(f'Scanning "{self.active_song.title}"')
        elif tag == "table":
            if self.state != ParseStates.SEEKING_REFERENCE:
                print(f'[W] Reached unexpected end of album in state {self.state}')
                self._finish_song()
                self.state = ParseStates.SEEKING_ALBUM

    def handle_data(self, data):
        if self.state == ParseStates.DONE:
            return
        if self.state == ParseStates.EATING_TITLE:
            self.active_song.title += nsndswap.util.reencode(data)
        elif self.state == ParseStates.EATING_REFERENCE:
            assert self.active_song.title != ""
            if len(self.active_song.references) is 0 or not self.got_new_this_round:
                self.active_song.references.append("")
                self.got_new_this_round = True
            self.active_song.references[-1] += nsndswap.util.reencode(data)


def parse(nsnd):
    parser = CookieParser()
    parser.feed(nsnd)
    return parser.all_songs
