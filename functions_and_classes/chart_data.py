#Builds the data behind the literature-level bar charts (these replaced the Tableau Public
#dashboards). Bars are the literature totals from lit_*_w_*.csv, in Treatise order; the
#per-publication scores let the charts be filtered to a single publication, as the Tableau
#dashboards could be.
import os
import json
import pandas as pd
from functions_and_classes.cloud_io import RUNTIME_DIR, df_from_gc_csv, p_dict_from_fire

def _publication_ids():
    return sorted(name[:-5] for name in os.listdir(os.path.join(RUNTIME_DIR, 'publications')) if name.endswith('.json'))

def _label(biblio):
    title = biblio.get('Title of Work')
    author = biblio.get('Author')
    year = biblio.get('Year')
    label = str(title)
    extras = [str(x) for x in (author, year) if isinstance(x, str) and x and x != 'nan']
    if extras:
        label += ' (' + ', '.join(extras) + ')'
    return label

def build_chart_data():
    pubs = {pid: p_dict_from_fire(pid) for pid in _publication_ids()}
    out = {'titles': {pid: _label(p['biblio']) for pid, p in pubs.items()}, 'levels': {}}
    for level, l_key in (('chapter', 'c'), ('paragraph', 'p')):
        level_out = {}
        for search, s_key in (('strict', 's'), ('aggressive', 'a')):
            lit = df_from_gc_csv('lit_' + s_key + '_w_' + l_key + '.csv')['Score']
            score_key = s_key + '_w_' + l_key
            by_pub = {}
            for pid, p in pubs.items():
                nonzero = {loc: round(v, 3) for loc, v in p[score_key].items() if v > 0}
                if nonzero:
                    by_pub[pid] = nonzero
            level_out[search] = {'literature': [round(v, 3) for v in lit.values], 'publications': by_pub}
            level_out['locations'] = [str(loc) for loc in lit.index]
        out['levels'][level] = level_out
    return out

chart_data_json = json.dumps(build_chart_data(), separators=(',', ':'))
