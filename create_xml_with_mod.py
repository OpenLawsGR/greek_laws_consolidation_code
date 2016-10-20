# -*- coding: utf-8 -*-
import os
import re
import sys
import itertools
from lxml import etree
from functions import *

'''
This is STEP 5 of the architecture of the semi-automatic system.
This module parses each law text, performs structural analysis and identifies
the structural elements according to the rules that the central commitee
has published.
'''

#Path of laws text files
src = 'path/to/text/laws/file'

#A user defined folder where the XML files will be stored
text_dest = 'path/to/destination'

if not os.path.exists(os.path.join(text_dest,'xml')):
    os.makedirs(os.path.join(text_dest,'xml'))

def createXMLtree(txt):
    '''
    Function that uses python's lxml API to create and manage XML files
    It creates the root node and manages special cases of laws (e.g. code law)
    to extract specific information
    '''
    global start

    #Get the number, fek, year of publication as attributes
    number = name.split('_')[1]
    fek = name.split('_')[2]
    year = name.split('_')[4].split('.')[0]

    #Root node
    start = etree.Element("law", attrib = {'number':str(number), 'fek':str(fek), 'year': str(year)})

    #Title
    law_title = re.findall(r'ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+\n(.*?)\nΟ ΠΡΟΕΔΡΟΣ\nΤΗΣ ΕΛΛΗΝΙΚΗΣ ΔΗΜΟΚΡΑΤΙΑΣ'+
                           '|ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+\n(.*?)\nO ΠΡΟΕΔΡΟΣ\nΤΗΣ ΕΛΛΗΝΙΚΗΣ ΔΗΜΟΚΡΑΤΙΑΣ'+
                           '|ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+\n(.*?)\nΟ ΠΡΟΕΔΡΟΣ ΤΗΣ ΕΛΛΗΝΙΚΗΣ ΔΗΜΟΚΡΑΤΙΑΣ'+
                           '|ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+\n(.*?)\nΚΕΦΑΛΑΙΟ\s\S+\n'+
                           '|ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+[.]\n(.*?)Ο ΠΡΟΕΔΡΟΣ\nΤΗΣ ΕΛΛΗΝΙΚΗΣ ΔΗΜΟΚΡΑΤΙΑΣ'+
                           '|ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+\n(.*?)Ο ΠΡΟΕΔΡΟΣ\nΤΗΣ ΕΛΛΛΗΝΙΚΗΣ ΔΗΜΟΚΡΑΤΙΑΣ'+
                           '|ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+\n(.*?)Άρθρο\s\d+', txt, re.DOTALL)
    if law_title:
        mlaw_title = [a or b or c or d or e or f or g  for a, b, c, d, e, f, g in law_title]
        title = etree.SubElement(start, 'title')
        title.text = mlaw_title[0].decode("UTF-8")

    #Check whether it is a Code Law
    if law_title:
        kurwsi = re.findall(r'Κώδικα|Κώδικας|Κύρωση|κύρωση|Kύρωση', mlaw_title[0], re.DOTALL)
        kwdikes = re.findall(r'Άρθρο μόνο\n|Άρθρο πρώτο\n|Άρθρο Μόνο\n', txt, re.DOTALL)
    else:
        kurwsi = False
        kwdikes = False
        
    if kurwsi and kwdikes:
        repl_values = [
            #Law 3439 probably uses another tone
            (r'ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+\n.*?Εκδίδοµε τον ακόλουθο νόµο που ψήφισε η Βουλή:\n',r''),
            (r'\nΑθήνα, \d+ \S+ \d+\nΟ ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ', r''),
            (r'ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+\n.*?Εκδίδομε τον ακόλουθο νόμο που ψήφισε η Βουλή:\n', r''),
            (r'ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+\n.*?Εκδίδομε τον ακόλουθο νόμο που ψήφισε η\nΒουλή:\n', r''),
            (r'Άρθρο πρώτο\n.*?όπως έχει τροποποιηθεί και ισχύει.', r''),
            (r'Άρθρο πρώτο\n.*?[:]\n', r''),
            (r'Άρθρο μόνο\n.*?[:]\n', r''),
            (r'Άρθρο Μόνο\n.*?[:]\n', r''),
            (r'\nΆρθρο δεύτερο\n.*?$', r''),
            (r'\nΆρθρο τρίτο\n.*?$', r''),
            (r'»[.]$', r''),
            ('»$', r''),
            ('^«', r''),
            (r'(−)', r''),
            (r'(Άρθρο\s\d+)([.] )', r'\1\n'),
            (r'(Άρθρο\s\d+)([.])', r'\1\n')
        ]

        #Remove the unnecessary text
        kurwsi_text = destroy_patterns(txt, repl_values)
        ch_data = return_changed_text(kurwsi_text, find_mod_references(kurwsi_text), 0)
        
        #There are laws where one or two articles may be present before any other law element
        #component, so we should check for that case
        match_articles = re.search(r'Άρθρο\s\d+', ch_data) 
        match_book = re.search(r'\nΒΙΒΛΙΟ\s\S+', ch_data)
        match_part = re.search(r'\nΜΕΡΟΣ\s\S+', ch_data)
        match_section = re.search(r'\nΤΜΗΜΑ\s\S+', ch_data)
        match_chapter = re.search(r'\nΚΕΦΑΛΑΙΟ\s\S+', ch_data)

        position = []
        if match_book:
            position.append(match_book.start(0))
        if match_part:
            position.append(match_part.start(0))
        if match_section:
            position.append(match_section.start(0))
        if match_chapter:
            position.append(match_chapter.start(0))

        if position:
            position.sort()
            if match_articles and match_articles.start(0) < position[0]:
                find_articles(ch_data[0:position[0]], start, 0)
        #Find books
        find_books(ch_data, start, 0)
    else:
        ch_data = return_changed_text(txt, find_mod_references(txt), 0)
        find_books(ch_data, start, 0)

    
