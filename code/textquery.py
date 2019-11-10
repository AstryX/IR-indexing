import math
import operator
from nltk.stem.porter import *

#Ranked score calculation for each term using TFIDF formula (1 + tf) * log10(N/df)
def calculateWeightsForTerm(term, invIndex, numDocs):
	wMap = {}
	#Check to make sure we avoid division by 0 when term does not exist
	if term in invIndex.keys():
		docFreq = len(invIndex[term].keys())
		for id in list(invIndex[term].keys()):
			#TFIDF formula for each document
			wMap[id] = (1 + math.log(len(invIndex[term][id]),10)) * math.log(numDocs/docFreq,10)
	return wMap		

#This function takes a list of words to be preprocessed using to-lowercase/stopping/stemming as requested
def preprocessQuery(query, shouldStop, shouldStem, stArr):
	modifiedQuery = query
	#Words change to lowercase
	for i in range(len(modifiedQuery)):
		modifiedQuery[i] = modifiedQuery[i].lower()
	
	#Stopwords removed
	stoplessArray = []
	if shouldStop == True:
		for i in range(len(modifiedQuery)):
			curWord = modifiedQuery[i]
			isStop = False
			for stopword in stArr:
				if curWord == stopword:
					isStop = True
					break
			if not isStop:
				stoplessArray.append(curWord)
	else:
		stoplessArray = modifiedQuery
				
	#Stemmer processing
	if shouldStem == True:
		#Porter stemmer
		stemmer = PorterStemmer()
		return [stemmer.stem(word) for word in stoplessArray]
	else:
		return stoplessArray
		
#Old code for boolean queries which used a binary representation of all documents for AND, OR, NOT queries
'''def performBinary(leftSide, operator, rightSide):
	result = ""
	leftLen = len(leftSide)
	rightLen = len(rightSide)
	operationLen = 0
	if operator == "AND":
		if leftLen > rightLen:
			operationLen = rightLen
		else:
			operationLen = leftLen
		for i in range(operationLen):
			if leftSide[i] == "1" and rightSide[i] == "1":
				result += "1"
			else:
				result += "0"
	elif operator == "OR":
		minimumLen = 0
		longerSide = ""
		if leftLen < rightLen:
			operationLen = rightLen
			longerSide = rightSide
			minimumLen = leftLen
		else:
			operationLen = leftLen
			longerSide = leftSide
			minimumLen = rightLen
		for i in range(minimumLen):
			if leftSide[i] == "1" or rightSide[i] == "1":
				result += "1"
			else:
				result += "0"
		for i in range(minimumLen, operationLen):
			if longerSide[i] == "1":
				result += "1"
			else:
				result += "0"
	elif operator == "NOT":
		for i in range(rightLen):
			if rightSide[i] == "1":
				result += "0"
			else:
				result += "1"
	return result'''
	
#Function used for phrase and proximity search of words
#Phrase is treated as a proximity search where the second word has to be directly after the first one
def searchMultipleTerms(termList, invIndex, isPhrase, maxDistance=0):
	docsList = []
	leftTerm = termList[0]
	rightTerm = termList[1]
	#Make sure both terms exist
	if leftTerm in invIndex.keys() and rightTerm in invIndex.keys():
		leftList = invIndex[leftTerm]
		rightList = invIndex[rightTerm]
		#Get a list of doc id's for each term
		leftKeys = list(leftList.keys())
		rightKeys = list(rightList.keys())
		#Main loop
		for curKey in leftKeys:
			#If an id from left term exists in the right map, there is overlap
			if curKey in rightKeys:
				#For each available position of the left key
				for position in leftList[curKey]:
					curPos = int(position)
					#If the two words are a phrase
					if isPhrase == True:
						#Next term pos checked on right side
						nextPos = str(curPos + 1)
						if nextPos in rightList[curKey]:
							docsList.append(curKey)
							break
					#Proximity
					else:
						foundMatch = False
						#Looking for positions of the second word in the right map and calculating distance
						for otherPosition in rightList[curKey]:
							if abs(int(otherPosition) - curPos) <= maxDistance:
								docsList.append(curKey)
								foundMatch = True
								break
						if foundMatch == True:
							break
								

	#Remove duplicate doc entries and sort the results
	return sorted(list(dict.fromkeys(docsList)))
	
#A simple getter function for ID's
def getIDListForTerm(term, invIndex):
	if term in invIndex.keys():
		return sorted(invIndex[term].keys())
	else:
		return []
	
