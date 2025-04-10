import codecs
import sys
import math
import re
import numpy

import QuestionaireMisc
sys.path.insert(1, '/Programming/Python/Command')

import QuestionaireMisc
from Command import Command


####################################### QUESTIONAIRE PROCESS CHECK #########################################
class QuestionaireProcessCheck:
	
	##############################################################################################################
	##################################### QUESTIONAIRE PROCESS CHECK - INIT ######################################
	################################################################################1#############################
	def __init__ (Self, Question, Debug=0):	
		Self.MaxWords=0	
		Self.Question = Question
		Self.ProcessType = ""
		Self.Headings = {}
	
		#FLAG LISTS 
		Self.DefinedFlags = {}		 #TRACKS ELMENTS DEFINED 
		Self.StateFlags = {}		 #STATE VARIABLES
		Self.FormatFlags = {}		 #FLAGS ASSOCIATED WITH FORMATTING
		Self.TextContentFlags = {}	 #FLAGS ASSOCIATED WITH TEXT CONTENT		
		Self.NumericValuesText = {}  #NUMERIC VALUES ASSOCIATED WITH ASSIGNED TEXT
		Self.TextProcessFlags = {} 	 #SPECIFIC PROCESSING FLAGS - MOSTLY ASSOCIATED WITH LOGIC (DEFINED FROM CONFIGS RATHER THAN PROGRAMMING)

		Self.BlockTrack = None    
		Self.TableTrack = None
		Self.ListDefTrack = None
		Self.QuestionTrack = None    
		Self.ListTrack = None

		Self.Text =""
		Self.CleanText  =""
		Self.InlineText = ""		#HOLDING VARIABLE FOR TEXT TO BE INSERTED IN THE MIDDLE OF A LINE DURING PROCESSING
		Self.Debug = Debug

		Self.LogicCodes = {}

	############# QuestionaireProcessCheck:Init Logic Codes #############
	#FUNCTION:   Adds values to the Logic Codes
	#PARAMATERS: Logic Code Category
	#RETURNS:	 Nothing
	def InitLogicCodes(Self, Configs, LogicCodeCat):
		#LOOP THROUGH LOGIC IN THE MAIN CONFIG
		for Logic in Configs['MAIN_CONFIG'].Config['LOGIC']:
			if LogicCodeCat in Logic:				
				for LogicKey in Logic[LogicCodeCat]:
					Self.LogicCodes[LogicKey] = 0


	######################################################################################################################
	#################################### QUESTIONAIRE PROCESS CHECK - VALUE SETTING ######################################
	######################################################################################################################
	############# QuestionaireProcessCheck:SetFlagValues #############
	#FUNCTION:   Provided a list of flags checks if they exist in one of the flag lists and sets them to 0
	
	#RETURNS:	 Nothing	
	def SetFlagValues(Self, FlagsList):	
		for Flag in FlagsList.keys():
			if(Flag in Self.DefinedFlags):
				Self.DefinedFlags[Flag]=FlagsList[Flag]
			elif(Flag in Self.StateFlags):
				Self.StateFlags[Flag]=FlagsList[Flag]
			elif(not(Self.ListDefTrack is None) and Flag in Self.ListDefTrack.Flags):
				Self.ListDefTrack.Flags[Flag]=FlagsList[Flag]
			elif(Flag in Self.TextContentFlags):
				Self.TextContentFlags[Flag]=FlagsList[Flag]
			elif(Flag in Self.FormatFlags):
				Self.FormatFlags[Flag]=FlagsList[Flag]
			else:
				print("ERROR: Flag "+Flag+" Not Found")


	############# QuestionaireProcessCheck:SetFlagValues #############
	#FUNCTION:   Provided a list of flags checks if they exist in one of the flag lists and sets them to 1 if not found returns an error
	#PARAMATERS: Flag List
	#RETURNS:	 Nothing	
	def SetFlagValue(Self, Flag, Value):	
		if(Flag in Self.DefinedFlags):
			Self.DefinedFlags[Flag]=Value
		elif(Flag in Self.StateFlags):
			Self.StateFlags[Flag]=Value
		elif(not(Self.ListDefTrack is None) and Flag in Self.ListDefTrack.Flags):
			Self.ListDefTrack.Flags[Flag]=Value
		elif(Flag in Self.TextContentFlags):
			Self.TextContentFlags[Flag]=Value
		elif(Flag in Self.FormatFlags):
			Self.FormatFlags[Flag]=Value
		else:
			print("ERROR: Flag "+Flag+" Not Found")


	############# QuestionaireProcessCheck:ClearNumericValues #############
	#FUNCTION:   Resets values in a provided trackign structure associated with list def
	#PARAMATERS: TrackStructure, LookupList
	#RETURNS:	 Nothing
	def ClearValues (Self, TrackStructure, LookupList):			
		#INIT VALUES TO 0
		for Key in LookupList:
			TrackStructure[Key] =0

	############# QuestionaireProcessCheck:MergeFlags #############
	#FUNCTION:   Provided a list of flags updates the flags with this list
	#PARAMATERS: Flag List
	#RETURNS:	 Nothing
	def MergeFlags(Self,FlagList):
		#LOOP THROUGH FLAGS
		for Flag in FlagList:
			if(Flag in Self.DefinedFlags):	
				Self.DefinedFlags[Flag]=FlagList[Flag]
			elif(Flag in Self.StateFlags):
				Self.StateFlags[Flag]=FlagList[Flag]
			elif(not(Self.ListDefTrack is None) and Flag in Self.ListDefTrack.Flags):
				Self.ListDefTrack.Flags[Flag]=FlagList[Flag]
			elif(Flag in Self.TextContentFlags):
				Self.TextContentFlags[Flag]=FlagList[Flag]
			elif(Flag in Self.FormatFlags):
				Self.FormatFlags[Flag]=FlagList[Flag]
			else:
				print("ERROR: Flag "+Flag+" Not Found")				

	############# QuestionaireProcessCheck:SetInlineText #############
	#FUNCTION:   Sets the Inline Text Value used post logic processing to add text directly into the line processed (nominally should only take place in segment level processing)
	#PARAMATERS: Text
	#RETURNS:	 Nothing
	def SetInlineText(Self, Text):
		Self.InlineText = Text

	######################################################################################################################
	################################## QUESTIONAIRE PROCESS CHECK - LOGIC PROCESSING #####################################
	######################################################################################################################

	############# QuestionairProcessCheck:CheckElements #############
	#FUNCTION:   Provided processed config, runs through specified checks generating a weight
	#PARAMATERS: Config, Text being checked, Debug Flag
	#RETURNS:	 Computed Weight
	def CheckElements(Self, Config, Text):
		Weight=0									#WEIGHT COMPUTED
		
		#INITIALIZE FLAGS
		Self.TextProcessFlags['TEXT_ALL_TAGS']=1;           		
		Self.TextProcessFlags['TEXT_ALL_KEYWORDS']=1;           	
		Self.TextProcessFlags['TEXT_ALL_KEYWORDS_POSITIVE']=1;  	
		Self.TextProcessFlags['TEXT_ALL_KEYWORDS_NEGATIVE']=1;  	
		Self.TextProcessFlags['TEXT_KEYWORD_COUNT']=0;  	

		if (Self.Debug==2): print (Text)
		#LOOP THROUGH REQUIREMENT CHECKS
		if('REQUIREMENTS' in Config.Config):
			for ReqCheck in Config.Config['REQUIREMENTS']:
				if (Self.Debug==2): print ("Requirement test: "+ReqCheck['CHECK']+": ")
				try:
					NewCommand = Command(ReqCheck['CHECK'])
					#CHECK 
					if(NewCommand.Execute(Self)):
						if (Self.Debug==2): print ("PASS")
					else:
						if (Self.Debug==2): print ("FAIL")
						Weight=-1000
				except:
					raise Exception ("List - Process Check Element - ")
			
		#CHECK IF WEIGHT IS GREATER THAN -1
		if (Weight > -1):
			#SET DEFUALT VALUE IF DEFINED
			if ('DEFAULT' in Config.Config): Weight = int(Config.Config['DEFAULT'])

			#SUM FORMAT WEIGHTS:
			if('FORMAT_DEFAULT' in Config.Config):
				for FormatVal in Self.FormatFlags.keys():											   
					if(Self.FormatFlags[FormatVal] == 1 and FormatVal in Config.Config['FORMAT_DEFAULT']):
						Weight += int(Config.Config['FORMAT_DEFAULT'][FormatVal])

			if (Self.Debug==2): print ("Weight Post Formats:" +str(Weight)) 
			
			#CHECK IF ALL TAGS
			CheckText = QuestionaireMisc.ClearTags(Text);
			if(re.search(r'[a-z0-9]',CheckText, re.IGNORECASE)): Self.TextProcessFlags['TEXT_ALL_TAGS']=0 
			
			#CHECK FOR KEYWORD DEFINITION 	
			if ('KEYWORDS' in  (Config.Config)):				
				RetWeight, RetAllPositiveUsed, RetAllNegativeUsed, RetAllUsed, RetKeywordCount = QuestionaireMisc.KeywordSearch(Text,Config.Config['KEYWORDS'])
				Weight += int(RetWeight)
				Self.TextProcessFlags['TEXT_ALL_TAGS']=1		
				Self.TextProcessFlags['TEXT_ALL_KEYWORDS']=RetAllUsed 
				Self.TextProcessFlags['TEXT_ALL_KEYWORDS_POSITIVE']=RetAllPositiveUsed
				Self.TextProcessFlags['TEXT_ALL_KEYWORDS_NEGATIVE']=RetAllNegativeUsed
				Self.TextProcessFlags['TEXT_KEYWORD_COUNT']=RetKeywordCount

			#STRIP LEADING AND TRAILING NON-ALPHANUMERIC VALUES FROM CHECK TEXT
			ClearCheckText = CheckText
			ClearCheckText = re.sub(r'^[^a-z0-9]+','',ClearCheckText, flags=re.IGNORECASE)
			ClearCheckText = re.sub(r'[^a-z0-9]+$','',ClearCheckText, flags=re.IGNORECASE)

			CheckText = re.sub(r"^\[","",CheckText)
			CheckText = re.sub(r"\]$","",CheckText)

			#ClearCheckText FOR STARTING KEYWORD DEFINITION 	
			if('KEYWORDS_START' in Config.Config):
				FirstWord = ""
				if(re.search(r'^([a-z0-9]+)',ClearCheckText, re.IGNORECASE)): FirstWord = re.search(r'^([a-z0-9]+)',ClearCheckText, re.IGNORECASE).group(1)
				FirstTwoWords = ""
				if(re.search(r'^([a-z0-9]+ [a-z0-9]+)',ClearCheckText, re.IGNORECASE)): FirstTwoWords = re.search(r'^([a-z0-9]+ [a-z0-9]+)',ClearCheckText, re.IGNORECASE).group(1)
				FirstTwoWords = FirstTwoWords.upper()
				FirstWord = FirstWord.upper()				
				#LOOP THROUGH KEYWORDS
				for Keyword in Config.Config['KEYWORDS_START'].keys():
					#CHECK FOR KEYWORK SEARCH NOT
					if (re.search(r'^'+Keyword, CheckText, re.IGNORECASE)):
						Weight += int(Config.Config['KEYWORDS_START'][Keyword])				
					#OTHERWISE MATCH AGAINST FIRST TWO WORD
					elif(FirstTwoWords == Keyword):
						Weight += int(Config.Config['KEYWORDS_START'][FirstTwoWords])			
					#OTHERWISE MATCH AGAINST FIRST WORD
					elif(FirstWord == Keyword):
						Weight += int(Config.Config['KEYWORDS_START'][Keyword]) 
			
			#ClearCheckText FOR STARTING KEYWORD DEFINITION 	
			if('KEYWORDS_END' in Config.Config):
				LastWord = ""
				if(re.search(r'([a-z0-9]+)$',ClearCheckText, re.IGNORECASE)): LastWord = re.search(r'([a-z0-9]+)$',ClearCheckText, re.IGNORECASE).group(1)
				LastTwoWords = ""
				if(re.search(r'([a-z0-9]+ [a-z0-9]+)$',ClearCheckText, re.IGNORECASE)): LastTwoWords = re.search(r'([a-z0-9]+ [a-z0-9]+)$',ClearCheckText, re.IGNORECASE).group(1)
				LastTwoWords = LastTwoWords.upper()
				LastWord = LastWord.upper()
				#LOOP THROUGH KEYWORDS
				for Keyword in Config.Config['KEYWORDS_END'].keys():					
					#CHECK FOR KEYWORK SEARCH NOT - DON'T WANT TO UPPER CASE THESE (DAMAGES EMBEDDED \d \s)
					if (re.search(Keyword+'$',CheckText, re.IGNORECASE)):
						Weight += int(Config.Config['KEYWORDS_END'][Keyword])				
					#OTHERWISE MATCH AGAINST FIRST TWO WORD
					elif(LastTwoWords == Keyword):
						Weight += int(Config.Config['KEYWORDS_END'][LastTwoWords])			
					#OTHERWISE MATCH AGAINST FIRST WORD
					elif(LastWord == Keyword):
						Weight += int(Config.Config['KEYWORDS_END'][Keyword])


			if (Self.Debug==2): print ("Weight Post Keyword:"+str(Weight)) 

			#LOOP THROUGH CHECKS
			if('CONDITIONS' in Config.Config):
				for Check in Config.Config['CONDITIONS']:
					if (Self.Debug==2): print (Check['CHECK']+": ", end="")
					try:			
						NewCommand = Command(Check['CHECK'])				
						if(NewCommand.Execute(Self)):
							Weight+=int(Check['WEIGHT'])

						if (Self.Debug==2): print (Weight)				
					except:
						raise Exception ("List - Process Check Element - "+Check['CHECK'])
					
			if (Self.Debug==2):print ("FINAL WEIGHT: "+str(Weight)+"\n") 

		return (Weight)


	############# QuestionairProcessCheck:Processor #############
	#FUNCTION:   Used by command to access referenced values - not currenlty setup
	#PARAMATERS: Value
	#RETURNS:	 Nothing
	def GetReference(Self, Type, Name):

		print("Reference: "+Type+" - "+Name)
		return(0)

	############# QuestionairProcessCheck:Processor #############
	#FUNCTION:   Used by command to trigger object specific functions
	#PARAMATERS: Value
	#RETURNS:	 Nothing
	def Processor(Self, Function, Paramaters):
		if(Function == 'CHECK_LIST_ID'):			
			return(Self.Question.CheckListID(Paramaters[0]))

		
		print("Processor: "+str(Function))
		return(0)

	############# QuestionairProcessCheck:GetValue #############
	#FUNCTION:   Used by command to trigger object specific functions
	#PARAMATERS: Value
	#RETURNS:	 Nothing
	def GetValue(Self, Value):		
		if(Value in Self.LogicCodes): return(Self.LogicCodes[Value])
		if(Value in Self.StateFlags): return(Self.StateFlags[Value])
		if(Value in Self.DefinedFlags): return(Self.DefinedFlags[Value])
		if(Value in Self.TextContentFlags): return(Self.TextContentFlags[Value])
		if(Value in Self.FormatFlags): return(Self.FormatFlags[Value])
		if(Value in Self.NumericValuesText): return(Self.NumericValuesText[Value])
		if(Value in Self.TextProcessFlags): return(Self.TextProcessFlags[Value])

		if(Value in Self.LogicCodes):
			return(Self.LogicCodes[Value])
		elif(re.search(r'^BLOCK_',Value)):
			Value = re.sub(r'^BLOCK_','',Value)
			if (not(Self.BlockTrack is None) and Value in Self.BlockTrack.Flags): return(Self.BlockTrack.Flags[Value])
			if (not(Self.BlockTrack is None) and Value in Self.BlockTrack.NumericValues): return(Self.BlockTrack.NumericValues[Value])
		elif(re.search(r'^TABLE_',Value)):			
			Value = re.sub(r'^TABLE_','',Value)
			#TABLE IS OPTIONAL DISPLAY 0 IF NOT DEFINED
			if(Self.TableTrack is None): return(0)
			if (Value in Self.TableTrack.Flags): return(Self.TableTrack.Flags[Value])
			if (Value in Self.TableTrack.NumericValues): return(Self.TableTrack.NumericValues[Value])
		elif(re.search(r'^LIST_DEF_', Value)):
			Value = re.sub(r'^LIST_DEF_','',Value)			
			#LIST DEF IS OPTIONAL DISPLAY 0 IF NOT DEFINED
			if(Self.ListDefTrack is None): return(0)
			if (Value in Self.ListDefTrack.Flags): return(Self.ListDefTrack.Flags[Value])
			if (Value in Self.ListDefTrack.NumericValues): return(Self.ListDefTrack.NumericValues[Value])
		elif(re.search(r'^QUESTION_',Value)):
			Value = re.sub(r'^QUESTION_','',Value)
			if (not(Self.QuestionTrack is None) and Value in Self.QuestionTrack.Flags): return(Self.QuestionTrack.Flags[Value])
			if (not(Self.QuestionTrack is None) and Value in Self.QuestionTrack.NumericValues): return(Self.QuestionTrack.NumericValues[Value])
		elif(re.search(r'^LIST_',Value)):
			Value = re.sub(r'^LIST_','',Value)				
			#LIST DEF IS OPTIONAL DISPLAY 0 IF NOT DEFINED
			if(Self.ListTrack is None): return(0)		
			if (Value in Self.ListTrack.Flags): return(Self.ListTrack.Flags[Value])
			if (Value in Self.ListTrack.NumericValues): return(Self.ListTrack.NumericValues[Value])

		print("TYPE:"+Self.ProcessType)
		print(Self.LogicCodes)
		print(Value in Self.LogicCodes)
		print("GetValue: Error Missing Value: "+Value)
		return("")

