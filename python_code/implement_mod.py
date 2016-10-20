# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import re
import sys
import itertools
import datetime
import time
import shutil
import pickle
import subprocess
import nltk.data
import nltk
from lxml import etree
from functions import *
from create_xml_with_mod import *

'''
This is STEP 6 and 7 of the system implemantion. To be able to use this module
you need to have VALID XML files, i.e files that have been manually corrected
due to erros in previous steps (scanned images) or due to author's errors
(the legislation author does not conform with Central Commitee's rules)

ALL VALID XML LAWS FILES are stored in a folder named (valid_xml_laws)
'''

#The folder that contains valid XML laws
src = '/path/to/valid/xml/laws'

#Path to XSL file
#xls_src = '/path/to/XSL/file'
xls_src = 'laws.xsl'

#Repository of XML files revisions (A user defined git folder
#for storing XML Laws revisions
xml_laws_repo = '/git/folder/for/xml/laws/revisions/'

#Repository of text files revisions (A user defined git folder
#for storing text laws files after applying XSL Transformation
text_laws_repo = '/git/folder/for/text/laws/revision/'

#19 patterns that match 96% of modifications according to test corpus
modif_patterns = [(r'(Ο\s)(τίτλος\sτου.*?)(από)\s*(γίνεται)\s[,]\s(οι\s(.*?)(αναριθμούνται)(.*?)(?=\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:]))(.*)', 1),
             (r'(Ο\s)(τίτλος\sτου.*?)(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|έχουν\sως\sεξής|αναδιατυπώνεται'+
              '|αναδιατυπώνονται|συμπληρώνεται|συμπληρώνονται)(.*?)(\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])(.*)', 2),
             (r'(Ο\s)((τίτλος\sκαι\s)(η|το|τα|οι)\s(στοιχείο|στοιχεία|υποπερίπτωση|υποπεριπτώσεις|περίπτωση|περ[.]|περιπτώσεις|εδάφιο|εδάφια|περίοδος'+
              '|περίοδοι|παράγραφος|παρ[.]|παραγράφος|παράγραφοι|άρθρο|άρθρα).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}'+
              '|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής'+
              '|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται|συμπληρώνονται|συμπληρώνεται|αναριθμούνται|αναριθμείται)(.*?)'+
              '(\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])(.*)', 3),
             (r'(Το|Τα|Τo)\s((\S+\sκαι\s(το\s){0,1}\S+\s)(εδάφια|άρθρα|εδάφιο|εδάφιo).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}'+
              '|((που|με\sτα\sοποία)\sκυρώθηκαν\s.*?){0,1}|((που|τα\sοποία)\sπροστέθηκαν\s.*?){0,1}|((με\sτα|τα)\sοποία\s.*?){0,1})'+
              '(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|αναδιατυπώνεται|συμπληρώνονται|αναδιατυπώνονται'+
              '|συμπληρώνεται|αναριθμούνται|αναριθμείται)(.*?)(\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])(.*)', 4),
             (r'(Τα|Το)\s((\S+\s){2}(εδάφια|άρθρα|εδάφιο).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτα\sοποία)\sκυρώθηκαν\s.*?){0,1}'+
              '|((που|τα\sοποία)\sπροστέθηκαν\s.*?){0,1}|((με\sτα|τα)\sοποία\s.*?){0,1})(αντικαθίστανται|αντικαθίσταται|τροποποιούνται|έχουν\sως\sεξής'+
              '|αναδιατυπώνονται|συμπληρώνονται|αναριθμούνται)(.*?)(\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])(.*)', 5),
             (r'(Η|H|Το|To|Tο|Τα|Οι)\s((?!νέα|νέο)(\S+\s){1}(στοιχείο|στοιχεία|υποπερίπτωση|υποπεριπτώσεις|περίπτωση|περ[.]|περιπτώσεις|εδάφιο|εδάφια|περίοδος'+
              '|περίοδοι|παράγραφος|παρ[.]|παραγράφος|παράγραφοι|άρθρο|άρθρα|κεφάλαιο|κεφάλαια).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}'+
              '|((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(αντικαθίσταται|αντικαθίστανται'+
              '|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται|συμπληρώνονται|συμπληρώνεται'+
              '|αναριθμούνται|αναριθμείται)(.*?)(\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])(.*)', 6), 
             (r'(Η|H|Το|To|Τα|Οι)\s((\S+\s){0}(στοιχείο|στοιχεία|υποπερίπτωση|υποπεριπτώσεις|περίπτωση|περ[.]|περιπτώσεις|εδάφιο|εδάφια|περίοδος|περίοδοι'+
              '|παράγραφος|παρ[.]|παραγράφος|παράγραφοι|άρθρο|άρθρα|κεφάλαιο|κεφάλαια).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}'+
              '|((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(αντικαθίσταται|αντικαθίστανται'+
              '|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται|συμπληρώνονται|συμπληρώνεται'+
              '|αναριθμούνται|αναριθμείται)(.*?)(\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])\s(.*)', 7),
             (r'(Προστίθεται)(.*?)((\sως\sεξής|\sως\sακολούθως){0,1}[:])(.*)', 8),
             (r'(Στην\s|Στο\s|Στον\s|Μετά\sαπό\sτο\s|Μετά\sτο\s|Μετά\sτον\s|Μετά\sτη\s|Μετά\sτην\s)(.*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο|η\sοποία|ο\sοποίος)\s(κυρώθηκε\s|τροποποιήθηκε\s'+
              '|προστέθηκε\s|αντικαταστάθηκε\s).*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(προστίθεται|προστίθενται|\bτίθενται)\s(.*?)(\n\S{0,2}[)]|\n\S{0,2}[.]\s'+
              '|\n\d+[.]\s|(\sως\sεξής|\sως\sακολούθως){0,1}[:])(.*)', 9),
             (r'(Στην\s|Στο\s|Στον\s|Μετά\sαπό\sτο\s|Μετά\sτο\s|Μετά\sτον\s|Μετά\sτη\s|Μετά\sτην\s)(.*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο|η\sοποία|ο\sοποίος)\s(κυρώθηκε\s|τροποποιήθηκε\s|'+
              'προστέθηκε\s|αντικαταστάθηκε\s).*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})η\s(φράση\s)(.*?)(αντικαθίσταται)\s(από\sτη\sφράση|σε|με\sτη\sφράση\s|'+
              'ως\sεξής[:]){0,1}(.*)', 10),
             (r'(Στις|Στην\s|Στο\s|Στον\s|Μετά\s)(.*?)(αντί\sτων\sλέξεων)\s(.*?)(\bτίθενται)(\sοι\sλέξεις\s)(.*)[.]', 11),
             (r'(Η|Οι)\s((διάταξη|διατάξεις).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτα\sοποία)\sκυρώθηκαν\s.*?){0,1}'+
              '|((που|τα\sοποία)\sπροστέθηκαν\s.*?){0,1}|((με\sτα|τα)\sοποία\s.*?){0,1})(αντικαθίστανται|αντικαθίσταται|τροποποιούνται'+
              '|τροποποιείται)(.*?)(\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])(.*)', 12),
             (r'(Στην\s|Στο\s|Στον\s|Μετά\s)(.*?)(όπως\sισχύει[,]{0,1}){0,1}(\sμετά\sτη\sφράση\s)(.*?)(προστίθεται|προστίθενται)\s(η\sφράση\s|οι\sλέξεις\s)(.*)[.]', 13),
             (r'(Από\s|Στις\s|Στην\s|Στο\s|Στον\s)(.*?)(διαγράφεται|διαγράφονται)\s(η\sφράση|στοιχείο|οι\sλέξεις)(.*)', 14),             
             (r'(Στην|Στη|Στο)(.*?)(οι\sλέξεις\s)(.*)(αντικαθίσταται|αντικαθίστανται)([,]{0,1})(\sαπό\sτις\sλέξεις[:]{0,1}\s{0,1})(.*)[.]', 15),
             (r'(Η)\s((\S+\s){1}(πρόταση|φράση).*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}'+
              '|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})(αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής'+
              '|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται|συμπληρώνονται|συμπληρώνεται|αναριθμούνται|αναριθμείται)(.*?)'+
              '(\n\S{0,2}[)]|\n\S{0,2}[.]\s|\n\d+[.]\s|[:])(.*)', 16),
             (r'(Η|H|Το|To|Τα|Οι|Ο)\s((\S+\s){0}(νόμος|νόμοι|ν[.]|στοιχείο|στοιχεία|υποπερίπτωση|υποπεριπτώσεις|περίπτωση|περ[.]|περιπτώσεις|εδάφιο|εδάφια'+
              '|περίοδος|περίοδοι|παράγραφος|παρ[.]|παραγράφος|παράγραφοι|άρθρο|άρθρα|κεφάλαιο|κεφάλαια|διάταξη|διατάξεις).*?)'+
              '((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}|((που|με\sτον\sοποίο)\sκυρώθηκε\s.*?){0,1}|((που|η\sοποία)\sπροστέθηκε\s.*?){0,1}'+
              '|((με\sτην|η)\sοποία\s.*?){0,1})(καταργείται|καταργούνται|παύει\sνα\sισχύει|παύουν\sνα\sισχύουν)', 17),
             (r'(Στην\s|Στο\s|Στον\s|Μετά\sαπό\sτο\s|Μετά\sτο\s|Μετά\sτον\s|Μετά\sτη\s|Μετά\sτην\s)(.*?)((σχετικά\sμε.*?){0,1}|(όπως\s.*?){0,1}'+
              '|((που|με\sτον\sοποίο|η\sοποία|ο\sοποίος)\s(κυρώθηκε\s|τροποποιήθηκε\s|προστέθηκε\s|αντικαταστάθηκε\s).*?){0,1}|((με\sτην|η)\sοποία\s.*?){0,1})'+
              '((διαγράφονται|διαγράφεται(?![.])).*?)(η\sφράση|οι\sλέξεις|η\sλέξη|στοιχείο|το\sκόμμα|η\sτελεία)(.*?)([«].*?[»])', 18),
             (r'(Καταργείται|Καταργούνται)\s(η|το|οι|κάθε)(.*?)[.]\n(?=(\n|\S{0,2}[.]|\S{0,2}[)]))', 19)
]