#This function runs linear merge between two lists containing document ID's and returns arrays in the form of [1,1] if both documents exist
def linearMerge(leftList, rightList):
	endLoop = False
	resultsDict = {}
	startSide = 'left'
	leftIt = 0
	rightIt = 0
	#Start from the right doc
	if len(rightList) > 0 and (len(leftList) == 0 or rightList[0] < leftList[0]):
		startSide = 'right'
	switchSide = False
	while endLoop != True:
		#If currently parsed document side needs to be changed
		if switchSide == True:
			if startSide == 'left':
				startSide = 'right'
			else:
				startSide = 'left'
			switchSide = False
			
		#Used for cases where one or both sides go out of array bounds signifying the end of the linear merge
		if startSide == 'left':
			if leftIt >= len(leftList):
				if rightIt >= len(rightList):
					break
				else:
					switchSide = True
					continue
		else:
			if rightIt >= len(rightList):
				if leftIt >= len(leftList):
					break
				else:
					switchSide = True
					continue
			
		#Used for cases where one of the sides runs out of bounds, so the other side can quickly compute that the term only exists in one side
		if startSide == 'left':
			if rightIt >= len(rightList):
				resultsDict[leftList[leftIt]] = [1, 0]
				leftIt += 1
				continue
		else:
			if leftIt >= len(leftList):
				resultsDict[rightList[rightIt]] = [0, 1]
				rightIt += 1
				continue

		#The entries upon which the arrows in linear merge are pointing to at the moment			
		curLeft = leftList[leftIt]
		curRight = rightList[rightIt]
		if startSide == 'left':
			#if right is bigger, then left must not exist
			if curRight > curLeft:
				resultsDict[curLeft] = [1, 0]
				leftIt += 1
			#if they are equal, we have found a match. shift positions of both entries
			elif curRight == curLeft:
				resultsDict[curLeft] = [1, 1]
				leftIt += 1
				rightIt += 1
			else:
				switchSide = True
				continue
		else:
			#if left is bigger then right must not exist in the other doc
			if curLeft > curRight:
				resultsDict[curRight] = [0, 1]
				rightIt += 1
			elif curLeft == curRight:
				resultsDict[curRight] = [1, 1]
				leftIt += 1
				rightIt += 1
			else:
				switchSide = True
				continue
				
	return resultsDict

#This function performs calculations on results of a linear merge which is a map which contains arrays in the form of [1,1] to signify existance
#Done for AND, OR, NOT
def operateOnMergeResults(mergeResult, operatorType, leftNotFlag, rightNotFlag):
	resultsList = []
	#If left or right NOT flags are set, then the results are inverted
	#Does not work well if NOT + OR are combined, but it is avoided in this assignment
	if leftNotFlag == True:
		for id in mergeResult.keys():	
			if mergeResult[id][0] == 1:
				mergeResult[id][0] = 0
			else:
				mergeResult[id][0] = 1
	if rightNotFlag == True:
		for id in mergeResult.keys():	
			if mergeResult[id][1] == 1:
				mergeResult[id][1] = 0
			else:
				mergeResult[id][1] = 1
	#For loop parsing the results
	for id in mergeResult.keys():
		#Perform AND on the results	
		if operatorType == "AND":
			if mergeResult[id][0] + mergeResult[id][1] == 2:
				resultsList.append(id)
		#Perform OR on the results
		elif operatorType == "OR":
			if mergeResult[id][0] + mergeResult[id][1] > 0:
				resultsList.append(id)
	#Return a list of ID's which satisfy the criteria
	return resultsList
	
