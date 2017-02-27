#!/usr/bin/env python3 -ttb
# nsndswap/xzaz_nsnd.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import html.parser
import enum
import nsndswap.util

@enum.unique
class ParseModes(enum.Enum):
    SEEKING_SONG = 0
    FOUND_SONG = 1
    SKIPPING_ORIGINAL_SONG = 2
    SEEKING_REFERENCE = 3
    EATING_REFERENCE = 4

class XzazParser(html.parser.HTMLParser):
    mode = ParseModes.SEEKING_SONG
    active_song = None
    all_songs = []

    def handle_starttag(self, tag, attrs):
        attrs = nsndswap.util.split_attrs(attrs)
        if self.mode == ParseModes.SEEKING_SONG and tag == "td":
            if 'class' not in attrs.keys():
                self.active_song = self.all_songs.pop()
                self.mode = ParseModes.FOUND_SONG
                print(f'Resuming {self.active_song.title}')
            elif 'original' in attrs['class']:
                self.mode = ParseModes.SKIPPING_ORIGINAL_SONG
            elif 'hasquotes' in attrs['class']:
                self.mode = ParseModes.FOUND_SONG
        elif self.mode == ParseModes.SEEKING_REFERENCE and tag == "td":
            self.mode = ParseModes.EATING_REFERENCE
    
    def handle_data(self, data):
        if self.mode == ParseModes.SKIPPING_ORIGINAL_SONG:
            print(f'Skipping "{data}" (flagged as original)')
            self.all_songs.append(nsndswap.util.Track(data))
        elif self.mode == ParseModes.FOUND_SONG:
            print(f'Scanning song "{data}"')
            self.active_song = nsndswap.util.Track(data)
        elif self.mode == ParseModes.EATING_REFERENCE:
            if data == "":
                return
            print(f'Got "{self.active_song.title}" referencing "{data}"')
            self.mode = ParseModes.SEEKING_REFERENCE
            self.active_song.references.append(data)

    def handle_endtag(self, tag):
        if self.mode == ParseModes.FOUND_SONG and tag == "td":
            self.mode = ParseModes.SEEKING_REFERENCE
        elif self.mode in (ParseModes.SEEKING_REFERENCE, ParseModes.SKIPPING_ORIGINAL_SONG) \
            and tag == "tr":
            self.mode = ParseModes.SEEKING_SONG
            self.all_songs.append(self.active_song)
            self.active_song = None

def parse(nsnd):
    parser = XzazParser()
    parser.feed(nsnd)
    return parser.all_songs
