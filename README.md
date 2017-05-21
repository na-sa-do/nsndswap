# `nsndswap`

A Python program that parses [this website](http://xzazupsilon.webs.com/nsnd.html) and [this one](https://wheals.github.io/canwc/nsnd.html), and outputs [gexf files](https://gephi.org/gexf/format/).

# How to use

Run `run.sh`. For the most part, the copious logs can be ignored.

# Output files

The following datasets are output to the `output/` directory:

- `homestuck` contains details of all songs on the first page (Homestuck soundtrack, unofficialmspafans, Homestuck Gaiden, and miscellaneous other things).
- `canwc` contains details of all songs on the second page (the Cool and New Web Comic soundtrack).
- `viko` contains a few additions I maintain (the raw form is in `viko_nsnd.py`.
- `everything` contains all the previous files' data.

These are dumped in five formats:

- `.gexf` - directed graphs of references
- `.txt` - simple _ad hoc_ plain-text format
- `.titles.txt` - the titles, one per line
- `.reverse.txt` - the format in `.txt`, but showing incoming references rather than outgoing
- `.unknown.txt` - titles, one per line, of things which are referenced, but which don't have reference lists of their own (useful for checking for name misspellings and such)
