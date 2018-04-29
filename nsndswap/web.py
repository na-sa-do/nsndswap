#!/usr/bin/env python3
# nsndswap/web.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import datetime
import random
import colorsys
import nsndswap.util


BOX_SIDE_MAXDEV = 5
BOX_SIDE_STDDEV = 100
SIZE_FACTOR = 197
SIZE_OFFSET = 3
SATURATION = 0.5
VALUE = 0.9


def _tween(amount, start, end):
    difference = end - start
    return start + (difference * amount)


def _xmlencode(string):
    chars = {
        # note that this one has to be first, or else the other &s are caught
        '&': '&amp;',
        '"': '&quot;',
        '\'': '&apos;',
        '<': '&lt;',
        '>': '&gt;',
    }
    for ch in chars.keys():
        string = string.replace(ch, chars[ch])
    return string


class NodeSnapshot:
    def __init__(self):
        self.original_index = None
        self.in_deg = 0
        self.out_deg = 0
        self.weighted_in_deg = 0
        self.weighted_out_deg = 0
        self.color = (0, 0, 0)  # between 0 and 256
        self.size = 1
        self.position = 0 + 0j

    @property
    def deg(self):
        return self.in_deg + self.out_deg

    @property
    def weighted_deg(self):
        return max(self.weighted_in_deg, self.weighted_out_deg)