#Each structure element may be verbally referenced so a mapping is necessary to
#find out the id of the corresponding element in XML
element_numbering = [
    (r'εικοστής\sόγδοης|εικοστού\sόγδοου|κη΄|κη’|κη´|εικοστό\sόγδοο', r'28'),
    (r'εικοστής\sέβδομης|εικοστού\sέβδομου|κζ΄|κζ’|κζ´|εικοστό\sέβδομο', r'27'),
    (r'εικοστής\sέκτης|εικοστού\sέκτου|κστ΄|κστ’|κστ´|εικοστό\sέκτο', r'26'),
    (r'εικοστής\sπέμπτης|εικοστού\sπέμπτου|κε΄|κε’|κε´|εικοστό\sπέμπτο', r'25'),
    (r'εικοστής\sτέταρτης|εικοστού\sτέταρτου|κδ΄|κδ’|κδ´|εικοστό\sτέταρτο', r'24'),
    (r'εικοστής\sτρίτης|εικοστού\sτρίτου|κγ΄|κγ’|κγ´|εικοστό\sτρίτο', r'23'),
    (r'εικοστής\sδεύτερης|εικοστού\sδεύτερου|κβ΄|κβ’|κβ´|εικοστό\sδεύτερο', r'22'),
    (r'εικοστής\sπρώτης|εικοστού\sπρώτου|κα΄|κα’|κα´|εικοστό\sπρώτο', r'21'),
    (r'εικοστής|εικοστού\s|κ΄|κ’|κ´|εικοστό', r'20'),
    (r'δέκατης\sενάτης|δέκατου\sενάτου|ιθ΄|ιθ’|ιθ´|δέκατο\sένατο', r'19'),
    (r'δέκατης\sόγδοας|δέκατου\sογδόου|ιη΄|ιη’|ιη´|δέκατο\sόγδοο', r'18'),
    (r'δέκατης\sέβδομης|δέκατου\sέβδομου|ιζ΄|ιζ’|δέκατο\sέβδομο', r'17'),
    (r'δέκατης\sέκτης|δέκατου\sέκτου|ιστ΄|ιστ’|ιστ´|δέκατο\sέκτο', r'16'),
    (r'δέκατης\sπέμπτης|δέκατου\sπέμπτου|ιε΄|ιε’|ιε´|δέκατο\sπέμπτο', r'15'),
    (r'δέκατης\sτέταρτης|δέκατου\sτέταρτου|δεκάτου\sτετάρτου|ιδ΄|ιδ’|ιδ´|δέκατο\sτέταρτο', r'14'),
    (r'δέκατης\sτρίτης|δέκατου\sτρίτου|ιγ΄|ιγ’|ιγ´|δέκατο\sτρίτο', r'13'),
    (r'δωδέκατης|δωδέκατου|δωδεκάτου|ιβ΄|ιβ’|ιβ´|δωδέκατο', r'12'),
    (r'ενδέκατης|εντέκατης|εντεκάτου|εντέκατου|ενδέκατου|ενδεκάτου|ια΄|ια’|ια´|ενδέκατο|εντέκατο', r'11'),
    (r'δέκατης|δέκατου|ι΄|ι’|ι´|δέκατο', r'10'),(r'ένατης|ένατου|θ΄|θ’|θ´|ένατο', r'9'),
    (r'όγδοης|όγδοου|η΄|η’|η´|η’|όγδοο', r'8'),(r'έβδομης|έβδομου|ζ΄|ζ’|ζ´|έβδομο', r'7'),
    (r'έκτης|έκτου|στ΄|στ’|στ´|έκτο', r'6'),(r'πέμπτης|πέμπτου|ε΄|ε’|ε´|πέμπτο', r'5'),
    (r'τέταρτης|τέταρτου|δ΄|δ’|δ´|τέταρτο', r'4'),(r'τρίτης|τρίτου|γ΄|γ’|γ´|τρίτο', r'3'),
    (r'δεύτερου|δευτέρου|δεύτερης|β΄|β’|β´|δεύτερο', r'2'),
    (r'πρώτης|πρώτου|α΄|α’|α´|πρώτο', r'1'),(r'τελευταίου|τελευταίας|τελευταίο', r'last')
]

