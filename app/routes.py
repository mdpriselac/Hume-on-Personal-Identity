from app import app, basedir
from flask import render_template, url_for, redirect, flash
from app.models import Paper, Citation, p_to_dict, p_from_dict, c_to_dict, c_from_dict
import pandas as pd
import json
from functions_and_classes.display_only_ops import article_comps as ac
from data import tsdict
from data.file_to_title_dict import file_to_title_dict
from data.reverse_loc_to_pubs import awprev_df, awcrev_df, swprev_df, swcrev_df
from data.lit_level_data import l_a_w_p, l_a_w_c, l_s_w_p, l_s_w_c
from functions_and_classes.display_only_ops import generateListOfCites, df_cns, generateCompData
from functions_and_classes.lit_level_operations import locationFrequency
from app.forms import readingListForm
from functions_and_classes.cloud_io import p_dict_from_fire
bookdict={'0':'Introduction', '1':'Book I', '2':'Book II', '3':'Book III', 'Abs':'Abstract', 'App':'Appendix'}


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title="Personal Identity in Hume's Treatise")


@app.route('/location')
def location():
    return render_template('book_select.html', title="Location based view of Literature")

@app.route('/location/<book>')
def book(book):
    bname = bookdict[book]
    if book=="0" or book=="App" or book=="Abs":
        sections = tsdict[book]
    elif book == "1" or book == "2" or book == "3":
        sections = tsdict[book].keys()
    return render_template('section_select.html', title="Location based view of Literuatre", sections=sections, book=book, bname=bname)

@app.route('/location/<book>/<sect>')
def section(book,sect):
    curr_location = bookdict[book]+', '+'Section '+sect
    chapters= tsdict[book][sect].keys()

    return render_template('chapter_select.html', title="Location based view of Literature", chapters=chapters, curr_location=curr_location, book=book, sect=sect)

@app.route('/location/<book>/display')
def book_lit_display(book):
    if book=="App":
        tloc = "App."
    else:
        tloc = book
    ac_list = locationFrequency(tloc, awcrev_df)
    sc_list = locationFrequency(tloc, swcrev_df)
    a_pubs = len(ac_list)
    s_pubs = len(sc_list)

    return render_template('bookLitDisplay.html', ac_list=ac_list, sc_list=sc_list, book=bookdict[book], a_pubs=a_pubs, s_pubs=s_pubs)

@app.route('/location/<book>/<sect>/display')
def sect_lit_display(book,sect):
    if book=="Abs":
        tloc = "Abs"+sect
    else:
        tloc = book+'.'+sect
    ap_list = locationFrequency(tloc, awprev_df)
    sp_list = locationFrequency(tloc, swprev_df)
    tlocation = bookdict[book]+" "+sect

    a_pubs = len(ap_list)
    s_pubs = len(sp_list)

    return render_template('sectLitDisplay.html', ap_list=ap_list, sp_list=sp_list, tlocation=tlocation, a_pubs=a_pubs, s_pubs=s_pubs)

@app.route('/location/<book>/<sect>/<chapter>')
def chapter(book,sect,chapter):
    paragraphs = tsdict[book][sect][chapter]
    curr_location = bookdict[book]+", section "+sect+", chapter "+chapter

    return render_template('para_select.html', title="Location based view of Literature", paragraphs=paragraphs, book=book, sect=sect, chapter=chapter, curr_location=curr_location)

@app.route('/location/<book>/<sect>/<chapter>/display')
def chap_lit_display(book,sect,chapter):
    curr_location = book+"."+sect+"."+chapter
    ac_list = locationFrequency(curr_location, awcrev_df)
    sc_list = locationFrequency(curr_location, swcrev_df)
    a_pubs = len(ac_list)
    s_pubs = len(sc_list)

    return render_template('chapLitDisplay.html', ac_list=ac_list, sc_list=sc_list, curr_location=curr_location, a_pubs=a_pubs, s_pubs=s_pubs)


