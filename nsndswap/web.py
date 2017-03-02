#!/usr/bin/env python3 -ttb
# nsndswap/web.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import datetime
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
        for next_song in nsnd:
            assert isinstance(next_song, nsndswap.util.Track)
            print(f'Turning references into map for "{next_song.title}"')

            node_id = self._get_id_of(next_song.title)

            # document references
            for ref in next_song.references:
                ref_node_id = self._get_id_of(ref)
                self.edges.append((node_id, ref_node_id))
                print(f'Followed a reference from "{next_song.title}" to "{ref}"')
    def dump_gexf(self, outf):
        print('Dumping web')
        outf.write(f"""<?xml version="1.0" encoding="UTF-8" ?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
    <meta lastmodifieddate="{str(datetime.date.today())}">
        <creator>nsndswap</creator>
        <description>This is a list of references (remixes, arrangements, samples, etc.) in Homestuck music.</description>
    </meta>
    <graph mode="static" defaultedgetype="directed">
        <nodes>\n""")
        for node_id in range(len(self.nodes)):
            outf.write(f"            <node id=\"{node_id}\" label=\"{self.nodes[node_id].replace('&', '&amp;')}\" />\n")
        outf.write("""
        </nodes>
        <edges>\n""")
        for edge_id in range(len(self.edges)):
            outf.write(f"            <edge id=\"{edge_id}\" source=\"{self.edges[edge_id][0]}\" target=\"{self.edges[edge_id][1]}\" />\n")
        outf.write("""
        </edges>
    </graph>
</gexf>\n""")
        print('Done dumping web')
