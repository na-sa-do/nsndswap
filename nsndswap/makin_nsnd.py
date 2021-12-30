#!/usr/bin/env python3# nsndswap/makin_nsnd.py
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
    SKIPPING_ARTIST_NAME = enum.auto()
    SEEKING_UNHOMESTUCK = enum.auto()
    EATING_UNHOMESTUCK = enum.auto()
    DONE = enum.auto()


@enum.unique
class Benchmarks(enum.IntEnum):
    # This is used to manage some songs with duplicated names.
    NONE = 0
    ALTERNIABOUND = 1
    MAYHEM_B = 2
    ONE_YEAR_OLDER = 3
    COLLIDE = 4
    LOFAM4 = 5
    STLAP = 6
    CARETAKERS = 7
    UNRELEASED = 998
    NONHOMESTUCK = 999


class MakinParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.state = ParseStates.SEEKING_SONG
        self.active_song = None
        self.all_songs = []
        self.benchmark = Benchmarks.NONE
        self.song_class = None
        self.allow_resume = False

    def handle_starttag(self, tag, attrs):
        if self.state == ParseStates.DONE:
            return
        attrs = nsndswap.util.split_attrs(attrs)
        if (tag == "tr" and 'class' in attrs.keys() and attrs['class'] is not None
                and 'unreleasedartist' in attrs['class']):
            self.state = ParseStates.SKIPPING_ARTIST_NAME
        elif self.state == ParseStates.SEEKING_SONG and tag == "td":
            if 'class' not in attrs.keys():
                if self.allow_resume:
                    self.active_song = self.all_songs.pop()
                    self.state = ParseStates.SEEKING_REFERENCE
                    print(f'Resuming "{self.active_song.title}"')
                else:
                    if self.benchmark >= Benchmarks.UNRELEASED:
                        print('Skipped a resume in unreleased, re-enabling resume')
                        self.allow_resume = True
                    else:
                        print('Skipped a resume')
            else:
                self.song_class = attrs['class']
                if 'original' in attrs['class']:
                    self.state = ParseStates.SKIPPING_ORIGINAL_SONG
                elif 'hasquotes' in attrs['class']:
                    self.state = ParseStates.FOUND_SONG
        elif self.state == ParseStates.SEEKING_REFERENCE and tag == "td":
            self.song_class = attrs.get('class', '')
            self.state = ParseStates.EATING_REFERENCE
        elif self.state == ParseStates.SEEKING_UNHOMESTUCK and tag == "td":
            if ('class' in attrs.keys() and attrs['class'] is not None
                    and 'nonhomestucksongname' in attrs['class']):
                self.state = ParseStates.EATING_UNHOMESTUCK

    def handle_data(self, data):
        if self.state == ParseStates.DONE:
            return
        if data == ' Unreleased or removed songs':  # note the leading space
            print('Reached unreleased')
            self.state = ParseStates.SEEKING_SONG
            self.benchmark = Benchmarks.UNRELEASED
        elif data == ' Non-Homestuck songs':  # note the leading space
            print('Reached non-Homestuck songs')
            self.state = ParseStates.SEEKING_UNHOMESTUCK
            self.benchmark = Benchmarks.NONHOMESTUCK
        elif self.state == ParseStates.SKIPPING_ORIGINAL_SONG:
            data = self._check_duplicate_title(data)
            self.all_songs.append(nsndswap.util.Track(data))
            print(f'Skipping "{self.all_songs[-1].title}" (flagged as original)')
            self.state = ParseStates.SEEKING_SONG
            self.allow_resume = False
        elif self.state == ParseStates.FOUND_SONG:
            if data == "":
                raise Exception("Unexpected blank field in state FOUND_SONG")
            data = self._check_duplicate_title(data)
            self.active_song = nsndswap.util.Track(data)
            self.state = ParseStates.SEEKING_REFERENCE
            self.allow_resume = True
            print(f'Scanning song "{self.active_song.title}"')
        elif self.state == ParseStates.EATING_REFERENCE:
            if data == "":
                return
            if data == "[see CANWC list]":
                print(f'Skipping "{self.active_song.title} linking to cookie list')
            else:
                print(f'Got "{self.active_song.title}" referencing "{data}"')
                self.active_song.references.append(data)
            self.state = ParseStates.SEEKING_REFERENCE
        elif self.state == ParseStates.EATING_UNHOMESTUCK:
            if data == "":
                return
            data = self._check_duplicate_title(data)
            print(f'Got unhomestuck song "{data}"')
            self.all_songs.append(nsndswap.util.Track(data))
            self.state = ParseStates.SEEKING_UNHOMESTUCK

    def handle_endtag(self, tag):
        if self.state == ParseStates.DONE:
            return
        if self.state == ParseStates.FOUND_SONG and tag == "td":
            self.state = ParseStates.SEEKING_REFERENCE
        elif self.state in (ParseStates.SEEKING_REFERENCE, ParseStates.SKIPPING_ORIGINAL_SONG) \
                and tag == "tr":
            self.state = ParseStates.SEEKING_SONG
            self.all_songs.append(self.active_song)
            self.active_song = None
            if self.benchmark == Benchmarks.UNRELEASED:
                print('Disabling resume for unreleased')
                self.allow_resume = False
        elif self.state == ParseStates.SKIPPING_ARTIST_NAME and tag == "td":
            self.state = ParseStates.SEEKING_SONG
        elif tag == 'body':
            self.state = ParseStates.DONE
            print('Finished at </body>')

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
        if title == 'Let It Snow':
            if self.benchmark < Benchmarks.ALTERNIABOUND:
                return 'Let It Snow (Homestuck for the Holidays)'
            else:
                return 'Let It Snow (original)'
        elif title == 'Frost':
            if self.benchmark < Benchmarks.ALTERNIABOUND:
                return 'Frost (Vol. 6)'
            else:
                return 'Frost (Medium)'
        elif title == "I Don't Want to Miss a Thing":
            if self.benchmark < Benchmarks.ALTERNIABOUND:
                return "I Don't Want to Miss a Thing (Bowman cover)"
            else:
                return "I Don't Want to Miss a Thing (original)"
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
            elif self.benchmark < Benchmarks.LOFAM4:
                return '♪ Disc 1 ♪'  # Beforus
            elif self.benchmark < Benchmarks.CARETAKERS:
                return 'Disc 1 (Stable Time Loops and Paradoxes)'
            else:
                return 'Disc 1 (Stable Time Loops and Paradoxes 2)'
        elif title == 'The End of Something Really Excellent':
            if self.benchmark < Benchmarks.LOFAM4:
                return 'The End of Something Really Excellent (Stuckhome Syndrome)'
            else:
                return 'The End of Something Really Excellent (Land of Fans and Music 4)'
        elif title == 'Null':
            if self.benchmark < Benchmarks.MAYHEM_B:
                return 'Null (Song of Skaia)'
            else:
                return 'Null (James Roach)'
        elif title == 'Aggress':
            if self.benchmark < Benchmarks.UNRELEASED:
                return 'Aggress (Weird Puzzle Tunes)'
            else:
                return 'Aggress (Mark Hadley)'
        elif title == 'Beatdown':
            if self.benchmark < Benchmarks.UNRELEASED:
                return 'Beatdown'  # this one specifically is just stupid, why bother disambiguating it
            else:
                return 'Beatdown (Toby Fox)'
        elif title == 'Already Here':
            if self.benchmark < Benchmarks.UNRELEASED:
                return 'Already Here (Stuckhome Syndrome)'
            else:
                return 'Already Here (Unknown)'
        elif title == '==>':
            # There's one of these in canmt and one here
            return '==> (Stuckhome Syndrome)'
        elif title == 'Checkmate':
            # as above
            return 'Checkmate (coloUrs and mayhem: Universe B)'
        elif title == 'Fanfare':
            # as above
            return 'Fanfare (Jailbreak Vol. 1)'
        elif title == 'Sunrise':
            # as above
            return 'Sunrise (One Year Older)'
        elif title == 'Strife Mayhem':
            # as above
            return 'Strife Mayhem (Land of Fans and Music 4)'
        elif title == 'Explored':
            # as above
            return 'Explored (Toby Fox & George Buzinkai)'
        elif title == 'Sunset':
            # as above
            return 'Sunset (Toby Fox)'
        elif title == 'Starsetter':
            # as above
            return 'Starsetter (Stable Time Loops and Paradoxes)'
        elif title == 'Premonition':
            # as above, but in viko_nsnd
            return 'Premonition (Stuckhome Syndrome)'
        elif title == 'Home':
            # as above
            return 'Home (Moons of Theseus)'
        elif title == 'Midnight':
            # two of these here AND one in canmt. wow
            if self.benchmark >= Benchmarks.UNRELEASED:
                return 'Midnight (Malcolm Brown)'
            else:
                return 'Midnight (Land of Fans and Music 4)'
        elif title == 'Rain':
            # as above
            if self.benchmark >= Benchmarks.NONHOMESTUCK:
                return 'Rain (Rob Scallon)'
            else:
                return 'Rain (Medium)'
        elif title == 'Stress':
            # one is under unreleased, one is Vol. 9
            if self.benchmark >= Benchmarks.UNRELEASED:
                return 'Stress (George Buzinkai)'
            else:
                return 'Stress (Vol. 9)'
        elif title == 'Contention':
            # as above
            if self.benchmark >= Benchmarks.UNRELEASED:
                return 'Contention (Toby Fox & Bill Bolin)'
            else:
                return 'Contention (Land of Fans and Music 3)'
        elif title == 'Mother':
            # as above
            if self.benchmark >= Benchmarks.UNRELEASED:
                return 'Mother (Malcolm Brown)'
            else:
                return 'Mother (One Year Older)'
        elif title == 'Mutiny':
            # as above
            if self.benchmark >= Benchmarks.UNRELEASED:
                return 'Mutiny (Bill Bolin)'
            else:
                return 'Mutiny (Ancestral)'
        elif title == 'Swan Song':
            # as above, but in non-homestuck
            if self.benchmark >= Benchmarks.NONHOMESTUCK:
                return 'Swan Song (Set It Off)'
            else:
                return 'Swan Song (Ancestral)'
        elif title == 'Main Theme':
            return 'Breath of the Wild Theme'
        elif title == 'Title Theme':
            return 'RollerCoaster Tycoon Theme'
        elif title == 'Daydreamer':
            if self.benchmark >= Benchmarks.STLAP:
                return 'Daydreamer (Stable Time Loops and Paradoxes)'
            else:
                return 'Daydreamer (Land of Fans and Music 4)'
        elif title == 'Cornered':
            if self.benchmark >= Benchmarks.CARETAKERS:
                return 'Cornered (Stuckhome Syndrome)'
            else:
                return 'Cornered (Hiveswap Act 2)'

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
            elif title == 'Merge' and self.benchmark < Benchmarks.LOFAM4:
                print('Reached benchmark: LOFAM4')
                self.benchmark = Benchmarks.LOFAM4
            elif title == 'Solicide' and self.benchmark < Benchmarks.STLAP:
                print('Reached benchmark: STLAP')
                self.benchmark = Benchmarks.STLAP
            elif title == 'A Paradox Legend' and self.benchmark < Benchmarks.CARETAKERS:
                print('Reached benchmark: CARETAKERS')
                self.benchmark = Benchmarks.CARETAKERS

        return title


def parse(nsnd):
    parser = MakinParser()
    parser.feed(nsnd)
    return parser.all_songs