def find_books(txt, parent, fromimplement):
    '''
    Searches for the element "ΒΙΒΛΙΟ" (book) inside a text and creates the
    corresponding nodes

    Args:
        txt: The text that the pattern will be applied to
        
        parent: the parent node
        
        fromimplement: 1 - the function is used to create the nodes for an amendment
                       0 - the function is used to create the nodes for a law
    '''

    if fromimplement:
        books = re.findall(r'(?=\n{0,1}(ΒΙΒΛΙΟ\s\S+.*?)(?=\nΒΙΒΛΙΟ\s\S+|\nΟ ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|$))', txt, re.DOTALL)
    else:
        books = re.findall(r'(?=\n(ΒΙΒΛΙΟ\s\S+.*?)(?=\nΒΙΒΛΙΟ\s\S+|\nΟ ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|$))', txt, re.DOTALL)

    if books:
        for n in range(0, len(books)):
            if fromimplement:
                law_books = parent
            else:
                law_books = etree.SubElement(parent, 'book')

            #Attributes
            book_id = re.match(r'^.*?(?=\n)', books[n])
            law_books.set('id', book_id.group(0).split(" ")[1].decode('UTF-8'))

            #Header node
            header_desc = etree.SubElement(law_books, 'header')
            header_desc.text = book_id.group(0).decode('UTF-8')

            #Title
            books_title = re.findall(r'ΒΙΒΛΙΟ\s\S+.*?\n(.*?)(?=ΜΕΡΟΣ\s\S+\n|ΤΜΗΜΑ\s\S+\n|ΚΕΦΑΛΑΙΟ\s\S+\n|KΕΦΑΛΑΙΟ\s\S+\n|Άρθρο\s\d+\n|΄Αρθρο\s\d+\n|Άρθρο\s\d+\S+\n)',books[n],re.DOTALL) 
            if books_title:
                title = etree.SubElement(law_books, 'title')
                title.text = books_title[0].decode('UTF-8')
            #Find law parts
            find_parts(books[n], law_books, 0) 
    else:
        find_parts(txt, parent, 0)


