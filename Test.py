import sys, getopt
import os
import re


from DConfig import DConfig

ConfigFile = 'K:/Programs/Development/SurveySetup Ver2/TESTING/TESTING.CONFIG'
TestDir = 'K:/Programs/Development/SurveySetup Ver2/TESTING/'

SelectedTest =0
ErrorFound = 0

if (len(sys.argv) >1):
	if (not(re.match(r"^\d+$",sys.argv[1]))):
		raise Exception("Please only provided a number for selected test: "+sys.argv[1])
	SelectedTest = int(sys.argv[1])

ConfigCommands={}
Config = DConfig(ConfigFile, ConfigCommands)	

#RETURNS A LIST OF QFI QUESTIONS
def ParseQFIQuestion(FileName, ErrorLog):
	global ErrorFound
	LineCount = 1
	Questions = {}
	CurrentQuestion = None
	#LOOP THORUGH FILE NAME
	with open(TestDir+FileName, 'r') as File:
		with open(TestDir+ErrorLog, 'a') as Error:
			for CurrentLine in File:
				#CHECK IF START OF NEW QUESTION
				if(re.match(r"^\~PAGE\:",CurrentLine)):
					NewQuestion = {}
					LineArray = []
					CurrentQuestion = NewQuestion
					CurrentQuestion['LINES'] = LineArray
					CurrentQuestion['LINE_START'] = LineCount
				#CHECK FOR QUESTION ID
				elif(re.match(r"\~NQ\:([^:]+)\:",CurrentLine)):
					QuestionID = re.search(r"\~NQ\:([^:]+)\:",CurrentLine).group(1)
					if QuestionID in Questions:
						Error.write(QuestionID+": Duplicate Question\n")
						ErrorFound = 1
					else:
						CurrentQuestion['QUESTION_ID'] = QuestionID
						Questions[QuestionID] = CurrentQuestion
				CurrentQuestion['LINES'].append(CurrentLine)
				LineCount+=1
	return Questions

#RETURNS A LIST OF VOXCO QUESTIONS
def	ParseVoxcoQuestion(FileName, ErrorLog):
	global ErrorFound
	LineCount = 1
	Questions = {}
	CurrentQuestion = None
	#LOOP THORUGH FILE NAME
	with open(TestDir+FileName, 'r') as File:		
		with open(TestDir+ErrorLog, 'a') as Error:
			#INITIALIZE INTRO TEXT 
			IntroText = {}
			Intro1LineArray = []
			CurrentQuestion = IntroText
			CurrentQuestion['LINES'] = Intro1LineArray
			CurrentQuestion['LINE_START'] = 1
			CurrentQuestion['QUESTION_ID'] = 'INTRO'
			Questions['INTRO'] = CurrentQuestion
			for CurrentLine in File:
				#CHECK IF START OF NEW QUESTION
				if(re.search(r"\*LL (\S+)",CurrentLine)):
					QuestionID = re.search(r"\*LL (\S+)",CurrentLine).group(1)
					NewQuestion = {}
					LineArray = []
					CurrentQuestion = NewQuestion
					CurrentQuestion['LINES'] = LineArray
					CurrentQuestion['LINE_START'] = LineCount
					if QuestionID in Questions:
						Error.write(QuestionID+": Duplicate Question\n")
						ErrorFound = 1
					else:
						CurrentQuestion['QUESTION_ID'] = QuestionID
						Questions[QuestionID] = CurrentQuestion
				CurrentQuestion['LINES'].append(CurrentLine)
				LineCount+=1
	return Questions

#RETURNS A LIST OF DECIPHER QUESTIONS
def ParseDecipherQuestion(FileName, ErrorLog):
	global ErrorFound
	LineCount = 0
	Questions = {}
	CurrentQuestion = None

	NewQuestion = 1
	with open(TestDir+FileName, 'r') as File:
		with open(TestDir+ErrorLog, 'a') as Error:	
	
			for CurrentLine in File:
				LineCount+=1
				#CHECK IF START OF NEW QUESTION	
				if(NewQuestion):
					CurrentQuestion = {}
					CurrentQuestion['LINES'] = []
					CurrentQuestion['LINE_START'] = LineCount
					CurrentQuestion['QUESTION_ID'] = ""
					NewQuestion = 0
				#TEST FOR TAG ENDING A QUESTION		
				if(re.search(r"\</samplesources\>",CurrentLine) or re.search(r"\<suspend\/\>",CurrentLine)):
					NewQuestion = 1
				#TEST FOR TAG
				if (CurrentQuestion['QUESTION_ID'] == "" and re.search(r"label\=\"([a-zA-Z0-9_-]+)\"",CurrentLine)):
					QuestionID = re.search(r"label\=\"([a-zA-Z0-9_-]+)\"",CurrentLine).group(1)
					if QuestionID in Questions:
						Error.write(QuestionID+": Duplicate Question\n")
						ErrorFound = 1
					else:
						CurrentQuestion['QUESTION_ID'] = QuestionID
						
						Questions[QuestionID] = CurrentQuestion
				CurrentQuestion['LINES'].append(CurrentLine)
	return Questions


