#Primary text processing script
from nltk.stem.porter import *
stemmer = PorterStemmer()

print("Name of the file to be indexed (txt):")
inputFileName = input()

applyStopping = True
applyStemming = True
stoppingName = "englishST.txt"
file = []
stSet = set()
inverseIndex = {}
success = True
#Load and parse the document file. Splitlines is used as it removes the \n symbols.
try:
	fileFull = open(inputFileName,"r+") 
	file = fileFull.read().splitlines()
	fileFull.close()
	print("File has been loaded...")
except:
	print("Could not find the specified file name for input " + inputFileName)
	success = False

#Support for different preprocessing configurations
if success == True:
	print("Would you like to use the default configuration? (1 - Yes; 2 - No)")
	choiceNum = int(input()) 

	if choiceNum == 2:
		print("Would you like to apply stopping? (1 - Yes; 2 - No)")
		choiceNum = int(input()) 
		if choiceNum == 2:
			applyStopping = False
			
		if applyStopping == True:
			print("Please input the custom stopwords file name (Default: englishST.txt):")
			stoppingName = input()
			
		print("Would you like to apply stemming? (1 - Yes; 2 - No)")
		choiceNum = int(input()) 	
		if choiceNum == 2:
			applyStemming = False

#Stopwords file is loaded
	if applyStopping == True:
		try:
			stopwords = open(stoppingName)
			stSet = set(stopwords.read().splitlines())
			stopwords.close()
		except:
			print("Could not find the specified file name for stopwords " + stoppingName)
			success = False

if success == True:
	#Currently parsed doc ID
	curID = 0
	#Total num of documents parsed
	numDocuments = 0
	#Keeps track of the parse position of words in each doc
	wordIndex = 1
	#Main loop for indexing
	for line in file:
		textLine = line.split(':', 1)
		#ID line signifies the start of a new document
		if textLine[0] == "ID":
			curID = int(textLine[1])
			wordIndex = 1
			numDocuments += 1
		else:
			textContents = textLine[1]
			#Tokenizer preprocessing
			fullArr = []
			curToken = ""
			removalFlag = False
			for letter in textContents:
				#if letter == " " or letter == "," or letter == "." or letter == "?" or letter == ":" or letter == "\\" or letter == "/" or letter == "(" or letter == ")" or letter == "-" or letter == "\'":
				if letter.isalnum() == False:	
					tokenLen = len(curToken)
					if removalFlag == True:
						removalFlag = False
						if tokenLen == 1:
							curToken = ""
							continue
					if (tokenLen == 1 or tokenLen == 2) and (letter == '-' or letter == "'"):
						if curToken.isalpha() == True:
							continue
						else:
							fullArr.append(curToken)
							curToken = ""
					else:
						if len(curToken) != 0:
							if letter == '-' or letter == "'":
								removalFlag = True
							fullArr.append(curToken)
							curToken = ""
						else:
							continue
				else:
					curToken += letter
			if curToken != "":
				fullArr.append(curToken)
				curToken = ""
					
			#To-lowercase words preprocessing
			fullArr = [curWord.lower() for curWord in fullArr]
		
			#Stopword removal preprocessing
			if applyStopping == True:
				fullArr = [curWord for curWord in fullArr if curWord not in stSet]

			#Porter stemmer preprocessing
			if applyStemming == True:
				#Porter stemmer
				fullArr = [stemmer.stem(word) for word in fullArr]
			
			#Storage of data about preprocessed words inside the correct place within our map 
			curKeys = inverseIndex.keys()
			for stemmedWord in fullArr:
				if stemmedWord in curKeys: 
					if curID in inverseIndex[stemmedWord]:
						inverseIndex[stemmedWord][curID].append(wordIndex)
					else:
						inverseIndex[stemmedWord][curID] = [wordIndex]
				else:
					inverseIndex[stemmedWord] = {}
					inverseIndex[stemmedWord][curID] = [wordIndex]
				wordIndex += 1
					
	#Saving inverted index map to a file in the required format
	output = open("index.txt","w+")
	for word in sorted(inverseIndex):
		output.write("%s:\n" % word)
		for id in sorted(inverseIndex[word]):
			output.write("\t%d: " % id)
			numPosition = 0
			for position in inverseIndex[word][id]:
				if numPosition == 0:
					output.write("%d" % position)
				else:
					output.write(",%d" % position)
				
				numPosition = numPosition + 1
			output.write("\n")
	output.close()

	#Saves the quantity of documents to a file so the query does not have to calculate them from the index map (which takes a very long time)
	numDocsFile = open("numdocs.txt","w+")
	numDocsFile.write("%d" % numDocuments)
	numDocsFile.close()
	print("Indexing job finished...")