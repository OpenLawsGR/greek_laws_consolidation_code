# -*- coding: utf-8 -*-
#from __future__ import print_function
import re
import itertools
import os
import shutil


def find_xpath(dictionary, num, element):
    '''
    Finds the element path tha should be replaced/repealed based on a dictionary

    dictionary: structure that contains all the elements found according to a regex
    num: id of the element that should be replace/add
    element: The type of element that we search for (article, paragraph etc)
    '''
    xpath = ""

    fromdict = []
    for key in dictionary.items():
        fromdict.append(key)
    
    for n in range(0, len(fromdict)):
        if fromdict[n][0]!=element:
            if fromdict[n][0] == 'book' and fromdict[n][1]:
                xpath = "/book[@id="'"'+fromdict[n][1]+'"'"]" + xpath
            if fromdict[n][0] == 'part' and fromdict[n][1]:
                xpath = "/part[@id="'"'+fromdict[n][1]+'"'"]" + xpath
            if fromdict[n][0] == 'section' and fromdict[n][1]:
                xpath = "/section[@id="'"'+fromdict[n][1]+'"'"]" + xpath
            if fromdict[n][0] == 'chapter' and fromdict[n][1]:
                xpath = "/chapter[@id="'"'+fromdict[n][1]+'"'"]" + xpath
            if fromdict[n][0] == 'article' and fromdict[n][1]:
                xpath = "/article[@id="'"'+fromdict[n][1]+'"'"]" + xpath
            if fromdict[n][0] == 'paragraph' and fromdict[n][1]:
                xpath = "/paragraph[@id="'"'+fromdict[n][1]+'"'"]" + xpath
        if fromdict[n][0]==element and element in ('book', 'part', 'section', 'chapter', 'article', 'paragraph'):
            xpath = "/"+element+"[@id="'"'+num+'"'"]" + xpath

    return "/" + xpath


def find_xpath_for_addition(dictionary):
    '''
    Finds the element path tha should be added based on a dictionary

    dictionary: structure that contains all the elements found according to a regex
    '''
    xpath = ""

    fromdict = []
    for key in dictionary.items():
        fromdict.append(key)

    for n in range(0, len(fromdict)):
        if fromdict[n][0] == 'book' and fromdict[n][1]:
            xpath = "/book[@id="'"'+fromdict[n][1]+'"'"]" + xpath
        if fromdict[n][0] == 'part' and fromdict[n][1]:
            xpath = "/part[@id="'"'+fromdict[n][1]+'"'"]" + xpath
        if fromdict[n][0] == 'section' and fromdict[n][1]:
            xpath = "/section[@id="'"'+fromdict[n][1]+'"'"]" + xpath
        if fromdict[n][0] == 'chapter' and fromdict[n][1]:
            xpath = "/chapter[@id="'"'+fromdict[n][1]+'"'"]" + xpath
        if fromdict[n][0] == 'article' and fromdict[n][1]:
            xpath = "/article[@id="'"'+fromdict[n][1]+'"'"]" + xpath
        if fromdict[n][0] == 'paragraph' and fromdict[n][1]:
            xpath = "/paragraph[@id="'"'+fromdict[n][1]+'"'"]" + xpath
    return "/" + xpath
    

def construct_law_name(law_type, law_num, law_year):
    '''
    Creates the name of the law tha the amendment refers to
    
    law_type: Type of the law (law, presidential decree etc.)
    law_num: The number of the law
    law_year: Year of publication
    '''
    
    LAW = ''

    if not law_type or not law_num or not law_year:
        pass
    else:
        if int(law_year) < 2004:
            pass
        elif law_type.encode('utf-8') in ('Π.Δ.', 'π.δ.','β.δ.'):
            pass
        else:
            LAW = 'ΝΟΜΟΣ_'+law_num.encode('utf-8')+"_"+"\d+"+"_A_"+law_year.encode('utf-8')+".xml"

        return LAW



def file_in_path(filename, path):
    '''
    Checks whether a file exists in a folder

    filename: The file that we search for
    path: The path that the search occurs
    '''
    
    file_exists = False

    if not os.listdir(path) == []:
        for root, dirs, files in os.walk(path):
            for name in files:
                if re.search(filename, name):
                    file_exists = True
                    law = re.search(filename, name).group(0)
                    break

    if file_exists:
        return law