def find_parts(txt, parent, fromimplement):
    '''
    Searches for the element "ΜΕΡΟΣ" (part) inside a text and creates the
    corresponding nodes

    Args:
        txt: The text that the pattern will be applied to
        
        parent: the parent node
        
        fromimplement: 1 - the function is used to create the nodes for an amendment
                       0 - the function is used to create the nodes for a law
    '''
    
    if fromimplement:
        parts = re.findall(r'(?=\n{0,1}(ΜΕΡΟΣ\s\S+.*?)(?=\nΜΕΡΟΣ\s\S+|\nΟ ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|$))', txt, re.DOTALL)
    else:
        parts = re.findall(r'(?=\n(ΜΕΡΟΣ\s\S+.*?)(?=\nΜΕΡΟΣ\s\S+|\nΟ ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|$))', txt, re.DOTALL)
        
    if parts:
        for i in range(0,len(parts)):
            if fromimplement:
                law_parts = parent
            else:
                law_parts = etree.SubElement(parent, 'part')

            #Attributes
            part_id = re.match(r'^.*?(?=\n)', parts[i])
            law_parts.set('id', part_id.group(0).split(" ")[1].decode('UTF-8'))

            #Header node
            header_desc = etree.SubElement(law_parts, 'header')
            header_desc.text = part_id.group(0).decode('UTF-8')
            
            #Title
            parts_title = re.findall(r'ΜΕΡΟΣ\s\S.*?\n(.*?)(?=ΤΜΗΜΑ\s\S+\n|ΚΕΦΑΛΑΙΟ\s\S+\n|KΕΦΑΛΑΙΟ\s\S+\n|Άρθρο\s\d+\n|΄Αρθρο\s\d+\n|Άρθρο\s\d+\S+\n)',parts[i],re.DOTALL)
            if parts_title:
                title = etree.SubElement(law_parts, 'title')
                title.text = parts_title[0].decode('UTF-8')
            #Find sections
            find_sections(parts[i], law_parts, 0)
    else:
        find_sections(txt, parent, 0)


def find_sections(txt, parent, fromimplement):
    '''
    Searches for the element "ΤΜΗΜΑ" (section) inside a text and creates the
    corresponding nodes

    Args:
        txt: The text that the pattern will be applied to
        
        parent: the parent node
        
        fromimplement: 1 - the function is used to create the nodes for an amendment
                       0 - the function is used to create the nodes for a law
    '''
    
    if fromimplement:
        sections = re.findall(r'(?=\n{0,1}(ΤΜΗΜΑ\s\S+.*?)(?=\nΤΜΗΜΑ\s\S+|\nΟ ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|$))', txt, re.DOTALL)
    else:
        sections = re.findall(r'(?=\n(ΤΜΗΜΑ\s\S+.*?)(?=\nΤΜΗΜΑ\s\S+|\nΟ ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|$))', txt, re.DOTALL)
        
    if sections:
        for k in range(0,len(sections)):
            if fromimplement:
                law_sections = parent
            else:
                law_sections = etree.SubElement(parent, 'section')

            #Attributes
            section_id = re.match(r'^.*?(?=\n)', sections[k])
            law_sections.set('id', section_id.group(0).split(" ")[1].decode('UTF-8'))

            #Header node
            header_desc = etree.SubElement(law_sections, 'header')
            header_desc.text = section_id.group(0).decode('UTF-8')
            
            #Title
            sections_title = re.findall(r'ΤΜΗΜΑ\s\S.*?\n(.*?)(?=ΚΕΦΑΛΑΙΟ\s\S+\n|KΕΦΑΛΑΙΟ\s\S+\n|Άρθρο\s\d+\n|΄Αρθρο\s\d+\n|Άρθρο\s\d+\S+\n)',sections[k],re.DOTALL)
            if sections_title:
                title = etree.SubElement(law_sections, 'title')
                title.text = sections_title[0].decode('UTF-8')
            #Find chapters
            find_chapters(sections[k], law_sections, 0)
    else:
        find_chapters(txt, parent, 0)