#Main boolean query parsing function
def parseBooleanSearchQuery(query, invIndex, applyStopping, applyStemming, stArr):

	curTask = ""
	taskStack = []
	leftNotFlag = False
	rightNotFlag = False
	curFlag = ""
	#If a phrase is currently parsed
	phraseFlag = False
	#If proximity query is currently parsed
	proximityFlag = False
	proximityDef = 0
	queryLen = len(query)
	#Main loop that parses the query letter by letter
	for i in range(queryLen):
		letter = query[i]
		if phraseFlag == True:
			if letter != "\"":
				curTask += letter
				continue
		elif proximityFlag == True:
			if letter == "(":
				proximityDef = int(curTask)
				curTask = ""
				continue
			elif letter != ")":
				curTask += letter
				continue
		#Signifies the start or end of a phrase
		if letter == "\"":
			if phraseFlag == False:
				phraseFlag = True
			else:
				#Preprocessing applied on the query
				preppedQuery = preprocessQuery(curTask.split(" "), applyStopping, applyStemming, stArr)
				#Phrase query function called
				phraseResult = searchMultipleTerms(preppedQuery, invIndex, True)
				#If stack has a result means that we must perform a AND or OR with the current result
				if len(taskStack) == 1:
					mergeResult = linearMerge(taskStack[0], phraseResult)
					filteredResult = operateOnMergeResults(mergeResult, curFlag, leftNotFlag, rightNotFlag)
					taskStack = []
					curFlag = ""
					leftNotFlag = False
					rightNotFlag = False
					taskStack.append(filteredResult)
				else:
					taskStack.append(phraseResult)
				curTask = ""
				phraseFlag = False
		#Start of proximity query
		elif letter == "#":
			proximityFlag = True
		#End of proximity query, similar logic to phrase parsing above
		elif letter == ")":
			splitQuery = curTask.split(",")
			for q in range(len(splitQuery)):
				splitQuery[q] = splitQuery[q].replace(" ", "")
			preppedQuery = preprocessQuery(splitQuery, applyStopping, applyStemming, stArr)
			proximityResult = searchMultipleTerms(preppedQuery, invIndex, False, proximityDef)
			if len(taskStack) == 1:
				mergeResult = linearMerge(taskStack[0], proximityResult)
				filteredResult = operateOnMergeResults(mergeResult, curFlag, leftNotFlag, rightNotFlag)
				taskStack = []
				curFlag = ""
				leftNotFlag = False
				rightNotFlag = False
				taskStack.append(filteredResult)
			else:
				taskStack.append(proximityResult)
			curTask = ""
			proximityDef = 0
			proximityFlag = False
		#End of a word or AND/OR/NOT
		elif letter == " " or i == queryLen - 1:
			#If it is the end of doc
			if i == queryLen - 1:
				curTask += letter
			if letter == " " and curTask == "":
				continue
			if curTask == "AND":
				curFlag = "AND"
			elif curTask == "OR":
				curFlag = "OR"
			elif curTask == "NOT":
				if len(taskStack) > 0:
					rightNotFlag = True
				else:
					leftNotFlag = True
			else:
				preprocessedWord = preprocessQuery([curTask], applyStopping, applyStemming, stArr)[0]
				curTaskIds = getIDListForTerm(preprocessedWord, invIndex)
				#If a simple word was read and another result already existed in the stack means we must merge
				if len(taskStack) == 1:
					mergeResult = linearMerge(taskStack[0], curTaskIds)
					filteredResult = operateOnMergeResults(mergeResult, curFlag, leftNotFlag, rightNotFlag)
					taskStack = []
					curFlag = ""
					leftNotFlag = False
					rightNotFlag = False
					taskStack.append(filteredResult)
				else:
					taskStack.append(curTaskIds)
			curTask = ""
		else:
			curTask += letter	
	return taskStack
	
print("Please specify the inverted index file name...")
fname = str(input()) 

file = []
success = True
#Inverted index load from file
try:
	fileFull = open(fname,"r+") 
	print("Loading inverted index into memory...")
	file = fileFull.read().splitlines()
	fileFull.close()
except:
	print("Could not find the specified file name for inverted index " + fname)
	success = False

numDocs = 0
#Load the quantity of documents used for the map
if success == True:	
	print("Inverted index has finished loading!")
	print("Please specify the document number file name...")
	fdocname = str(input()) 
	try:
		fileDoc = open(fdocname,"r+") 
		tempDocLines = fileDoc.read().splitlines()
		numDocs = int(tempDocLines[0])
		print("Number of documents has been retrieved!")
	except:
		print("Could not find the specified file name for document number " + fdocname)
		success = False
		
applyStopping = True
applyStemming = True
stopwordFileName = "englishST.txt"
stArr = []
#Configuration options for query preprocessing are selected
if success == True:	
	print("Would you like to use the default query configuration? (1 - Yes; 2 - No)")
	choiceNum = int(input()) 

	if choiceNum == 2:
		print("Would you like to apply stopping to queries? (1 - Yes; 2 - No)")
		choiceNum = int(input()) 
		if choiceNum == 2:
			applyStopping = False
			
		if applyStopping == True:
			print("Please input the custom stopwords file name (Default: englishST.txt):")
			stopwordFileName = input()
			
		print("Would you like to apply stemming to queries? (1 - Yes; 2 - No)")
		choiceNum = int(input()) 	
		if choiceNum == 2:
			applyStemming = False

	try:
		stopwords = open(stopwordFileName)
		stArr = stopwords.read().splitlines()
		stopwords.close()
	except:
		print("Could not find the specified file name for stopwords " + stopwordFileName)
		success = False
		
