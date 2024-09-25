# Produce markdown document listing tests from 
# intermediate csv list of tests TG2_tests.csv 
# and TG2_multirecord_measure_tests.csv
#
# @author Paul J. Morris 
#
# Assumes run from generation/build directory of tg2 repository.
#
# TODO; Include header/footer templates.
#
# Quick reference shows only: 
# prefLabel
# Label	
# Resource Type
# GUID	
# DateLastUpdated	
# Description
# InformationElement:ActedUpon
# InformationElement:Consulted	
# Specification
# Parameters
# Examples	
# UseCases
# Notes
#
import pandas	# provides data frames
import re		# regular expression library
import sys		# input/output
import yaml		# Library to parse yaml files
# To copy files from build/templates/ to /docs/
import glob
import shutil

# Configuration 

# Vocabulary file
inputTermsCsvFilename = "../vocabulary/bdqcore_terms.csv"
# output file 
outputDirectory = "../docs/terms/bdqcore/"
outputFilename = "{}index.md".format(outputDirectory)
outputUseCaseIndexFilename = "../docs/terms/bdqcore/qrg_index_by_usecase.md"
outputInformationElementIndexFilename = "../docs/terms/bdqcore/qrg_index_by_ie_actedupon.md"
# Files for header/footer
contributors_yaml_file = 'authors_configuration.yaml'
term_list_document = "temp_term-lists.csv"
local_metadata_config_file = 'temp_namespaces.yaml'
sourceDirectory = 'templates/terms/bdqcore_qrg/'
headerFileName = '{}bdqcore_quickreference-header.md'.format(sourceDirectory)
footerFileName = '{}bdqcore_quickreference-footer.md'.format(sourceDirectory)
document_configuration_yaml_file = '{}/document_configuration.yaml'.format(sourceDirectory)

has_namespace = True
namespace_uri = 'https://rs.tdwg.org/bdqcore'
pref_namespace_prefix = "bdqcore"

# Setup for header/footer templates

# Load the contributors YAML file from its local location.
with open(contributors_yaml_file) as cyf:
	contributors_yaml = yaml.load(cyf, Loader=yaml.FullLoader)

with open ("../vocabulary/bdq_term_versions.csv") as vocabfile: 
	try: 
		vocabDataFrame = pandas.read_csv(vocabfile);
	except pandas.errors.ParserError as e:
		sys.exit("Error reading bdq vocabulary csv file: {}".format(e)) 