def find_chapters(txt, parent, fromimplement):
    '''
    Searches for the element "ΚΕΦΑΛΑΙΟ" (chapter) inside a text and creates the
    corresponding nodes

    Args:
        txt: The text that the pattern will be applied to
        
        parent: the parent node
        
        fromimplement: 1 - the function is used to create the nodes for an amendment
                       0 - the function is used to create the nodes for a law
    '''
    
    if fromimplement:
        chapters = re.findall(r'(?=\n{0,1}(ΚΕΦΑΛΑΙΟ\s\S+.*?|KΕΦΑΛΑΙΟ\s\S+.*?)(?=\nΚΕΦΑΛΑΙΟ\s\S+|\nKΕΦΑΛΑΙΟ\s\S+\n|\nΟ ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|$))', txt, re.DOTALL)
    else: 
        chapters = re.findall(r'(?=\n(ΚΕΦΑΛΑΙΟ\s\S+.*?|KΕΦΑΛΑΙΟ\s\S+.*?)(?=\nΚΕΦΑΛΑΙΟ\s\S+|\nKΕΦΑΛΑΙΟ\s\S+\n|\nΟ ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|$))', txt, re.DOTALL)

    if chapters:
        for m in range(0,len(chapters)):
            if fromimplement:
                law_chapters = parent
            else:
                law_chapters = etree.SubElement(parent, 'chapter', attrib={"id":str(m+1)})

            #Attributes
            chapter_id = re.match(r'^.*?(?=\n)', chapters[m])
            law_chapters.set('id', chapter_id.group(0).split(" ")[1].decode('UTF-8'))

            #Header node
            header_desc = etree.SubElement(law_chapters, 'header')
            header_desc.text = chapter_id.group(0).decode('UTF-8')
            
            #Title
            chapters_title = re.findall(r'ΚΕΦΑΛΑΙΟ\s\S+\n(.*?)(?=\nΆρθρο\s\d+\n|\n΄Αρθρο\s\d+\n|Άρθρο\s\d+\n|Άρθρο\s\d+\S+\n)', chapters[m], re.DOTALL)
            if chapters_title:
                title = etree.SubElement(law_chapters, 'title')
                title.text = chapters_title[0].decode('UTF-8')
            #Find articles
            find_articles(chapters[m], law_chapters, 0)
    else:
        find_articles(txt, parent, 0)


def find_articles(txt, parent, fromimplement):
    '''
    Searches for the element "ΑΡΘΡΟ" (article) inside a text and creates the
    corresponding nodes

    Args:
        txt: The text that the pattern will be applied to
        
        parent: the parent node
        
        fromimplement: 1 - the function is used to create the nodes for an amendment
                       0 - the function is used to create the nodes for a law
    '''

    if fromimplement:
        articles = re.findall(r'(?=(Άρθρο\s\d+.*?|΄Αρθρο\s\d+.*?|Άρθρο\s\d+\S+.*?|Άρθρo\s\d+.*?)(?=\nΆρθρο\s\d+\n|\n΄Αρθρο\s\d+\n|\nΆρθρο\s\d+\S+|Άρθρo\s\d+\n|Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|$))', txt, re.DOTALL)
    else:
        articles = re.findall(r'(?=\n(Άρθρο\s\d+.*?|΄Αρθρο\s\d+.*?|Άρθρο\s\d+\S+.*?|Άρθρo\s\d+.*?)(?=\nΆρθρο\s\d+\n|\n΄Αρθρο\s\d+\n|\nΆρθρο\s\d+\S+|Άρθρo\s\d+\n|Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|$))', txt, re.DOTALL)

    if articles:
        try:
            for q in range(0, len(articles)):
                #Attributes
                article_num = re.match(r'^.*?(?=\n)', articles[q])
                law_articles = etree.SubElement(parent, 'article', attrib={"id":article_num.group(0).split(" ")[1].decode('UTF-8')})

                #Header node
                articles_desc = etree.SubElement(law_articles, 'header')
                articles_desc.text = article_num.group(0).decode('UTF-8')
                
                #Title
                articles_title = find_articles_title(articles[q], law_articles)

                #Find paragraphs
                find_paragraphs(articles[q], law_articles, 0)
        except ValueError, e:
            print "Error: Can not create article. %s" % e
    else:
        find_paragraphs(txt, parent, 0)


