import os
import json
import csv
import pandas as pd
from io import StringIO
from functions_and_classes.treatise_reference_data import treatise_paragraph_list
from functions_and_classes.paper_processing import process_and_score_paper as psp
from functions_and_classes.paper_processing import chapterScores, relativeScoreCalc
from functions_and_classes.paper_io import p_from_dict, p_to_dict, c_from_dict, c_to_dict
from functions_and_classes.cloud_io import p_dict_from_fire
from data.file_to_title_dict import file_to_title_dict, file_list
#generate lit level scores for all 8 kinds by reading from stored JSON data
def lit_scores_from_jsons():
    #create the list of paragraphs to serve as the score sheet
    master_strict_para_list = {}
    for para in treatise_paragraph_list:
        master_strict_para_list[para] = 0
    #create the list of chapter to serve as the c

    master_agg_para_list = {}
    for para in treatise_paragraph_list:
        master_agg_para_list[para] = 0
    #create the list of chapter to serve as the c

    for filer in file_list:
        jd = p_dict_from_fire(filer)
        paper = p_from_dict(jd)
        paper.name = jd['name']

        for para in master_strict_para_list.keys():
                master_strict_para_list[para] += paper.s_w_p[para]
        if paper.totalStrictCites < 1:
                print(paper.name, 'has no strict cites')

        for para in master_agg_para_list.keys():
                master_agg_para_list[para] += paper.a_w_p[para]
        if paper.totalAggressiveCites < 1:
                print(paper.name, 'has no aggressive cites')

    lit_s_w_c = chapterScores(master_strict_para_list)
    lit_a_w_c = chapterScores(master_agg_para_list)
    lit_s_l_p = relativeScoreCalc(master_strict_para_list)
    lit_s_l_c = chapterScores(lit_s_l_p)
    lit_a_l_p = relativeScoreCalc(master_agg_para_list)
    lit_a_l_c = chapterScores(lit_a_l_p)

    od = {'lit_s_w_p': master_strict_para_list, 'lit_s_w_c': lit_s_w_c, 'lit_a_w_p': master_agg_para_list, 'lit_a_w_c': lit_a_w_c, 'lit_s_l_p': lit_s_l_p, 'lit_s_l_c': lit_s_l_c, 'lit_a_l_p': lit_a_l_p, 'lit_a_l_c': lit_a_l_c}

    return od

def write_lit_chap_dict_to_gc_csv(din, file_name):
    sio = StringIO()
    wtr = csv.writer(sio)
    wtr.writerow(('Chapter', 'Score'))
    for chap in din.keys():
        wtr.writerow((chap, din[chap]))
    from functions_and_classes.cloud_io import _bucket
    blob = _bucket().blob(file_name+'.csv')
    blob.upload_from_string(sio.getvalue())
    sio.close()
    print('done uploading', file_name)

def write_lit_para_dict_to_gc_csv(din, file_name):
    sio = StringIO()
    wtr = csv.writer(sio)
    wtr.writerow(('Paragraph', 'Score'))
    for para in din.keys():
        wtr.writerow((para, din[para]))
    from functions_and_classes.cloud_io import _bucket
    blob = _bucket().blob(file_name+'.csv')
    blob.upload_from_string(sio.getvalue())
    sio.close()
    print('done uploading', file_name)

def lit_to_csv(dict_of_dicts):
    for dname in dict_of_dicts.keys():
        if 'p' in dname:
            write_lit_para_dict_to_gc_csv(dict_of_dicts[dname], dname)
            print('generated csv for', dname)
        elif 'c' in dname:
            write_lit_chap_dict_to_gc_csv(dict_of_dicts[dname], dname)
            print('generated csv for', dname)

def locationFrequency(location, df):
    location_series = df.loc[location]
    zfilter = location_series > 0
    csloc_series = location_series[zfilter].sort_values(ascending=False)

    out_list = []

    for article in csloc_series.index:
        out_list.append((article, file_to_title_dict[article], round(csloc_series.loc[article],3)))

    return out_list