with open (inputTermsCsvFilename, newline='') as csvfile:
	sys.stdout = open(outputFilename,"w")
	outputUseCaseIndex = open(outputUseCaseIndexFilename,"w")
	outputInformationElementIndex = open(outputInformationElementIndexFilename,"w")
	rawDataFrame = pandas.read_csv(csvfile)
	dataFrame = rawDataFrame.sort_values(by=['Type','IE Class', 'Label'],ascending=[False,True,True])
	# Filter out multirecord mesures into one data frame
	multirecordDataFrame = dataFrame[dataFrame['Label'].str.startswith('MULTIRECORD_MEASURE',na=False)]
	multirecordheader_names = list(multirecordDataFrame.columns)
	# Exclude multirecord measures from dataFrame, limit to singe record tests
	dataFrame = dataFrame[~dataFrame['Label'].str.startswith('MULTIRECORD_MEASURE',na=False)]
	header_names = list(dataFrame.columns)
	try: 
		# Load header, replace fields

		# Load the document configuration YAML file from its local location.  For a draft standard, database is not available from rs.tdwg.org
		# load from local file
		with open(document_configuration_yaml_file) as dcfy:
			document_configuration_yaml = yaml.load(dcfy, Loader=yaml.FullLoader)

		## Produce a table of contents from the headings 
		toc = ""
		regexHeadings = "^#+ [0-9]+.*"
		with open(headerFileName) as headerFile:
			separator = ""
			for line in headerFile:
				aHeading = re.search(regexHeadings,line)
				if (aHeading) : 
					headingText = aHeading.group().replace("#","")
					headingAnchor = headingText.replace(" ","-").lower().replace(".","").replace(":","")[1:]
					toc = toc + separator + "- [" + aHeading.group().replace("#","") + "](#" + headingAnchor + ")"
					separator = "\n"
			headerFile.close()
	
		# read in header and footer, merge with terms table, and output
		headerObject = open(headerFileName, 'rt', encoding='utf-8')
		header = headerObject.read()
		headerObject.close()
		
		text = ""
	
		# Build the Markdown for the contributors list
		contributors = ''
		separator = ''
		for contributor in contributors_yaml:
			if contributor['contributor_iri'] :
				contributors += separator + '[' + contributor['contributor_literal'] + '](' + contributor['contributor_iri'] + ') '
			else : 
				contributors += separator + contributor['contributor_literal'] + ' '
			if contributor['affiliation'] :
				if contributor['affiliation_uri'] :
					contributors += '([' + contributor['affiliation'] + '](' + contributor['affiliation_uri'] + '))'
				else :
					contributors += '(' + contributor['affiliation'] + ')'
			separator = ", "
		
		# Substitute values of ratification_date and contributors into the header template
		header = header.replace('{document_title}', document_configuration_yaml['documentTitle'])
		header = header.replace('{ratification_date}', document_configuration_yaml['doc_modified'])
		header = header.replace('{created_date}', document_configuration_yaml['doc_created'])
		header = header.replace('{contributors}', contributors)
		header = header.replace('{standard_iri}', document_configuration_yaml['dcterms_isPartOf'])
		header = header.replace('{current_iri}', document_configuration_yaml['current_iri'])
		header = header.replace('{abstract}', document_configuration_yaml['abstract'])
		header = header.replace('{creator}', document_configuration_yaml['creator'])
		header = header.replace('{publisher}', document_configuration_yaml['publisher'])
		header = header.replace('{comment}', document_configuration_yaml['comment'])
		header = header.replace('{toc}','\n{}'.format(toc))
		year = document_configuration_yaml['doc_modified'].split('-')[0]
		header = header.replace('{year}', year)
		if has_namespace:
			header = header.replace('{namespace_uri}', namespace_uri)
			header = header.replace('{pref_namespace_prefix}', pref_namespace_prefix)
	
		warning = "<!--- This file is generated from templates by code, DO NOT EDIT by hand --->\n"
		print(warning)
		print(header)
		print()
		# Index by UseCase
		usecaseDict = dict()
		for index, row in dataFrame.iterrows():
			usecasesTerm = str(row["UseCases"])
			test = row['Label']
			foundUseCases = [val.strip() for val in usecasesTerm.split(',')]
			for useCase in foundUseCases: 
				usecaseDict.setdefault(useCase,[]).append(test)
		outputUseCaseIndex.write("# UseCase Index to the {}\n".format(document_configuration_yaml['documentTitle']))
		outputUseCaseIndex.write("\n")
		outputUseCaseIndex.write("Title\n")
		outputUseCaseIndex.write(": Terms used in the {}\n".format(document_configuration_yaml['documentTitle']))
		outputUseCaseIndex.write("\n")
		outputUseCaseIndex.write("Part of the [{}](index.md)\n".format(document_configuration_yaml['documentTitle']))
		outputUseCaseIndex.write("\n")
		outputUseCaseIndex.write("## Index of Tests by UseCase\n")
		for useCase in usecaseDict.keys(): 
			outputUseCaseIndex.write("## "+useCase)
			outputUseCaseIndex.write("\n")
			definitionRow = vocabDataFrame.loc["bdq:"+vocabDataFrame["term_localName"]==useCase]
			try: 
				definitionCell = definitionRow.iloc[0]["definition"]
				outputUseCaseIndex.write(definitionCell)
				outputUseCaseIndex.write("\n")
			except: 
				outputUseCaseIndex.write("error extracting definition\n")
			outputUseCaseIndex.write("\n")
			for test in usecaseDict[useCase]:
				outputUseCaseIndex.write("- [" + test + "](index.md#" + test +")\n")
			outputUseCaseIndex.write("\n\n")
		# Index by information element
		informationelementDict = dict()
		for index, row in dataFrame.iterrows():
			informationelementsTerm = str(row['InformationElement:ActedUpon'])
			test = row['Label']
			foundInformationElements = [val.strip() for val in informationelementsTerm.split(',')]
			for useCase in foundInformationElements: 
				informationelementDict.setdefault(useCase,[]).append(test)
		outputInformationElementIndex.write("# InformationElement ActedUpon Index to the {}\n".format(document_configuration_yaml['documentTitle']))
		outputInformationElementIndex.write("\n")
		outputInformationElementIndex.write("Title\n")
		outputInformationElementIndex.write(": Terms used in the {}\n".format(document_configuration_yaml['documentTitle']))
		outputInformationElementIndex.write("\n")
		outputInformationElementIndex.write("Part of the [{}](index.md)\n".format(document_configuration_yaml['documentTitle']))
		outputInformationElementIndex.write("\n")
		outputInformationElementIndex.write("## Index of Tests by InformationElement ActedUpon\n")
		for useCase in informationelementDict.keys(): 
			outputInformationElementIndex.write("## "+useCase)
			outputInformationElementIndex.write("\n")
			definitionRow = vocabDataFrame.loc["bdq:"+vocabDataFrame["term_localName"]==useCase]
			try: 
				definitionCell = definitionRow.iloc[0]["definition"]
				outputInformationElementIndex.write(definitionCell)
				outputInformationElementIndex.write("\n")
			except: 
				outputInformationElementIndex.write("error extracting definition\n")
			outputInformationElementIndex.write("\n")
			for test in informationelementDict[useCase]:
				outputInformationElementIndex.write("- [" + test + "](index.md#" + test +")\n")
			outputInformationElementIndex.write("\n\n")
		#
		# Base alphabetical index.
		for index, row in dataFrame.sort_values('Label').iterrows():
			print("- [{}](#{})".format(row['Label'],row['Label']))
		print()
		print("********************")
		print()
		print("# 3 The BDQ Core Tests")
		print()
		print("## 3.1 Validations, Amendments, Measures operating on SingleRecords.")
		print()
		for index, row in dataFrame.iterrows():
			print("### ",row['Label'])
			print()
			print("#### ",row['prefLabel'])
			print("https://rs.tdwg.org/bdqcore/terms/{}/{}".format(row['GUID'],row['DateLastUpdated']))
			print("Acts upon ",row['Resource Type'])
			print()
			print("#### Description")
			print()
			print(row['Description'])
			print()
			print("#### Specification")
			print()
			print(row['Specification'])
			print()
			print("#### Information Elements")
			if not pandas.isna(row['InformationElement:ActedUpon']) : 
				print()
				print("Acted Upon: ")
				print(row['InformationElement:ActedUpon'])
				print()
			if not pandas.isna(row['InformationElement:Consulted']) : 
				print("Consulted: ")
				print(row['InformationElement:Consulted'])
				print()
			if not pandas.isna(row['Parameters']) : 
				print("#### Parameters")
				print()
				print(row['Parameters'])
				print()
			if not pandas.isna(row['AuthoritiesDefaults']) : 
				print("#### Default Parameter Values")
				print()
				print(row['AuthoritiesDefaults'])
				print()
			print("#### Examples")
			print()
			examplesRaw = row['Examples']
			# examples are paired in the form [key:value response:value],[key:value response:value]
			# display as two lines without the enclosing square brackets.
			examples = [val.strip() for val in examplesRaw.split('],[')]
			for example in examples: 
				print(re.sub("\]$","",re.sub("^\[","",example)))
				print()
			print()
			print("#### Use Cases")
			print()
			print(row['UseCases'])
			print()
			if not pandas.isna(row['Notes']) : 
				print("#### Notes")
				print()
				print(row['Notes'])
				print()
			print("********************")
			print()
		print()
		print("## 3.2 Measures operating on test Responses for MultiRecords (data sets).")
		print()
		for index, row in multirecordDataFrame.iterrows():
			print("### ",row['Label'])
			print()
			print("#### ",row['prefLabel'])
			print("https://rs.tdwg.org/bdqcore/terms/{}/{}".format(row['GUID'],row['DateLastUpdated']))
			print("Acts upon ",row['Resource Type'])
			print()
			print("#### Description")
			print()
			print(row['Description'])
			print()
			print("#### Specification")
			print()
			print(row['Specification'])
			print()
			print("#### Information Elements")
			if not pandas.isna(row['InformationElement:ActedUpon']) : 
				print()
				print("Acted Upon: ")
				print(row['InformationElement:ActedUpon'])
				print()
			if not pandas.isna(row['InformationElement:Consulted']) : 
				print("Consulted: ")
				print(row['InformationElement:Consulted'])
				print()
			if not pandas.isna(row['Parameters']) : 
				print("#### Parameters")
				print()
				print(row['Parameters'])
				print()
			print("#### Use Cases")
			print()
			print(row['UseCases'])
			print()
			print("#### Notes")
			print()
			print(row['Notes'])
			print()
			print("********************")
			print()
		print()

		# Footer
		footerObject = open(footerFileName, 'rt', encoding='utf-8')
		footer = footerObject.read()
		footerObject.close()
		footer = footer.replace('{license_statement}', document_configuration_yaml['license_statement'])
		footer = footer.replace('{publisher}', document_configuration_yaml['publisher'])
		footer = footer.replace('{license_uri}', document_configuration_yaml['license_uri'])
		footer = footer.replace('{publisher}', document_configuration_yaml['publisher'])
		footer = footer.replace('{creator}', document_configuration_yaml['creator'])
		footer = footer.replace('{year}', year)
		footer = footer.replace('{document_title}', document_configuration_yaml['documentTitle'])
		footer = footer.replace('{current_iri}', document_configuration_yaml['current_iri'])
		footer = footer.replace('{ratification_date}', document_configuration_yaml['doc_modified'])
		print(footer)
	
		# Temporary solution to list of definitions not in quick reference guide.
		# Copy list of definitions file bdqcore_qrg_term_descriptions.md
		for file in glob.glob('{}bdqcore_qrg_term_descriptions.md'.format(sourceDirectory)):
			shutil.copy(file, outputDirectory)

	except pandas.errors.ParserError as e:
		sys.exit("Error reading core test csv file: {}".format(e)) 