def check_which_matching(txt, listA):
    '''
    checks whether a law name corresponds to law number
    (this is due to cases such as code laws where the author cite the name
    of the law instead of its number (e.g. "Κώδικας Δημοσίων Υπαλλήλων"))

    txt: The name of the code law
    listA: A List containing all code law names and their corresponding law's number
    '''
    found = False
    
    for n in range(0, len(listA)):
        if isinstance(txt, unicode):
            match = re.search(listA[n][0].decode('utf-8'), txt, re.DOTALL)
        else:
            match = re.search(listA[n][0], txt, re.DOTALL)

        if match:
            found = True
            break

    if found:
        return listA[n][1].decode('utf-8')
    else:
        return found


def destroy_patterns(txt, listA):
    for n in range(0,len(listA)):
        if isinstance(txt, unicode):
            txt = re.sub(listA[n][0].decode('UTF-8'), listA[n][1], txt, flags=re.DOTALL)
        else:
            txt = re.sub(listA[n][0], listA[n][1], txt, flags=re.DOTALL)
    return txt



def return_text_no_quotes(text, start_stop):
    '''
    Returnig amandment paragraphs without the amending text
    Used for constructig a corpus of amenmdemt texts to create regular expressions
    
    text: the text
    start_stop: A List containing all code law names and their corresponding law's number
    '''
    begin = start_stop[0]
    end = start_stop[1]
    for f,b in itertools.izip(begin, end):
        text = text.replace(text[f:b], '')
        new_points = find_mod_references(text)
        return return_text_no_quotes(text, new_points)
    return text


def find_mod_references(text):
    '''
    Used to find all the amendment text inside a modificatory provision
    There are special cases where «» are used multiple times so a simple
    regular expression is not valid to remove such text
    '''
    if isinstance(text, unicode):
        # check where all "«»" that reference amendments start and stop
        iter_1 = re.finditer(r"«".decode('UTF-8'), text)
        iter_2 = re.finditer(r"»".decode('UTF-8'), text)
    else:
        iter_1 = re.finditer(r"«", text)
        iter_2 = re.finditer(r"»", text)

    start = [m.start(0) for m in iter_1]
    end = [m.end(0) for m in iter_2]
    
    for n in range(1, len(start)):
        try:
            while start[n] < end[n-1]:
                start.pop(n)
                end.pop(n - 1)
        except IndexError:
            break
    return start, end


