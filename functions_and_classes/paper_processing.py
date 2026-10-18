import os
import re
import pandas as pd
from functions_and_classes.classes import *
from functions_and_classes.text_processing import ultimateParser as uP
from data.biblio_data import dl_files

#the takeaway from this set of functions is:
#process_and_score_paper(filename, data_frame)
#you'll need a file name and a data frame with bibliographic information to
#pair the file name with



def processPaper(paper_obj):
    #this function take a paper object in and will fill the search lists with citations
    #First, conduct the searches
    paper_obj.NortonSearch()
    paper_obj.SbnSearch()
    paper_obj.parenthesesCapture()

    #second, set the easy .cleanedCitations
    for cite in paper_obj.nortonCites:
        cite.cleanedCitation = cite.rawCitationText
    for cite in paper_obj.sbnCites:
        cite.cleanedCitation = cite.rawCitationText[3:]

    #third, sort the parentheses
    #in the sorting, we'll do a first pass to get the citations that start with T or Hume or THN or Treatise:
    strict_check = re.compile(r'(Hume|Treatise|THN|T)(([, \-\–\—p\.]*)((?<!\d)\d{1,3}(?!\d)))+', re.I)
    num_check = re.compile(r'(([, \-\–\—p\.]*)((?<!\d)\d{1,3}(?!\d)))+', re.I)
    for cite in paper_obj.rawParenthesesCapture:
        #make the strict check:
        #I start it at the first character to ignore the open parens that
        if strict_check.match(cite.rawCitationText[1:]) != None:
            if num_check.search(cite.rawCitationText) != None:
                num_text = num_check.search(cite.rawCitationText).group().replace(' ', '')
                #remove 'p', 'P', '.' from the nubmers
                num_text = num_text.replace('p','')
                num_text = num_text.replace('P','')
                num_text = num_text.replace('.','')
                #set the cleanedCitation to the num_text
                cite.cleanedCitation = num_text
                #add the cite to the tCites
                paper_obj.tCites.append(cite)
        else:
            if num_check.search(cite.rawCitationText) != None:
                num_text = num_check.search(cite.rawCitationText).group().replace(' ', '')
                #remove 'p', 'P', '.' from the nubmers
                num_text = num_text.replace('p','')
                num_text = num_text.replace('P','')
                num_text = num_text.replace('.','')
                #set the cleanedCitation to the num_text
                cite.cleanedCitation = num_text
                #add the cite to pageNumCites, if it's more than one digit
                #because otherwise we catch too much argument numbering use
                #of parentheses:
                if len(num_text) > 1:
                    paper_obj.pageNumCites.append(cite)

    print (paper_obj.name, 'processed')

def chapterScores(para_scores):
    #this function takes in a dictionary score sheet for paragraph scores
    #and returns a dictionary score sheet for chapter scores
    chapter_scores = {}
    chapter_pattern = re.compile(r'(Abs)|(App\.)|(0)|(\d\.\d\.\d{1,2})')
    for para in para_scores.keys():
        chapter = chapter_pattern.match(para).group()
        if chapter not in chapter_scores.keys():
            chapter_scores[chapter] = 0
        chapter_scores[chapter] += para_scores[para]
    return chapter_scores



def citesToScores(cite_collection):
    #this function takes in a list of cites as you'd have in a paper object that's been processed
    #and returns a dictionary object with a count of total successful cites that were scored
    #and a scoresheet dictionary at the paragraph level
    out_sheet = {}
    successful_cites = 0
    for para in treatise_paragraph_list:
        out_sheet[para] = 0
    for cite in cite_collection:
        try:
            for pair in uP(cite.cleanedCitation):
                out_sheet[pair[0]] += pair[1]
            successful_cites += 1
        except Exception as e:
            print(cite.cleanedCitation, 'generated an error while scoring:', e)

    do = {}
    do['score_sheet'] = out_sheet
    do['total_cites'] = successful_cites

    return do

def relativeScoreCalc(score_dict):
    #this function calculates a score sheet relative to the paper object that is processed
    #ie how what percentage of the article's total cites go to a particular paragraph
    #get the total number of points awarded in the score_dict
    total_points = 0
    for entry in score_dict.keys():
        total_points += score_dict[entry]

    if total_points == 0:
        return score_dict

    else:
        #create the blank relative sheet
        relative_sheet = {}
        for para in treatise_paragraph_list:
            relative_sheet[para] = 0
        #fill in the blank relative sheet
        for para in relative_sheet.keys():
            relative_sheet[para] = 100 * score_dict[para]/total_points

        return relative_sheet


def paperScoreSetter(paper_obj):
    paper_obj.rawNortonScore = citesToScores(paper_obj.nortonCites)['score_sheet']
    paper_obj.rawSbnScore = citesToScores(paper_obj.sbnCites)['score_sheet']
    paper_obj.rawTScore = citesToScores(paper_obj.tCites)['score_sheet']
    paper_obj.rawPageNumScore = citesToScores(paper_obj.pageNumCites)['score_sheet']

    if len(paper_obj.nortonCites) > 5:
        paper_obj.s_w_p = paper_obj.rawNortonScore
        paper_obj.totalStrictCites = citesToScores(paper_obj.nortonCites)['total_cites']

    else:
        if len(paper_obj.sbnCites) > 5:
            strict_cites = paper_obj.nortonCites + paper_obj.sbnCites
            paper_obj.s_w_p = citesToScores(strict_cites)['score_sheet']
            paper_obj.totalStrictCites = citesToScores(strict_cites)['total_cites']
        else:
            strict_cites = paper_obj.nortonCites + paper_obj.sbnCites + paper_obj.tCites
            paper_obj.s_w_p = citesToScores(strict_cites)['score_sheet']
            paper_obj.totalStrictCites = citesToScores(strict_cites)['total_cites']

    agg_cites = paper_obj.nortonCites + paper_obj.sbnCites + paper_obj.tCites + paper_obj.pageNumCites
    paper_obj.totalAggressiveCites = citesToScores(agg_cites)['total_cites']
    paper_obj.a_w_p = citesToScores(agg_cites)['score_sheet']

    paper_obj.s_l_p = relativeScoreCalc(paper_obj.s_w_p)
    paper_obj.a_l_p = relativeScoreCalc(paper_obj.a_w_p)

    paper_obj.s_w_c = chapterScores(paper_obj.s_w_p)
    paper_obj.s_l_c = chapterScores(paper_obj.s_l_p)
    paper_obj.a_w_c = chapterScores(paper_obj.a_w_p)
    paper_obj.a_l_c = chapterScores(paper_obj.a_l_p)

    print('finished setting scores for', paper_obj.name)

def biblioGenerator(base_file_name, data_frame):
    filename_filter = data_frame['Filename'].str.contains(base_file_name)
    df_row = data_frame[filename_filter]
    do = {}
    do['Author'] = df_row['Author'].values[0]
    do['Title of Work'] = df_row['Title of Work'].values[0]
    do['Journal'] = df_row['Journal'].values[0]
    do['Volume'] = str(df_row['Volume'].values[0])
    do['Issue'] = str(df_row['Issue'].values[0])
    do['Pages'] = str(df_row['Pages'].values[0])
    do['Year'] = str(df_row['Year'].values[0])
    do['Book Title'] = df_row['Book Title'].values[0]

    return do

def biblioSetter(paper_obj, data_frame):
    paper_obj.biblio = biblioGenerator(paper_obj.name, data_frame)

def process_and_score_paper(filename):
    paper = Paper(filename)
    processPaper(paper)
    paperScoreSetter(paper)
    biblioSetter(paper, dl_files)

    return paper
