import sys
import roman
import re

import QuestionaireMisc

from QuestionaireLine import QuestionaireLine
from QuestionaireProcessCheck import QuestionaireProcessCheck
from QuestionaireSegment import QuestionaireSegment
from QuestionaireLogic import QuestionaireLogic
from QuestionaireCleanUp import QuestionaireCleanUp


class QuestionaireListItem (QuestionaireLine):
	  
	##################################################################################################################
	########################################## QUESTIONAIRE LIST ITEM- INIT ##########################################
	################################################################################1#################################
	############# QuestionaireLine:Init #############
	#FUNCTION:   Object Constructor - Builds a Question object
	#PARAMATERS: Question Text Array, Line Index, Previous Id Type, List Def Track, Table Track, Block Track, State Flags, Track Output, Track Output File, Configs, Word Document File Name
	#RETURNS:	 Nothing
	def __init__ (Self, Question, List,  Text, Index, PrevID, PrevIDType, ListDefTrack, TableTrack, BlockTrack, QuestionTrack, ListTrack, StateFlags, DefinedFlags, TrackOutput, Configs, FileName, UpdateTracks=True, Debug=0 , Logic=None):
		QuestionaireLine.__init__(Self, Question, Text, Index, PrevIDType, ListDefTrack, TableTrack, BlockTrack, QuestionTrack, ListTrack, StateFlags, DefinedFlags, TrackOutput, Configs, FileName, UpdateTracks, Debug)	
		Self.ProcessType = "LIST_ITEM" 
		Self.ListItemText = ""			#TEXT OF THIS LIST ITEM
		Self.ListItemID = ""			#ID OF THIS LIST ITEM
		Self.ListItemIDType = ""	    #ID TYPE		
		Self.ListItemPrevID = PrevID	#ID OF THE PREVIOUS LINE
		Self.ListPrepend = []			#TEXT TO APPEND TO THE START OF THIS LINE		
		Self.ListAppend = []			#TEXT TO APPEND TO THE END OF THIS LINE		
		Self.ListClear = []				#TEXT TO REMOVE FROM THIS LINE	
		Self.List = List #LIST OBJECT
		Self.InitLogicCodes(Configs,'LIST_ITEM_VALUE')      

		if Logic is not None:
			for LogicValue in Logic.keys():
				Self.LogicCodes[LogicValue] = Logic[LogicValue]

		Self.AddText(Text)

	##################################################################################################################
	#################################### QUESTIONAIRE LIST ITEM - PROCEESSING ########################################
	##################################################################################################################	
	############# QuestionaireLine:CheckNewLIst #############
	#FUNCTION:   Checks if a new list is required
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def CheckNewList(Self):
		#BUILD WEIGHTS FOR EACH ELEMENT		
		if(Self.Debug == 2): 
			print("\n\n###############################################################")
			print("NEW LIST: "+Self.Text)   
			print("LINE: "+Self.Text)   
		Weight = Self.CheckElements(Self.Configs['ID_LIST_NEW'],Self.Text)
		if(Weight > int(Self.Configs['ID_LIST_NEW'].Config['THRESHOLD'])):
			return True
		else:
			return False
		
	##################################################################################################################
	################################### QUESTIONAIRE LIST ITEM - SET VALUES ##########################################
	##################################################################################################################	  
	############# QuestionaireLine:SetType #############
	#FUNCTION:   Sets the line items type
	#PARAMATERS: Type
	#RETURNS:	 Nothing
	def SetType(Self, Type):
		Self.ListItemIDType = Type

	############# QuestionaireQuestion:Add Question Text #############
	#FUNCTION:   Updates the question text
	#PARAMATERS: Line Structure to add
	#RETURNS:	 Nothing
	def AddText(Self, Text):
		#LIST TEXT LOGIC 
		ListLogic = QuestionaireLogic("LIST_TEXT", Self, Self.List, Self.Question, Text, Self.Index, Self.PrevIDType, Self.ListDefTrack, Self.TableTrack, Self.BlockTrack, Self.QuestionTrack, Self.ListTrack, Self.StateFlags, Self.DefinedFlags, Self.TrackOutput, Self.Configs, Self.FileName, False, Self.Debug)

		Segments = QuestionaireMisc.SegmentText(Text)
		#PROCESS SEGMENTS
		for SegmentIndex, SegmentText in enumerate(Segments):
			#BUILD SEGMENT OBJECT
			Segment = QuestionaireSegment(Self, SegmentText, SegmentIndex, len(Segments), Self.ListDefTrack, Self.TableTrack, Self.BlockTrack, Self.QuestionTrack, Self.ListTrack, Self.TrackOutput, Self.Configs, Self.Debug)
			#ID
			#NOTE - FOR NOW JUST ADDED TO TEXT - PROCESSED AS THE ENTIRE LIST AT LIST LEVEL (KEPT SEPERATE FOR FUTURE CONSIDERATION)
			if(Segment.Type == 'ID'):
				Self.ListItemText += Segment.Text
			#TEXT
			elif(Segment.Type == 'TEXT'):
				Self.ListItemText += Segment.Text
			#LOGIC
			elif(Segment.Type == 'LOGIC'):
				Logic = QuestionaireLogic("LIST", Self, Self.List, Self.Question, Segment.Text, Self.Index, Self.PrevIDType, Self.ListDefTrack, Self.TableTrack, Self.BlockTrack, Self.QuestionTrack, Self.ListTrack, Self.StateFlags, Self.DefinedFlags, Self.TrackOutput, Self.Configs, Self.FileName, False, Self.Debug)
				Self.Question.AddLogic(Logic)
				#CHECK IF INLINE TEXT HAS BEEN SET
				if(Self.InlineText != ""):
					Self.ListItemText += Self.InlineText
					Self.InlineText = ""

	##################################################################################################################
	################################### QUESTIONAIRE LIST ITEM - GET VALUES ##########################################
	##################################################################################################################	



	##################################################################################################################
	################################ QUESTIONAIRE LIST ITEM - LOGIC PROCESSING #######################################
	##################################################################################################################	


	############# QuestionairProcessCheck:Processor #############
	#FUNCTION:   Used by command to access referenced values - not currenlty setup
	#PARAMATERS: Value
	#RETURNS:	 Nothing
	def GetReference(Self, Type, Name):
		return QuestionaireProcessCheck.GetReference(Self, Type, Name)

	############# QuestionairProcessCheck:Processor #############
	#FUNCTION:   Used by command to trigger object specific functions
	#PARAMATERS: Value
	#RETURNS:	 Nothing
	def Processor(Self, Function, Paramaters):
		return QuestionaireProcessCheck.Processor(Self, Function, Paramaters)

	############# QuestionairProcessCheck:GetValue #############
	#FUNCTION:   Used by command to trigger object specific functions
	#PARAMATERS: Value
	#RETURNS:	 Nothing
	def GetValue(Self, Value):
		#line
		if(Value == 'TEXT_ID'):
			return(Self.ListItemID)
		elif(Value == 'TEXT_PREV_ID'):
			return(Self.ListItemPrevID)
		return QuestionaireProcessCheck.GetValue(Self, Value)


	##################################################################################################################
	###################################### QUESTIONAIRE LIST ITEM - FINALIZE #########################################
	##################################################################################################################	

	############# QuestionaireList:Finalize #############
	#FUNCTION:   Cleans up text and structure to prepare for export
	#PARAMATERS: Config File
	#RETURNS:	 Nothing
	def Finalize (Self,Scale, QuestionType):
		#MOVE ID TO LIST ID IF NOT SET (LIST ID IS CURRENTLY ONLY SET BY SPECIFIC LOGIC FUNCTIONS)
		Config = Self.Configs['MAIN_CONFIG'].Config   #MAIN CONFIG CONTROLLING OUTPUT FORMAT
		
		InitClean = QuestionaireCleanUp(Self.Configs['CLEANUP'].Config)
		Self.ListItemText = InitClean.UpdateText(Self.ListItemText,'FINAL_CLEANING_START')	
	

		#UPDTE TEXT REMOVING ILLEGAL NESTED FORMATING
		Self.ListItemText= QuestionaireMisc.CleanupNestedTags (Self.ListItemText)	
		Self.ListItemText= QuestionaireMisc.CleanupOrphanTags (Self.ListItemText)

		#PREPEND ADDED TEXT
		for Text in Self.ListPrepend:
			Self.ListItemText = Text + Self.ListItemText

		#APPEND ADDED TEXT
		for Text in Self.ListAppend:
			Self.ListItemText += Text
		
		#CLEAR TEXT
		for Text in Self.ListClear:
			Self.ListItemText = re.sub(Text,"",Self.ListItemText)


		#UPDATE QUESTION TEXT
		if ('BOLD_START' in Config and 'BOLD_END' in Config):
			Self.ListItemText = re.sub(r'<<B>>',Config['BOLD_START'],Self.ListItemText) #BOLD START
			Self.ListItemText = re.sub(r'<<\/B>>',Config['BOLD_END'],Self.ListItemText) #BOLD END

		if ('BOLD_START' in Config and 'ITALIC_END' in Config):
			Self.ListItemText = re.sub(r'<<I>>',Config['ITALIC_START'],Self.ListItemText) #ITALIC START
			Self.ListItemText = re.sub(r'<<\/I>>',Config['ITALIC_END'],Self.ListItemText) #ITALIC END

		if ('UNDERLINE_START' in Config and 'UNDERLINE_END' in Config):
			Self.ListItemText = re.sub(r'<<U>>',Config['UNDERLINE_START'],Self.ListItemText) #UNDERLINE START
			Self.ListItemText = re.sub(r'<<\/U>>',Config['UNDERLINE_END'],Self.ListItemText) #UNDERLINE END

		Self.ListItemText = InitClean.UpdateText(Self.ListItemText,'FINAL_CLEANING_END')	
		#TODO - MOVE TO A MORE DYNAMIC SYSTEM
		#SCALE CHANGES - CHECK IF SCALE
		if (Scale):
			#CHECK IF QUESTIONT TYPE EXISTS IN SCALE DEFINTION
			if ('SCALE_FORMATTING' in Config and QuestionType in Config['SCALE_FORMATTING']):
				#LOOP THROUGH CHANGES
				for Command in Config['SCALE_FORMATTING'][QuestionType]:
					Check = Command['CONDITION']  #CHECK CONDITION TO PASS TO REGULAR EXPRESSION
					#CHECK FOR A LIST CONTAINS COMMAND AND CHECK AGAINST LIST ENTRIES
					if (not ('LIST_CONTAINS' in Command) or Self.List.ContainsItem(Command['LIST_CONTAINS'])):
						#CHECK IF TEXT MATCHES COMMAND
						if(re.match(r'^'+Check+'$',Self.ListItemText,re.IGNORECASE)):
							ExceptionCheck=0
							#CHECK IF EXCEPTIONS EXIST
							if('EXCEPTIONS' in Command):
								#LOOP THROUGH EXCEPTIONS
								for Exception in Command['EXCEPTIONS']:
									#CODE EXCEPTIONS
									if (Exception['TYPE'] == "CODE"):
										ExceptionCheck = 1 if (Self.ID == Exception['VALUE']) else 0
									#TEXT EXCEPTIONS
									if (Exception['TYPE'] == "TEXT"):
										ExceptionCheck = 1 if (re.search(Exception['VALUE'],Self.TEXT,re.IGNORECASE)) else 0
							#IF EXCEPTION
							if (ExceptionCheck == 0):
								#CHECK IF LEADING CHANGE IS REQUIRED
								if ('ADD_LEADING' in Command):	
									AddText = Command['ADD_LEADING']  #TEXT TO ADD TO LIST TEXT
									ID = int(Self.ListItemID)
									AddText = AddText.replace('{ID}',str(ID))									
									Self.ListItemText = AddText+Self.ListItemText
								#CHECK IF TRALING CHANGE IS REQUIRED
								if ('ADD_TRAILING' in Command):
									AddText = Command['ADD_TRAILING']  #TEXT TO ADD TO LIST TEXT
									ID = int(Self.ListItemID)
									AddText = AddText.replace('{ID}',str(ID))
									Self.ListItemText += AddText			
										
		#ADDITIONAL CLEANUP CODE
		Self.ListItemText= QuestionaireMisc.RunReformat(Self.ListItemText, Config['ADDITIONAL_CLEANUP'])
		#REMOVE EXTRA SPACES
		Self.ListItemText = re.sub(r"\s+", " ", Self.ListItemText)