class amendments:
    
    """ Class for amendments """

    def __init__(self, obj):
        self.text = obj.text


    def check_if_cases(self):
        '''
        Checks wether a paragraph is written in cases
        Amendments are written in cases mainly after 2010
        '''
        pattern = r'^(\d[.]\s){0,1}[α-ω|Α-Ω]{1}([.]|[)])'
        
        if isinstance(self.text, unicode):
            self.if_cases = re.match(pattern.decode('UTF-8'), self.text)
        else:
            self.if_cases = re.match(pattern, self.text)

        if self.if_cases:
            return True
        else:
            return False
    

    def split_cases(self):
        '''Splits paragraph into cases'''

        self.ch_text = return_changed_text(self.text, find_mod_references(self.text), 1)
        cases_pat = [
            (r'(\n)(ν|Ν|π|Π|Κ|κ|β)([.])(?=ν|δ|Δ|Φ[.]Ε[.]|Β[.]Σ[.]|Π[.]Δ[.]|Πολ[.]Δ[.])', r'\1\2!\3'),
            (r'(\n)(ν|Ν|παρ)([.])(?=\s|\d)', r'\1\2!\3')
        ]

        self.ch_text_ = destroy_patterns(self.ch_text, cases_pat)
        split_pattern = r'((([α-ω]|[Α-Ω]){1,3}[)]\s|([α-ω]|[Α-Ω]){1,3}[.]\s)(.*?[»]{0,2})(?=[»]{0,1}[.]{0,1}\n([α-ω]|[Α-Ω]){1,3}[)]\s|[»]{0,1}[.]{0,1}\n([α-ω]|[Α-Ω]){1,3}[.]\s|$))'

        if isinstance(self.text, unicode):
            self.cases = re.findall(split_pattern.decode('UTF-8'), self.ch_text_, re.DOTALL)
        else:
            self.cases = re.findall(split_pattern, self.ch_text_, re.DOTALL)

        if self.cases:
            return self.cases
        else:
            pass

    def find_mod_pattern(self, text):
        '''
        Method that returns the matching pattern and its ID according
        to "modif_patterns" list

        Args:
            text: The text to apply the 19 patterns to match an amendment
        '''
        self.text = text
        
        for n in range(0, len(modif_patterns)):
            if isinstance(self.text, unicode):
                self.mod = re.search(modif_patterns[n][0].decode('UTF-8'), self.text, re.DOTALL)
            else:
                self.mod = re.search(modif_patterns[n][0], self.text, re.DOTALL)

            if self.mod:
                self.num_of_pattern = modif_patterns[n][1]
                self.pattern = modif_patterns[n][0]
                return self.num_of_pattern, self.pattern 
                break
            else:
                pass

    def analyze_amendment(self, text, num_of_pat, pattern):
        '''
        Method for analyzing the returning pattern. It returns the path to be
        followed for apply the amendment, the type of the amendment, the element
        to be added/removed/replaced and the amendment text if present

        Args:
            text: The text to match the pattern

            num_of_pat: The Id of the pattern returned in previous step

            pattern: The pattern returned
        '''
        self.text = text
        self.num_of_pat = num_of_pat
        self.pattern = pattern

        #Initialization of path for using with XML Path
        self.path = {'type':'', 'year':'', 'num':'', 'book':'', 'part':'', 'section':'',
                     'chapter':'', 'article':'', 'paragraph':'', 'edafio':'', 'case':'', 'subcase':'', 'stoixeio':'',
                     'diataksi':'', 'phrase':'', 'after':'', 'end':'', 'words':''}

        #Find the type of modification
        #The verb "ΤΙΘΕΝΤΑΙ" is used in different types of amendments
        amendment_category = [
            (r'αντικαθίσταται|αντικαθίστανται|τροποποιείται|τροποποιούνται|έχει\sως\sεξής|έχουν\sως\sεξής|αναδιατυπώνεται|αναδιατυπώνονται|γίνεται', 'substitute'),
            (r'αναριθμείται|αναριθμούνται', 'renumbering'),
            (r'Καταργείται|Καταργούνται|καταργείται|καταργούνται|παύει\sνα\sισχύει|παύουν\sνα\sισχύουν|διαγράφονται|διαγράφεται', 'repeal'),
            (r'συμπληρώνονται|συμπληρώνεται|Προστίθεται|Προστίθενται|προστίθεται|προστίθενται', 'addition')
            ]

        if self.num_of_pat == 11:
            amendment_category.append((r'τίθενται', 'subsitute'))
        elif self.num_of_pat == 9:
            amendment_category.append((r'τίθενται', 'addition'))
        else:
            pass

        #A list contain corresponding laws and code laws
        kwdikes_nomoi = [
            (r'Αγορανομικού\sΚώδικα',   r'ν.δ. 135/1946'),
            (r'(Αστικού\sΚώδικα|Α[.]Κ[.])',     r'Π.Δ. 456/1984'),
            (r'(Κώδικα\sΠοινικής\sΔικονομίας|Κ.Π.Δ.)',      r'Π.Δ. 258/1986'),
            (r'Ποινικού\sΚώδικα',       r'Π.Δ. 283/1985'),
            (r'Εθνικού\sΤελωνειακού\sΚώδικα',       r'ν. 2960/2001'),
            (r'Κώδικα\sΟργανισμού\sΔικαστηρίων\sκαι\sΚατάστασης\sΔικαστικών\sΛειτουργών',       r'ν. 1756/1988'),
            (r'(Κώδικα\sΒιβλίων\sκαι\sΣτοιχείων|Κ.Β.|Κ.\sΒ.\sΣ.)',      r'Π.Δ. 186/1992'),
            (r'(Κώδικα\sΦόρου\sΠροστιθέμενης\sΑξίας|Κώδικα\sΦ[.]Π[.]Α[.])',     r'ν. 2859/2000'),
            (r'Κώδικα\sΔιοικητικής\sΔικονομίας',        r'ν. 2717/1999'),
            (r'(Κώδικα\sΦορολογίας\sΕισοδήματος|Κ.Φ.Ε)',        r'Ν. 2238/1994'),
            (r'Κώδικα\sΦορολογίας\sΚληρονομιών,\sΔωρεών,\sΓονικών\sΠαροχών\sκαι\sΚερδών\sαπό\sΛαχεία',  r'ν. 2961/2001'),
            (r'Κώδικα Διοικητικής Διαδικασίας',     r'Ν. 2690/1999'),
            (r'Κώδικα\sΔήμων\sκαι\sΚοινοτήτων',     r'ν. 3463/2006'),
            (r'Κώδικα\sΔικαστικών\sΥπαλλήλων',      r'ν. 2812/2000'),
            (r'Κώδικα\sτης\sΕλληνικής\sΙθαγένειας|Κώδικα\sΕλληνικής\sΙθαγένειας',       r'ν. 3284/2004'),
            (r'(Κώδικα\sΠροσωπικού\sΛιμενικού\sΣώματος|Κ[.]Π[.]Λ[.]Σ[.])',      r'ν. 3079/2002'),
            (r'(Κώδικα\sΠολιτικής\sΔικονομίας|Κ[.]Πολ[.]Δ[.])',     r'Π.Δ. 503/1985'),
            (r'Κώδικα\sΝόμων\sγια\sτα\sΝαρκωτικά',      r'ν. 3459/2006'),
            (r'Σωφρονιστικού\sΚώδικα',      r'ν. 2776/1999'),
            (r'Πτωχευτικού\sΚώδικα',        r'ν. 3588/2007')
            ]

        #List of structured elements
        xml_elements = [
            (r'παρ[.]|παράγραφος|παραγράφος|παράγραφοι|παράγραφο', 'paragraph'),
            (r'περ[.]|\bπερίπτωση|\bπεριπτώσεις|περίπτωση', 'case'),
            (r'εδάφιο|εδάφια', 'edafio'),
            (r'στοιχείο|στοιχεία', 'stoixeio'),
            (r'υποπερίπτωση|υποπεριπτώσεις', 'subcase'),
            (r'περίοδος|περίοδοι|περίοδο', 'period'),
            (r'άρθρο|άρθρα', 'article'),
            (r'κεφάλαιο|κεφάλαια|Κεφάλαιο|Κεφάλαια', 'chapter'),
            (r'φράση', 'phrase'),
            (r'λέξη|λέξεις', 'words'),
            (r'διάταξη|διατάξεις', 'diataksi')
            ]
        
        if isinstance(self.text, unicode):
            pattern_elements = re.search(self.pattern.decode('utf-8'), self.text, re.DOTALL).groups()
        else:
            pattern_elements = re.search(self.pattern, self.text, re.DOTALL).groups()
 
        self.nomos = re.search(r'(κ[.]ν[.]|α[.]ν[.]|ν[.]δ[.]|ν[.]|v[.]|Κ[.]Ν[.]|Ν[.]Δ[.]|Ν[.]Δ|Ν[.]|Π[.]Δ[.]|π[.]δ[.]|β[.]δ[.])\s{0,1}(\d+\s{0,1}[/]\s{0,1}\d+)'.decode('utf-8'), pattern_elements[1], re.DOTALL)
        self.kwdikas = check_which_matching(pattern_elements[1], kwdikes_nomoi)
        
        if self.nomos:
            self.fek_type = self.nomos.group(1)
            self.nomos_number = self.nomos.group(2).split('/')[0].strip()
            self.nomos_year = self.nomos.group(2).split('/')[1].strip()
            self.path['type'] = self.fek_type
            self.path['num'] = self.nomos_number
            self.path['year'] = self.nomos_year
        elif self.kwdikas:
            self.fek_type = self.kwdikas.split('/')[0].split(' ')[0]
            self.nomos_number = self.kwdikas.split('/')[0].split(' ')[1]
            self.nomos_year = self.kwdikas.split('/')[1]
            self.path['type'] = self.fek_type
            self.path['num'] = self.nomos_number
            self.path['year'] = self.nomos_year
        else:
            self.fek_type = ''
            self.nomos_number = ''
            self.nomos_year = ''
        
        self.edafio = re.search(r'του\sεδαφίου\s((\S+\s){0,2})|του\s((\S+\s){0,2})εδαφίου'.decode('utf-8'), pattern_elements[1])
        self.case = re.search(r'της\sπερίπτωσης\s(\S+)|της\s((\S+\s){0,2})περίπτωσης'.decode('utf-8'), pattern_elements[1])
        self.subcase = re.search(r'της\sυποπερίπτωσης\s(\S+)|της\s(\S+)\sυποπερίπτωσης'.decode('utf-8'), pattern_elements[1])
        self.paragrafos = re.search(r'της\s(παρ[.]|παραγράφου)\s(\d+)|της\s((\S+\s){1,2})(παρ[.]|παραγράφου)'.decode('utf-8'), pattern_elements[1])
        self.arthro = re.search(r'του\sάρθρου\s(\S+)|του\sάρθρου\s(\d+\S{0,2})|του\s((\S+\s){0,2})άρθρου'.decode('utf-8'), pattern_elements[1])
        self.stoixeio = re.search(r'του\s(\S+)\sστοιχείου|του\sστοιχείου\s(\S+)\s'.decode('utf-8'), pattern_elements[1])
        self.diataksi = re.search(r'της\s(\S+)\sδιάταξης|της\sδιαταξης\s(\S+)\s'.decode('utf-8'), pattern_elements[1])
        self.chapter = re.search(r'του\s(\S+)\sκεφαλαίου|του\sκεφαλαίου\s(\S+)\s'.decode('utf-8'), pattern_elements[1])
        self.section = re.search(r'του\s(\S+)\sτμήματος|του\sτμήματος\s(\S+)\s'.decode('utf-8'), pattern_elements[1])
        self.book = re.search(r'του\s(\S+)\sβιβλίου|του\sβιβλίου\s(\S+)\s'.decode('utf-8'), pattern_elements[1])
        self.part = re.search(r'του\s(\S+)\sμέρους|του\sμέρους\s(\S+)\s'.decode('utf-8'), pattern_elements[1])

        if self.edafio:
            if self.edafio.group(1):
                self.path['edafio'] = check_which_matching(self.edafio.group(1), element_numbering)
            else:
                self.path['edafio'] = check_which_matching(self.edafio.group(3), element_numbering)

        if self.case:
            if self.case.group(1):
                self.path['case'] = self.case.group(1)
            else:
                self.path['case'] = self.case.group(3)

        if self.subcase:
            if self.subcase.group(1):
                self.path['subcase'] = self.subcase.group(1)
            else:
                self.path['subcase'] = self.subcase.group(3)
       
        if self.paragrafos:
             if self.paragrafos.group(1):
                self.path['paragraph'] = self.paragrafos.group(2)
             else:
                self.path['paragraph'] = check_which_matching(self.paragrafos.group(3), element_numbering)

        if self.arthro:
             if self.arthro.group(1):
                self.path['article'] = self.arthro.group(1)
             else:
                self.path['article'] = check_which_matching(self.arthro.group(3), element_numbering)

        if self.stoixeio:
            if self.stoixeio.group(1):
                self.path['stoixeio'] = self.stoixeio.group(1)
            else:
                self.path['stoixeio'] = self.stoixeio.group(2)

        if self.diataksi:
            if self.diataksi.group(1):
                self.path['diataksi'] = self.diataksi.group(1)
            else:
                self.path['diataksi'] = self.diataksi.group(3)

        if self.chapter:
            if self.chapter.group(1):
                self.path['chapter'] = self.chapter.group(1)
            else:
                self.path['chapter'] = self.chapter.group(2)

        if self.section:
            if self.section.group(1):
                self.path['section'] = self.section.group(1)
            else:
                self.path['section'] = self.section.group(2)

        if self.part:
            if self.part.group(1):
                self.path['part'] = self.part.group(1)
            else:
                self.path['part'] = self.part.group(2)

        if self.book:
            if self.book.group(1):
                self.path['book'] = self.book.group(1)
            else:
                self.path['book'] = self.book.group(2)

        #All other elements are based on the ID of the returning pattern
        if self.num_of_pat in(6, 7):

            self.rima = pattern_elements[13]

            #Amendment type
            self.category = check_which_matching(self.rima, amendment_category)

            #Element ID to be replaced
            self.change_element = check_which_matching(pattern_elements[3], xml_elements)
            if self.num_of_pat == 7:
                self.change_element_id = re.search(r''+pattern_elements[3]+'\s{0,1}(.*?)(του|της|ΠΚ)'.decode('utf-8'), pattern_elements[1], re.DOTALL)
            elif self.num_of_pat == 6:
                self.change_element_id = re.search(r'(\S+){1}\s'+pattern_elements[3]+'\s(του|της)'.decode('utf-8'), pattern_elements[1], re.DOTALL)

            #Update element's ID
            if self.change_element_id:
                self.path[self.change_element] = self.change_element_id.group(1).strip()
            else:
                pass

            #Amendment text
            self.tropopoihsh = pattern_elements[16]
            self.tropopoihsh = re.sub(r'([α-ω]*)(!)([.]|[)])'.decode('utf-8'), r'\1\3', self.tropopoihsh, re.DOTALL)
            self.epipleon_modif = pattern_elements[14]

            #If we want to keep log information for amendments
            #print ("KEIMENO KOMBOY mod " +elem.get('id')+ " : "+self.text.encode('utf-8')+"\n", file = log)
            #print ("TROPOPOIHSH: "+self.tropopoihsh.encode('utf-8')+"\n", file = log)
            #print ("PATTERN ME ARITHMO: "+str(self.num_of_pat)+"\n", file = log)
            #print ("KLITHEISA SUNARTISI: "+self.category.encode('utf-8')+"\n", file = log)
            #print ("RHMA TROPOPOIHSHS: "+self.rima.encode('utf-8') + "\n", file = log)
            #if self.fek_type:
            #    print ("TYPOS: "+self.fek_type.encode('utf-8'), file = log)
            #if self.nomos_number:
            #    print ("ARITHMOS: "+self.nomos_number.encode('utf-8'), file = log)
            #if self.nomos_year:
            #    print ("ETOS : "+self.nomos_year.encode('utf-8')+"\n\n", file = log)
          
            #print ("Location Dictionary me slots:   ", file = log)
            #print (self.path, file = log)
            return self.path, self.category, self.change_element, self.tropopoihsh, self.epipleon_modif
            

        elif self.num_of_pat == 9 :

            self.rima = pattern_elements[10]
            #Amendment type
            self.category = check_which_matching(self.rima, amendment_category)

            after = re.search(r'Μετά'.decode('utf-8'), pattern_elements[0], re.DOTALL)
            if after:
                self.path['after'] = '1'
            
            end = re.search(r'τέλος'.decode('utf-8'), pattern_elements[1], re.DOTALL)
            if end:
                self.path['end'] = '1'
            

            #This type of pattern contains a special case
            self.edafio_ = re.search(r'(\S+)\sεδάφιο\s|εδάφιο\s(\S+)'.decode('utf-8'), pattern_elements[1])
            self.case_ = re.search(r'(\S+)\sπερίπτωση\s|περίπτωση\s(\S+)'.decode('utf-8'), pattern_elements[1])
            self.subcase_ = re.search(r'(\S+)\sυποπερίπτωση\s|υποπερίπτωση\s(\S+)'.decode('utf-8'), pattern_elements[1])
            if not self.paragrafos:
                self.paragrafos_ = re.search(r'(\S+)\s(παρ[.]|παράγραφο)\s|(παρ[.]|παράγραφο)\s(\d*\S*)'.decode('utf-8'), pattern_elements[1])

                if self.paragrafos_:
                    if self.paragrafos_.group(1):
                        self.path['paragraph'] = check_which_matching(self.paragrafos_.group(1), element_numbering)
                    else:
                        self.path['paragraph'] = self.paragrafos_.group(4)

            self.arthro_ = re.search(r'(\S+)\sάρθρο\s|άρθρο\s(\d+\S{0,2})'.decode('utf-8'), pattern_elements[1])
            self.stoixeio_ = re.search(r'(\S+)\sστοιχείο\s|στοιχείο\s(\S+)'.decode('utf-8'), pattern_elements[1])
            self.diataksi_ = re.search(r'(\S+)\sδιάταξη\s|διαταξης\s(\d*\S*)\s'.decode('utf-8'), pattern_elements[1])
            self.chapter_ = re.search(r'(\S+)\sκεφάλαιο\s|κεφάλαιο\s(\S+)'.decode('utf-8'), pattern_elements[1])
            self.section_ = re.search(r'(\S+)\sτμήμα\s|τμήμα\s(\S+)'.decode('utf-8'), pattern_elements[1])
            self.book_ = re.search(r'(\S+)\sβιβλίο\s|βιβλίο\s(\S+)'.decode('utf-8'), pattern_elements[1])
            self.part_ = re.search(r'(\S+)\sμέρος\s|μέρος\s(\S+)'.decode('utf-8'), pattern_elements[1])

            if self.edafio_:
                if self.edafio_.group(1):
                    self.path['edafio'] = check_which_matching(self.edafio_.group(1), element_numbering)
                else:
                    self.path['edafio'] = check_which_matching(self.edafio_.group(2), element_numbering)
            
            if self.case_:
                if self.case_.group(1):
                    self.path['case'] = check_which_matching(self.case_.group(1), element_numbering)
                else:
                    self.path['case'] = self.case_.group(2)
                    
            if self.subcase_:
                if self.subcase_.group(1):
                    self.path['subcase'] = check_which_matching(self.subcase_.group(1), element_numbering)
                else:
                    self.path['subcase'] = self.subcase_.group(2)
            
            if self.arthro_:
                 if self.arthro_.group(1):
                    self.path['article'] = check_which_matching(self.arthro_.group(1), element_numbering)
                 else:
                    self.path['article'] = self.arthro_.group(2)

            if self.stoixeio_:
                if self.stoixeio_.group(1):
                    self.path['stoixeio'] = check_which_matching(self.stoixeio_.group(1), element_numbering)
                else:
                    self.path['stoixeio'] = self.stoixeio_.group(2)

            if self.diataksi_:
                if self.diataksi_.group(1):
                    self.path['diataksi'] = self.diataksi_.group(1)
                else:
                    self.path['diataksi'] = self.diataksi_.group(2)

            if self.chapter_:
                if self.chapter_.group(1):
                    self.path['chapter'] = self.chapter_.group(1)
                else:
                    self.path['chapter'] = self.chapter_.group(2)

            if self.section_:
                if self.section_.group(1):
                    self.path['section'] = self.section_.group(1)
                else:
                    self.path['section'] = self.section_.group(2)

            if self.part_:
                if self.part_.group(1):
                    self.path['part'] = self.part_.group(1)
                else:
                    self.path['part'] = self.part_.group(2)

            if self.book_:
                if self.book_.group(1):
                    self.path['book'] = self.book_.group(1)
                else:
                    self.path['book'] = self.book_.group(2)


            #The element to be inserted
            self.insert_element = pattern_elements[11].strip()
            self.insert_element = check_which_matching(self.insert_element, xml_elements)
            
            #Amendment text
            self.tropopoihsh = pattern_elements[14]
            self.tropopoihsh = re.sub(r'([α-ω]*)(!)([.]|[)])(\s)'.decode('utf-8'), r'\1\3\4', self.tropopoihsh, re.DOTALL)

            #For log file
            #print ("KEIMENO KOMBOY mod " +elem.get('id')+ " : "+self.text.encode('utf-8')+"\n", file = log)
            #print ("TROPOPOIHSH: "+self.tropopoihsh.encode('utf-8')+"\n", file = log)
            #print ("PATTERN ME ARITHMO: "+str(self.num_of_pat)+"\n", file = log)
            #print ("KLITHEISA SUNARTISI: "+self.category.encode('utf-8')+"\n", file = log)
            #print ("RHMA TROPOPOIHSHS: "+self.rima.encode('utf-8') + "\n", file = log)
            #if self.fek_type:
            #    print ("TYPOS: "+self.fek_type.encode('utf-8'), file = log)
            #if self.nomos_number:
            #    print ("ARITHMOS: "+self.nomos_number.encode('utf-8'), file = log)
            #if self.nomos_year:
            #    print ("ETOS : "+self.nomos_year.encode('utf-8')+"\n\n", file = log)

            #print ("Location Dictionary me slots:   ", file = log)
            #print (self.path, file = log)
            return self.path, self.category, self.insert_element, self.tropopoihsh
                  
        elif self.num_of_pat == 17 :

            self.rima = pattern_elements[13]

            #Amendment type
            self.category = check_which_matching(self.rima, amendment_category)

            #Element and its ID to be changed
            self.change_element = check_which_matching(pattern_elements[3], xml_elements)
            self.change_element_id = re.search(r''+pattern_elements[3]+'\s{0,1}(.*?)(του|της|ΠΚ)'.decode('utf-8'), pattern_elements[1], re.DOTALL)
            if self.change_element_id:
                self.path[self.change_element] = self.change_element_id.group(1).strip()
            else:
                pass

            #For log file
            #print ("KEIMENO KOMBOY mod " +elem.get('id')+ " : "+self.text.encode('utf-8')+"\n", file = log)
            #print ("PATTERN ME ARITHMO: "+str(self.num_of_pat)+"\n", file = log)
            #print ("KLITHEISA SUNARTISI: "+self.category.encode('utf-8')+"\n", file = log)
            #print ("RHMA TROPOPOIHSHS: "+self.rima.encode('utf-8') + "\n", file = log)
            #if self.fek_type:
            #    print ("TYPOS: "+self.fek_type.encode('utf-8'), file = log)
            #if self.nomos_number:
            #    print ("ARITHMOS: "+self.nomos_number.encode('utf-8'), file = log)
            #if self.nomos_year:
            #    print ("ETOS : "+self.nomos_year.encode('utf-8')+"\n\n", file = log)

            #print ("Location Dictionary me slots:   ", file = log)
            #print (self.path, file = log)
            return self.path, self.category, self.change_element
            
        #All other patterns have not been analyzed yet
        else:
            print ("Other type of Pattern, proceed with next pattern...", file = log)
            pass

    def substitute(self, dict_path, amend_elem, amend_text, extra_amend):
        '''
        Method for implementing the substitution

        Args:
            dict_path: The dictionary for constructing the XML path
            
            amend_elem: The structure element to be substitued

            amend_text: The amendment text that will be inserted

            extra_amend: If the modificatory provision contains extra modifications
                        return the corresponding text (for complex modifications)
        '''
        
        self.dict_path = dict_path
        self.amend_elem = amend_elem
        self.amend_text = amend_text
        self.extra_amend = extra_amend
    
        count_elements = []
        
        try:
            if re.search(r'έως'.decode('utf-8'), self.dict_path[self.amend_elem], re.DOTALL):
                rm = re.sub(r'και\s'.decode('utf-8'), r'', self.dict_path[self.amend_elem], re.DOTALL)      
                split = rm.split('έως'.decode('utf-8'))
        
                for n in range(int(split[0].strip()), int(split[1].strip()) + 1):
                    count_elements.append(str(n).decode('UTF-8'))
            else:  
                split = self.dict_path[self.amend_elem].split('και'.decode('utf-8'))

                if len(split) > 1:
                    if split[0]:
                        split_ = split[0].split(',')
                        if split_:
                            for n in range(0, len(split_)):
                                count_elements.append(split_[n].strip())
                    if split[1]:
                        count_elements.append(split[1].strip())
                else:
                    count_elements.append(split[0].strip())
        except UnicodeEncodeError:
            pass

        #Prepare the amendment text
        if self.amend_text.startswith('\n«'.decode('utf-8')):
            self.amend_text = self.amend_text[2:].strip()
        elif self.amend_text.startswith('«'.decode('utf-8')):
            self.amend_text = self.amend_text[1:].strip()

        if self.amend_text.endswith('.'.decode('utf-8')):
            self.amend_text = self.amend_text[:-2]
        else:
            self.amend_text = self.amend_text[:-1]
          
        #Construct Law name to apply the modification
        NOMOS = construct_law_name(self.dict_path['type'], self.dict_path['num'], self.dict_path['year'])

        if NOMOS:
            law_in_cpfolder = file_in_path(NOMOS, xml_laws_repo)
            law_in_src = file_in_path(NOMOS, src)
            
            if not law_in_cpfolder:
                if law_in_src:
                    shutil.copy(os.path.join(src, law_in_src), xml_laws_repo)
                else:
                    print ("No such Law in folder", file = log)

            if law_in_cpfolder:

                if law_in_cpfolder in cm_laws_msg:
                    pass
                else:
                    cm_laws_msg.append(law_in_cpfolder)
                    
                xmltree = etree.parse(os.path.join(xml_laws_repo, law_in_src))
                rootnode = xmltree.getroot()
                
                func = [
                    ('paragraph', find_paragraphs),('article', find_articles), ('chapter', find_chapters),
                    ('sections', find_sections), ('part', find_parts),
                    ('book', find_books)
                ]

                if self.amend_elem in ('paragraph','article', 'chapter', 'book', 'part', 'section'):
                    for k in func:
                        if k[0] == self.amend_elem:
                            elparent = etree.Element(k[0], attrib={"id":dict_path[self.amend_elem]})
                            k[1](self.amend_text.encode('utf-8'), elparent, 1)
                            #print (etree.tostring(elparent, pretty_print=True, encoding="UTF-8"), file = log)

                    for n in count_elements:
                        for elem1 in elparent.xpath('/'+self.amend_elem+'/'+self.amend_elem+"[@id="'"'+n+'"'"]"):
                            nodeidx_ = elem1.getparent().index(elem1)
                            eltochange = elem1.getparent()[nodeidx_]
                        try:    
                            for elem in xmltree.xpath(find_xpath(self.dict_path, n, self.amend_elem)):
                                nodeidx = elem.getparent().index(elem)
                                elem.getparent()[nodeidx] = eltochange
                        except UnboundLocalError:
                            pass

                elif self.amend_elem in ( 'edafio', 'case', 'subcase', 'stoixeio', 'diataksi'):
                    ele_list = [('edafio', self.dict_path['edafio']), ('diataksi', self.dict_path['diataksi']),
                                ('case', self.dict_path['case']), ('subcase', self.dict_path['subcase']), ('stoixeio', self.dict_path['stoixeio'])]

                    elinpara = check_elinpar(ele_list, self.dict_path)
                    for elem in xmltree.xpath(find_xpath(self.dict_path, 0, self.amend_elem)):
                        if not elinpara:
                            pass

                        elif elinpara and len(elinpara) == 1:
                            for n in count_elements:
                                #Based on type of changing element
                                if self.amend_elem == 'case' or self.amend_elem == 'stoixeio':
                                    if re.search(r'[(]', n, re.DOTALL):
                                        n = n[1:-1]
                                    else:
                                        n = n[:-1]

                                    if elem.getchildren():
                                        for komvos in elem.getchildren():
                                            if komvos != "header" and komvos.tag != "title":
                                                node = komvos
                                    else:
                                        node = elem
                                        
                                    repltext = re.findall(r'('+n+'[).]\s{0,1}[Α-Ω-α-ω-0-9].*?(?=\n[α-ω][).]\s|$))'.decode('utf-8'), node.text, re.DOTALL)
                                    instext = re.findall(r'('+n+'[).]\s[Α-Ω-α-ω-0-9].*?(?=\n[α-ω][).]\s|$))'.decode('utf-8'), self.amend_text, re.DOTALL)
                                    #Substitution will be applied if both cases exist in two texts
                                    if repltext and instext:
                                        node.text = node.text.replace(repltext[0], instext[0])
                                        
                                elif self.amend_elem == 'edafio':
                                    #Use trained tokenizer to split sentences and apply the substitution
                                    if elem.getchildren() and elem.getchildren()[0].tag == "mod":
                                        node = elem.getchildren()[0]
                                    else:
                                        node = elem
                                        
                                    numpar = re.search(r'^\d+[.]\s', node.text, re.DOTALL)
                                    sent_list = sent_tokenizer.tokenize(node.text)
                                    #print (n.encode('utf-8'), file = log)

                                    if numpar:
                                        try:
                                            if (check_which_matching(n, element_numbering)) == 'last':
                                                repltext = sent_list[-1]
                                            else: 
                                                repltext = sent_list[int(check_which_matching(n, element_numbering))]

                                            if repltext and self.amend_text:
                                                is_int = re.search(r'^\d+[.]', self.amend_text)
                                                
                                                if is_int:
                                                    node.text = node.text.replace(repltext, self.amend_text[len(is_int.group(0)):])
                                                else:
                                                    node.text = node.text.replace(repltext, self.amend_text)
                                        except (ValueError, IndexError) as error:
                                            pass
                                            
                                    else:
                                        try:
                                            if (check_which_matching(n, element_numbering)) == 'last':
                                                repltext = sent_list[-1]
                                            else:  
                                                repltext = sent_list[int(check_which_matching(n, element_numbering))-1]
                                                
                                            if repltext and self.amend_text:
                                                node.text = node.text.replace(repltext, self.amend_text)
                                        except (ValueError, IndexError) as error:
                                            pass
                        else:
                            if self.amend_elem == 'edafio':
                                repltext = elem.text
                                try:
                                    if self.dict_path['case']:
                                        repltext = re.findall(r'('+self.dict_path['case'][:-1]+'[).]\s[Α-Ω-α-ω-0-9].*?(?=\n[α-ω][).]\s|$))'.decode('utf-8'), repltext, re.DOTALL)[0]
                                        
                                    if self.dict_path['subcase']:
                                        repltext = re.findall(r'('+self.dict_path['subcase'][:-1]+'[).]\s[Α-Ω-α-ω-0-9].*?(?=\n\S{2}[).]\s|$))'.decode('utf-8'), repltext, re.DOTALL)[0]

                                    sent_list = sent_tokenizer.tokenize(repltext)
                                    for n in count_elements:
                                        start_teleia = re.search(r'^\S{2}[.]\s', repltext, re.DOTALL)

                                        if start_teleia:
                                            repltext = sent_list[int(check_which_matching(n, element_numbering))]
                                            if repltext and self.amend_text:
                                                elem.text = elem.text.replace(repltext, self.amend_text)
                                        else:
                                            repltext = sent_list[int(check_which_matching(n, element_numbering))-1]
                                            if repltext and self.amend_text:
                                                elem.text = elem.text.replace(repltext, self.amend_text)
                                except IndexError:
                                    pass

                            elif self.amend_elem == 'subcase':
                                repltext = elem.text
                            
                                try:
                                    if self.dict_path['case']:
                                        repltext = re.findall(r'('+self.dict_path['case'][:-1]+'[).]\s[Α-Ω-α-ω-0-9].*?(?=\n[α-ω][).]\s|$))'.decode('utf-8'), repltext, re.DOTALL)[0]
                                    
                                    for n in count_elements:
                                        if re.search(r'[(]', n, re.DOTALL):
                                            n = n[1:-1]
                                        else:
                                            n = n[:-1]

                                        repltext_ = re.findall(r'('+n+'[).]\s[Α-Ω-α-ω-0-9].*?(?=\n\S{2}[).]\s|$))'.decode('utf-8'), repltext, re.DOTALL)[0]
                                        instext = re.findall(r'('+n+'[).]\s[Α-Ω-α-ω-0-9].*?(?=\n\S{2}[).]\s|$))'.decode('utf-8'), self.amend_text, re.DOTALL)[0]
                                    
                                        if repltext_ and instext:
                                            elem.text = elem.text.replace(repltext_, instext)
                                except IndexError:
                                        pass
                                

                #Create a new ElementTree instance and store it to XML file
                newtree = etree.ElementTree(rootnode)
                newtree.write(os.path.join(xml_laws_repo, law_in_src), pretty_print=True, encoding="UTF-8", xml_declaration =True)
                parser = etree.XMLParser(remove_blank_text=True)
                tree = etree.parse(os.path.join(xml_laws_repo, law_in_src), parser)
                tree.write(os.path.join(xml_laws_repo, law_in_src), pretty_print=True, encoding="UTF-8", xml_declaration =True)
                #etree.tostring(rootnode, pretty_print=True, encoding="UTF-8")
                        
    def addition(self, dict_path, ins_elem, amend_text):
        '''
        Method for implementing addition

        Args:
            dict_path: The dictionary for constructing the XML path
            
            ins_elem: The structure element to be inserted

            amend_text: The amendment text that will be inserted
        '''
        
        self.dict_path = dict_path
        self.ins_elem = ins_elem
        self.amend_text = amend_text
    
        #Prepare the amendment text
        if self.amend_text.startswith('\n«'.decode('utf-8')):
            self.amend_text = self.amend_text[2:]
        elif self.amend_text.startswith('«'.decode('utf-8')):
            self.amend_text = self.amend_text[1:]

        if self.amend_text.endswith('.'.decode('utf-8')):
            self.amend_text = self.amend_text[:-2]
        else:
            self.amend_text = self.amend_text[:-1]

        #Construct Law name
        NOMOS = construct_law_name(self.dict_path['type'], self.dict_path['num'], self.dict_path['year'])
        
        if NOMOS:

            law_in_cpfolder = file_in_path(NOMOS, xml_laws_repo)
            law_in_src = file_in_path(NOMOS, src)

            if not law_in_cpfolder:
                if law_in_src:
                    shutil.copy(os.path.join(src, law_in_src), xml_laws_repo)
                else:
                    print ("No such law in folder", file = log)

            if law_in_cpfolder:

                if law_in_cpfolder in cm_laws_msg:
                    pass
                else:
                    cm_laws_msg.append(law_in_cpfolder)
                
                xmltree = etree.parse(os.path.join(xml_laws_repo, law_in_cpfolder))
                rootnode = xmltree.getroot()
                
                func = [
                    ('paragraph', find_paragraphs),('article', find_articles), ('chapter', find_chapters),
                    ('sections', find_sections), ('part', find_parts),
                    ('book', find_books)
                ]
                
                if self.ins_elem in ('paragraph','article', 'chapter', 'book', 'part', 'section'):
                    for k in func:
                        if k[0] == self.ins_elem:
                            elparent = etree.Element(k[0])
                            k[1](self.amend_text.encode('utf-8'), elparent, 1)
                            #print (etree.tostring(elparent, pretty_print=True, encoding="UTF-8"), file = log)
                    
                    for elem1 in elparent.getchildren():
                        #print elem1.get('id')
                        nodeidx_ = elem1.getparent().index(elem1)
                        eltochange = elem1.getparent()[nodeidx_]

                        try:
                            for elem in xmltree.xpath(find_xpath_for_addition(self.dict_path)):
                                if elem.tag != eltochange.tag:
                                    elem.insert(int(eltochange.get('id'))+1, eltochange)
                                    count_child = elem.getchildren()
                                else:
                                    elem.getparent().insert(int(eltochange.get('id'))+1, eltochange)
                                    count_child = elem.getparent().getchildren()
                        except:
                            pass
                    #Renumbering all elements of this parent
                    try:
                        for a in range(1, len(count_child)):
                            if count_child[a].tag not in ('title', 'header'):
                                try:
                                    if int(count_child[a+1].get('id')) != int(count_child[a].get('id')) + 1:
                                        count_child[a+1].set('id', str(int(count_child[a].get('id')) + 1))
                                        upd_num = count_child[a+1].get('id')
                                        count_child[a+1].text = re.sub(r'^(\d+)([.]\s)'.decode('utf-8'), r''+upd_num+'\\2', count_child[a+1].text)
                                except (IndexError, TypeError) as e:
                                    pass
                    except UnboundLocalError:
                        pass

                elif self.ins_elem in ('edafio', 'case', 'subcase', 'stoixeio', 'diataksi', 'phrase', 'words'):
                    ele_list = [('edafio', self.dict_path['edafio']), ('diataksi', self.dict_path['diataksi']),
                                ('case', self.dict_path['case']), ('subcase', self.dict_path['subcase']), ('stoixeio', self.dict_path['stoixeio'])]
                    elinpara = check_elinpar(ele_list, self.dict_path)

                    for elem in xmltree.xpath(find_xpath(self.dict_path, 0, self.ins_elem)):
                        if not elinpara:
                            if self.ins_elem == 'case' or self.ins_elem == 'stoixeio':
                                if elem.getchildren():
                                    for child in elem.getchildren():
                                        if child.tag != "header":
                                            child.text = child.text+"\n"+self.amend_text
                                else:
                                    elem.text = elem.text+"\n"+self.amend_text

                            else:
                                if elem.getchildren():
                                    for child in elem.getchildren():
                                        try:
                                            if child.tag != "header":
                                                sent_list = sent_tokenizer.tokenize(child.text)
                                        except TypeError:
                                            pass
                                else:     
                                    try:
                                        sent_list = sent_tokenizer.tokenize(elem.text)
                                    except TypeError:
                                        pass

                                if self.ins_elem == 'edafio':
                                    sent_list.insert((len(sent_list)+1), "\n" + self.amend_text)
                                elif self.ins_elem == 'words':
                                    sent_list[len(sent_list)-1] = sent_list[len(sent_list)-1].replace('.', '')
                                    sent_list.insert((len(sent_list)+1), "" + self.amend_text)
                                elif self.ins_elem == 'phrase':
                                    sent_list.insert((len(sent_list)+1), "\n" + self.amend_text)

                                if elem.getchildren():
                                    child.text = " ".join(sent_list)
                                else:
                                    elem.text = " ".join(sent_list)
                            
                        elif (elinpara and len(elinpara) == 1):
                            numpar = re.search(r'^\d+[.]\s', elem.text, re.DOTALL) 
                            sent_list = sent_tokenizer.tokenize(elem.text)

                            if self.dict_path['edafio']:
                                if self.ins_elem == 'edafio':
                                    if numpar:
                                        try:
                                            sent_list.insert(int(elinpara[0][1]) + 1, self.amend_text)
                                        except ValueError:
                                            pass
                                    else:
                                        sent_list.insert(int(elinpara[0][1]), self.amend_text)

                                elif self.ins_elem == 'phrase':
                                    if numpar:
                                        try:
                                            sent_list.insert(int(elinpara[0][1]) + 1, self.amend_text)
                                        except ValueError:
                                            pass
                                    else:
                                        sent_list.insert(int(elinpara[0][1]), self.amend_text)

                                elif self.ins_elem == 'stoixeio':
                                    if numpar:
                                        sent_list.insert(int(elinpara[0][1]) + 1, self.amend_text)
                                    else:
                                        sent_list.insert(int(elinpara[0][1]), self.amend_text)

                                elem.text = " ".join(sent_list)

                            elif self.dict_path['case']:
                                try:
                                    repltext = re.findall(r'('+self.dict_path['case'][:-1]+'[).]\s[Α-Ω-α-ω-0-9].*?(?=\n[α-ω][).]\s|$))'.decode('utf-8'), elem.text, re.DOTALL)[0]
                                    instext = "\n".join([repltext, self.amend_text])
                                    elem.text = elem.text.replace(repltext, instext)
                                except IndexError:
                                    pass
                        else:
                            pass


                #Create a new elementtree instance and store it to XML file
                newtree = etree.ElementTree(rootnode)
                newtree.write(os.path.join(xml_laws_repo, law_in_src), pretty_print=True, encoding="UTF-8", xml_declaration =True)
                parser = etree.XMLParser(remove_blank_text=True)
                tree = etree.parse(os.path.join(xml_laws_repo, law_in_src), parser)
                tree.write(os.path.join(xml_laws_repo, law_in_src), pretty_print=True, encoding="UTF-8", xml_declaration =True)
                #etree.tostring(rootnode, pretty_print=True, encoding="UTF-8")
                            
    def repeal(self, dict_path, del_elem):
        '''
        Method for implementing repeal

        Args:
            dict_path: The dictionary for constructing the XML path
            
            del_elem: The element to be removed
        '''
        
        self.dict_path = dict_path
        self.del_elem = del_elem
        
        count_elements = [] 

        #Construct Law name
        NOMOS = construct_law_name(self.dict_path['type'], self.dict_path['num'], self.dict_path['year'])
        if NOMOS:
            try:
                if self.dict_path[self.del_elem] != '' and re.search(r'έως'.decode('utf-8'), self.dict_path[self.del_elem], re.DOTALL):
                    rm = re.sub(r'και\s'.decode('utf-8'), r'', self.dict_path[self.del_elem], re.DOTALL)      
                    split = rm.split('έως'.decode('utf-8'))
            
                    for n in range(int(split[0].strip()), int(split[1].strip()) + 1):
                        count_elements.append(str(n).decode('UTF-8'))
                else:  
                    split = self.dict_path[self.del_elem].split('και'.decode('utf-8'))
            
                    if len(split) > 1:
                        if split[0]:
                            split_ = split[0].split(',')
                            if split_:
                                for n in range(0, len(split_)):
                                    count_elements.append(split_[n].strip())
                        if split[1]:
                            count_elements.append(split[1].strip())
                    else:
                        count_elements.append(split[0].strip())
            except UnicodeEncodeError, KeyError:
                pass
            
            law_in_cpfolder = file_in_path(NOMOS, xml_laws_repo)
            law_in_src = file_in_path(NOMOS, src)

            if not law_in_cpfolder:
                if law_in_src:
                    shutil.copy(os.path.join(src, law_in_src), xml_laws_repo)
                else:
                    print ("No such law in folder", file = log)

            if law_in_cpfolder:
                
                if law_in_cpfolder in cm_laws_msg:
                    pass
                else:
                    cm_laws_msg.append(law_in_cpfolder)
                
                xmltree = etree.parse(os.path.join(xml_laws_repo, law_in_cpfolder))
                rootnode = xmltree.getroot()
                
                if self.del_elem in ('paragraph','article', 'chapter', 'book', 'part', 'section'):
                    for n in count_elements:
                        try:    
                            for elem in xmltree.xpath(find_xpath(self.dict_path, n, self.del_elem)):
                                parent = elem.getparent()
                                elem.getparent().remove(elem)

                                count_child = parent.getchildren()
                    
                                for a in range(1, len(count_child)):
                                    if count_child[a].tag not in ('title', 'header'):
                                        try:
                                            if int(count_child[a+1].get('id')) != int(count_child[a].get('id')) + 1:
                                                count_child[a+1].set('id', str(int(count_child[a].get('id')) + 1))
                                                upd_num = count_child[a+1].get('id')
                                                count_child[a+1].text = re.sub(r'^(\d+)([.]\s)'.decode('utf-8'), r''+upd_num+'\\2', count_child[a+1].text)
                                        except (IndexError, TypeError) as e:
                                            pass 
                        except UnboundLocalError:
                            pass
                else:
                    pass
                
                
                newtree = etree.ElementTree(rootnode)
                newtree.write(os.path.join(xml_laws_repo, law_in_src), pretty_print=True, encoding="UTF-8", xml_declaration =True)
                parser = etree.XMLParser(remove_blank_text=True)
                tree = etree.parse(os.path.join(xml_laws_repo, law_in_src), parser)
                tree.write(os.path.join(xml_laws_repo, law_in_src), pretty_print=True, encoding="UTF-8", xml_declaration =True)
                #etree.tostring(rootnode, pretty_print=True, encoding="UTF-8")