def find_paragraphs(txt, parent, fromimplement):
    '''
    Searches for the element "Παράγραφος" (paragraph) inside an article and creates the
    corresponding nodes

    Args:
        txt: The text that the pattern will be applied to
        
        parent: the parent node
        
        fromimplement: 1 - the function is used to create the nodes for an amendment
                       0 - the function is used to create the nodes for a law
    '''

    #This list has been used due to the fact that patterns matched elements inside
    #amendment text and they have detrimental effect in structuring a law
    #In such case we destroy the pattern by changing the text inside an amendment
    #text and correct the text in later stage
    correct_par=[
        (r'(ΒΙΒΛΙΟ)([$])(\s\S+\n)', r'\1\3'),
        (r'(ΜΕΡΟΣ)([$])(\s\S+\n)', r'\1\3'),
        (r'(ΤΜΗΜΑ)([$])(\s\S+\n)', r'\1\3'),
        (r'(ΚΕΦΑΛΑΙΟ)([$])(\s\S+\n)', r'\1\3'),
        (r'(Άρθρο)([$])(\s\d+\S*\n)', r'\1\3'),
        (r'(\d+)([!])([.])', r'\1\3'),
    ]
    
    if fromimplement:
        paragraphs = re.findall(r'(\d+[.] [^\n].*?(?=\n\d+[.] |$))', txt, re.DOTALL)
    else:
        paragraphs = re.findall(r'(?=\n(\d+[.] [^\n].*?(?=\n\d+[.] |$)))', txt, re.DOTALL)
        
    if paragraphs:
        for d in range(0,len(paragraphs)):
            law_paragraphs = etree.SubElement(parent, 'paragraph')

            #Attributes
            paragraph_id = re.match(r'^.*?(?=[.])', paragraphs[d])
            law_paragraphs.set('id', paragraph_id.group(0).decode('UTF-8'))
            
            #Modify the text so as to have the correct text
            text_ = destroy_patterns(paragraphs[d],correct_par)
            
            #Check if paragraph contains a modificatory provision
            check_if_modif(text_, law_paragraphs, 0)

    #Case where the only paragraph in an article is not numbered
    else:
        law_paragraphs = etree.SubElement(parent, 'paragraph', attrib={"id":"1"})
        correct_txt = destroy_patterns(txt,correct_par)
        check_if_modif(correct_txt, law_paragraphs, 1)


