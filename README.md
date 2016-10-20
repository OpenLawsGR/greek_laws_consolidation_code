# greek_laws_consolidation_code
This repository contains the source code in Python of a semi-automatic system for the consolidation of Greek laws. The whole process consists of 7 steps as described at this [OpenlawsGR blog post](http://www.openlaws.gr/legislation/2016/10/17/revised-architecture/). The resulted consolidated laws are currently published at [this repository](https://github.com/OpenLawsGR/greek_laws_alpha)

## Dependencies
This code has been tested with Python 2.7. Many modules depend on Python's lxml API (see [lxml](http://lxml.de/tutorial.html)) and Natural Language Toolkit (see [nltk](http://www.nltk.org/api/nltk.html)). [pdftotext](https://linux.die.net/man/1/pdftotext) is also needed.

## Important Note
**Before each step make sure that src and text_dest variables in the respective .py file are set**

## STEP 1
See the tutorial of ultraclarity-crawler [here](https://github.com/OpenLawsGR/ultraclarity-crawler) for downloading PDF files of the Government Gazzette.

## STEP 2
pdftotext is used to transform PDF files to plain text documents. The utility has several problems when used in PDF files containing scanned images (laws mainly published before 2004).
> python pdfotext.py

## STEP 3
The distinction of laws from other types of legislative texts (e.g. Presidential Decrees) is necessary as our work currently focuses solely on laws. Use extract_laws.py as shown below. However, it is necessary to define the source and destinations folders at the beginning of the python file. To run this module in terminal type:
> python extract_laws.py

## STEP 4
In this step split_laws_international_agreements.py is used to correct several errors, either already present in the PDF files or produced during the previous steps. Moreover international agreements are removed due to containing scanned images and non-Greek text. To run this module in terminal type:
> python split_laws_international_agreements.py

## STEP 5
This step implements structural analysis and produces xml files from the txt files of the laws.
To run this module in terminal type:
> python create_xml_with_mod.py

Before moving to steps 6 and 7 an extra step of Validation and Manual Editing is necessary. Law texts may contain grammar or syntax errors and misprints. Moreover, rules and patterns are not always followed by law makers. All text files that contain valid laws (2004-2015 period) are listed in valid_text_laws.txt.

## STEPS 6 and 7
Use *implement_mod.py* to automatically apply all modifications found in the XML files of the laws. Non-valid xml files are ignored. In this last step the appropriate XSL transformations are applied to the XML files that represent laws revisions in order to generate user friendly text versions of them. Before using this module it is necessary to initialize 2 git repository and declare them at the beginning of the script. 
To run this module in terminal type:
> python implement_mod.py