if __name__ == "__main__":

    f = open("greek.pickle")
    sent_tokenizer = pickle.load(f)
    f.close()

    ord_files = []
    log = open(os.path.join(xml_laws_repo, "amendments_log.txt"), "a")
    for root, dirs, files in os.walk(src):
        
        #Laws sorting
        for name in files:
            if name.endswith('.xml'):
                ord_files.append(int(name.split("_")[1]))

        ord_files.sort(key=int)

        for num in ord_files:
            if num > 0:
                law = file_in_path("ΝΟΜΟΣ_"+str(num)+"_\d+_A_\d+", src)
                
                #Commit message
                cm_laws_msg = []

                print(law+"\n", file = log)

                with open (os.path.join(root, law + ".xml"), "r") as fin:
                    doc = etree.parse(fin)
                    #print ("Number of Amendments: "+str(len(doc.findall('.//mod')))+"\n", file = log)
                    
                    for elem in doc.findall('.//mod'):
                        #if elem.get('id') == '2':
                        elem_mod = amendments(elem)
                        
                        #If paragraph is written in cases
                        if elem_mod.check_if_cases():
                            cases = elem_mod.split_cases()
                            for n in range(0, len(cases)):
                                match_pattern = elem_mod.find_mod_pattern(cases[n][0])
                                
                                if match_pattern:
                                    path = elem_mod.analyze_amendment(cases[n][0], match_pattern[0], match_pattern[1])
                                    if path:
                                        if path[1].encode('utf-8') == 'substitute':
                                            elem_mod.substitute(path[0], path[2], path[3], path[4])

                                        elif path[1].encode('utf-8') == 'addition':
                                            elem_mod.addition(path[0], path[2], path[3])

                                        elif path[1].encode('utf-8') == 'repeal':
                                            elem_mod.repeal(path[0], path[2])

                                        elif path[1].encode('utf-8') == 'renumbering':
                                            elem_mod.renumbering()

                                    else:
                                        pass
                                        #print ("No amandment verb found!", file = log)     
                                else:
                                    pass
                        else:
                            match_pattern = elem_mod.find_mod_pattern(elem_mod.text)
                           
                            if match_pattern:
                                path = elem_mod.analyze_amendment(elem_mod.text, match_pattern[0], match_pattern[1])
                                if path:
                                    if path[1].encode('utf-8') == 'substitute':
                                        elem_mod.substitute(path[0], path[2], path[3], path[4])
                                    
                                    elif path[1].encode('utf-8') == 'addition':
                                        elem_mod.addition(path[0], path[2], path[3])

                                    elif path[1].encode('utf-8') == 'repeal':
                                        elem_mod.repeal(path[0], path[2])

                                    elif path[1].encode('utf-8') == 'renumbering':
                                        elem_mod.renumbering()

                                else:
                                    #print ("No amandment verb found!", file = log)
                                    pass
                                #print ("--------------------------------------------------------------------------------------------------\n\n", file = log)
                                
                            #Διαφορετικά προσπέρνα
                            else:
                                pass

                shutil.copy(os.path.join(src, law + ".xml"), xml_laws_repo)
                message = "Μεταφόρτωση του νόμου: " + law + "\n"

                if len(cm_laws_msg) > 0:
                    message = message + "Τροποποίηση των νόμων: "
                    for n in cm_laws_msg:
                        message = message + n[:-4] + " "
                #print message
                os.chdir( '../xml_laws_repo/' )

                #print os.getcwd()
                subprocess.call("git add --all", shell=True)
                subprocess.call(["git", "commit", "-m", message])


                txt = XMLtoXHTML(os.path.join(xml_laws_repo, law + ".xml"), os.path.join(xls_src, 'laws.xsl'))
                with open (os.path.join(text_laws_repo, law + ".txt"), "w") as fin:
                    fin.write(str(txt))

                message = "Μεταφόρτωση του νόμου: " + law + "\n"

                if len(cm_laws_msg) > 0:
                    message = message + "Τροποποίηση των νόμων: "
                    for n in cm_laws_msg:
                        txt = XMLtoXHTML(os.path.join(xml_laws_repo, n), os.path.join(xls_src, 'laws.xsl'))
                        with open (os.path.join(text_laws_repo, n[:-4] + ".txt"), "w") as fin:
                            fin.write(str(txt))

                        message = message + n[:-4] + " "
                    
                #print message
                os.chdir( '../text_laws_repo/' )

                subprocess.call("git add --all", shell=True)
                subprocess.call(["git", "commit", "-m", message])
                