@app.route('/location/<book>/<sect>/<chapter>/<para>/display')
def para_lit_display(book,sect,chapter,para):
    curr_location = book+"."+sect+'.'+chapter+'.'+para
    ap_list = locationFrequency(curr_location, awprev_df)
    sp_list = locationFrequency(curr_location, swprev_df)
    a_pubs = len(ap_list)
    s_pubs = len(sp_list)

    return render_template('paraLitDisplay.html', curr_location=curr_location, ap_list=ap_list, sp_list=sp_list, a_pubs=a_pubs, s_pubs=s_pubs)




@app.route('/publications')
def publications():
    df_sc = ac('Literature', p_or_c='c', a_or_s='s')
    sc_data = generateCompData(df_sc, 'Literature')
    df_sp = ac('Literature', p_or_c='p', a_or_s='s')
    sp_data = generateCompData(df_sp, 'Literature')
    df_ac = ac('Literature', p_or_c='c', a_or_s='a')
    ac_data = generateCompData(df_ac, 'Literature')
    df_ap = ac('Literature', p_or_c='p', a_or_s='a')
    ap_data = generateCompData(df_ap, 'Literature')
    return render_template('publications.html', title="List of Publications Processed", sc=sc_data, sp=sp_data, ac=ac_data, ap=ap_data)

@app.route('/publication/<identifier>')
def publication(identifier):
    if identifier == "Literature":
        return redirect(url_for('literature'))
    else:
        try:
            pub = p_dict_from_fire(identifier)
            ppurl="https://philpapers.org/rec/"+identifier
            df_sc = ac(identifier, min_num_cites=10, min_num_comps=10, p_or_c='c', a_or_s='s')
            sc_data = generateCompData(df_sc, identifier)
            df_sp = ac(identifier, min_num_cites=10, min_num_comps=10, p_or_c='p', a_or_s='s')
            sp_data = generateCompData(df_sp, identifier)
            df_ac = ac(identifier, min_num_cites=10, min_num_comps=10, p_or_c='c', a_or_s='a')
            ac_data = generateCompData(df_ac, identifier)
            df_ap = ac(identifier, min_num_cites=10, min_num_comps=10, p_or_c='p', a_or_s='a')
            ap_data = generateCompData(df_ap, identifier)

            swp = generateListOfCites(identifier, a_s="s", c_p="p")
            swc = generateListOfCites(identifier, a_s="s", c_p="c")
            awp = generateListOfCites(identifier, a_s="a", c_p="p")
            awc = generateListOfCites(identifier, a_s="a", c_p="c")

            return render_template('publication.html', pub=pub, title=pub['name'], ppurl=ppurl, sc=sc_data, sp=sp_data, ac=ac_data, ap=ap_data, swp=swp, swc=swc, awp=awp, awc=awc)

        except:
            return render_template('no_such_file.html', title="Whoops!", filename=identifier)

@app.route('/literature', methods=['GET','POST'])
def literature():


    citeList = []
    readlist = df_cns(l_s_w_c,10)
    for loc in readlist.index:
        citeList.append((loc, round(readlist['Score'][loc],3)))

    form = readingListForm()
    if form.validate_on_submit():
        srch = form.searchSelect.data
        loca = form.locationSelect.data
        nums = form.numberLocations.data
        return redirect(url_for('reading_list', search=srch, location=loca, number_return=nums))

    return render_template('literature.html', title="Overview of the Personal Identity Literature", citeList=citeList, form=form)


@app.route('/literature/<search>/<location>/<number_return>')
def reading_list(search,location,number_return):
    if search == 'strict':
        if location == 'chapter':
            dataf = l_s_w_c
        elif location == 'paragraph':
            dataf = l_s_w_p

    if search == 'aggressive':
        if location == 'chapter':
            dataf = l_a_w_c
        elif location == 'paragraph':
            dataf = l_a_w_p

    cite_list = []
    readlist = df_cns(dataf,int(number_return))
    for loc in readlist.index:
        cite_list.append((loc, round(readlist['Score'][loc],3)))

    return render_template('reading_list.html', title='Reading List on Peronal Identity', cite_list=cite_list, search=search, location=location, number_return=number_return)


@app.route('/project')
def project():
    return render_template('project.html', title="Overview of the Project")
