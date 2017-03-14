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
    DONE = 5

class XzazParser(html.parser.HTMLParser):
    mode = ParseModes.SEEKING_SONG
    active_song = None
    all_songs = []

    def handle_starttag(self, tag, attrs):
        attrs = nsndswap.util.split_attrs(attrs)
        if tag == "hr":
            self.mode = ParseModes.DONE
        elif self.mode == ParseModes.SEEKING_SONG and tag == "td":
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
        data = nsndswap.util.reencode(data)
        if self.mode != ParseModes.DONE and data == "?" * len(data):
            if self.mode in (ParseModes.SKIPPING_ORIGINAL_SONG, ParseModes.SEEKING_SONG):
                print('Scanning a song with ??? (GODDAMMIT RJ)')
                self.active_song = nsndswap.util.Track(data)
            else:
                print('Caught a question marks zone, ending now')
                self.mode = ParseModes.DONE
        elif self.mode == ParseModes.SKIPPING_ORIGINAL_SONG:
            self.all_songs.append(nsndswap.util.Track(data))
            print(f'Skipping "{self.all_songs[-1].title}" (flagged as original)')
        elif self.mode == ParseModes.FOUND_SONG:
            self.active_song = nsndswap.util.Track(data)
            print(f'Scanning song "{self.active_song.title}"')
        elif self.mode == ParseModes.EATING_REFERENCE:
            data = nsndswap.util.reencode(data)
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
