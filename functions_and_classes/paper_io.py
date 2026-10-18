from functions_and_classes.classes import *

def p_to_dict(paper):
    od = {}
    od['name'] = paper.name
    norton_cites_out = []
    for cite in paper.nortonCites:
        norton_cites_out.append(c_to_dict(cite))
    od['nortonCites'] = norton_cites_out
    sbn_cites_out = []
    for cite in paper.sbnCites:
        sbn_cites_out.append(c_to_dict(cite))
    od['sbnCites'] = sbn_cites_out
    raw_out = []
    for cite in paper.rawParenthesesCapture:
        raw_out.append(c_to_dict(cite))
    od['rawParenthesesCapture'] = raw_out
    t_out = []
    for cite in paper.tCites:
        t_out.append(c_to_dict(cite))
    od['tCites'] = t_out
    pageNumOut = []
    for cite in paper.pageNumCites:
        pageNumOut.append(c_to_dict(cite))
    od['pageNumCites'] = pageNumOut
    od['rawNortonScore'] = paper.rawNortonScore
    od['rawSbnScore'] = paper.rawSbnScore
    od['rawTScore'] = paper.rawTScore
    od['rawPageNumScore'] = paper.rawPageNumScore
    od['a_l_p'] = paper.a_l_p
    od['a_w_p'] = paper.a_w_p
    od['s_l_p'] = paper.s_l_p
    od['s_w_p'] = paper.s_w_p
    od['totalStrictCites'] = paper.totalStrictCites
    od['totalAggressiveCites'] = paper.totalAggressiveCites
    od['s_w_c'] = paper.s_w_c
    od['s_l_c'] = paper.s_l_c
    od['a_w_c'] = paper.a_w_c
    od['a_l_c'] = paper.a_l_c
    od['biblio'] = paper.biblio

    return od

def c_to_dict(cite):
    od = {}
    od['order'] = cite.order
    od['paper'] = cite.paper
    od['startPoint'] = cite.startPoint
    od['endPoint'] = cite.endPoint
    od['rawCitationText'] = cite.rawCitationText
    od['cleanedCitation'] = cite.cleanedCitation

    return od

def p_from_dict(in_dict):
    #this is '.txt' is just so the naming stays correct
    paper = Paper(in_dict['name']+'.txt')
    for cite in in_dict['nortonCites']:
        paper.nortonCites.append(c_from_dict(cite))
    for cite in in_dict['sbnCites']:
        paper.sbnCites.append(c_from_dict(cite))
    for cite in in_dict['rawParenthesesCapture']:
        paper.rawParenthesesCapture.append(c_from_dict(cite))
    for cite in in_dict['tCites']:
        paper.tCites.append(c_from_dict(cite))
    for cite in in_dict['pageNumCites']:
        paper.pageNumCites.append(c_from_dict(cite))
    paper.rawNortonScore = in_dict['rawNortonScore']
    paper.rawSbnScore = in_dict['rawSbnScore']
    paper.rawTScore = in_dict['rawTScore']
    paper.rawPageNumScore = in_dict['rawPageNumScore']
    paper.totalStrictCites = in_dict['totalStrictCites']
    paper.totalAggressiveCites = in_dict['totalAggressiveCites']
    paper.a_l_p = in_dict['a_l_p']
    paper.a_w_p = in_dict['a_w_p']
    paper.a_l_c = in_dict['a_l_c']
    paper.a_w_c = in_dict['a_w_c']
    paper.s_l_p = in_dict['s_l_p']
    paper.s_w_p = in_dict['s_w_p']
    paper.s_l_c = in_dict['s_l_c']
    paper.s_w_c = in_dict['s_w_c']
    paper.biblio = in_dict['biblio']

    return paper


def c_from_dict(in_dict):
    cite = Citation(in_dict['paper'], in_dict['order'], in_dict['rawCitationText'])
    cite.startPoint = in_dict['startPoint']
    cite.endPoint = in_dict['endPoint']
    cite.cleanedCitation = in_dict['cleanedCitation']

    return cite
