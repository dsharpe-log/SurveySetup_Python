
import sys
import roman
import re


import QuestionaireMisc

from QuestionaireList import QuestionaireList
from QuestionaireListItem import QuestionaireListItem
from QuestionaireLine import QuestionaireLine
from QuestionaireLogic import QuestionaireLogic
from QuestionaireSegment import QuestionaireSegment

from QuestionaireCleanUp import QuestionaireCleanUp
from QuestionaireProcessCheck import QuestionaireProcessCheck
from QuestionaireProcessCheck import QuestionaireListTrack

#from QuestionaireProcessCheck import QuestionaireProcessCheckLine
#from QuestionaireProcessCheck import QuestionaireProcessCheckQuestion
#from QuestionaireProcessCheck import QuestionaireProcessCheckSegment

########################################################################################################
########################################## QUESTIONAIRE QUESTION #######################################
########################################################################################################
#DESCRIPTION: Class structure used to hold a question - used by Questionaire
#TODO:
#CHANGE LOG:

########################################################################################################
################################################# NOTES ################################################
########################################################################################################

########################################### QUESTION FLAGS #############################################

MODEL_LINE_TYPE = {
	'0':"ID",
	'1':"TEXT",
	'2':"LIST",
	'3':"TABLE_HEADING",
	'4':"SECOND_TABLE_HEADING",
	'5':"LOGIC"
}


VALID_IDS = {	
	'ADDED_TERM':1,
	'QUESTION_ID':1,
	'QUESTION_TEXT':1,
	'QUESTION_MIN':1,
	'QUESTION_MAX':1,
	'QUESTION_SKIP_LOGIC':1,
	'QUESTION_SKIP_LOGIC_TEXT':1,
	'QUESTION_EXTRA_LOGIC':1,
	'QUESTION_OPTIONAL': 1,  #CURRENTLY UN-POPULATED
	'CHOICE_RANDOMIZE':1,
	'CHOICE_ID':1,	
	'CHOICE_INDEX':1,	
	'CHOICE_FIRST_ID':1,
	'CHOICE_LAST_ID':1,	
	'CHOICE_TEXT':1,
	'CHOICE_LIST':1,
	'CHOICE_LENGTH':1,
	'CHOICE_OTHER':1,
	'CHOICE_NONE':1,
	'CHOICE_DONT_KNOW':1,
	'CHOICE_REFUSED':1,
	'CHOICE_HEADING':1,
	'CHOICE_LIST_SKIP_LOGIC':1,
	'CHOICE_LIST_SKIP_LOGIC_TEXT':1,
	'STATEMENT_1_RANDOMIZE':1,
	'STATEMENT_1_ID':1,
	'STATEMENT_1_INDEX':1,
	'STATEMENT_1_FIRST_ID':1,
	'STATEMENT_1_LAST_ID':1,
	'STATEMENT_1_TEXT':1,
	'STATEMENT_1_LIST_SKIP_LOGIC':1,
	'STATEMENT_1_LIST_SKIP_LOGIC_TEXT':1,
	'STATEMENT_1_LIST':1,
	'STATEMENT_2_RANDOMIZE':1,
	'STATEMENT_2_ID':1,
	'STATEMENT_1_INDEX':1,
	'STATEMENT_2_FIRST_ID':1,
	'STATEMENT_2_LAST_ID':1,
	'STATEMENT_2_TEXT':1,
	'STATEMENT_2_LIST':1,
	'STATEMENT_2_LIST_SKIP_LOGIC':1,
	'STATEMENT_2_LIST_SKIP_LOGIC_TEXT':1
}



LINE_TYPE_ID               		= 0
LINE_TYPE_TEXT             		= 1
LINE_TYPE_LIST			 		= 2
LINE_TYPE_TABLE_HEADING			= 3
LINE_TYPE_SECOND_TABLE_HEADING	= 4
LINE_TYPE_LOGIC					= 5

#SEGMENT TYPES
SEGMENT_TYPE_TEXT              = 0
SEGMENT_TYPE_ID                = 1
SEGMENT_TYPE_LOGIC	           = 2
SEGMENT_TYPE_LEADING_ID	       = 3
SEGMENT_TYPE_TRAILING_ID	   = 4
SEGMENT_TYPE_LIST        	   = 5

