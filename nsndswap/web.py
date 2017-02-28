#!/usr/bin/env python3 -ttb
# nsndswap/web.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import nsndswap.util

class Web(object):
    def __init__(self):
        self.nodes = [] # list of strings
        self.edges = [] # list of edges, as (from, to) tuples
    def _get_id_of(self, title):
        try:
            return self.nodes.index(title)
        except ValueError:
            print(f'Discovered a new song, "{title}"')
            self.nodes.append(title)
            r = len(self.nodes) - 1
            assert self.nodes[r] is title
            return r
    def append(self, nsnd):
        while True:
            try:
                next_song = nsnd.pop()
            except IndexError:
                return # cave johnson, we're done here
            assert isinstance(next_song, nsndswap.util.Track)
            print(f'Turning references into map for "{next_song.title}"')

            node_id = self._get_id_of(next_song.title)

            # document references
            for ref in next_song.references:
                ref_node_id = self._get_id_of(ref)
                self.edges.append((node_id, ref_node_id))
                print(f'Followed a reference from "{next_song.title}" to "{ref}"')