def CompareQuestions(QuestionA,QuestionB,FileA, FileB,ErrorLog):
	global ErrorFound
	with open(TestDir+ErrorLog, 'a') as Error:		
		#LOOP THROUGH QUESTIONS IN QUESTION A;
		for QuestionID in QuestionA.keys():
			#LOOK THAT QUESTION EXISTS IN QUESTION B
			if (not(QuestionID in QuestionB)):
				Error.write("Found Question "+QuestionID+" in "+FileA+" but not int "+FileB+"\n")
				ErrorFound = 1
			#LOOP THROUGH QUESTION TEXT
			else:
				for LineIndex in range(0,len(QuestionA[QuestionID]['LINES'])):
					if LineIndex >= len(QuestionB[QuestionID]['LINES']):
						Error.write(QuestionID+" - Line not found.\n")
						Error.write("\t"+QuestionA[QuestionID]['LINES'][LineIndex]+"\n")
						ErrorFound = 1
					elif QuestionA[QuestionID]['LINES'][LineIndex] != QuestionB[QuestionID]['LINES'][LineIndex]:
						Error.write(QuestionID+" - Line mismatch detected.\n")
						Error.write("\t"+QuestionA[QuestionID]['LINES'][LineIndex])
						Error.write("\t"+QuestionB[QuestionID]['LINES'][LineIndex]+"\n")
						ErrorFound = 1
		for QuestionID in QuestionB.keys():
			#LOOK THAT QUESTION EXISTS IN QUESTION A
			if QuestionID not in QuestionA:
				Error.write("Found Question "+QuestionID+" in "+FileB+" but not int "+FileA+"\n")
				ErrorFound = 1


#RUNS TEST
def RunTest (Test):
	global ErrorFound	
	ErrorFound = 0 #RESET ERROR FLAG
    

	if (re.match(r'^QFI$',Test['TYPE'])):
		os.system('SurveySetup.py "'+TestDir+Test['SOURCE']+'" "'+TestDir+Test['DEST']+'"')
	else:
		os.system('SurveySetup.py -t '+Test['TYPE']+' "'+TestDir+Test['SOURCE']+'" "'+TestDir+Test['DEST']+'"')

	with open(TestDir+Test['OUTPUT'], 'w') as File:
		File.write('')

	print ("Testing: "+Test['NAME'], end='')
	#CHECK IF QFI
	if('QFI' in Test['TYPE']):		
		Questions = ParseQFIQuestion(Test['DEST'],Test['OUTPUT'])
		Compare = ParseQFIQuestion(Test['COMPARE'],Test['OUTPUT'])
		
		CompareQuestions (Questions, Compare,Test['DEST'],Test['COMPARE'],Test['OUTPUT'])

		if (ErrorFound):
			print (" - Errors found", end='')
		
	#CHECK IF VOXCO
	elif('VOXCO' in Test['TYPE']):
		Questions = ParseVoxcoQuestion(Test['DEST'],Test['OUTPUT'])
		Compare = ParseVoxcoQuestion(Test['COMPARE'],Test['OUTPUT'])

		CompareQuestions (Questions, Compare,Test['DEST'],Test['COMPARE'],Test['OUTPUT'])
		if (ErrorFound):
			print (" - Errors found", end='')


	#CHECK IF DECIPHER
	elif('DECIPHER' in Test['TYPE']):	
		Questions = ParseDecipherQuestion(Test['DEST'],Test['OUTPUT'])
		Compare = ParseDecipherQuestion(Test['COMPARE'],Test['OUTPUT'])
		CompareQuestions (Questions, Compare,Test['DEST'],Test['COMPARE'],Test['OUTPUT'])
		
		if (ErrorFound):
			print (" - Errors found", end='')

	print ("\n", end='')


#CHECK IF SELECTED TEXT HAS BEEN SET
if (SelectedTest >0):
	RunTest (Config.Config['TEST_LIST'][SelectedTest-1])
#LOOP THROUGH CONFIG FILE
else:
	for CurrentTest in Config.Config['TEST_LIST']:
		RunTest( CurrentTest)
	



		








	




