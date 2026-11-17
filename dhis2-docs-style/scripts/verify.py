#!/usr/bin/env python3
"""Check that a style edit did not change protected content.

Usage: verify.py BEFORE AFTER
Compares, as multisets: inline code, code blocks, link targets, image paths,
{ #anchors }, bold UI labels, numbers, and URLs. Exit code 1 if any differ.
Differences are printed so a human can judge whether each is intended.
Bold-label changes are marked REVIEW (removing a step title is allowed; changing
a UI label is not) and do not set the exit code.
"""
import re, sys
from collections import Counter

def items(t):
    d = {}
    d['code blocks'] = re.findall(r'```.*?```', t, flags=re.S)
    flat = re.sub(r'\s+', ' ', re.sub(r'```.*?```', '', t, flags=re.S))
    d['inline code'] = re.findall(r'`[^`]+`', flat)   # whitespace-normalised: survives line wraps
    d['link targets'] = re.findall(r'\]\(([^)\s]+)', t)
    d['bare urls'] = re.findall(r'https?://[^\s)>\]]+', t)
    d['anchors'] = re.findall(r'\{\s*#[^}]+\}', t)
    d['bold labels'] = [re.sub(r'\s+', ' ', b).strip() for b in re.findall(r'\*\*([^*]+)\*\*', t)]
    prose = re.sub(r'```.*?```', '', t, flags=re.S)
    prose = re.sub(r'`[^`]*`|\(https?://[^)]*\)|\([^)]*\.(png|jpg|svg|gif)[^)]*\)|\{[^}]*\}', '', prose)
    d['numbers'] = re.findall(r'\b\d+(?:[.,]\d+)*\b', prose)
    return d

if len(sys.argv) != 3:
    sys.exit('usage: verify.py BEFORE AFTER')
try:
    a, b = items(open(sys.argv[1], encoding='utf-8').read()), items(open(sys.argv[2], encoding='utf-8').read())
except OSError as e:
    sys.exit(f'cannot read file: {e}')
bad = 0
for k in a:
    ca, cb = Counter(a[k]), Counter(b[k])
    lost, gained = ca - cb, cb - ca
    status = 'OK' if not lost and not gained else ('REVIEW' if k == 'bold labels' else 'DIFF')
    print(f'{k:14s} before={sum(ca.values()):4d} after={sum(cb.values()):4d}  {status}')
    for x, n in lost.items():
        print(f'    - {n}x {x[:110]!r}')
        bad = bad or (k != 'bold labels')
    for x, n in gained.items():
        print(f'    + {n}x {x[:110]!r}')
        bad = bad or (k != 'bold labels')
sys.exit(bad)
