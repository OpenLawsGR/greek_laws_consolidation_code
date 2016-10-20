# -*- coding: utf-8 -*-
import os
import glob
import re
import shutil

'''
This is STEP 4 of the system architecture. In Greek laws considerable number
of text consists of international agreements. These types of text are usually
incorporated in scanned images, or contain english text so they usually do
not attract attention from citizens and should be excluded

Moreover, law text preprocessing corrects several errors, either present in the
PDF files or produced during previous steps
'''

#Folder that contains all laws from step 3
src = 'path/to/laws/folder/'

#Destination folder 
text_dest = '/path/to/destination/'


if not os.path.exists(os.path.join(text_dest,'nomoi')):
    os.makedirs(os.path.join(text_dest,'nomoi'))

if not os.path.exists(os.path.join(text_dest,'int_agreement')):
    os.makedirs(os.path.join(text_dest,'int_agreement'))

if not os.path.exists(os.path.join(text_dest,'laws_after_processing')):
    os.makedirs(os.path.join(text_dest,'laws_after_processing'))


def subs_text(text, dic):
    for n in range(0,len(dic)):
        text = re.sub(dic[n][0], dic[n][1], text, flags=re.DOTALL)
    return text

#Some data inside text files provide no legal information (garbages) so create rules to remove them
rules=[(r'^.*?(?=\d+)','ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. '),
       (r'Digitally signed by.*?Verified',''),
       (r'ΦΕΚ\s\d+\sΕΦΗΜΕΡΙΣ ΤΗΣ ΚΥΒΕΡΝΗΣΕΩΣ \(ΤΕΥΧΟΣ ΠΡΩΤΟ\)\s\d+\n',''),
       (r'\d+\sΕΦΗΜΕΡΙΣ ΤΗΣ ΚΥΒΕΡΝΗΣΕΩΣ \(ΤΕΥΧΟΣ ΠΡΩΤΟ\)\n\s|\d+\sΕΦΗΜΕΡΙΣ ΤΗΣ ΚΥΒΕΡΝΗΣΕΩΣ \(ΤΕΥΧΟΣ ΠΡΩΤΟ\)\n',''),
       (r'ΕΦΗΜΕΡΙΣ ΤΗΣ ΚΥΒΕΡΝΗΣΕΩΣ \(ΤΕΥΧΟΣ ΠΡΩΤΟ\)\s\d+\n\s|ΕΦΗΜΕΡΙΣ ΤΗΣ ΚΥΒΕΡΝΗΣΕΩΣ \(ΤΕΥΧΟΣ ΠΡΩΤΟ\)\s\d+\n',''),
       #(r'\n\d+\n\s',''),
       (r'Φ.Ε.Κ. \d+ ', r''),
       (r'º','Ι'),
       (r'\n\d+\n','\n'),
       (r'[\*]\d+[\*]\n',''),
       (r'\n(\s+)','\n'),
       (r'-\n(\S+)\s+', r'\1\n'),
       (r'-\n(\S+)\s+', r'\1\n'), #other symbol of dehyphenation 
       (r'−\n(\S+)\s+', r'\1\n'), #again other symbol 
       (r'−\n(S+)\s+', r'\1\n'), #again same problem (copy-paste from file)
       (r'΄Αρθρο', r'Άρθρο'),
       (r'Αρθρο', r'Άρθρο'),
       (r'Το παρόν ΦΕΚ.*?κυκλοφορούντος ταυταρίθμου[.]\n', r''),
       (r'(Άρθρο\s\d+)([:] )', r'\1\n'),
       (r'(\n[«]*\d+[.])([^ 0-9])', r'\1 \2'),
       (r'(\n[«]*\d+[.] )(α[.]|α[)]|Α[.]|Α[)])(\S)', r'\1\2 \3')
    ]


if __name__ == "__main__":
    for root, dirs, files in os.walk(src, topdown=False):
        for name in files:
            if name.endswith('.txt'):
                with open(os.path.join(root, name), "r") as fin:
                    data = fin.read()

                    abstract = re.findall(r'^.*?Ο ΠΡΟΕΔΡΟΣ|^.*?O ΠΡΟΕΔΡΟΣ', data, re.DOTALL)
                    
                    if abstract:
                        new_abstract = re.sub(r'^.*?(?=\d+)','ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. ', abstract[0])
                        validation = re.search(r'^ΝΟΜΟΣ ΥΠ\' ΑΡΙΘ. \d+[.]*\n(Κύρωση|Kύρωση|Μνημόνιο Κατανόησης|Συμφωνία των Αντιπροσώπων των Κρατών−Μελών)', new_abstract, re.DOTALL)
                    
                        not_validation = re.search(r'(?<!Τελικής\s)Πράξης|Κώδικα|Κωδικοποίησης|κωδικοποίησης|πράξης νομοθετικού|Πράξεως Νοµοθετικού',new_abstract, re.DOTALL)
                        if validation:
                            if not not_validation:
                                shutil.copy(os.path.join(root, name), os.path.join(text_dest,'int_agreement'))
                            else:
                                shutil.copy(os.path.join(root, name), os.path.join(text_dest,'nomoi'))
                        else:
                            shutil.copy(os.path.join(root, name), os.path.join(text_dest,'nomoi'))
                    else:
                        print("No abstract in law")


    for root, dirs, files in os.walk(os.path.join(text_dest,'nomoi'), topdown=False):
        for name in files:
            if name.endswith('.txt'):
                with open(os.path.join(os.path.join(text_dest,'laws_after_processing'),name), "wt") as fout:
                    with open(os.path.join(root, name), "r") as fin:
                        data = fin.read()
                        txt = subs_text(data, rules)
                        fout.write(txt)