if success == True:
	inverseIndex = {}
	curWord = " "

	#Inverted index from the read file is loaded into a map of maps of integers structure
	for line in file:
		textLine = line.split(':', 1)
		if "\t" in textLine[0]:
			curID = int(textLine[0])
			curLocations = (textLine[1][1:]).split(',')
			for loc in curLocations:
				if curWord in inverseIndex.keys(): 
					if curID in inverseIndex[curWord]:
						inverseIndex[curWord][curID].append(loc)
					else:
						inverseIndex[curWord][curID] = [loc]
				else:
					inverseIndex[curWord] = {}
					inverseIndex[curWord][curID] = [loc]
		else:
			curWord = textLine[0]
			
	
	inputNum = 0
	#Endless loop until exit is called, can run any number of queries on the loaded index
	while inputNum < 3:
		print("(1) Boolean Search")
		print("(2) Ranked IR based on TFIDF")
		print("(3) Exit")
		inputNum = int(input()) 
		#Option 1 for boolean search
		if inputNum == 1:
			print("Input the file name for Boolean Search queries:")
			fdocname = str(input()) 
			queryLines = []
			#Queries are loaded from a file
			try:
				fileDoc = open(fdocname,"r+") 
				queryLines = fileDoc.read().splitlines()
				fileDoc.close()
				if len(queryLines) > 0:
					print("Queries have been retrieved!")
				else:
					print("No queries found in the file!")
					success = False
			except:
				print("Could not find the specified file name for queries " + fdocname)
				success = False
				
			if success == True:
				#Results are saved to this file
				booleanFile = open("results.boolean.txt","w+")
				numQuery = 1
				#Each query is run on the inverted index
				for curQuery in queryLines:
					#Main boolean parse function call
					#Queries are split on the first space to remove the first number
					searchResult = parseBooleanSearchQuery((curQuery.split(' ', 1))[1], inverseIndex, applyStopping, applyStemming, stArr)
					limit = 1000
					numPrinted = 0
					if len(searchResult) != 1:
						continue
					#Up to 1000 results for each query are printed in the required format
					for boolResult in searchResult[0]:
						if numPrinted == limit:
							break
						booleanFile.write("%d 0 " % numQuery)
						booleanFile.write("%d 0 " % boolResult)
						booleanFile.write("1 0\n")
						numPrinted += 1
					numQuery += 1
				booleanFile.close()
				print("Query results have been printed to a file: results.boolean.txt")
		#Option 2 for ranked search
		elif inputNum == 2:
			print("Input the file name for Ranked IR queries:")
			fdocname = str(input()) 
			queryLines = []
			#Ranked queries loaded from a file
			try:
				fileDoc = open(fdocname,"r+") 
				queryLines = fileDoc.read().splitlines()
				fileDoc.close()
				if len(queryLines) > 0:
					print("Queries have been retrieved!")
				else:
					print("No queries found in the file!")
					success = False
			except:
				print("Could not find the specified file name for queries " + fdocname)
				success = False
				
			if success == True:
				#This is the file query results are saved to
				rankedFile = open("results.ranked.txt","w+")
				numQuery = 1
				#Main query parsing loop
				for curQuery in queryLines:
					#Main ranked query processing function call
					#Queries are split using a tokenization technique and first number is ignored
					fullArr = []
					curToken = ""
					curLine = curQuery.split(' ', 1)[1]
					removalFlag = False
					for letter in curLine:
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
					rankedList = preprocessQuery(fullArr, applyStopping, applyStemming, stArr)
					totalWeights = {}
					
					#Retrieves ranked score for each term and adds it to the total map
					for term in rankedList:
						curWeights = calculateWeightsForTerm(term, inverseIndex, numDocs)
						for idToAdd in curWeights.keys():
							if idToAdd in totalWeights.keys():
								totalWeights[idToAdd] += curWeights[idToAdd]
							else:
								totalWeights[idToAdd] = curWeights[idToAdd]
					#Sorts the weights inside our weight map in descending order
					sortedWeights = sorted(totalWeights.items(), key=operator.itemgetter(1), reverse=True)
					
					#Up to 1000 ranked results are printed in the required format for a query
					limit = 1000
					numPrinted = 0
					for tuple in sortedWeights:
						if numPrinted == limit:
							break
						rankedFile.write("%d 0 " % numQuery)
						rankedFile.write("%d 0 " % tuple[0])
						rankedFile.write("%s 0\n" % str(round(tuple[1], 4)))
						numPrinted += 1
					numQuery += 1
				rankedFile.close()
				print("Query results have been printed to a file: results.ranked.txt")
		#Exit choice
		elif inputNum == 3:
			print("Exiting...")
			break
		else:
			print("Selected numerical option does not exist: " + str(inputNum))


			
