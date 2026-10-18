import re
import roman
import os
from functions_and_classes.treatise_reference_data import *
#Core takeaway from this set of functions is ultimateParser. Import it as uP


#ultimate Parsing and Scoring Functions
# these functions take in either SBN or Norton citaitons of the following kind:
    # SBN it needs to be pure numbers or roman numerals
    # Norton will be cleaned but it shouldn't have a T in front of it, it can have roman numerals in the
    # page slots
# ultimateParser returns list of pairs of paragraphs and relative scores
# ultimateScorer doesn't return anything, it updates in accord with the relative scores returned by ultimateParser


#General purpose functions for expanding page ranges and lists; can't
#use without modification on norton paragraphs
def rangeExpander(cite_in):
    page_range = []
    dash_expression = re.compile('[-–—]')
    if dash_expression.search(cite_in):
        first_num = re.split(dash_expression, cite_in)[0]
        second_num = re.split(dash_expression, cite_in)[1]
        diff_in_len = len(first_num)-len(second_num)
        if diff_in_len >= 0:
            expanded_second_num = first_num[:diff_in_len]+second_num
            for num in range(int(first_num), int(expanded_second_num)+1):
                page_range.append(str(num))
        elif diff_in_len < 0:
            for num in range(int(first_num), int(second_num)+1):
                page_range.append(str(num))
    else:
        page_range.append(cite_in)
    return page_range

def listExpander(cite_in):
    page_list = []
    if ',' in cite_in:
        for entry in cite_in.split(','):
            page_list.append(entry.strip())
    else:
        page_list.append(cite_in)
    return page_list

def fullExpander(cite_in):
    final_list = []
    for entry in listExpander(cite_in):
        for item in rangeExpander(entry):
            final_list.append(item)
    return final_list

def romanDigitRangeCorrector(cite_in):
    dash_expression = re.compile('[-–—]')
    if dash_expression.search(cite_in):

        first_roman_num = re.split(dash_expression, cite_in)[0]
        second_roman_num = second_num = re.split(dash_expression, cite_in)[1]
        first_num = str(roman.fromRoman(first_roman_num.upper()))
        second_num = str(roman.fromRoman(second_roman_num.upper()))
        arabic_range = first_num + '-' + second_num

        return arabic_range
    else:
        return str(roman.fromRoman(cite_in.upper()))

def romanHandler(cite_in):
    final_out = []
    roman_in_list = listExpander(cite_in)
    arabic_intermediate_list = []
    for entry in roman_in_list:
        arabic_intermediate_list.append(romanDigitRangeCorrector(entry))
    arabic_final_list = []
    for entry in arabic_intermediate_list:
        for page in fullExpander(entry):
            arabic_final_list.append(page)
    for page in arabic_final_list:
        final_out.append(roman.toRoman(int(page)).lower())

    return final_out

def getListOfPagesFromCite(cite_in):
    final_out = []
    list_version_of_cite = listExpander(cite_in)
    roman_check = re.compile('[xvi]|[XVI]')
    for cite in list_version_of_cite:
        if roman_check.search(cite):
            for page in romanHandler(cite):
                final_out.append(page)
        else:
            for page in fullExpander(cite):
                final_out.append(page)

    return final_out

#functions for processing Norton Texts
#the key function to use from here is fullNortonCleaner(cite_in); it takes a
#norton citation that hasn't been turned into a list of invididual
#paragraphs and returns a version that is properly formatted for scoring


def romanSubber(text):
    roman_checker = re.compile('[ixv]|[IXV]')
    if roman_checker.search(text):
        return str(roman.fromRoman(text.upper()))
    else:
        return text

def dashFixer(text):
    dash_checker = dash_checker = re.compile('[-–—]')
    if dash_checker.search(text):
        dash_list = re.split(dash_checker, text)
        new_dash_list = []
        for dash_item in dash_list:
            new_dash_list.append(romanSubber(dash_item))
        text_out = '-'.join(new_dash_list)
        return text_out
    else:
        return text