def check_if_modif(txt, parent, flag):
    '''
    Checks if a paragraph contains a modificatory provision according to regexes in patt_mods
    Patterns have been constructed after an analysis of a sample of 100 random laws with the use
    of an online regex service (www.regex101.com)
    If there exist an amendment it creates a node (mod) as a child of paragraph node

    Args:
        txt: The text that the pattern will be applied to
        
        parent: the parent node
        
        flag: 1 - the function is used to create the nodes for an amendment
              0 - the function is used to create the nodes for a law
    '''

    patt_mods = [(r'(Ο\s)(τίτλος\sτου.*?)(από)\s*(γίνεται)\s[,]\s(οι\s(.*?)(αναριθμούνται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:]))'),
                 (r'(Ο\s)(τίτλος\sτου.*?)(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται|συμπληρώνεται|συμπληρώνονται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])'),
                 (r'(Ο\s)((τίτλος\sκαι\s)(η|το|τα|οι)\s(στοιχείο|στοιχεία|υποπερίπτωση|υποπεριπτώσεις|περίπτωση|περ[.]|περιπτώσεις|εδάφιο|εδάφια|περίοδος|περίοδοι|παράγραφος|παρ[.]|παραγράφος|παράγραφοι|άρθρο|άρθρα).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται|συμπληρώνονται|συμπληρώνεται|αναριθμούνται|αναριθμείται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])'),
                 (r'(Το|Τα|Τo)\s((\S+\sκαι\s(το\s){0,1}\S+\s)(εδάφια|άρθρα|εδάφιο|εδάφιo).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτα\sοποία)\sκυρώθηκαν\s.*?){0,1}|((που|τα\sοποία)\sπροστέθηκαν\s.*?){0,1}|((με\sτα|τα)\sοποία\s.*?){0,1})(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|αναδιατυπώνεται|συμπληρώνονται|αναδιατυπώνονται|συμπληρώνεται|αναριθμούνται|αναριθμείται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])'),
                 (r'(Τα|Το)\s((\S+\s){2}(εδάφια|άρθρα|εδάφιο).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτα\sοποία)\sκυρώθηκαν\s.*?){0,1}|((που|τα\sοποία)\sπροστέθηκαν\s.*?){0,1}|((με\sτα|τα)\sοποία\s.*?){0,1})(αντικαθίστανται|αντικαθίσταται|τροποποιούνται|έχουν\sως\sεξής|αναδιατυπώνονται|συμπληρώνονται|αναριθμούνται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])'),
                 (r'(Η|H|Το|To|Tο|Τα|Οι)\s((?!νέα|νέο)(\S+\s){1}(στοιχείο|στοιχεία|υποπερίπτωση|υποπεριπτώσεις|περίπτωση|περ[.]|περιπτώσεις|εδάφιο|εδάφια|περίοδος|περίοδοι|παράγραφος|παρ[.]|παραγράφος|παράγραφοι|άρθρο|άρθρα|κεφάλαιο|κεφάλαια).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται|συμπληρώνονται|συμπληρώνεται|αναριθμούνται|αναριθμείται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])'),
                 (r'(Η|H|Το|To|Τα|Οι)\s((\S+\s){0}(στοιχείο|στοιχεία|υποπερίπτωση|υποπεριπτώσεις|περίπτωση|περ[.]|περιπτώσεις|εδάφιο|εδάφια|περίοδος|περίοδοι|παράγραφος|παρ[.]|παραγράφος|παράγραφοι|άρθρο|άρθρα|κεφάλαιο|κεφάλαια).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται|συμπληρώνονται|συμπληρώνεται|αναριθμούνται|αναριθμείται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])'),
                 (r'(Προστίθεται)(.*?)(?=(\sως\sεξής|\sως\sακολούθως){0,1}[:])'),
                 (r'(Στην\s|Στο\s|Στον\s|Μετά\sτο|Μετά\sτον|Μετά\sτη|Μετά\sτην)(.*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο|η\sοποία|ο\sοποίος)\s(κυρώθηκε\s|τροποποιήθηκε\s|προστέθηκε\s|αντικαταστάθηκε\s).*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(προστίθεται|προστίθενται|\bτίθενται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|(\sως\sεξής|\sως\sακολούθως){0,1}[:])'),
                 (r'(Στην\s|Στο\s|Στον\s|Μετά\sτο|Μετά\sτον|Μετά\sτη|Μετά\sτην)(.*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο|η\sοποία|ο\sοποίος)\s(κυρώθηκε\s|τροποποιήθηκε\s|προστέθηκε\s|αντικαταστάθηκε\s).*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})η\s(φράση\s*)(αντικαθίσταται)\s(από\sτη\sφράση|σε|με\sτη\sφράση\s|ως\sεξής[:]){0,1}'),
                 (r'(Στις|Στην\s|Στο\s|Στον\s|Μετά\s)(.*?)(αντί\sτων\sλέξεων\s*)(\bτίθενται)(\sοι\sλέξεις\s)'),
                 (r'(Η|Οι)\s((διάταξη|διατάξεις).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτα\sοποία)\sκυρώθηκαν\s.*?){0,1}|((που|τα\sοποία)\sπροστέθηκαν\s.*?){0,1}|((με\sτα|τα)\sοποία\s.*?){0,1})(αντικαθίστανται|αντικαθίσταται|τροποποιούνται|τροποποιείται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])'),
                 (r'(Στην\s|Στο\s|Στον\s|Μετά\s)(.*?)(όπως\sισχύει[,]{0,1}){0,1}(\sμετά\sτη\sφράση\s*.*?)(προστίθεται|προστίθενται)\s(η\sφράση|οι\sλέξεις)'),
                 (r'(Στις|Στην\s|Στο\s|Στον\s|Από\s)(.*?)(διαγράφεται|διαγράφονται)\s(η\sφράση|στοιχείο|οι\sλέξεις)'),
                 (r'(Στην|Στη|Στο)(.*?)(οι\sλέξεις\s*)(αντικαθίσταται|αντικαθίστανται)([,]{0,1})(\sαπό\sτις\sλέξεις)'),
                 (r'(Η)\s((\S+\s){1}(πρόταση|φράση).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται|συμπληρώνονται|συμπληρώνεται|αναριθμούνται|αναριθμείται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])'),
                 (r'(Η|H|Το|To|Τα|Οι|Ο)\s((\S+\s){0}(νόμος|νόμοι|ν[.]|στοιχείο|στοιχεία|υποπερίπτωση|υποπεριπτώσεις|περίπτωση|περ[.]|περιπτώσεις|εδάφιο|εδάφια|περίοδος|περίοδοι|παράγραφος|παρ[.]|παραγράφος|παράγραφοι|άρθρο|άρθρα|κεφάλαιο|κεφάλαια|διάταξη|διατάξεις).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(καταργείται|καταργούνται|παύει\sνα\sισχύει|παύουν\sνα\sισχύουν)'),
                 (r'(Στην\s|Στο\s|Στον\s|Μετά\sαπό\sτο\s|Μετά\sτο\s|Μετά\sτον\s|Μετά\sτη\s|Μετά\sτην\s)(.*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο|η\sοποία|ο\sοποίος)\s(κυρώθηκε\s|τροποποιήθηκε\s|προστέθηκε\s|αντικαταστάθηκε\s).*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})((διαγράφονται|διαγράφεται(?![.])).*?)(η\sφράση|οι\sλέξεις|η\sλέξη|στοιχείο|το\sκόμμα|η\sτελεία)(.*?)([«].*?[»])'),
                 (r'(Καταργείται|Καταργούνται)\s(η|το|οι|κάθε)(.*?)[.]\n(?=(\n|\S{0,2}[.]|\S{0,2}[)]))')
    ]
    
    try:
        #ch_txt = return_text_no_quotes(txt, find_mod_references(txt))
        #pat = re.search(r'(Η|H|Το|To|Τα|Οι)\s((\S+\s){0}(στοιχείο|στοιχεία|υποπερίπτωση|υποπεριπτώσεις|περίπτωση|περ[.]|περιπτώσεις|εδάφιο|εδάφια|περίοδος'+
        #                '|περίοδοι|παράγραφος|παρ[.]|παραγράφος|παράγραφοι|άρθρο|άρθρα|κεφάλαιο|κεφάλαια).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|'+
        #                '((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})'+
        #                '(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται'+
        #                '|συμπληρώνονται|συμπληρώνεται|αναριθμούνται|αναριθμείται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])', txt, re.DOTALL)

        #pat = re.search(r'(καταργείται|καταργούνται|Καταργείται|Καταργούνται|παύει|παύουν|ανακαλείται|ανακαλούνται|ακυρώνεται|διαγράφεται|διαγράφονται|'+
        #            'αναστέλλεται|Αναστέλλεται|αναστέλλονται|αφαιρείται|αφαιρούνται|Αφαιρείται|Αναστέλλονται)', ch_txt, re.DOTALL)

        #if pat:
        #    with open(os.path.join(root, "katargiseis.txt"), "a") as f:
         #       f.write(name+"\n"+txt+"\n\n")
         
        ismodif = False
        for n in range(0, len(patt_mods)):
            check = re.search(patt_mods[n], txt, re.DOTALL)
            if check:
                ismodif = True
                break
        try:
            global modif_num
            if ismodif:  
                modif_num = modif_num + 1
                modif = etree.SubElement(parent, 'mod')
                modif.set('id', str(modif_num))
                if flag == 0:
                    modif.text = txt.decode('UTF-8')
                else:
                    modif.text = re.sub(r'^.*?\n',r'',txt).decode('UTF-8').strip()
            else:
                if flag == 0:
                    parent.text = txt.decode('UTF-8')
                else:
                    parent.text = re.sub(r'^.*?\n',r'',txt).decode('UTF-8').strip()
        except NameError:
            pass
    except RuntimeError:
        print "runtime error: Passed this paragraph"
        pass


