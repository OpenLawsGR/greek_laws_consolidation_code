# -*- coding: utf-8 -*-
import os
import re
import glob
import subprocess
from datetime import datetime
import shutil

'''
This is STEP 2 of the architecture of the semi-automatic system for the
consolidation of Greek legislation. All files that are mentioned here
have been downloaded with Scrapy according to the instructions found
here: https//github.com/OpenLawsGR/ultraclarity-crawler

PDF files are not machine readable so it is important to transform them
in plain text format in order to start their analysis using natural language
processing techniques.
'''

now = datetime.now()

#The location of the PDF files that contains Laws
src = '/path/to/files/'

#The destination of the text files (This is a user defined folder where
#text files will be stored to subfolders according to their year of publication)
text_dest = '/path/to/destination/'

#PDF files between 2000-2005 provide no encoding information
#so this file is necessary for character mapping
#rules_file = '/path/to/characters/replacement/file'
rules_file = 'replacements.txt'

def replace_all(text, dic):
    '''
    Replaces the characters of a text according to a dictionary

    Args:
        text: The text that the function will replace wrong characters

        dic: A dictionary with key, value pairs of characters
             key -> the old characters that will be replaced
             values-> the new characters that will be inserted
    '''
    for key, value in dic.iteritems():
        text = text.replace(key, value)
    return text


if __name__ == '__main__':
    #Create a rule dictionary based on rules_file
    rules={}
    with open (rules_file, "r") as file:
        for line in file:
            rules_list = line.split('=')
            rules[rules_list[0]] = re.sub(r'\n$', '', rules_list[1])

    #Transform PDF files to text
    for root, dirs, files in os.walk(src, topdown=False):
        for name in files:
            subprocess.call(["pdftotext", "-raw", os.path.join(root,name)])

    #Organize each text file according to its year of publication
    for root, dirs, files in os.walk(src, topdown=False):
        for name in files:
            if name.endswith('.txt'):
                year = name.split("_")[2].replace('.txt', '')
                
                if not os.path.exists(os.path.join(text_dest, year)):
                    os.makedirs(os.path.join(text_dest, year))

                shutil.move(os.path.join(root,name), os.path.join(text_dest, year))

    #Files between 2000-2005 have wrong character encoding
    for n in range(2000, 2006):
        filename = glob.glob(os.path.join(text_dest, str(n)+'/*'))
        for name in filename:
           if name.endswith('.txt'):
               with open(name+"_pre_", "wt") as fout:
                    with open(name, "r") as fin:
                        mytext = fin.read()
                        txt = replace_all(mytext, rules)
                        fout.write(txt)
                        os.remove(name)
                        os.rename(name+"_pre_", name)