def commaFixer(text):
    if ',' in text:
        new_comma_list = []
        for entry in text.split(','):
            new_entry = dashFixer(entry)
            new_entry = romanSubber(new_entry)
            new_comma_list.append(new_entry)

        return ','.join(new_comma_list)
    else:
        return text



def romanCleaner(cite_in):
    cite_out_list = []
    for item in cite_in.split('.'):
        to_write = item
        to_write = commaFixer(to_write)
        to_write = dashFixer(to_write)
        to_write = romanSubber(to_write)

        cite_out_list.append(to_write)

    cite_out = '.'.join(cite_out_list)

    return cite_out

def dotAppAdder(cite_in):
    cite_in = cite_in.replace('§',"")
    appChecker = re.compile('(App(?![.|e]))|(Appendix)')
    if appChecker.search(cite_in):
        return re.sub(appChecker, 'App.', cite_in)
    else:
        return cite_in

def abstractCleaner(cite_in):
    cite_in = cite_in.replace('§',"")
    absChecker = re.compile('(Abs\.)|(Abstract)')
    if absChecker.search(cite_in):
        return re.sub(absChecker, 'Abs', cite_in)
    else:
        cite_out = cite_in
    return cite_in

def fullNortonCleaner(cite_in):
    cite_out = abstractCleaner(cite_in)
    cite_out = dotAppAdder(cite_out)
    if cite_out[0] != "A":
        cite_out = romanCleaner(cite_out)
    return cite_out

#these functions for scoring a citation
#the important functions are:
# anyMasterScoreUpdater(cite_in)
    #if you call this function, it has no output, it will update the master_score_sheet based on the citation it takes in
    #it draws on the following two functions
# sbnScoring(cite_in)
    #this function takes any SBN citation in and returns a list of pairs of paragraphs and scores for that paragraph
# nortonScoring(cite_in)
    #this fucntion takes any Norton citation in and returns a list of pairs of paragraphs and scores for that paragraph

def sbnScoring(cite_in):
    #get all the pages from the citation in a list
    page_list = getListOfPagesFromCite(cite_in)
    #get the count of pages, to be used in distributing credit from the citation across all pages
    total_pages = len(page_list)
    #this number will be used to noramlize our weights back up to 1 by dividing 1 by it
    total_para_weights = 0

    #now we'll get a list of all the paras, paired with their page-relative-weight
    pre_normalized_list_of_para_weight_pairs = []
    for page in page_list:
        try:
            para_list = sbn_to_norton_dictionary[page]
            total_paras = len(para_list)
            for para in para_list:
                pre_normalized_list_of_para_weight_pairs.append((para, 1/total_paras))
                total_para_weights += 1/total_paras
        except KeyError:
            print(page, "generated a key error when trying to find matching paragraphs")

    #now we'll normalize all page-relative para weights so they add up to 1
    final_list_of_para_weight_pairs = []
    normalizing_factor = 1/total_para_weights
    total_weight_check = 0
    for pair in pre_normalized_list_of_para_weight_pairs:
        try:
            final_list_of_para_weight_pairs.append((pair[0], round(pair[1]*normalizing_factor,3)))
            total_weight_check += pair[1]*normalizing_factor
        except KeyError:
               print(page, "generated a Key Error when trying to find correspondign paragraphs")
    #print(total_weight_check)
    return final_list_of_para_weight_pairs

