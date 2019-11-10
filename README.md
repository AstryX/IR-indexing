# IR-indexing
By Robertas Dereskevicius 2019/10 used for TTDS First Coursework in University of Dundee
The following repository takes a set of documents and computes an inverse term index which is then used to perform boolean querying and ranked IR
The tool uses nltk for word stemming. It must be installed.

The tool is comprised of two scripts:

*textindex.py: This file reads documents that contain ID, Headline and Text. 
It applies selected preprocessing and transforms document collections into inverse term tables.

*textquery.py: This file allows the user to query the generated index table using
either Boolean queries or Ranked IR.

textindex.py is typically run prior to textquery.py

How to use:

textindex.py:
1. Run the script using: "python textindex.py"
2. Type in the collection file name to be indexed.
3. Select preprocessing parameters(1-default, 2-choose)
	3.1 If second option is taken, write 1 if you would like stopwords to be removed and 2 if not.
		3.1.1 If stopwords are removed, type in the stopword file name (default englishST.txt)
	3.2 Type 1 if you would like stemming to be applied, 2 if not.
4. Wait for a short while for the documents to be indexed. When completed, 
	the program will output two files - index.txt(the inverse term table) and
	numdocs.txt(the amount of documents found inside the collection)
	
You can now proceed to query the inverse table.
textindex.py
1. Run the script using: "python textindex.py"
2. Type in the name of the index to be queried(Usually index.txt)
3. Type in the file name of where number of documents inside the 
	index is stored (Usually numdocs.txt)
4. Select query preprocessing parameters(1-default, 2-choose)
	4.1 If second option is taken, write 1 if you would like stopwords to be removed and 2 if not.
		4.1.1 If stopwords are removed, type in the stopword file name (default englishST.txt)
	4.2 Type 1 if you would like stemming to be applied, 2 if not.
5. Choose what kind of query you would like (1-boolean, 2-ranked ir, 3-exit)
	You can run any number of queries as these options are cyclic.
	5.1 Input the name of a file that contains boolean 
	queries in the following form:QueryNumber Query
	Each line should have a separate query
	Query results will be stored in a file named results.boolean.txt
	5.2 Input the name of a file that contains ranked IR 
	queries in the following form:QueryNumber Query
	Each line should have a separate query
	Query results will be stored in a file named results.ranked.txt
	5.3 Option exits the program.
6. After queries have been run you can find results in the previously described files.
They contain up to 1000 results for each query sorted in the document ID order (boolean)
or the relevancy score order (ranked IR)


