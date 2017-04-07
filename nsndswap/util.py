#!/usr/bin/env python3
# nsndswap/util.py
# copyright 2017 ViKomprenas, 2-clause BSD license (LICENSE.md)

class Track(object):
    # encapsulation? what encapsulation? just use the properties
    def __init__(self, title):
        self.title = title
        self.references = []
    def __repr__(self):
        return f'Track("{self.title}", {self.references})'

def split_attrs(attrs):
    ret = {}
    for attr in attrs:
        ret[attr[0]] = attr[1]
    return ret

def reencode(string):
    return string.encode('utf-8').decode('ascii', 'ignore')