####################################### QUESTIONAIRE VALUE TRACK #########################################
class QuestionaireValueTrack:
	######################################################################################################################
	################################### QUESTIONAIRE PROCESS CHECK - INITIALIZATION ######################################
	######################################################################################################################
	############# QuestionaireValueTrack:Init #############
	#FUNCTION:   Object Constructor - Builds a Question Vlaue Track
	#RETURNS:	 Nothing
	#PARAMATERS: Nothing
	def __init__ (Self):	
		Self.Type=""
		Self.TextList = []
		Self.NumericValues = {'LENGTH':0,'LENGTH_AVERAGE':0,'LENGTH_STD_DEV':0,'BREAK_COUNT':0}
		Self.BreakFlag = 0				#FLAG FOR BREAKS, TO PREVENT MULTIPLE BLANK LINES FROM REPEATED INCREMENTS
		Self.Flags  = {}

	######################################################################################################################
	#################################### QUESTIONAIRE PROCESS CHECK - VALUE SETTING ######################################
	######################################################################################################################
	############# QuestionaireValueTrack:AddText #############
	#FUNCTION:   Adds a line of text to the structure
	#PARAMATERS: Question Text Array
	#RETURNS:	 Nothing		
	def AddText(Self, Text):	
		Self.TextList.append(Text)
		Self.NumericValues['LENGTH']+=1
		Self.NumericValues['INDEX']=0
		Self.NumericValues['LENGTH_AVERAGE']=0

		#CHECK FOR BREAK
		if(QuestionaireMisc.ClearTags(Text) == ""): Self.AddBreak()	
		else: Self.BreakFlag = 0	
		
		#SET LINE LENGTH AVERAGE		
		for Line in Self.TextList:
			CleanLine = QuestionaireMisc.ClearTags(Line)
			Self.NumericValues['LENGTH_AVERAGE']+=len(CleanLine)
		Self.NumericValues['LENGTH_AVERAGE']= Self.NumericValues['LENGTH_AVERAGE']/Self.NumericValues['LENGTH']
		#SET STANDARD DEVIATION
		Self.NumericValues['LENGTH_STD_DEV']=0
		for Line in Self.TextList:
			CleanLine = QuestionaireMisc.ClearTags(Line)			
			Self.NumericValues['LENGTH_STD_DEV']+=abs(len(CleanLine)-Self.NumericValues['LENGTH_AVERAGE'])	
		Self.NumericValues['LENGTH_STD_DEV']=math.sqrt(Self.NumericValues['LENGTH_STD_DEV']/Self.NumericValues['LENGTH'])	

	############# QuestionaireValueTrack:AddBreak #############
	#FUNCTION:   Increments the break coutner
	#PARAMATERS: Question Text Array
	#RETURNS:	 Nothing	
	def AddBreak(Self):
		if(Self.BreakFlag == 0):
			Self.NumericValues['BREAK_COUNT']+=1
			Self.BreakFlag = 1

	######################################################################################################################
	################################ QUESTIONAIRE LIST DEF TRACK - TESTING FUNCTIONS #####################################
	######################################################################################################################
	############# QuestionaireValueTrack:Test Prints #############	
	#FUNCTION: Prints the current values of the object
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def TestPrint(Self):
		print("NumLines: "+str(Self.NumericValues['NumLines']))
		print("LineLengthAverage: "+str(Self.NumericValues['LineLengthAverage']))
		print("LineLengthStdDev: "+str(Self.NumericValues['LineLengthStdDev']))
		print("BreakCount: "+str(Self.NumericValues['BreakCount']))
		print("Flags: "+str(Self.Flags))
		print("TextList: ", end="")
		print(str(Self.TextList).encode('utf-8'))
		print("NumericValues: "+str(Self.NumericValues))
		print("BreakFlag: "+str(Self.BreakFlag))

