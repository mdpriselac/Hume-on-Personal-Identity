import pandas as pd
from data.file_to_title_dict import file_to_title_dict, file_list
from functions_and_classes.cloud_io import df_from_gc_csv, upload_csv_from_df
#This file has two categories of thigns worth importing for usage:
#first is a function for generating comparisons:
#article_comps(filename, min_num_cites=1, min_num_comps=100, a_or_s="a", p_or_c="p")
#Second are the comparative data frame updaters:
#updateALCcomps, updateALPcomps, updateSLCcomps, updateSLPcomps
#those will update the a_l_p_comp csvs and when the data module is reloaded it will
#draw the new data frames.

def df_col_similarity(df, colx, coly):
    total_diff = 0
    for para in df.index:
        total_diff += abs(df[colx][para] - df[coly][para])
    return total_diff


#goal is to create a csv with comparative data
s_l_p = df_from_gc_csv('lit_s_l_p.csv').rename(columns={'Score':'Literature'})
a_l_p = df_from_gc_csv('lit_a_l_p.csv').rename(columns={'Score':'Literature'})
s_l_c = df_from_gc_csv('lit_s_l_c.csv').rename(columns={'Score':'Literature'})
a_l_c = df_from_gc_csv('lit_a_l_c.csv').rename(columns={'Score':'Literature'})

#generate a df that pairs names of files with total cites of both strict and aggressive
strict_cite_count = {}
agg_cite_count = {}

#I probably should just pull these paper dicts ONCE and make a paper dict that goes from
#file names to the other thing. I might want to separate out the latter functions from here so the
#updates aren't triggered every time...
file_to_pdict_dict = {}
for file in file_list:
    file_to_pdict_dict[file] = p_dict_from_fire(file)

for file in file_list:
    jd = file_to_pdict_dict[file]
    strict_cite_count[jd['name']] = jd['totalStrictCites']
    agg_cite_count[jd['name']] = jd['totalAggressiveCites']

scc_df = pd.DataFrame.from_dict(strict_cite_count, orient='index', columns=['totalStrictCites'])
agg_df = pd.DataFrame.from_dict(agg_cite_count, orient='index', columns=['totalAggressiveCites'])
total_strict_cites = scc_df['totalStrictCites'].sum()
total_agg_cites = agg_df['totalAggressiveCites'].sum()
lit_scc = pd.DataFrame([total_strict_cites], index=['Literature'], columns=['totalStrictCites'])
#this pairs strict cite count with file names
scc_df = scc_df.append(lit_scc)
lit_agg = pd.DataFrame([total_agg_cites], index=['Literature'], columns=['totalAggressiveCites'])
#this pairs aggressive cite counts with file names
agg_df = agg_df.append(lit_agg)

#first let's work on slps
for file in file_list:
    jd = file_to_pdict_dict[file]
    if int(jd['totalStrictCites']) > 0:
        pdf = pd.DataFrame.from_dict(jd['s_l_p'], orient='index', columns=['Score'])
        s_l_p[jd['name']] = pdf['Score']

def updateSLPcomps():
    s_l_p_comps = pd.DataFrame(columns=s_l_p.columns, index=s_l_p.columns)
    for column in s_l_p_comps.columns:
        for ind in s_l_p_comps.index:
            s_l_p_comps[column][ind] = df_col_similarity(s_l_p,column,ind)
    s_l_p_comps = pd.merge(s_l_p_comps, scc_df, left_index=True, right_index=True)
    upload_csv_from_df('s_l_p_comp.csv', s_l_p_comps)


#second alps
for file in file_list:
    jd = file_to_pdict_dict[file]
    if int(jd['totalAggressiveCites'])>0:
        pdf = pd.DataFrame.from_dict(jd['a_l_p'], orient='index', columns=['Score']))
        a_l_p[jd['name']] = pdf['Score']

def updateALPcomps():
    a_l_p_comps = pd.DataFrame(columns=a_l_p.columns, index=a_l_p.columns)
    for column in a_l_p_comps.columns:
        for ind in a_l_p_comps.index:
            a_l_p_comps[column][ind] = df_col_similarity(a_l_p,column,ind)
    a_l_p_comps = pd.merge(a_l_p_comps, agg_df, left_index=True, right_index=True)
    upload_csv_from_df('a_l_p_comp.csv', a_l_p_comps)


#third slcs
for file in file_list:
    jd = file_to_pdict_dict[file]
    if int(jd['totalStrictCites']) > 0:
        pdf = pd.DataFrame.from_dict(jd['s_l_c'], orient='index', columns=['Score'])
        s_l_c[jd['name']] = pdf['Score']

def updateSLCcomps():
    s_l_c_comps = pd.DataFrame(columns=s_l_c.columns, index=s_l_c.columns)
    for column in s_l_c_comps.columns:
        for ind in s_l_c_comps.index:
            s_l_c_comps[column][ind] = df_col_similarity(s_l_c,column,ind)
    s_l_c_comps = pd.merge(s_l_c_comps, scc_df, left_index=True, right_index=True)
    upload_csv_from_df('s_l_c_comp.csv', s_l_c_comps)

#fourth alcs
alcs = []
for file in file_list:
    jd = file_to_pdict_dict[file]
    if int(jd['totalAggressiveCites'])>0:
        pdf = pd.DataFrame.from_dict(jd['a_l_c'], orient='index', columns=['Score']))
        a_l_c[jd['name']] = pdf['Score']

def updateALCcomps():
    a_l_c_comps = pd.DataFrame(columns=a_l_c.columns, index=a_l_c.columns)
    for column in a_l_c_comps.columns:
        for ind in a_l_c_comps.index:
            a_l_c_comps[column][ind] = df_col_similarity(a_l_c,column,ind)
    a_l_c_comps = pd.merge(a_l_c_comps, agg_df, left_index=True, right_index=True)
    upload_csv_from_df('a_l_c_comp.csv', a_l_c_comps)

def updateCompData():
    updateALCcomps()
    print('done updating Aggresive Chapter Comp data')
    updateSLCcomps()
    print('done updating Strict Chapter Comp data')
    updateALPcomps()
    print('done updating Aggressive Paragraph Comp data')
    updateSLPcomps()
    print('done updating Strict Paragraph Comp data')
    print('done updating all data')
#now that we've finished the functions for generating and saving data I'll add functions for generating comparative data for an individual article
