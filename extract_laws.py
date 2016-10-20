# -*- coding: utf-8 -*-
import os
import glob
import re
import shutil

'''
This is STEP 3 of the system implemantation. All PDF files that have been
transformed to texts may contain different types of legislative texts (e.g.
laws, presidential decrees, ministerial decisions etc.).

Distinguishing laws is based on regular expressions by identifying the text
patterns that flag the existence of a law.
'''

#This is the folder of text files from step 2
src = 'path/to/laws/texts/'

#A user defined folder for storing the isolated Laws
text_dest = 'path/to/destination/'

#Create the correspondig directory according to the type of the law
#Laws
if not os.path.exists(os.path.join(text_dest,'nomoi')):
    os.makedirs(os.path.join(text_dest,'nomoi'))

#Presidential decrees
if not os.path.exists(os.path.join(text_dest, 'pd')):
    os.makedirs(os.path.join(text_dest, 'pd'))


def onomasia(datalist):
    eidos = datalist.split()
    numlaw = re.findall(r'(?=NOMOΣ|ΝΟΜΟΣ|ΝOMOΣ|NOMΟΣ|NOΜΟΣ|NΟΜΟΣ).*?(\d+)', datalist, re.DOTALL)

    if eidos[0] == "ΠΡΟΕΔΡΙΚΟ":
        return eidos[0] + "_" + eidos[1]+ "_" + eidos[4].split("/")[0] 
    elif eidos[0] == "ΠΡΑΞΗ":
        return eidos[0] + "_" + eidos[1]+ "_" + eidos[2]
    else:
        return 'ΝΟΜΟΣ' + "_" + numlaw[0]


def match_nomos(string):
    return re.findall(r'(ΝΟΜΟΣ ΥΠ.*?Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|ΝΟΜΟΣ ΥΠ.*?Ο ΠΡΟΕΔΡΟΣ\nΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|ΝOMOΣ ΥΠ.*?Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|ΝΟΜΟΣ ΥΠ.*?O ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|NOMOΣ ΥΠ.*?Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|NOMOΣ ΥΠ.*?Ο ΠΡΟΕΔΡΟΣ ΤΗ Σ ΔΗΜΟΚΡΑΤΙΑΣ|NOMOΣ ΥΠ.*?Ο ΠΡΟΕΔΡΟΣ\nΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|NOMΟΣ ΥΠ.*?Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|NOΜΟΣ ΥΠ.*?Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|NΟΜΟΣ ΥΠ.*?Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|ΝΟΜΟΣ YΠ.*?Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|NOMOΣ ΥΠ’ ΑΡΙΘ[.].*?Ο ΠΡΟΕ∆ΡΟΣ ΤΗΣ ∆ΗΜΟΚΡΑΤΙΑΣ|ΝΟΜΟΣ ΥΠ’ ΑΡΙΘ[Μ]*[.]*\s\d+.*?Ο ΠΡΟΕ∆ΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ)',string, re.DOTALL)

def match_pd(string):
    return re.findall(r'(ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ’ ΑΡΙΘ[Μ]*[.]\s\d+.*?Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ|ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ´ ΑΡΙΘ[Μ]*[.]\s\d+.*?Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ)',string, re.DOTALL)


#Splits the file into types (laws and presidential decrees)
def write_to_files(datalist):
    for n in range(0, len(datalist)):
        onoma = onomasia(datalist[n]) + "_" + os.path.basename(name)
        with open(onoma, 'w') as fout:
            fout.writelines(datalist[n])
            
            if onoma.split('_')[0] == "ΝΟΜΟΣ":
                shutil.move(os.path.join(os.getcwd(), onoma), os.path.join(text_dest,'nomoi'))
            if onoma.split('_')[0] == "ΠΡΟΕΔΡΙΚΟ":
                shutil.move(os.path.join(os.getcwd(), onoma), os.path.join(text_dest, 'pd'))


rules = (match_nomos, match_pd)

#Divide the file object according to the type of law text in it
def split_into_types(fileobj):
    data = fileobj.read()
    #if a rule matches
    for match_rules in rules:
        if match_rules(data):
            write_to_files(match_rules(data))


if __name__ == "__main__":
    #Traverse all text file in src
    for root, dirs, files in os.walk(src, topdown=False):
        for name in files:
            if name.endswith('.txt'):
                with open(os.path.join(root, name), "r") as fin:
                    split_into_types(fin)
