# greek_laws_consolidation_code
This folder contains all the code for implementing a semi-automatic system for the consolidation of Greek legislative texts. It is divided up to modules executing one step at a time of the architecture described at [Openlaws](http://www.openlaws.gr/legislation/2016/10/17/revised-architecture/).

To be able to use all the modules the user must have downloaded all PDF files of the Official Gazzette as described in ultraclarity-spider.

## Dependencies
Many modules depend on Python's lxml API (see [lxml](http://lxml.de/tutorial.html)) and Natural Language Toolkit ([nltk](http://www.nltk.org/api/nltk.html) mostly on steps 5 and 6 as described below.

## STEP 1
see tutorial of ultraclarity-crawler [here](https://github.com/OpenLawsGR/ultraclarity-crawler)

## STEP 2
As Law documents are published in PDF format there is the need to transform them in a format that can easily be processed. An open sourve utility named 'pdftotext' is being used to transform PDF files to plain text documents. This utility has several problems when it is used in PDF files, usually published before 2004 due to scanned images

## STEP 3

## STEP 4

## STEP 5

## STEP 6 and 7


