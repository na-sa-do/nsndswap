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
class ParseModes(enum.Enum):
    SEEKING_ALBUM = -2
    SKIPPING_ALBUM_HEADER = -1
    SEEKING_SONG = 0
    SKIPPING_TRACK_NUM = 1
    EATING_TITLE = 2
    SKIPPING_ARTIST = 3
    SKIPPING_ALBUM_ARTIST = 4
    SEEKING_REFERENCE = 5
    EATING_REFERENCE = 6
    RESUMING = 7
    DONE = 8

class CookieParser(html.parser.HTMLParser):
    mode = ParseModes.SEEKING_ALBUM
    active_song = None
    all_songs = []
    got_new_this_round = False

    def _finish_song(self):
        if self.active_song is not None:
            if self.active_song.title != "":
                print(f'Finished "{self.active_song.title}"')
                self.all_songs.append(self.active_song)
                self.active_song = None

    def handle_starttag(self, tag, attrs):
        if self.mode == ParseModes.DONE: return
        attrs = nsndswap.util.split_attrs(attrs)
        if tag == "table" and "class" in attrs.keys() and "no-artist" in attrs["class"]:
            print('Reached unreleased?, ending')
            self.mode = ParseModes.DONE
        elif self.mode == ParseModes.SEEKING_ALBUM and tag == "tr":
            self.mode = ParseModes.SKIPPING_ALBUM_HEADER
        elif self.mode == ParseModes.SEEKING_SONG and tag == "tr" and 'class' in attrs.keys() and 'no-sep' in attrs['class']:
            self.mode = ParseModes.RESUMING
        elif self.mode != ParseModes.SKIPPING_ALBUM_HEADER and tag == "td":
            self.mode = {
                    ParseModes.SEEKING_SONG: ParseModes.SKIPPING_TRACK_NUM,
                    ParseModes.SKIPPING_TRACK_NUM: ParseModes.EATING_TITLE,
                    ParseModes.EATING_TITLE: ParseModes.SKIPPING_ARTIST,
                    ParseModes.RESUMING: ParseModes.SKIPPING_ARTIST,
                    ParseModes.SKIPPING_ARTIST: ParseModes.SKIPPING_ALBUM_ARTIST,
                    ParseModes.SKIPPING_ALBUM_ARTIST: ParseModes.SEEKING_REFERENCE,
                    ParseModes.SEEKING_REFERENCE: ParseModes.EATING_REFERENCE,
                    ParseModes.EATING_REFERENCE: ParseModes.EATING_REFERENCE,
                    }[self.mode]
            if self.mode in (ParseModes.EATING_TITLE, ParseModes.SKIPPING_TRACK_NUM): # ???
                self._finish_song()
                self.active_song = nsndswap.util.Track("")

    def handle_endtag(self, tag):
        if self.mode == ParseModes.DONE: return
        if self.mode in (ParseModes.SKIPPING_ALBUM_HEADER, ParseModes.SEEKING_REFERENCE) and tag == "tr":
            self.mode = ParseModes.SEEKING_SONG
        elif tag == "td":
            if self.mode == ParseModes.EATING_REFERENCE:
                self.mode = ParseModes.SEEKING_REFERENCE
                if self.active_song.references[-1] != "":
                    print(f'Got a reference from "{self.active_song.title}" to "{self.active_song.references[-1]}"')
                self.got_new_this_round = False
            elif self.mode == ParseModes.EATING_TITLE:
                self.mode = ParseModes.SKIPPING_ARTIST
                if self.active_song.title == "":
                    self.active_song = self.all_songs.pop()
                    print(f'Resuming "{self.active_song.title}"')
                else:
                    print(f'Scanning "{self.active_song.title}"')
        elif tag == "table":
            if self.mode != ParseModes.SEEKING_REFERENCE:
                print(f'[W] Reached unexpected end of album in mode {self.mode}')
                self._finish_song()
                self.mode = ParseModes.SEEKING_ALBUM

    def handle_data(self, data):
        if self.mode == ParseModes.DONE: return
        if self.mode == ParseModes.EATING_TITLE:
            self.active_song.title += nsndswap.util.reencode(data)
        elif self.mode == ParseModes.EATING_REFERENCE:
            assert self.active_song.title != ""
            if len(self.active_song.references) is 0 or not self.got_new_this_round:
                self.active_song.references.append("")
                self.got_new_this_round = True
            self.active_song.references[-1] += nsndswap.util.reencode(data)

def parse(nsnd):
    parser = CookieParser()
    parser.feed(nsnd)
    return parser.all_songs
