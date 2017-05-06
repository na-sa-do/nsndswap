# `nsndswap`

A Python program that parses [this website](http://xzazupsilon.webs.com/nsnd.html) and [this one](https://wheals.github.io/canwc/nsnd.html), and outputs [gexf files](https://gephi.org/gexf/format/). Made because Makin wanted to automate maintenance of [this page](http://recordcrash.com/nsnd/nsnd_ultimate.html) (offline as of 2017-05-05). Currently, it does almost all of the work, but positioning has to be done in Gephi because my attempt at implementing an algorithm for that was too slow to be workable (even after translation to Cython).

# How to use

```
py3 -m nsndswap
```

For the most part, the copious logs can be ignored. This creates four files in the working directory: `homestuck.gexf`, `canwc.gexf`, `almost_everything.gexf`, and `everything.gexf`, containing different subsets of the data used. All node positions are randomized so that a positioning algorithm in Gephi has better luck.

# Output files

The following files are output to the `output/` directory:

- `homestuck` contains details of all songs on the first page (Homestuck soundtrack, unofficialmspafans, Homestuck Gaiden, and miscellaneous other things).
- `canwc` contains details of all songs on the second page (the Cool and New Web Comic soundtrack).
- `almost_everything` contains both of the previous files' data.
- `everything` contains the previous file's data and a few additions of my own (which you can find in `viko_nsnd.py`, if you're interested in their raw form).

These files are dumped in two formats:

- `.gexf` - directed graphs of references
- `.titles.txt` - the titles, one per line