class Web:
    def __init__(self):
        self.nodes = []  # list of strings
        self.edges = []  # list of edges, as (from, to) tuples
        self._nodes_discovered_via_entries = []  # list of node indexes that we've seen the reflists for

    def _get_id_of(self, title):
        try:
            return self.nodes.index(title)
        except ValueError:
            print(f'Discovered a new song, "{title}"')
            self.nodes.append(title)
            r = len(self.nodes) - 1
            assert self.nodes[r] is title
            return r

    def append(self, nsnd, *, override_on_duplicate=[], skip_on_duplicate=[]):
        duplicates_shared = set(override_on_duplicate) & set(skip_on_duplicate)
        if len(duplicates_shared) > 0:
            print('override_on_duplicate and skip_on_duplicate share entries, aborting!')
            print('The duplicate entries are:')
            print(', '.join(duplicates_shared))
            raise SystemExit(2)
        for next_song in nsnd:
            assert isinstance(next_song, nsndswap.util.Track)
            if next_song.title == "":
                print('Skipping a null song')
                continue
            print(f'Turning references into map for "{next_song.title}"')

            node_id = self._get_id_of(next_song.title)
            if node_id in self._nodes_discovered_via_entries:
                if next_song.title in override_on_duplicate:
                    print(f'[W] Overriding "{next_song.title}" on duplicate')
                    self.edges = [x for x in self.edges if x[0] != node_id]
                elif next_song.title in skip_on_duplicate:
                    print(f'[W] Skipping "{next_song.title}" on duplicate')
                    continue
                else:
                    print('Illegal duplicated song, stopping')
                    raise SystemExit(2)
            else:
                self._nodes_discovered_via_entries.append(node_id)

            # document references
            for ref in next_song.references:
                if ref.lower() in ("", "n/a"):
                    print('Skipping a null reference')
                    continue
                ref_node_id = self._get_id_of(ref)
                if ref_node_id == node_id:
                    print(f'Skipping a reference from "{next_song.title}" to itself')
                    continue
                edge = (node_id, ref_node_id)
                if edge in self.edges:
                    print(f'Skipping a duplicated reference from "{next_song.title}" to "{ref}"')
                    continue
                self.edges += [edge]
                print(f'Followed a reference from "{next_song.title}" to "{ref}"')

    def make_snapshot(self, reverse_size=False):
        snapshot = [NodeSnapshot() for _ in self.nodes]

        print('Adding basics to snapshot')
        for i in range(len(self.nodes)):
            snapshot[i].index = i
            snapshot[i].name = self.nodes[i]

        print('Adding degrees to snapshot')
        for ref in self.edges:
            snapshot[ref[0]].out_deg += 1
            snapshot[ref[1]].in_deg += 1

        print('Computing largest degree (for weighted degrees)')
        largest_in = 1
        largest_out = 1
        for data in snapshot:
            largest_in = max(largest_in, data.in_deg)
            largest_out = max(largest_out, data.out_deg)

        print('Computing weighted degrees, sizes')
        for data in snapshot:
            data.weighted_in_deg = data.in_deg / largest_in
            data.weighted_out_deg = data.out_deg / largest_out
            size_deg = data.weighted_in_deg if not reverse_size else data.weighted_out_deg
            # don't ask me where this off-by-one comes from
            data.size = size_deg * SIZE_FACTOR + SIZE_OFFSET - 1

        print('Randomizing node locations and colors')

        def make_component(r):
            return min(max(r.gauss(0, BOX_SIDE_STDDEV), -BOX_SIDE_STDDEV * BOX_SIDE_MAXDEV),
                       BOX_SIDE_STDDEV * BOX_SIDE_MAXDEV)

        for i in range(len(snapshot)):
            r = random.Random()
            r.seed(self.nodes[i])
            snapshot[i].position = complex(make_component(r), make_component(r))
            snapshot[i].color = tuple(round(x * 255) for x
                in colorsys.hsv_to_rgb(r.random(), SATURATION, VALUE))

        print('Done building node data')
        return snapshot

    def dump_gexf(self, outf, reverse_size=False):
        reverse_str = 'reversed ' if reverse else ''
        snapshot = self.make_snapshot(reverse=reverse)
        print(f'Dumping {reverse_str}web')
        outf.write(f"""<?xml version="1.0" encoding="UTF-8" ?>
<gexf xmlns="http://www.gexf.net/1.3" version="1.3" xmlns:viz="http://www.gexf.net/1.3/viz">
    <meta lastmodifieddate="{str(datetime.date.today())}">
        <creator>nsndswap</creator>
        <description>This is a list of references (remixes, arrangements, samples, etc.) in Homestuck music.</description>
    </meta>
    <graph mode="static" defaultedgetype="directed">
        <nodes>""")
        for node_id in range(len(self.nodes)):
            outf.write(f"""
            <node id=\"{node_id}\" label=\"{_xmlencode(self.nodes[node_id])}\">
                <viz:size value="{snapshot[node_id].size}"></viz:size>
                <viz:position x="{snapshot[node_id].position.real}" y="{snapshot[node_id].position.imag}"></viz:position>
                <viz:color r="{snapshot[node_id].color[0]}" g="{snapshot[node_id].color[1]}" b="{snapshot[node_id].color[2]}"></viz:color>
            </node>""")
        outf.write("""
        </nodes>
        <edges>""")
        for edge_id in range(len(self.edges)):
            edge = self.edges[edge_id]
            if reverse_size:
                edge = edge[1], edge[0]
            outf.write(f"""
            <edge id="{edge_id}" source="{edge[0]}" target="{edge[1]}">
                <viz:color r="192" g="192" b="192"></viz:color>
            </edge>""")
        outf.write("""
        </edges>
    </graph>
</gexf>\n""")
        print('Done dumping web')

    def dump_titles(self, outf):
        print('Dumping titles')
        for title in self.nodes:
            outf.write(title + '\n')
        print('Done dumping titles')

    def dump_unknown_references(self, outf):
        print('Dumping unknown references')
        unknownrefs = set(self.nodes) - set(self.nodes[x] for x in self._nodes_discovered_via_entries)
        for title in unknownrefs:
            outf.write(title + '\n')
        print('Done dumping unknown references')

    def dump_plaintext(self, outf, reverse=False):
        reverse_str = 'reversed ' if reverse else ''
        print(f'Dumping {reverse_str}plaintext')
        for node_i in range(len(self.nodes)):
            references = []
            for ref in self.edges:
                if ref[0 if not reverse else 1] == node_i:
                    references.append(self.nodes[ref[1 if not reverse else 0]])
            if references:
                outf.write(f'{self.nodes[node_i]}:' + '\n  - '.join([''] + references).rstrip() + '\n')
            elif node_i in self._nodes_discovered_via_entries:
                outf.write(f'{self.nodes[node_i]}: none.\n')
        print(f'Done dumping {reverse_str}plaintext')

    def dump_unicode_titles(self, outf):
        print('Dumping unicode titles')
        for node in self.nodes:
            if node != node.encode('ascii', 'ignore').decode('ascii'):
                outf.write(f'{node}\n')
        print('Done dumping unicode titles')

    def dump_pickle(self, outf):
        from pickle import dump
        print('Pickling the web')
        dump(self, outf)
        print('Done pickling')
