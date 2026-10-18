import os
import pandas as pd
from functions_and_classes.classes import *
from data.comparison_data import a_l_p_comp, a_l_c_comp, s_l_p_comp, s_l_c_comp
from data.file_to_title_dict import file_to_title_dict
from functions_and_classes.cloud_io import p_dict_from_fire
#note: When I do this with Firestore, I think the easier way to do this will be to go through the paper object to access
#the relevant score sheet dictionary as it's saved there and load the dictionary and then load teh data frame from
#the dictinoary direclty.

#I'll want to change this to pull from database directly papername-scores-document(a_l_c).get().to_dict(), and then turn that into the dataframe instead of the csv.
def generateListOfCites(filename, a_s="a", c_p="c", w_l="w"):
    scores = p_dict_from_fire(filename)
    if a_s == "a":
        if c_p == "c":
            if w_l == "w":
                doc_dict = scores['a_w_c']
            elif w_l == 'l':
                doc_dict = scores['a_l_c']
        elif c_p == 'p':
            if w_l == "w":
                doc_dict = scores['a_w_p']
            elif w_l == 'l':
                doc_dict = scores['a_l_p']
    elif a_s == "s":
        if c_p == "c":
            if w_l == "w":
                doc_dict = scores['s_w_c']
            elif w_l == 'l':
                doc_dict = scores['s_l_c']
        elif c_p == 'p':
            if w_l == "w":
                doc_dict = scores['s_w_p']
            elif w_l == 'l':
                doc_dict = scores['s_l_p']
                ###NEED TO FIGURE OUT HOW TO GO FROM THIS DICT TO SAME DF with INDEX
    dlistpairs = []
    for pair in doc_dict.items():
        key = pair[0]
        value = pair[1]
        lp = [key, value]
        dlistpairs.append(lp)
    df = pd.DataFrame(dlistpairs,  columns=['Location', 'Count'])
    nz = df['Count'] > 0
    scdf = df[nz].sort_values('Count', ascending=False)
    entries = scdf['Location'].count()
    out_list = []
    for i in range(0,entries):
        pair = (scdf.iloc[i]['Location'], round(scdf.iloc[i]['Count'],3))
        out_list.append(pair)
    return out_list


def df_cns(df_in,n_many_return=25):
    n = min(n_many_return, int(df_in.count()))
    zfilter = df_in['Score'] > 1
    return df_in[zfilter].sort_values('Score', ascending=False)[:n]

def n_agg_filter(df_in, num):
    return df_in['totalAggressiveCites'] > num

def m_agg_similar(filename, min_cites, min_similar, df_in):
    min_cit = max(0,min_cites)
    min_c = n_agg_filter(df_in, min_cit)
    min_si = min(min_similar,len(df_in[min_c].index)-1)
    sim_score_to_beat = 1.05 * df_in[min_c].sort_values(filename)[min_si:min_si+1][filename].values[0]
    score_to_beat_filter = df_in[min_c][filename] <= sim_score_to_beat

    return df_in[min_c][score_to_beat_filter].sort_values(filename)

def a_l_c_comp_process(file, minimum_comp_cites, minimum_sim_comps):
    df = pd.merge(a_l_c_comp[file], a_l_c_comp['totalAggressiveCites'], left_index=True, right_index=True)
    return m_agg_similar(file, minimum_comp_cites, minimum_sim_comps, df)[1:]

def a_l_p_comp_process(file, minimum_comp_cites, minimum_sim_comps):
    df = pd.merge(a_l_p_comp[file], a_l_p_comp['totalAggressiveCites'], left_index=True, right_index=True)
    return m_agg_similar(file, minimum_comp_cites, minimum_sim_comps, df)[1:]

def n_strict_filter(df_in, num):
    return df_in['totalStrictCites'] > num

def m_strict_similar(filename, min_cites, min_similar, df_in):
    min_cit = max(0,min_cites)
    min_c = n_strict_filter(df_in, min_cit)
    min_si = min(min_similar,len(df_in[min_c].index)-1)
    sim_score_to_beat = 1.05 * df_in[min_c].sort_values(filename)[min_si:min_si+1][filename].values[0]
    score_to_beat_filter = df_in[min_c][filename] <= sim_score_to_beat

    return df_in[min_c][score_to_beat_filter].sort_values(filename)

def s_l_c_comp_process(file, minimum_comp_cites, minimum_sim_comps):
    df = pd.merge(s_l_c_comp[file], s_l_c_comp['totalStrictCites'], left_index=True, right_index=True)
    return m_strict_similar(file, minimum_comp_cites, minimum_sim_comps, df)[1:]

def s_l_p_comp_process(file, minimum_comp_cites, minimum_sim_comps):
    df = pd.merge(s_l_p_comp[file], s_l_p_comp['totalStrictCites'], left_index=True, right_index=True)
    return m_strict_similar(file, minimum_comp_cites, minimum_sim_comps, df)[1:]

#this is in the end all that needs to be imported from this file to generate the comparative data for an individaul file, along with the a_l_p_comp etc dfs from data
def article_comps(filename, min_num_cites=1, min_num_comps=100, a_or_s="a", p_or_c="p"):
    if a_or_s == "a":
        if p_or_c == "p":
            return a_l_p_comp_process(filename, minimum_comp_cites=min_num_cites, minimum_sim_comps=min_num_comps)
        elif p_or_c == "c":
            return a_l_c_comp_process(filename, minimum_comp_cites=min_num_cites, minimum_sim_comps=min_num_comps)
        else:
            return print('be sure to choose "p" or "c" for the p_or_c argument')
    elif a_or_s == "s":
        if p_or_c == "p":
            return s_l_p_comp_process(filename, minimum_comp_cites=min_num_cites, minimum_sim_comps=min_num_comps)
        elif p_or_c == "c":
            return s_l_c_comp_process(filename, minimum_comp_cites=min_num_cites, minimum_sim_comps=min_num_comps)
        else:
            return print('be sure to choose "p" or "c" for the p_or_c argument')
    else:
        return print('be sure to choose "a" or "s" for the a_or_s argument')

def generateCompData(df_in,filename):
    count = df_in[filename].count()
    out_list = []
    for i in range(0,count):
        file_comp_info = {}
        file_comp_info['rank'] = i+1
        file_comp_info['score'] = round(df_in.iloc[i][filename],3)
        if df_in.iloc[i].name.strip() == "Literature":
            file_comp_info['file'] = "Literature"
            file_comp_info['title'] = "Literature"
            file_comp_info['cites'] = df_in.iloc[i][df_in.columns[1]]
        else:
            file_comp_info['file'] = df_in.iloc[i].name.strip()
            file_comp_info['title'] = file_to_title_dict[df_in.iloc[i].name.strip()]
            file_comp_info['cites'] = int(df_in.iloc[i][df_in.columns[1]])
        out_list.append(file_comp_info)
    return out_list