def return_changed_text(txt, start_stop, flag):
    '''
    Συνάρτηση που καταστρέφει τα πατερνς που δημιουργούν πρόβλημα κατά την εκτέλεση
    κάποιων ενεργειών (δημιουργία xml κτλ.)

    txt: Το κείμενο που θέλουμε να αλλάξουμε

    start_stop: Λίστα που περιέχει την αρχή και το τέλος των « » που περιέχουν την
    τροποποίηση (προέρχεται από την find_mod_references)

    flag: Σημαία που δείχνει την ενέργεια που προέρχεται η προσπέλαση της συνάρτησης
    0 -> κατά τη δημιουργία του xml αρχείου
    1 -> κατά τον έλεγχο της παραγράφου αν περιέχει περιπτώσεις να χωριστεί το κείμενο
         με βάση τις περιπτώσεις
    '''
    begin = start_stop[0]
    end = start_stop[1]
    
    if len(begin)!=len(end):
        print "Wrong modification inside modifications"
        return txt
    else:
        try:
            if flag == 0:
                for n in range(0, len(begin)):
                    #print txt[begin[n]:end[n]]+"----------------------"
                    #Βρίσκουμε όλα τα « » που βρίσκονται μέσα στα όρια του κειμένου από
                    #τους πίνακες begin και end (αναφορές μέσα σε αναφορές)
                    #ΔΕΝ ΕΧΟΥΜΕ ΕΛΕΓΧΟ ΓΙΑ UNICODE ΓΙΑΤΙ ΧΡΗΣΙΜΟΠΟΙΕΊΤΑΙ ΜΟΝΟ ΣΕ ΑΠΟ ΚΑΤΑ ΤΗ ΔΗΜΙΟΥΡΓΙΑ
                    #ΤΟΥ XML ΚΑΙ ΕΊΝΑΙ BYTES Ο ΤΥΠΟΣ ΚΕΙΜΕΝΟΥ ΑΠΟ ΤΑ PDF
                    patt_1 = re.findall(r'(?=(ΒΙΒΛΙΟ|ΜΕΡΟΣ|ΤΜΗΜΑ|ΚΕΦΑΛΑΙΟ)(?=\s\S+\n))', txt[begin[n]:end[n]], re.DOTALL)
                    patt_2 = re.findall(r'(?=(Άρθρο)(?=\s\d+\n))', txt[begin[n]:end[n]], re.DOTALL)
                    patt_4 = re.findall(r'(?=(Άρθρο)(?=\s\d+\S+\n))', txt[begin[n]:end[n]], re.DOTALL)
                    patt_3 = re.findall(r'(\d+)([.])', txt[begin[n]:end[n]], re.DOTALL) 

                    if patt_1:
                        text = re.sub(r'(ΒΙΒΛΙΟ|ΜΕΡΟΣ|ΤΜΗΜΑ|ΚΕΦΑΛΑΙΟ)(?=\s\S+\n)', r'\1$', txt[begin[n]:end[n]], re.DOTALL)
                        txt = txt.replace(txt[begin[n]:end[n]], text)
                        new_points = find_mod_references(txt)
                        return return_changed_text(txt, new_points, 0)
                    if patt_2:
                        #for n in range(0, len(patt_2)):
                        #    print patt_2[n]
                        text = re.sub(r'(Άρθρο)(?=\s\d+\n)', r'\1$', txt[begin[n]:end[n]], re.DOTALL)
                        txt = txt.replace(txt[begin[n]:end[n]], text)
                        new_points = find_mod_references(txt)
                        return return_changed_text(txt, new_points, 0)
                    if patt_3:
                        #for n in range(0, len(patt_3)):
                        #    print patt_3[n]
                        text = re.sub(r'(\d+)([.])', r'\1!\2', txt[begin[n]:end[n]], re.DOTALL)
                        txt = txt.replace(txt[begin[n]:end[n]], text)
                        new_points = find_mod_references(txt)
                        return return_changed_text(txt, new_points, 0)
                    if patt_4:
                        #for n in range(0, len(patt_3)):
                        #    print patt_3[n]
                        text = re.sub(r'(Άρθρο)(?=\s\d+\S+\n)', r'\1$', txt[begin[n]:end[n]], re.DOTALL)
                        txt = txt.replace(txt[begin[n]:end[n]], text)
                        new_points = find_mod_references(txt)
                        return return_changed_text(txt, new_points, 0)
                return txt

            else:
                for n in range(0, len(begin)):
                #Βρίσκουμε όλα τα « » που βρίσκονται μέσα στα όρια του κειμένου από
                #τους πίνακες begin και end (αναφορές μέσα σε αναφορές)
                    if isinstance(txt, unicode):
                        patt_5 = re.findall(r'(\n|[«]{1}|1[.]\s)([α-ω|Α-Ω]{1,3})([)]|[.])'.decode('UTF-8'), txt[begin[n]:end[n]], re.DOTALL)
    
                        if patt_5:
                            text = re.sub(r'(\n|[«]{1}|1[.]\s)([α-ω|Α-Ω]{1,3})([)]|[.])'.decode('UTF-8'), r'\1\2!\3', txt[begin[n]:end[n]], re.DOTALL)
                            txt = txt.replace(txt[begin[n]:end[n]], text)
                            new_points = find_mod_references(txt)
                            return return_changed_text(txt, new_points, 1)
                    else:
                        patt_5 = re.findall(r'(\n|[«]{1}|1[.]\s)([α-ω|Α-Ω]{1,3})([)]|[.])', txt[begin[n]:end[n]], re.DOTALL)

                        if patt_5:
                            text = re.sub(r'(\n|[«]{1}|1[.]\s)([α-ω|Α-Ω]{1,3})([)]|[.])', r'\1\2!\3', txt[begin[n]:end[n]], re.DOTALL)
                            txt = txt.replace(txt[begin[n]:end[n]], text)
                            new_points = find_mod_references(txt)
                            return return_changed_text(txt, new_points, 1)
                return txt
        except IndexError:
            #print name
            #print ("Wrong modification inside modifications", file = log)
            print "Wrong modification inside modifications"
            return txt



def check_elinpar(list_, path_):
    '''
    Checks if an element exist in a structure
    '''
    count = []
    for n in list_:
        if path_[n[0]]:
            count.append(n)

    return count


def XMLtoXHTML(XMLfile, XSLfile):
    '''
    Turns an XML file to txt according to an XSL file

    XMLfile: The XML file that
    XSLfile: The XSL file that we use to tranform the XML file
    '''
    from lxml import etree
    
    xmltree = etree.parse(XMLfile)
    xsl = etree.parse(XSLfile)

    transform = etree.XSLT(xsl)
    NewXmlTree = transform(xmltree)

    return NewXmlTree