####################################### QUESTIONAIRE QUESTION #########################################
class QuestionaireQuestion (QuestionaireProcessCheck):
	DefineFlags = ['DEFINED_CHOICE','DEFINED_STATEMENTS']
	NumericLineValues=['CHOICE_COUNT','STATEMENT_COUNT','CHOICE_SPECIAL_COUNT']
  	
	########################################################################################################
	##################################### QUESTIONAIRE QUESTION - INIT #####################################
	########################################################################################################
	############# QuestionaireQuestion:Init #############
	#FUNCTION:   Object Constructor - Builds a Question object
	#PARAMATERS: Question Text Array
	#RETURNS:	 Nothing
	def __init__ (Self, FileName, LineList, Configs, QuestionIDTrack, TrackOutput, Debug=0):
		QuestionaireProcessCheck.__init__(Self, None,Debug)	
		Self.ProcessType = "QUESTION"
		
		def PopulateValues(DefaultList):
			ReturnList={}
			for Key in DefaultList:
				ReturnList[Key] =0
			return (ReturnList)

		Self.FileName = FileName
		Self.LineList = LineList
		#ADD QUESTIN REFERENCE TO QUESTION
		for Line in Self.LineList:	
			Line.Question = Self
		Self.TrackOutput = TrackOutput	
		
		Self.QuestionID = ""
		Self.Configs = Configs		
		Self.QuestionIDTrack = QuestionIDTrack			
		Self.QuestionTrack = LineList[0].QuestionTrack		#QUESTION PROCESS TRACK
		

		Self.QuestionText = ""	#TEXT OF THIS QUESTION0		
		Self.QuestionType = ""	#TYPE OF THIS QUESTION0		

		Self.Lists = []         #LIST OF LISTS IN THE QUESTION
		Self.Choices=None       #LIST OF CHOICES
		Self.Statements=[]      #LIST OF STATEMENT LISTS	
		Self.Logic=[]           #LIST OF LOGICAL CONDITIONS
		Self.NextLineLogic={}   #LIST OF LOGICAL CONDITIONS FOR NEXT LINE
		Self.NextListLogic={}   #LIST OF LOGICAL CONDITIONS FOR NEXT LIST - TECHNICALLY NOT ALWAYS THE NEXT LIST GENERATED, APPLIED UPON PROCESSING THE NEXT LINE
		
		Self.ProcessState = ""

		Self.LogicCodes["QUESTION_MIN"]=1
		Self.LogicCodes["QUESTION_MAX"]=1
		Self.LogicCodes["MULTI"]=0
	
		Self.CurrentList = None	#CURRENT LIST BEING BUILT

		Self.DefinedFlags = PopulateValues(QuestionaireQuestion.DefineFlags)
		Self.NumericValuesText= PopulateValues(QuestionaireQuestion.NumericLineValues)   
	
		for Value in Self.Configs['TRACKING_VALUES']['QUESTION_VALUE']:
			Self.LogicCodes[Value]=0
		
		Self.InitLogicCodes(Configs,'QUESTION_VALUE')
		Self.InitLineTypes()
		
		
	############# QuestionaireQuestion:InitLineTypes #############
	#FUNCTION:   Initializes the type of each line in the question
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def InitLineTypes(Self):
		DefinedFlags = {}		#USED TO TRACK DEFINED FLAGS AS QUESTION IS PROCESSED - USED TO UPDATE PROCESS CHECK STRUCTURES
		StateFlags = {}			#USED TO TRACK STATE FLAGS AS QUESTION IS PROCESSED - USED TO UPDATE PROCESS CHECK STRUCTURES
		PrevNextLine={}			#HOLDING VARIABLE FOR PREVIOUS NEXT LINE LOGIC FLAGS

		ListTrack = None		#HOLDING VARIABLE FOR CURRENT LIST TRACK DATA STRCUTUR		

		CurrentListID = ""		#LAST ID USED IN A LIST
		LastState = ""			#LAST STATE PROCESSED

		if(Self.Debug > 0):
			print("")
			for Line in Self.LineList:
				print(Line.Text)

		#LOOP THROUGH EACH LINE
		for Line in Self.LineList:
			
			Line.MergeFlags(DefinedFlags)		
			Line.MergeFlags(StateFlags)			
			
			
			#ADD NEXT LIEN LOGIC FLAGS	
			for Element in Self.NextLineLogic.keys():
				Line.LogicCodes[Element] = Self.NextLineLogic[Element]
			
			#CLEAR NEXT LINE FLAG
			PrevNextLine = Self.NextLineLogic.copy() #VARIABLE USED TO HOLD PREVIOUS NEXT LINE LOGIC, USED IF SECOND LOGIC LINE IS DEFINED YO FURTHER PROJECT THESE VALUES
			Self.NextLineLogic = {}	
			
			Line.SetType()		

			#CHECK FOR PROCESS STATE
			if('PROCESS_STATES' in Self.Configs['MAIN_CONFIG'].Config):				
				for State in Self.Configs['MAIN_CONFIG'].Config['PROCESS_STATES']:
					for Word in State['WORDS']:						
						if(Word in Line.Text):
							if(Self.Debug > 0): print("FOUND STATE: "+State['STATE'])
							Self.ProcessState = State['STATE']		
							Line.Text = Line.Text.replace(Word,'')							
							#APPEND PREV NEXT LINE LOGIC
							for Element in PrevNextLine.keys():
								Self.NextLineLogic[Element] = PrevNextLine[Element]		
							break
							
			LineText = Line.Text
			if(QuestionaireMisc.ClearTags(LineText)==""): continue
			
			#CLEAR STATE VARIABLES
			StateFlags={}
			#QUESTION ID	
			if((Line.LineType == 'ID' and Self.ProcessState == "") or (Self.ProcessState == "Q_TEXT" and (Line.LineType == 'ID'))):
				DefinedFlags['DEFINED_QUESTION_ID'] = 1
				StateFlags['IN_ID_LINE'] = 1
				if (re.search(r'ID_VALUE=([^>]+)', LineText)):
					Self.QuestionID = re.search(r'ID_VALUE=([^>]+)', LineText).group(1)					
				else:
					FirstWordLine = LineText + " "
					FirstWordLine = QuestionaireMisc.ClearTags(FirstWordLine)
					FirstWordLine = re.sub(r'^Q\.', '', str(FirstWordLine))
					FirstWordLine = re.sub(r'\.', '. ', str(FirstWordLine))
					if(re.search(r'^\s*(\S+) ', str(FirstWordLine))):
						FirstWordLine = re.search(r'^\s*(\S+) ', str(FirstWordLine)).group(1)
					Self.QuestionID = FirstWordLine
					LineText = re.sub(r'(Q)?(\.)?' + re.escape(Self.QuestionID), '', LineText)

				Self.QuestionID = re.sub(r'[^0-9a-zA-Z]+', '', Self.QuestionID)
				Self.QuestionID = Self.QuestionID.upper()
				Self.QuestionIDTrack[Self.QuestionID] = 1
				
				Line.StateFlags['IS_ID_LINE']=1						 
				#CHECK IF LINE STILL CONTAINS TEXT
				if(re.search(r'[A-Za-z0-9]', QuestionaireMisc.ClearTags(LineText))):								   
					TextLine = QuestionaireLine(Self, LineText, Line.Index, Line.PrevIDType, Line.ListDefTrack, Line.TableTrack, Line.BlockTrack, Line.QuestionTrack, Line.ListTrack, Line.StateFlags, Line.DefinedFlags, Self.TrackOutput, Self.Configs, Self.FileName, False, Self.Debug)					
					Line.StateFlags['IS_TEXT']=1
					#MIGHT WANT TO MOVE THIS LATER TO CONSIDER THE ENTIRE QUESTION TEXT - NOT SURE IF THIS WILL BE NECESSARY
					Logic = QuestionaireLogic("QUESTION_TEXT", Line, None, Self, LineText, Line.Index, Line.PrevIDType, Line.ListDefTrack, Line.TableTrack, Line.BlockTrack, Line.QuestionTrack, Line.ListTrack, Line.StateFlags, Line.DefinedFlags, Self.TrackOutput, Self.Configs, Self.FileName, False, Self.Debug, Logic=Line.LogicCodes)				
				
					#ADD NEW LINE AFTER CURRENT LINE
					Self.AddQuestionText(TextLine)
					DefinedFlags['DEFINED_QUESTION_TEXT'] = 1
				LastState = "ID"
			#QUESTION TEXT
			elif((Line.LineType == 'TEXT' and Self.ProcessState == "") or Self.ProcessState == "Q_TEXT"):
				DefinedFlags['DEFINED_QUESTION_TEXT'] = 1
				StateFlags['IN_TEXT'] = 1
				Line.StateFlags['IS_TEXT']=1						 
				#IF NO ID SET AND THE LINE CONTAINS A LIST DEF		
				if(not('DEFINED_QUESTION_ID' in DefinedFlags) and re.search(r"ID_VALUE=([^>]+)",LineText)):										
					Self.QuestionID = re.search(r"ID_VALUE=([^>]+)",LineText).group(1)
					Self.QuestionID = re.sub(r'[^0-9a-z]+', '', Self.QuestionID, flags=re.IGNORECASE)					
					Self.QuestionID = Self.QuestionID.upper()
					DefinedFlags['DEFINED_QUESTION_ID'] = 1	
					Self.QuestionIDTrack[Self.QuestionID] = 1
						
				Logic = QuestionaireLogic("QUESTION_TEXT", Line, None, Self, LineText, Line.Index, Line.PrevIDType, Line.ListDefTrack, Line.TableTrack, Line.BlockTrack, Line.QuestionTrack, Line.ListTrack, Line.StateFlags, Line.DefinedFlags, Self.TrackOutput, Self.Configs, Self.FileName, False, Self.Debug, Logic=Line.LogicCodes)				
				Self.AddQuestionText(Line)
				LastState = "TEXT"
			#LOGIC
			elif((Line.LineType == 'LOGIC' and Self.ProcessState == "") or Self.ProcessState == "Q_LOGIC"):
				DefinedFlags['DEFINED_LOGIC'] = 1
				StateFlags['IN_LOGIC'] = 1
				Line.StateFlags['IS_LOGIC']=1
				#NEED TO UPDATE THIS DEFINITION WITH LOGIC SPECIFIC CONTEXT FLAGS
				Logic = QuestionaireLogic("QUESTION", Line, None, Self, LineText, Line.Index, Line.PrevIDType, Line.ListDefTrack, Line.TableTrack, Line.BlockTrack, Line.QuestionTrack, Line.ListTrack, Line.StateFlags, Line.DefinedFlags, Self.TrackOutput, Self.Configs, Self.FileName, False, Self.Debug, Logic=Line.LogicCodes)								
				Self.Logic.append(Logic)
				LastState = "LOGIC"
				#APPEN PREV NEXT LINE LOGIC
				for Element in PrevNextLine.keys():
					Self.NextLineLogic[Element] = PrevNextLine[Element]				
			#LIST
			elif((Line.LineType == 'LIST' or Line.LineType == 'LIST_HEADING' and Self.ProcessState == "") or (Self.ProcessState == "Q_CHOICE" or Self.ProcessState == "Q_STATEMENT") or (LastState == "TABLE_HEAIDNG" and Self.ProcessState == "Q_GRID")):								 
				DefinedFlags['DEFINED_LIST'] = 1
				StateFlags['IN_LIST'] = 1
				Line.StateFlags['IS_LIST']=1				
				if(Line.LineType == 'LIST_HEADING'):					
					DefinedFlags['DEFINED_LIST_HEADING'] = 1
					StateFlags['IN_LIST_HEADING'] = 1
					Line.StateFlags['IS_LIST_HEADING']=1
				
				ListItemStruct = QuestionaireListItem(Self, Self.CurrentList, LineText, Line.Index, CurrentListID, Line.PrevIDType, Line.ListDefTrack, Line.TableTrack, Line.BlockTrack, Line.QuestionTrack, Line.ListTrack, Line.StateFlags, Line.DefinedFlags, Self.TrackOutput, Self.Configs, Self.FileName, False, Self.Debug, Logic=Line.LogicCodes)
				ListItemStruct.NumericValuesText['LIST_DEF_ID_PREV'] = Line.NumericValuesText['LIST_DEF_ID_PREV']
				Line.ListTrack = ListTrack
				ListItemStruct.ListTrack = ListTrack
				CurrentListID = ListItemStruct.ListItemID			

				#CHECK IF A NEW LIST IS NEEEDED - EITHER NO LIST EXISTS OR A NEW LIST IS DEFINED
				if (Self.CurrentList is None or (Self.ProcessState == "" and ListItemStruct.CheckNewList()) or (Self.ProcessState != "" and ((Self.ProcessState == "Q_CHOICE" and Self.CurrentList.ListType != "CHOICE") or (Self.ProcessState == "Q_STATEMENT" and Self.CurrentList.ListType != "STATEMENT")))):
					Self.CurrentList = QuestionaireList(Self, len(Self.Lists), Self.TrackOutput, Self.Configs, Self.FileName, Self.Debug)
					Self.QuestionTrack.NumericValues ['NUM_LISTS']+=1
					ListTrack = QuestionaireListTrack()
					ListTrack.NumericValues ['INDEX'] =len(Self.Lists)
					#SET LIST TYPE IF TYPE IS SET 
					if(Self.ProcessState != ""):
						#SET AS CHOICE
						if(Self.ProcessState == "Q_CHOICE"):
							Self.CurrentList.ListType = "CHOICE"	
						#SET AS STATEMENT
						if(Self.ProcessState == "Q_STATEMENT"):
							Self.CurrentList.ListType = "STATEMENT"	
					ListItemStruct.List = Self.CurrentList
					Line.ListTrack = ListTrack
					Self.CurrentList.ListTrack = ListTrack
					ListItemStruct.ListTrack = ListTrack
					Self.Lists.append(Self.CurrentList)					
					#ADD NEXT LINE LOGIC FLAGS

				#UPDATE LIST WITH ANY NEXT LIST LOGIC DEFINED AND THEN CLEAR
				for Element in Self.NextListLogic.keys():
					Self.CurrentList.LogicCodes[Element] = Self.NextListLogic[Element]
				#CLEAR NEXT LIST FLAGS
				Self.NextListLogic = {}	
						
				#ADD LIST ENTRY TO LIST		
				ListTrack.AddText(Line.Text)	
				Self.CurrentList.AddListItem(ListItemStruct)
				if(Line.LineType == 'LIST_HEADING'):
					ListItemStruct.SetType('LIST_HEADING')
					Self.CurrentList.SetFlagValue('DEFINED_LIST_HEADING',1)
				LastState = "LIST"
			#TABLE HEADING
			elif((Line.LineType == 'TABLE_HEADING' and Self.ProcessState == "") or Self.ProcessState == "Q_GRID"):
				DefinedFlags['DEFINED_LIST'] = 1
				DefinedFlags['DEFINED_TABLE_HEADING'] = 1	
				StateFlags['IN_TABLE_HEADING'] = 1
				Line.StateFlags['IS_TABLE_HEADING']=1
		
				Delimit = QuestionaireMisc.GetDelimiter(LineText)
				
				HeadingList = LineText.split(Delimit)
				HeadingList = QuestionaireMisc.CleanupListTags(HeadingList)
				Self.CurrentList = QuestionaireList(Self, len(Self.Lists), Self.TrackOutput, Self.Configs, Self.FileName, Self.Debug)
				Self.CurrentList.SetFlagValue('IN_TABLE_HEADING',1)	
				Self.QuestionTrack.NumericValues ['NUM_LISTS']+=1
				ListTrack = QuestionaireListTrack()
				ListTrack.NumericValues ['INDEX'] =len(Self.Lists)
				Self.Lists.append(Self.CurrentList)
				FillCol=0	#FLAG TRACKING IF A COLUMN IS FILLED
				#LOOP THORUGH LINE SPLITS 
				for Item in HeadingList:
					#CHECK IF THE CURRENT COLUMN HAS TEXT, OR IF LITS ITEMS HAVE ALREADY BEEN ADDED (WANT TO MAINTAIN POST START BLANKS)
					if(re.search(r"[0-9a-z]",QuestionaireMisc.ClearTags(Item),re.IGNORECASE) or FillCol==1):
						ListItemStruct = QuestionaireListItem(Self,Self.CurrentList, Item, Line.Index, CurrentListID, Line.PrevIDType, Line.ListDefTrack, Line.TableTrack, Line.BlockTrack, Line.QuestionTrack, ListTrack, Line.StateFlags, Line.DefinedFlags, Self.TrackOutput, Self.Configs, Self.FileName, False, Self.Debug,Logic=Line.LogicCodes)
						ListItemStruct.NumericValuesText['LIST_DEF_ID_PREV'] = Line.NumericValuesText['LIST_DEF_ID_PREV']
						CurrentListID = ListItemStruct.ListItemID
						ListItemStruct.ListTrack = ListTrack
						ListTrack.AddText(Item)	
						Self.CurrentList.AddListItem(ListItemStruct)
						FillCol=1
				Self.CurrentList.ListTrack = ListTrack
				LastState = "TABLE_HEADING"			
				if(Self.ProcessState == "Q_GRID"):
					#SET GRID FLAG
					Self.CurrentList.ListType = "CHOICE"
					Self.ProcessState = "Q_STATEMENT"
			#SECOND TABLE HEADING
			elif(Line.LineType == 'SECOND_TABLE_HEADING' and Self.ProcessState == ""):
				DefinedFlags['DEFINED_LIST'] = 1			
				DefinedFlags['DEFINED_SECOND_TABLE_HEADING'] = 1	
				StateFlags['IN_TABLE_HEADING'] = 1

				Delimit = QuestionaireMisc.GetDelimiter(LineText)
				HeadingList = LineText.split(Delimit)                                            
				Self.CurrentList.MergeLabels (HeadingList, Line, CurrentListID, DefinedFlags, StateFlags, Self.TrackOutput, Self.Configs, Self.FileName, Self.Debug)
				LastState = "SECOND_TABLE_HEADING"
    #DefineFlags = ['DEFINED_LIST','DEFINED_LIST_HEADING','DEFINED_LOGIC','DEFINED_QUESTION_ID','DEFINED_QUESTION_TEXT','DEFINED_TABLE_HEADING','DEFINED_SECOND_TABLE_HEADING','DEFINED_CHOICE','DEFINED_STATEMENTS','DEFINED_INSTRUCTIONS']
    #StateFlags = ['IN_ID_LINE','IN_LIST','IN_TABLE_DEF','IN_TABLE','IN_POST_TABLE','IN_TEXT','IN_LOGIC','IN_LIST_HEADING','IN_TABLE_HEADING','IN_LIST_DEF','IN_BLANK_LINE']

	############# QuestionaireQuestion:BuildQuestion #############
	#FUNCTION:   Runs a series of functions to build the question
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def BuildQuestion(Self):
		Weights = {}	#HOLDS THE WEIGHTS OF EACH QUESTION TYPE
		if(Self.Debug ==2):	
			print("BUILDING QUESTION + "+Self.QuestionID)
		#FOR EACH LIST SET SCALE FLAG
		NewLists = []
		for Index, List in enumerate(Self.Lists):
			List.RemoveBlankElements()
			if(len(List.ListItems)==0): continue
			#IF ONLY ONE ITEM IN LIST ADD IT TO THE NEXT LIST AND DELETE CURRENT ONE
			if(len(List.ListItems)==1 and Index+1 < len(Self.Lists)):
				Self.Lists[Index+1].ListItems.insert(0,List.ListItems[0])							
			else:
				NewLists.append(List)	
				if(Self.Debug ==2): 
					print("SET ID")			
				List.SetListIDS()
				if(Self.Debug == 2): 
					print("SET LIST FLAGS")			
				List.ProcessListFlags()			
		Self.Lists = NewLists

		#SET CHOICE LIST
		if(Self.ProcessState == ""):
			for Index,List in enumerate(Self.Lists):	
				Weights[Index] = List.ChoiceWeight

		if(Self.Debug == 2): 
			print("SELECT CHOICE")			
		ChoiceIndex = QuestionaireMisc.SelectHigh(Weights,Self.Debug)
		for Index,List in enumerate(Self.Lists):
			if(Index == ChoiceIndex or List.ListType == "CHOICE"):
				Self.Choices = List
				List.ListType = "CHOICE"				
				Self.DefinedFlags['DEFINED_CHOICE'] = 1
				Self.NumericValuesText['CHOICE_COUNT'] = len(List.ListItems)
				#LOOP THROUGH CHOICES
				for Choice in List.ListItems:
					if("SPECIAL" in Choice.LogicCodes and int(Choice.LogicCodes['SPECIAL']) == 1):
						Self.NumericValuesText['CHOICE_SPECIAL_COUNT'] += 1
			else:
				Self.Statements.append(List)
				List.ListType = "STATEMENT"
				Self.DefinedFlags['DEFINED_STATEMENTS'] = 1

				#TODO - FIGURE OUT A DYNAMIC MECHANISM TO COMPENSATE FOR RANDOMIZATION BEING APPLIED TO CHOICES RATHER THAN STATEMENTS
				#CURRENTLY CHECKS IF THE QUESTION HAS A RANDOMIZE TAG IN LOGIC AND PROJECTS IT INTO STATEMENTS LIST
				if(Self.LogicCodes["RANDOMIZE"] == 1):
					List.LogicCodes['RANDOMIZE'] = 1
					
				#HARD OVERRIDE FOR 
				Self.NumericValuesText['STATEMENT_COUNT'] = len(List.ListItems)
			#SET ID TYPE FOR LIST
			List.SetListIDS()
			#UPDATE IDS IN LIST
			List.ReformatIDs()

		#CONFIRM DEFINED
		Weights = {}
		
		#LOOP THROUGH EACH LIST BUILDING SETTING FLAGS AND COMPUTING THE STATEMENT VS CHOICE WEIGHT
		for QType in Self.Configs["QTYPE_CONFIG"].keys():
			Weights[QType] = Self.CheckElements(Self.Configs['QTYPE_CONFIG'][QType],Self.QuestionText)
		
		Self.QuestionType = QuestionaireMisc.SelectHigh(Weights,Self.Debug)
		if(Self.TrackOutput):
			FileTrackOutHandle = open(Self.Configs['TRACK_OUTPUT_FILE']+"_QUESTION.txt", 'a')	#OUTPUT FILE HANDLE
			FileTrackOutHandle.write(Self.QuestionType+"\n")
			FileTrackOutHandle.close()

		#CLEAN UP ID
		Self.QuestionID = QuestionaireMisc.ClearTags(Self.QuestionID)
		Self.QuestionID = re.sub(r'\s', '', Self.QuestionID)


		Self.Finalize()

	############# QuestionaireQuestion:Add Question Text #############
	#FUNCTION:   Updates the question text
	#PARAMATERS: Line Structure to add
	#RETURNS:	 Nothing
	def AddQuestionText(Self, Line):
		#SET NEW LINE FLAG
		AddNewLine = 1	#NEW LINE FLAG - TRIGGERS THE ADDITION OF A NEW LINE IF THE CURRENT LINE IS EMPTY
		if(Self.QuestionText == ""):
			AddNewLine = 0

		Segments = QuestionaireMisc.SegmentText(Line.Text)
		
		#PROCESS SEGMENTS
		for SegmentIndex, SegmentText in enumerate(Segments):						
			#BUILD SEGMENT OBJECT				
			Segment = QuestionaireSegment(Self, SegmentText, SegmentIndex, len(Segments), Line.ListDefTrack, Line.TableTrack, Line.BlockTrack, Line.QuestionTrack, Line.ListTrack, Self.TrackOutput, Self.Configs, Self.Debug)
			#ID
			if(Segment.Type == 'ID'):
				Self.QuestionID += Segment.Text
			#TEXT
			elif(Segment.Type == 'TEXT'):
				if(AddNewLine):
					Self.QuestionText += "<<N>>"
					AddNewLine = 0
				Self.QuestionText += Segment.Text
			#LOGIC
			elif(Segment.Type == 'LOGIC'):				                     
				Logic = QuestionaireLogic("QUESTION", Line, None, Self, Segment.Text, Line.Index, Line.PrevIDType, Line.ListDefTrack, Line.TableTrack, Line.BlockTrack, Line.QuestionTrack, Line.ListTrack, Line.StateFlags, Line.DefinedFlags, Self.TrackOutput, Self.Configs, Self.FileName, False, Self.Debug, Logic=Line.LogicCodes)
				Self.AddLogic(Logic)
				#CHECK IF INLINE TEXT HAS BEEN SET
				if(Self.InlineText!= ""):
					Self.QuestionText += Self.InlineText
					Self.InlineText = ""

	############# QuestionaireQuestion:Add Logic #############
	#FUNCTION:   Adds a new logic structure to the question invoking check
	#PARAMATERS: Logic
	#RETURNS:	 Nothing
	def AddLogic (Self, Logic):	
		Self.Logic.append(Logic)

	############# QuestionaireQuestion:Add Next List Logic #############
	#FUNCTION:   Adds a new logic structure to the question invoking check
	#PARAMATERS: Logic (as dict)
	#RETURNS:	 Nothing
	def AddNextListLogic (Self, Logic):
		#LOOP THROUGH PROVIDED DICT
		for Element in Logic.keys():	
			Self.NextListLogic[Element] = Logic[Element]

	############# QuestionaireQuestion:Add Next Line Logic #############
	#FUNCTION:   Adds a new logic structure to the question invoking check
	#PARAMATERS: Logic (as dict)
	#RETURNS:	 Nothing
	def AddNextLineLogic (Self, Logic):
		#LOOP THROUGH PROVIDED DICT
		for Element in Logic.keys():
			Self.NextLineLogic[Element] = Logic[Element]

	############# QuestionaireQuestion:Check List ID#############
	#FUNCTION:   Checks the current list for a specific ID
	#PARAMATERS: ID
	#RETURNS:	 True/False
	def CheckListID(Self, ID):		
		return (ID in Self.CurrentList.IDTrack)
	
	############# QuestionaireQuestion:Export Question #############
	#FUNCTION:   Exports the question based on the appropriate template
	#PARAMATERS: Nothing
	#RETURNS:	 Text of this question 
	def ExportQuestion(Self, FileOutHandle):
		#UPDATE 
		#IF MULTI
		if(int(Self.LogicCodes['MULTI']) == 1):
			if(Self.Choices is None):				
				Self.LogicCodes['QUESTION_MAX']= 0
			else:
				Self.LogicCodes['QUESTION_MAX']= len(Self.Choices.ListItems)

		#LOOP THROUGH ADDITION TEXT DEFINTIONS
		for Element in Self.Configs['MAIN_CONFIG'].Config['LOGIC']:
			if(Element['ID'] in Self.LogicCodes and 'PRE_QUESTION_ADD' in Element):
				Self.Configs['TEMPLATES']["PRE_"+Element['ID']].Export(Self, FileOutHandle)			
		
		#LOOP THROUGH LEADING ADDITIONS
		#EXPORT QUESTION TEXT
		Self.Configs['TEMPLATES'][Self.QuestionType].Export(Self, FileOutHandle)
		#LOOP THROUGH ADDITION TEXT DEFINTIONS
		for Element in Self.Configs['MAIN_CONFIG'].Config['LOGIC']:
			if(Element['ID'] in Self.LogicCodes and 'POST_QUESTION_ADD' in Element):
				Self.Configs['TEMPLATES']["POST_"+Element['ID']].Export(Self, FileOutHandle)			

	############# QuestionaireQuestion:Finalize #############
	#FUNCTION:   Completes a number of minor revisions to the question prior to 
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def Finalize(Self):
		
		Config = Self.Configs['MAIN_CONFIG'].Config   #MAIN CONFIG CONTROLLING OUTPUT FORMAT          

		InitClean = QuestionaireCleanUp(Self.Configs['CLEANUP'].Config)
		#UPDATE MIN AND MAX IF NECESSARY - NOT SURE HOW I WANT TO PROCESS THIS MOVING FORWARD - FEELS LIKE IT SHOULD BE INTEGRATED INTO LOGIC
		#CHECK IF CHARACTER(S) ARE SET TO BE ADDED TO START OF QUESTION
		if ('QID_START' in Config):			
			#ADD DEFINED CHARACTERS IF THEY DO NOT EX
			if(not(re.search(r"^"+Config['QID_START'],Self.QuestionID, re.IGNORECASE))):
				Self.QuestionID = Config['QID_START'] + str(Self.QuestionID)
				
		Self.QuestionText = InitClean.UpdateText(Self.QuestionText,'FINAL_CLEANING_START')	

		#CLEANUP FORMATTING
		#Self.QuestionText= QuestionaireMisc.RunReformat($Self->{QUESTION_TEXT}, 	$CleanupConfig->{FORMATTING_CLEANUP});	

		#REMOVE LEADING NON-ALPHA NUMBERIC
		#Self.QuestionText=~ s/^[a-z0-9]+//;	
		#UPDTE TEXT REMOVING ILLEGAL NESTED FORMATING

		
		Self.QuestionText= QuestionaireMisc.CleanupNestedTags (Self.QuestionText)
		Self.QuestionText= QuestionaireMisc.CleanupOrphanTags (Self.QuestionText)

		Self.QuestionText = InitClean.UpdateText(Self.QuestionText,'FINAL_CLEANING_FORMATS')	

		#UPDATE QUESTION TEXT
		if ('BOLD_START' in Config and 'BOLD_END' in Config):
			Self.QuestionText = re.sub(r'<<B>>',Config['BOLD_START'],Self.QuestionText) #BOLD START
			Self.QuestionText = re.sub(r'<<\/B>>',Config['BOLD_END'],Self.QuestionText) #BOLD END

		if ('BOLD_START' in Config and 'ITALIC_END' in Config):
			Self.QuestionText = re.sub(r'<<I>>',Config['ITALIC_START'],Self.QuestionText) #ITALIC START
			Self.QuestionText = re.sub(r'<<\/I>>',Config['ITALIC_END'],Self.QuestionText) #ITALIC END

		if ('UNDERLINE_START' in Config and 'UNDERLINE_END' in Config):
			Self.QuestionText = re.sub(r'<<U>>',Config['UNDERLINE_START'],Self.QuestionText) #UNDERLINE START
			Self.QuestionText = re.sub(r'<<\/U>>',Config['UNDERLINE_END'],Self.QuestionText) #UNDERLINE END

		#CLEAR TRAILING
		#Self.QuestionText = QuestionaireMisc.RunReformat(Self.QuestionText, $CleanupConfig->{TRAILING_CLEANUP});
		
		#CLEAR LEADING
		#my @CleanupList = (@{$CleanupConfig->{LEADING_CLEANUP}}, @{$CleanupConfig->{LEADING_CLEANUP_QUESTIONTEXT}});
		#Self.QuestionText = QuestionaireMisc::RunReformat(Self.QuestionText, $CleanupConfig->{LEADING_CLEANUP});

		#CLEAR LEADING
		#Self.QuestionText = QuestionaireMisc::RunReformat(Self.QuestionText, $CleanupConfig->{UPDATE_FINAL});
 		
		Self.QuestionText = InitClean.UpdateText(Self.QuestionText,'FINAL_CLEANING_END')	

		if ('QTEXT_START' in Config):
			Self.QuestionText = Config['QTEXT_START'] + Self.QuestionText 
		if ('QTEXT_END' in Config):
			Self.QuestionText += Config['QTEXT_END']
		
		if('QTEXT_BLANK_LINE' in Config):
			Self.QuestionText = re.sub(r"\s*<<N>>\s*<<N>>\s*", Config['QTEXT_BLANK_LINE'], Self.QuestionText)
		if('QTEXT_NEW_LINE' in Config):
			Self.QuestionText = re.sub(r"\s*<<N>>\s*", Config['QTEXT_NEW_LINE'], Self.QuestionText)

		#CLEAR LEADING
		Self.QuestionText = InitClean.UpdateText(Self.QuestionText,'FINAL_CLEANING_END')	
		
		Self.QuestionText= QuestionaireMisc.RunReformat(Self.QuestionText, Config['ADDITIONAL_CLEANUP'])

		#REMOVE EXTRA SPACES
		Self.QuestionText = re.sub(r"\s+", " ", Self.QuestionText)
		#CHECK QUESTION TEXT FOR LEADING QUESTION ID AND REMOVE IF PRESENT
		if ('REMVOE_LEADING_ID' in Config):
			SearchID = Self.QuestionID
			SearchID = re.sub(r"^Q", "", SearchID)
			Self.QuestionText = re.sub(r"^((<[^>]+>)*)Q?"+SearchID+r"\.?\s+", "", Self.QuestionText)
			
		#LOOP THROUGH LOGIC - REMOVING BLANK LINES
		for Logic in Self.Logic:	
			NewLogicList = []  #NEW ARRAY
			#CHECK LIST SIZE
			if (re.search(r"[A-Z0-9]",Logic.Text,re.IGNORECASE)):
				NewLogicList.append(Logic)					

		#FINALIZE CHOICES
		if (Self.Choices is not None):
			Self.Choices.Finalize(Self.QuestionType)
		
		#FINALIZE STATEMENTS
		for StatementList in Self.Statements:
			StatementList.Finalize(Self.QuestionType)


	############# QuestionaireQuestion:GetIdentifierValue #############
	#FUNCTION:   Returns appropriate structure based on provided identifier and index.
	#PARAMATERS: Element Identifier
	#RETURNS:	 Value of provided identifier
	def GetIdentifierValue(Self, Identifier, Index):	
		#QUESTION ID
		if(Identifier == 'QUESTION_ID'):
			return Self.QuestionID
		#QUESTION TEXT	
		elif(Identifier == 'QUESTION_TEXT'):
			return Self.QuestionText
		#CHOICE LOOKUP
		elif(re.search(r"^CHOICE_", Identifier, re.IGNORECASE)):			
			if(Self.Choices is None):
				if(Identifier == 'CHOICE_LIST'):
					return ([])
				print ("Error: Question Choice - Identifier "+Identifier+" used but no choices defined")
				return ("")
			Identifier = re.sub(r"^CHOICE_", "", Identifier)	
			return(Self.Choices.GetIdentifierValue(Identifier, Index))
		#STATEMENT LOOKUP
		elif(re.search(r"^STATEMENT_", Identifier, re.IGNORECASE)):

			Identifier = re.sub(r"^STATEMENT_", "", Identifier)
			#CHECK IF NEXT CHARACTER IS A NUMBER IF NOT ERROR AND RETURN BLANK
			if(not(re.search(r"^\d", Identifier))):
				print ("Error: Question Statement - Unrecognized indentifier keyword: STATEMENT_"+Identifier)
				return ("")
			#GET LEADING INDEX -
			StatementIndex = re.search(r"^(\d+)", Identifier, re.IGNORECASE).group(1)
			Identifier = re.sub(r"^(\d+)_", "", Identifier)

			#GET STATEMENT LIST INDEX - LIKELY NOT USED MUCH SINCE PARSING WILL TEND TO ONLY GENERATE UP TO TWO LISTS
			return(Self.Statements[int(StatementIndex)-1].GetIdentifierValue(Identifier, Index))
		#EXTRA LOGIC	
		elif(Identifier == 'EXTRA_LOGIC'):			
			LogicText = ""
			for Logic in Self.Logic:
				if(Logic.Source == "LIST"):
					LogicText += "<<LOGIC_LIST>>"
				else:
					LogicText += "<<LOGIC>>"
				LogicText +=  QuestionaireMisc.ClearTags(Logic.Text) +"\n"
				
			return(LogicText)	
		#CHECK LOGIC
		elif(Identifier in Self.LogicCodes):
			return Self.LogicCodes[Identifier]
	
		#IF UNKNOW PRINT ERROR AND RETURN BLANK
		else:	
			print ("Error: Quesiton - Unrecognized indentifier keyword: "+Identifier)			
			return ("")
		

