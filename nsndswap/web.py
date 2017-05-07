#!/usr/bin/env python3
# nsndswap/web.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

import datetime
import random
import nsndswap.util


BOX_SIDE_MAXDEV = 5
BOX_SIDE_STDDEV = 100
COLOR_BLUE_CONSTANT = 0
COLOR_GREEN_FACTOR = 127
COLOR_GREEN_OFFSET = 32
COLOR_RED_FACTOR = 127
COLOR_RED_OFFSET = 32
SIZE_FACTOR = 60


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


class NodeData:
    def __init__(self):
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
        return (self.weighted_in_deg + self.weighted_out_deg) / 2


class Web:
    def __init__(self):
        self.nodes = []  # list of strings
        self.edges = []  # list of edges, as (from, to) tuples

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
            if next_song.title == "":
                print('Skipping a null song')
                continue
            print(f'Turning references into map for "{next_song.title}"')

            node_id = self._get_id_of(next_song.title)

            # document references
            for ref in next_song.references:
                if ref == "":
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

    def _build_node_data(self):
        nodes_data = [NodeData() for _ in self.nodes]

        print('Adding degrees to node_data')
        for i in range(len(self.nodes)):
            for ref in self.edges:
                if ref[0] == i:
                    nodes_data[i].out_deg += 1
                elif ref[1] == i:
                    nodes_data[i].in_deg += 1

        print('Computing largest degree (for weighted degrees)')
        largest_in = 1
        largest_out = 1
        for data in nodes_data:
            largest_in = max(largest_in, data.in_deg)
            largest_out = max(largest_out, data.out_deg)

        print('Computing weighted degrees, colors, sizes')
        for data in nodes_data:
            data.weighted_in_deg = data.in_deg / largest_in
            data.weighted_out_deg = data.out_deg / largest_out
            data.color = [data.weighted_in_deg * COLOR_RED_FACTOR, data.weighted_out_deg * COLOR_GREEN_FACTOR, 0]
            data.color = tuple([round(data.color[0]) + COLOR_RED_OFFSET, round(data.color[1]) + COLOR_GREEN_OFFSET, COLOR_BLUE_CONSTANT])
            assert len(data.color) == 3
            data.size = data.weighted_in_deg * (SIZE_FACTOR - 1) + 1

        print('Randomizing node locations')

        def make_component():
            return min(max(random.gauss(0, BOX_SIDE_STDDEV), -BOX_SIDE_STDDEV * BOX_SIDE_MAXDEV),
                       BOX_SIDE_STDDEV * BOX_SIDE_MAXDEV)

        for node_data in nodes_data:
            node_data.position = complex(make_component(), make_component())

        print('Done building node data')
        return nodes_data

    def dump_gexf(self, outf):
        node_data = self._build_node_data()
        print('Dumping web')
        outf.write(f"""<?xml version="1.0" encoding="UTF-8" ?>
<gexf xmlns="http://www.gexf.net/1.3" version="1.3" xmlns:viz="http://www.gexf.net/1.3/viz">
    <meta lastmodifieddate="{str(datetime.date.today())}">
        <creator>nsndswap</creator>
        <description>This is a list of references (remixes, arrangements, samples, etc.) in Homestuck music.</description>
    </meta>
    <graph mode="static" defaultedgetype="directed">
        <nodes>\n""")
        for node_id in range(len(self.nodes)):
            outf.write(f"""
            <node id=\"{node_id}\" label=\"{_xmlencode(self.nodes[node_id])}\" >
                <viz:size value="{node_data[node_id].size}"></viz:size>
                <viz:position x="{node_data[node_id].position.real}" y="{node_data[node_id].position.imag}"></viz:position>
                <viz:color r="{node_data[node_id].color[0]}" g="{node_data[node_id].color[1]}" b="{node_data[node_id].color[2]}"></viz:color>
            </node>""")
        outf.write("""
        </nodes>
        <edges>\n""")
        for edge_id in range(len(self.edges)):
            outf.write(f"""
            <edge id="{edge_id}" source="{self.edges[edge_id][0]}" target="{self.edges[edge_id][1]}">
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

    def dump_plaintext(self, outf, reverse=False):
        reverse_str = 'reversed ' if reverse else ''
        print(f'Dumping {reverse_str}plaintext')
        for node_i in range(len(self.nodes)):
            references = []
            for ref in self.edges:
                if ref[0 if not reverse else 1] == node_i:
                    references.append(self.nodes[ref[1 if not reverse else 0]])
            if references:
                outf.write(f'{self.nodes[node_i]}:' + '\n  - '.join([''] + references).rstrip())
            else:
                outf.write(f'{self.nodes[node_i]}: none.')
            outf.write('\n')
        print(f'Done dumping {reverse_str}plaintext')
