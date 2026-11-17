#!/usr/bin/env python3
"""Readability and style signals for a DHIS2 docs markdown file.

Usage: measure.py FILE [FILE ...]
These are SIGNALS, not scores. Code, tables, headings, links and HTML are
excluded from the prose counts. Grade is Flesch-Kincaid and ignores jargon.
"""
import re, sys

def clean(t):
    t = re.sub(r'^---.*?---\n', '', t, flags=re.S)
    t = re.sub(r'```.*?```', '', t, flags=re.S)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', t)
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)
    t = re.sub(r'^\s*\|.*$', '', t, flags=re.M)
    t = re.sub(r'^#+\s.*$', '', t, flags=re.M)
    t = re.sub(r'`[^`]*`', 'X', t)
    t = re.sub(r'^\s*>?\s*[-*]\s+', '\n\n', t, flags=re.M)   # list items are their own sentences
    t = re.sub(r'^\s*\d+\.\s+', '\n\n', t, flags=re.M)
    return re.sub(r'[*_]{1,3}', '', t)

def syl(w):
    w = re.sub(r'[^a-z]', '', w.lower())
    if not w:
        return 0
    c = len(re.findall(r'[aeiouy]+', w))
    if w.endswith('e') and c > 1:
        c -= 1
    return max(c, 1)

PATTERNS = {
    'em dash': r'—| -- ',
    'e.g./i.e./etc.': r'\b(e\.g\.|i\.e\.|etc\.|viz\.)',
    'simply/just/easy': r'\b(simply|just|easily|easy|quickly|obviously|of course)\b',
    'please': r'\bplease\b',
    'we/our/let\'s': r"\b(we|our|let's)\b",
    '"the user(s)"': r'\bthe users?\b|\busers\b',
    'will': r'\bwill\b',
    'may': r'\bmay\b',
    'click on': r'\bclick(ing)? on\b',
    'above/below': r'\b(above|below)\b',
    'in order to / via / prior to': r'\b(in order to|via|prior to|subsequent|utili[sz]e|leverage|facilitate|hence|thus|whereby)\b',
    'currently/recently/new': r'\b(currently|recently|new|latest)\b',
    'meta-data': r'\bmeta-data\b',
    'orgunit': r'\borgunit\b',
    'organization (US)': r'\borgani[z]ation\b',
}

def measure(path):
    raw = open(path, encoding='utf-8', errors='ignore').read()
    t = clean(raw)
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n\s*\n', t) if len(s.split()) >= 3]
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", t)
    n, ns = max(len(words), 1), max(len(sents), 1)
    lens = [len(s.split()) for s in sents]
    fk = 0.39 * n / ns + 11.8 * sum(syl(w) for w in words) / n - 15.59
    lo = t.lower()
    out = {
        'words': n,
        'sentences': ns,
        'avg sentence length': round(n / ns, 1),
        '% sentences > 25 words': round(100 * sum(x > 25 for x in lens) / ns),
        '% sentences > 35 words': round(100 * sum(x > 35 for x in lens) / ns),
        'FK grade': round(fk, 1),
        'passive (approx)': len(re.findall(r'\b(is|are|was|were|be|been|being)\s+(\w+ly\s+)?\w+(ed|en)\b', lo)),
        'DHIS 2 (spaced)': raw.count('DHIS 2'),
    }
    for k, p in PATTERNS.items():
        src = raw if k in ('em dash',) else lo
        out[k] = len(re.findall(p, src))
    return out, sorted(zip(lens, sents), reverse=True)[:5]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: measure.py FILE [FILE ...]')
    for p in sys.argv[1:]:
        try:
            m, longest = measure(p)
        except OSError as e:
            sys.exit(f'cannot read {p}: {e}')
        print(f'== {p}')
        for k, v in m.items():
            print(f'  {k:32s} {v}')
        print('  longest sentences:')
        for l, s in longest:
            print(f'    [{l}] {" ".join(s.split())[:160]}')
