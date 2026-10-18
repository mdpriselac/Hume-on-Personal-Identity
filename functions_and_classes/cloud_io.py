#The site originally read its static data from a Cloud Storage bucket and its per-publication
#data from Firestore. Both now live as plain files under data/runtime/ and ship with the app;
#the read functions below keep their original names and return shapes so callers don't change.
#The upload/write functions are kept for the offline processing notebooks and still need the
#google-cloud packages and a configured project.
import os
import pandas as pd
import json
from io import StringIO, BytesIO
from functions_and_classes.paper_io import *

RUNTIME_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'runtime')
BUCKET_NAME = os.environ.get('CLOUD_STORAGE_BUCKET', 'treatise-mapping-project.appspot.com')

def _bucket():
    from google.cloud import storage
    return storage.Client().bucket(BUCKET_NAME)

def _firedb():
    from google.cloud import firestore
    return firestore.Client()

#Read functions: these pull from the files in data/runtime/
def df_from_gc_csv(csv_name):
    return pd.read_csv(os.path.join(RUNTIME_DIR, csv_name), index_col=0)

##This does the same thing but for JSON objects
def dic_from_gc_json(json_name):
    with open(os.path.join(RUNTIME_DIR, json_name)) as f:
        return json.load(f)

#Same thing but for txt files, returns a list of lines
def txt_from_gc_txt(txt_name):
    with open(os.path.join(RUNTIME_DIR, txt_name), encoding='utf-8') as f:
        return f.read().split('\n')

#Here's a function to upload to a given file name in the bucket from a given path. It
#was used for the first upload of static docs to the cloud.
def upload_to_gc(file_name, file_path):
    blob = _bucket().blob(file_name)
    blob.upload_from_filename(file_path)

    print(file_name, 'uploaded to gcloud storage')

#the following two functinos write directly from a file to the cloud storage bucket, the first takes a
#data frame in and outputs a csv to the cloud with the file_name. The second takes a dictionary in
#and outputs a json to the cloud with the file_name.
def upload_csv_from_df(file_name, df):
    #this doesn't seem to work as well as the basic upload_to_gc as above
    blob = _bucket().blob(file_name)
    file_obj = StringIO(df.to_csv())
    blob.upload_from_file(file_obj)
    print(file_name, 'uploaded!')

def upload_json_from_dict(file_name, dic_in):
    #enter a name for the file and the dictinoary, will upload json.
    blob = _bucket().blob(file_name)
    file_obj = StringIO(json.dumps(dic_in))
    blob.upload_from_file(file_obj)
    print(file_name, 'uploaded!')

def updateFileToTitleDict():
    #just run this function to update alongside the other updates to static files
    file_to_title_dict = {}
    for name in os.listdir(os.path.join(RUNTIME_DIR, 'publications')):
        if name.endswith('.json'):
            basedict = p_dict_from_fire(name[:-5])
            file_to_title_dict[basedict['name']] = basedict['biblio']['Title of Work']
    with open(os.path.join(RUNTIME_DIR, 'file_to_title_dict.json'), 'w') as f:
        json.dump(file_to_title_dict, f)



##From here down we have Functions for firestore database connections for paper objects:
def upload_paper_dict_to_firedb(paper_dict):
    base_line = {}
    base_line['biblio'] = paper_dict['biblio']
    base_line['name'] = paper_dict['name']
    base_line['totalAggressiveCites'] = paper_dict['totalAggressiveCites']
    base_line['totalStrictCites'] = paper_dict['totalStrictCites']
    base_line['rawNortonScore'] = paper_dict['rawNortonScore']
    base_line['rawSbnScore'] = paper_dict['rawSbnScore']
    base_line['rawTScore'] = paper_dict['rawTScore']
    base_line['rawPageNumScore'] = paper_dict['rawPageNumScore']

    #set the basic information
    basic_ref = _firedb().collection(u'publications').document(paper_dict['name'])
    basic_ref.set(base_line)

    #set the cites
    cites_ref = basic_ref.collection(u'citations')
    cites = {}
    cites[('nortonCites')] = paper_dict['nortonCites']
    cites[('sbnCites')] = paper_dict['sbnCites']
    cites[('tCites')] = paper_dict['tCites']
    cites[('pageNumCites')] = paper_dict['pageNumCites']
    cites[('rawParenthesesCapture')] = paper_dict['rawParenthesesCapture']
    cites_ref.document('cites').set(cites)

    #set the scores
    scores_ref = basic_ref.collection(u'scores')
    scores_ref.document('a_l_p').set(paper_dict['a_l_p'])
    scores_ref.document('a_l_c').set(paper_dict['a_l_c'])
    scores_ref.document('a_w_p').set(paper_dict['a_w_p'])
    scores_ref.document('a_w_c').set(paper_dict['a_w_c'])
    scores_ref.document('s_l_p').set(paper_dict['s_l_p'])
    scores_ref.document('s_l_c').set(paper_dict['s_l_c'])
    scores_ref.document('s_w_p').set(paper_dict['s_w_p'])
    scores_ref.document('s_w_c').set(paper_dict['s_w_c'])

    print('done uploading', paper_dict['name'])

def p_dict_from_fire(fname):
    #publications are stored one JSON file per paper, with the same fields the Firestore documents had
    with open(os.path.join(RUNTIME_DIR, 'publications', os.path.basename(fname) + '.json')) as f:
        return json.load(f)

def paper_from_fire(filename):
    d_from_fire = p_dict_from_fire(filename)
    paper = p_from_dict(d_from_fire)
    return paper

def paper_to_fire(paper_obj):
    p_dict = p_to_dict(paper_obj)
    upload_paper_dict_to_firedb(p_dict)
    print('Done uploading', paper_obj.name)