####################################### QUESTIONAIRE BLOCK TRACK #########################################
class QuestionaireBlockTrack (QuestionaireValueTrack):
	############# QuestionaireBlockTrack:Init #############
	#FUNCTION:   Object Constructor - Builds a Question Vlaue Track
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def __init__ (Self):		
		QuestionaireValueTrack.__init__(Self)	
		Self.Type="Block"
		AddedValues = {'COUNT_LIST_DEF':0}
		Self.NumericValues =  {**Self.NumericValues , **AddedValues}
		
	############# QuestionaireValueTrack:AddText #############
	#FUNCTION:   Adds a line of text to the structure
	#PARAMATERS: Question Text Array
	#RETURNS:	 Nothing		
	def AddText(Self, Text):
		QuestionaireValueTrack.AddText(Self, Text)	
        #IF LIST DEF
		if(re.search(r'<<LIST_ID=(\d+)',Text)):	
			Self.NumericValues['COUNT_LIST_DEF']+=1
####################################### QUESTIONAIRE TABLE TRACK #########################################
class QuestionaireTableTrack(QuestionaireValueTrack):
	############# QuestionaireTableTrack:Init #############
	#FUNCTION:   Object Constructor - Builds a Question Vlaue Track
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def __init__ (Self):		
		QuestionaireValueTrack.__init__(Self)	
		AddedValues = {'COUNT_ROW':0,'COUNT_COL':0,'TAB_AVERAGE':0}
		Self.NumericValues =  {**Self.NumericValues , **AddedValues}
		Self.Type="Table"

	############# QuestionaireValueTrack:AddText #############
	#FUNCTION:   Adds a line of text to the structure
	#PARAMATERS: Question Text Array
	#RETURNS:	 Nothing		
	def AddText(Self, Text):
		QuestionaireValueTrack.AddText(Self, Text)	
		Self.NumericValues['COUNT_ROW']+=1
		if(Self.NumericValues['COUNT_COL']==0):
			Self.NumericValues['COUNT_COL'] = len(Text.split('<<T>>'))
		#BUILD TAB AVERAGE
		for Line in Self.TextList:
			Self.NumericValues['TAB_AVERAGE']+=len(Line.split('<<T>>'))
		Self.NumericValues['TAB_AVERAGE'] = Self.NumericValues['TAB_AVERAGE']/Self.NumericValues['COUNT_ROW']

