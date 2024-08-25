# Script to build dist/bdqcore_tests_vertical.csv from vocabulary/bdqcore_terms.csv
#
# @author Paul J. Morris 
#
# Assumes run from tg2/_review/build directory.
#
import pandas
import re
import sys
with open ("../vocabulary/bdqcore_terms.csv") as csvfile: 
	try: 
		sys.stdout = open("../dist/bdqcore_tests_vertical.csv","w")
		# Header
		# "#","GUID","DateLastUpdated","Label","prefLabel","IE Class","InformationElement:ActedUpon","InformationElement:Consulted","Parameters","Specification","Description","Criterion Label","Type","Resource Type","Dimension","Examples","Source","References","Example Implementations (Mechanisms)","Link to Specification Source Code","Notes","IssueState","IssueLabels","UseCases"
		rawDataFrame = pandas.read_csv(csvfile)
		dataFrame = rawDataFrame.sort_values(by=['Type','IE Class', 'Label'],ascending=[False,True,True])
		# header
		print('"Label","prefLabel","qualifiedName"');
		for index, row in dataFrame.iterrows():
			print('"{}","{}","bdqcore:{}"'.format(row['Label'],row['prefLabel'],row['GUID']))
	except pandas.errors.ParserError as e:
		sys.exit("Error reading file: {}".format(e)) 