def find_articles_title(txt, parent):
    '''
    Finds the title of an article

    Args
        txt: The text that the pattern will be applied to
        
        parent: the parent node
    '''
    titles = re.findall(r'Άρθρο\s\d+\S+(.*?)\n(?=\d+[.] )|Άρθρο\s\d+(.*?)\n(?=\d+[.] )',txt, re.DOTALL)
    if titles:
        arthro_title = [x or y for x, y in titles]
        if arthro_title[0] != '':
            title = etree.SubElement(parent, 'title')
            title.text = arthro_title[0][1:].decode('UTF-8')



if __name__ == "__main__":
    for root, dirs, files in os.walk(src):
        for name in files:
            #Parsing all Laws
            if name.endswith('.txt'):
                print name
                with open(os.path.join(os.path.join(text_dest,'xml'),name.split(".")[0]+".xml"), "w") as fout:
                    with open(os.path.join(root, name), "r") as fin:
                        data = fin.read()

                        #Avoid control characters and NULL bytes that XML cannot manage
                        #see (http://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python)
                        def valid_xml_char_ordinal(c):
                            codepoint = ord(c)
                            #conditions ordered by presumed frequency
                            return (
                                0x20 <= codepoint <= 0xD7FF or
                                codepoint in (0x9, 0xA, 0xD) or
                                0xE000 <= codepoint <= 0xFFFD or
                                0x10000 <= codepoint <= 0x10FFFF
                                )

                        data = ''.join(c for c in data if valid_xml_char_ordinal(c))
                        modif_num = 0

                        xml = createXMLtree(data)
                        doc = etree.ElementTree(start)

                        doc.write(fout, pretty_print=True, encoding="UTF-8", xml_declaration=True)
                        #print etree.tostring(start, pretty_print=True, encoding="UTF-8", xml_declaration =True)
                            
