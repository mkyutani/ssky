import re

from ssky.login import Login

def summarize(source, length_max=0):
    summary = re.sub(r'\s', '_', ''.join(list(map(lambda c: c if c > ' ' else ' ', source))))
    if length_max > 0 and len(summary) > length_max:
        summary = ''.join(summary[:length_max - 2]) + '..'
    return summary

def expand_actor(name: str) -> str:
    if name == 'myself':
        actor = Login().did()
    else:
        actor = name
    return actor