def nortonExpander(cite_in):
    final_out = []
    #first, establish the chapter
    capture_chapter = re.compile('(\d+\.\d+\.\d+)|(App)|(Abs)')
    #second, create the chapter slice:
    chapter_slice = cite_in[:capture_chapter.match(cite_in).end()]
    #next, create the remainder slice.
    remainder_slice = cite_in[capture_chapter.match(cite_in).end():]
    #if the chapter is all there is, we'll just append the chapter to the list out
    if remainder_slice == '':
        final_out.append(cite_in)

    #if the remainder slice isn't empty and it isn't a ., suggesting there's a paragraph
    #ie if it's going to be a range or list of chapters
    elif remainder_slice[0] != '':
        if remainder_slice[0] !='.':
            #we're going to find the last match of '.numbers'
            #the 's' is in the re to capture abstract cases, App. is already captured by dot
            dot_d_finder = re.compile('[.s]\d+')
            d_list = dot_d_finder.finditer(cite_in)
            for match in d_list:
                last_match = match
            #we'll take the start position of that, ie the last dot, and add one
            chapter_start = last_match.start() + 1
            chapter_range = cite_in[chapter_start:]
            #now let's run it through a listExpander and then the range expander:
            for list_entry in listExpander(chapter_range):
                for range_entry in getListOfPagesFromCite(list_entry):
                    final_out.append(cite_in[:chapter_start]+range_entry)

    #if the cite is neither a solitary chapter nor a list or range of chapters, then it's a paragraph
    #or list or range of paragraphs, so we'll epxand that.
        else:
            #create a list of everything that remains, split by ,
            remainder_list = listExpander(remainder_slice)
            for para in remainder_list:
                #remove the . from any item in that list
                new_para = para.replace('.','')
                #expand the ranges of anything and then append it
                for item in getListOfPagesFromCite(new_para):
                    final_out.append(chapter_slice+'.'+item)

    return final_out

def nortonChapterExpander(cite_in):
    final_list = []
    is_a_chapter = re.compile('(\d+\.\d+\.\d+)(?!\.)')
    if is_a_chapter.match(cite_in) != None:
        for para in treatise_paragraph_list:
            if cite_in == para[:len(cite_in)]:
                final_list.append(para)
        if len(final_list)<1:
            final_list.append(cite_in)
    else:
        final_list.append(cite_in)
    return final_list

def nortonFullExpander(cite_in):
    final_list = []
    for entry in nortonExpander(cite_in):
        for item in nortonChapterExpander(entry):
            final_list.append(item)

    return final_list

def nortonScoring(cite_in):
    final_list = []
    total_paras = len(nortonFullExpander(cite_in))
    for para in nortonFullExpander(cite_in):
        final_list.append((para, round(1/total_paras,3)))

    return final_list

def sbnMasterScoreUpdater(cite_in):
    for pair in sbnScoring(cite_in):
        try:
            #print("The old score of", pair[0], "was:", str(master_score_sheet[pair[0]]))
            master_score_sheet[pair[0]] += pair[1]
            #print("The new score of", pair[0], "is:", str(master_score_sheet[pair[0]]))

        except KeyError:
            print(pair[0], 'generated a key error when trying to update the scoresheet, check the citation')


def nortonMasterScoreUpdater(cite_in):

    for pair in nortonScoring(cite_in):
        try:
            #print("The old score of", pair[0], "was:", str(master_score_sheet[pair[0]]))
            master_score_sheet[pair[0]] += pair[1]
            #print("The new score of", pair[0], "is:", str(master_score_sheet[pair[0]]))
        except KeyError:
             print(pair[0], 'generated a key error when trying to update the scoresheet, check the citation')


#ultimate Parsing and Scoring Functions
# these functions take in either SBN or Norton citaitons of the following kind:
    # SBN it needs to be pure numbers or roman numerals
    # Norton will be cleaned but it shouldn't have a T in front of it, it can have roman numerals in the
    # page slots
# ultimateParser returns list of pairs of paragraphs and relative scores
# ultimateScorer doesn't return anything, it updates in accord with the relative scores returned by ultimateParser

def ultimateParser(cite_in):
    norton_check = re.compile("(T?A)|([123Ii]+\.)+")
    if norton_check.match(cite_in) != None:
        #let's just make sure we don't have a 'T'
        if cite_in[0]=="T":
            clean_cite = cite_in[1:]
        else:
            clean_cite = cite_in
        cleaner_cite = fullNortonCleaner(clean_cite)
        #need to add a citation quality checker here. we have one by default
        #with the Key Errors for SBN cases but not for Norton cases
        for pair in nortonScoring(cleaner_cite):
            if not pair[0] in treatise_paragraph_list:
                print(pair[0], "is not a paragraph in the Treatise, check the citation")
        return nortonScoring(cleaner_cite)
    else:
        return sbnScoring(cite_in)