####################################### QUESTIONAIRE LIST DEF TRACK #########################################
class QuestionaireListDefTrack (QuestionaireValueTrack):

	############# QuestionaireListDefTrack:Init #############
	#FUNCTION:   Object Constructor - Builds a Question Vlaue Track
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def __init__ (Self):		
		QuestionaireValueTrack.__init__(Self)	
		AddedValues = {'QUESTION_TEXT':0,'QUESTION_ID':0,'BROKEN':0}
		Self.Flags =  {**Self.Flags , **AddedValues}
		Self.Type="ListDef"

####################################### QUESTIONAIRE QUESTION TRACK #########################################
class QuestionaireQuestionTrack (QuestionaireValueTrack):

	############# QuestionaireQuestionTrack:Init #############
	#FUNCTION:   Object Constructor - Builds a Question Vlaue Track
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def __init__ (Self):		
		QuestionaireValueTrack.__init__(Self)	
		AddedValues = {'NUM_LISTS':0}
		Self.NumericValues =  {**Self.NumericValues , **AddedValues}
		Self.Type="Question"

####################################### QUESTIONAIRE LIST TRACK #########################################
class QuestionaireListTrack (QuestionaireValueTrack):

	############# QuestionaireListTrack:Init #############
	#FUNCTION:   Object Constructor - Builds a List Vlaue Track
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def __init__ (Self):		
		QuestionaireValueTrack.__init__(Self)	
		AddedValues = {'INDEX':0}		
		Self.NumericValues =  {**Self.NumericValues , **AddedValues}
		Self.Type="List"
