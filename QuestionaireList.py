import sys
import roman
import re

import QuestionaireMisc

from QuestionaireProcessCheck import QuestionaireProcessCheck
from QuestionaireListItem import QuestionaireListItem
from QuestionaireProcessCheck import QuestionaireBlockTrack
from QuestionaireProcessCheck import QuestionaireTableTrack
from QuestionaireProcessCheck import QuestionaireListDefTrack
from QuestionaireProcessCheck import QuestionaireQuestionTrack
from QuestionaireProcessCheck import QuestionaireListTrack

class QuestionaireList (QuestionaireProcessCheck):
	DefinedFlags = ['DEFINED_LIST_HEADING']
	StateFlags = ['IN_TABLE_HEADING']
	TextFlags = ['TEXT_NUMERIC','NON_CONSECUTIVE_CODES','ID_LENGTH']
	
	##################################################################################################################
	##################################### QUESTIONAIRE PROCESS CHECK LINE- INIT ######################################
	################################################################################1#################################
	############# QuestionaireList:Init #############
	#FUNCTION:   Object Constructor - Builds a Question object
	#PARAMATERS: ListIndex, TrackOutput, Configs Structure, FileName, Debug Flag
	#RETURNS:	 Nothing
	def __init__ (Self, Question, Index, TrackOutput, Configs, FileName, Debug=0):
		QuestionaireProcessCheck.__init__(Self, Question, Debug)	  
		Self.ProcessType = "LIST" 
		def PopulateValues(DefaultList):
			ReturnList={}
			for Key in DefaultList:
				ReturnList[Key] =0
			return (ReturnList)

		Self.FileName = FileName
		Self.Configs = Configs
		Self.TrackOutput = TrackOutput

		Self.StateFlags = PopulateValues(QuestionaireList.StateFlags)
		Self.DefinedFlags = PopulateValues(QuestionaireList.DefinedFlags)
		Self.TextContentFlags = PopulateValues(QuestionaireList.TextFlags) 

		Self.TableTrack = None
		Self.BlockTrack = None    
		Self.QuestionTrack = None      #SET LATER
		Self.ListTrack = None          #SET LATER
		Self.ListDefTrack = None

		Self.Index = Index
		Self.IDTrack = []	#TRACK OF IDS USED IN THIS LIST
		Self.ListItems =[]
		Self.IDLength = 0

		Self.Scale = 0			    #FLAG DENOTING THAT THIS LIST IS A SCALE
		Self.ChoiceWeight = 0		#WEIGHT OF VALUE THAT THIS LIST IS A SET OF CHOCIES
		Self.ListType = "0" 		#FLAG DENOTING THE TYPE OF LIST
        
		for Value in Self.Configs['TRACKING_VALUES']['LIST_VALUE']:
			Self.LogicCodes[Value]=0

		Self.InitListTypes(Configs)
		Self.InitLogicCodes(Configs,'LIST_VALUE')      

	############# QuestionaireProcessCheck:Init List Types #############
	#FUNCTION:   Adds values to the Stateflag defition based on fgics
	#PARAMATERS: Configs
	#RETURNS:	 Nothing
	def InitListTypes(Self, Configs):
		#LOOP THROUGH LOGIC IN THE MAIN CONFIG
		for Logic in Configs['MAIN_CONFIG'].Config['LIST_TYPE']:
			if 'STATE' in Logic:				
				Self.LogicCodes[Logic['STATE']] = 0

    ############# QuestionaireList:AddListItem #############
    #FUNCTION:   Add a list item to this list
    #PARAMATERS: ListItem
    #RETURNS:	 Nothing
	def AddListItem (Self, ListItem):   
		Self.ListItems.append(ListItem)

	############# QuestionaireList:SetListIDS #############
	#FUNCTION:   Set the IDS of each list item in this list
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def SetListIDS (Self):
		Config = Self.Configs['ID_LIST_ID'].Config
		Totals = {}								#TOTAL OF WEIGHTS		

		if (Self.Debug>1): print ("\n\n")
		if (not('IDENTIFICATION' in Config)):
			raise Exception("Questionaire List - No Identification defintion found in provided config\n")
		
		#LOOP THROUGH ENUMERATED CONFIG DEFINTIONS:	
		for IDIndex, IDConfig in enumerate(Config['IDENTIFICATION']):
			Lookup = IDConfig['LOOKUP']						#LOOKUP EXPRESSION FROM CONFIG
			IDsFound = {}										#TRACKING IDS FOUND FOR THIS LIST
			LastEntry = None									#VARIABLE USED TO TRACK THE LAST ENTRY FOUND
			CurrentPatternCount=0								#CURRENT BLOCK OF MATCHES TO PROVIDED EXPRESSION
			MaxPatternCount=0									#LARGEST BLOCK OF MATCHES TO PROVIDE EXPRESSION

			if (Self.Debug>1): print ("*********"+IDConfig['NAME']+"*********\n")		
			Totals[IDIndex]=0
			if ('BASE_WEIGHT' in IDConfig): Totals[IDIndex]=int(IDConfig['BASE_WEIGHT'])

			if (Self.Debug>1): print ("BASE WEIGHT: "+str(Totals[IDIndex])+"\n\n")					
				
			#LOOP THROUGH LIST ITEMS
			for ListEntryIndex, ListEntry in enumerate(Self.ListItems):
				ListEntryText =  ListEntry.ListItemText		#TEXT OF THE CURRENT LIST LINE
				IDValue=""									#ID EXTRACTED FROM LIST DEF

				#EXTRACT ID VALUE FROM LIST DEF
				if(re.search(r'ID_VALUE=([^>]+)',ListEntryText)):
					IDValue= re.search(r'ID_VALUE=([^>]+)',ListEntryText).group(1)
					IDValue+=" "
				
				#REMOVE LEADING LIST DEF AND ADD ID TO START OF LINE
				ListEntryText = re.sub(r'<<LIST_ID[^>]+>>','',ListEntryText)
				#TRAILING/ LEADING SPACE+TAG / UNDERSCORE

				ListEntryText = re.sub(r'^(\s*(<<T>>)*_*\s*)+','',ListEntryText, flags=re.IGNORECASE)
				ListEntryText = re.sub(r'\s*(<<T>>)*_*\s*$','',ListEntryText, flags=re.IGNORECASE)
				ListEntryText = IDValue+ListEntryText
				
				if (Self.Debug>1): print (ListEntryText)	

				Match=0		#FLAG DENOTING THAT THIS LINE MATCHES CONDTIONS
				Code=None
				Pass=0
				#CHECK IF CURRENT LINE MATCHES ASSOCIATE EXPRESSION
				if (re.search(Lookup,ListEntryText,re.IGNORECASE)):		
					Pass=1
					if (Self.Debug>1): print ("MATCH: "+IDConfig['NAME'])
					Code=re.search(r'('+Lookup+')',ListEntryText,re.IGNORECASE).group(1)
					#RUNCLEANUP IF DEFINED.
					if('CLEANUP' in IDConfig):
						Replace = IDConfig['CLEANUP']
						Code = re.sub(Replace,'',Code)
					
					#ADD TO TOTAL
					Totals[IDIndex]+=int(IDConfig['PER_MATCH'])
					if (Self.Debug>1): print ("MATCH: "+str(Totals[IDIndex]))

					#CHECK FOR CONSECUTIVE
					if(LastEntry and 'NON_CONSECUTIVE' in IDConfig):
						if (LastEntry != QuestionaireMisc.GetPrevCode(Code) and LastEntry != QuestionaireMisc.GetNextCode(Code)):
							Totals[IDIndex]+=int(IDConfig['NON_CONSECUTIVE'])
							if (Self.Debug>1): print ("CONSECUTIVE: "+str(Totals[IDIndex]))
					
					LastEntry = Code
					#CHECK FOR DUPLICATE
					if(Code in IDsFound):
						Totals[IDIndex]+=int(IDConfig['DUPLICATE'])
						if (Self.Debug>1): print ("DUPLICATE: "+str(Totals[IDIndex]))
						#IF DUPLICATE DO NOT COUNT TO PATTERN MATCH COUNT
						CurrentPatternCount=CurrentPatternCount-1
					#ADD TO ID LIST
					else:
						IDsFound[Code]=1

					#PRECEDING TEXT CHECKS
					if('PRECEEDING_TEXT' in IDConfig):
						#CONFIRM CHECK TYPE 						
						if (IDConfig['POSITION'] == 'TRAILING'):
							#REMOVE LOOKUP TEXT
							Text = re.sub(r'('+Lookup+')','',ListEntryText)
							Text = Text.upper()
							#LOOP THROUGH DEFINED WORDS
							for LookupText in IDConfig['PRECEEDING_TEXT']:
								#IF MATCH MODIFY THE TOTAL 
								if (re.search(LookupText+'$',Text,re.IGNORECASE)):
									
									Totals[IDIndex]+=int(IDConfig['PRECEEDING_TEXT'][LookupText])
									if(int(IDConfig['PRECEEDING_TEXT'][LookupText]) < 0):
										Pass=0
							if (Self.Debug>1): print ("PRECEEDING TEXT: "+str(Totals[IDIndex]))

					#FOLLOWING TEXT CHECKS
					if('FOLLOWING_TEXT' in IDConfig):
						#CONFIRM CHECK TYPE 						
						if (IDConfig['POSITION'] == 'LEADING'):
							#REMOVE LOOKUP TEXT
							Text = re.sub(r'('+Lookup+')','',ListEntryText)
							Text = Text.upper()
							#LOOP THROUGH DEFINED WORDS
							for LookupText in IDConfig['FOLLOWING_TEXT']:
								#IF MATCH MODIFY THE TOTAL
								if (re.search(r'^'+LookupText,Text,re.IGNORECASE)):
									Totals[IDIndex]+=int(IDConfig['FOLLOWING_TEXT'][LookupText])
									if(int(IDConfig['FOLLOWING_TEXT'][LookupText]) < 0):
										Pass=0									
							if (Self.Debug>1): print ("FOLLOWING TEXT: "+str(Totals[IDIndex]))
				if(Pass):
					#PATTERN COUNT
					CurrentPatternCount+=1
					if(CurrentPatternCount>MaxPatternCount): MaxPatternCount=CurrentPatternCount
					if (Self.Debug>1): print ("PATTERN COUNT: "+str(CurrentPatternCount))			

				else:
					Totals[IDIndex]+=int(IDConfig['PER_MISS'])					
					CurrentPatternCount=0

				#ADD TO TOTALS
				Totals[IDIndex]+=MaxPatternCount*float(IDConfig['LONGEST_PATTERN_LENGTH']) 
		
		#SELECTED
		SelectedID = QuestionaireMisc.SelectHigh(Totals, Self.Debug)
		#CONFIRM THAT COMPUTED TOTAL EXCEEDS THRESHHOLD
		if(Totals[SelectedID] >= int(Config['THRESHHOLD'])):
			Lookup = Config['IDENTIFICATION'][SelectedID]['LOOKUP']	#LOOKUP EXPRESSION FROM CONFIG
			for ListIndex, ListEntry in enumerate(Self.ListItems):			
				IDValue=""									#ID EXTRACTED FROM LIST DEF	
				#EXTRACT ID VALUE FROM LIST DEF
				if(re.search(r'ID_VALUE=([^>]+)',Self.ListItems[ListIndex].ListItemText)):
					IDValue= re.search(r'ID_VALUE=([^>]+)',Self.ListItems[ListIndex].ListItemText).group(1)
					IDValue+=" "
				
				#REMOVE LEADING LIST DEF AND ADD ID TO START OF LINE
				Self.ListItems[ListIndex].ListItemText = re.sub(r'<<LIST_ID[^>]+>>','',Self.ListItems[ListIndex].ListItemText)
				Self.ListItems[ListIndex].ListItemText = re.sub(r'^(\s*(<<T>>)*_*\s*)+','',Self.ListItems[ListIndex].ListItemText, flags=re.IGNORECASE)
				Self.ListItems[ListIndex].ListItemText = re.sub(r'\s*(<<T>>)*_*\s*$','',Self.ListItems[ListIndex].ListItemText, flags=re.IGNORECASE)			
				Self.ListItems[ListIndex].ListItemText = IDValue+Self.ListItems[ListIndex].ListItemText
				#CHECK IF CURRENT ENTRY 
				if(re.search(r'('+Lookup+')',Self.ListItems[ListIndex].ListItemText,re.IGNORECASE) and Self.ListItems[ListIndex].ListItemID == ""):			
					PrevText = Self.ListItems[ListIndex].ListItemText
					Self.ListItems[ListIndex].ListItemID=re.search(r'('+Lookup+')',Self.ListItems[ListIndex].ListItemText,re.IGNORECASE).group(1)
					#RUNCLEANU
					# P IF DEFINED.
					if('CLEANUP' in Config['IDENTIFICATION'][SelectedID]):
						Replace = Config['IDENTIFICATION'][SelectedID]['CLEANUP']
						Self.ListItems[ListIndex].ListItemID = re.sub(Replace,'',Self.ListItems[ListIndex].ListItemID)
					#STRIP IDS OF ANY REMANING NON-ALPHANUMERIC CHARACTERS
					Self.ListItems[ListIndex].ListItemID = re.sub(r'[^a-zA-Z0-9]','',Self.ListItems[ListIndex].ListItemID)
					#REMOVE ID FROM TEXT
					Self.ListItems[ListIndex].ListItemText = re.sub(r'('+Lookup+')','',Self.ListItems[ListIndex].ListItemText, flags=re.IGNORECASE)
					#CHECK IF REMOVING THE ID CLEARS THE TEXT 
					if (QuestionaireMisc.ClearTags(Self.ListItems[ListIndex].ListItemText) == ""): Self.ListItems[ListIndex].ListItemText = PrevText									
				#IF ID MATCHES BUT LIST ID HAS BEEN FILLED
				elif(re.search(r'('+Lookup+')',Self.ListItems[ListIndex].ListItemText,re.IGNORECASE) and Self.ListItems[ListIndex].ListItemID != ""):		
					#REMOVE ID FROM START OF QUESTIONS
					Self.ListItems[ListIndex].ListItemText = re.sub(r'('+Lookup+')','',Self.ListItems[ListIndex].ListItemText, flags=re.IGNORECASE)					
				
				IDOverride = 0 #FLAD DENOTING OVERRIDE ENCOUTNERED
				#LOOP THROUGH OVERRIDES FOR ID REMOVAL
				if('LEAVE_ID' in Config['IDENTIFICATION'][SelectedID]):				
					for OverrideCond in Config['IDENTIFICATION'][SelectedID]['LEAVE_ID']:
						if(re.search(OverrideCond,Self.ListItems[ListIndex].ListItemText,re.IGNORECASE)):
							IDOverride=1

				#IF LIST TEXT IS NOW EMPTY OR AN OVERRIDE CONDITION WAS ADD ID BACK IN
				if(not(re.search(r"[0-9a-zA-Z]", QuestionaireMisc.ClearTags(Self.ListItems[ListIndex].ListItemText))) or IDOverride == 1):					
					Self.ListItems[ListIndex].ListItemText = Self.ListItems[ListIndex].ListItemID + Self.ListItems[ListIndex].ListItemText	
		#else:
		#	IndexCount = 1 #TRACKS INDEX ONLY ICNREASES FOR NON-HEADINGS 
		#	0
		#	for ListIndex in range(0,len(Self.ListItems)):
		#		Self.ListItems[ListIndex].ID = ListIndex+1			


	############# QuestionairProcessCheck:SetListIDs #############
	#FUNCTION:   Cleans up list adding extra list items to build a consecutive list
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing
	def  ReformatIDs(Self):
		IDFormat = ""				#STRING DECLARING FORMAT OF THE IDS
		ListItemIDType = None
		IDHeadingIndex = 100		#INDEX USED TO CHOOSE THE NEXT HEADING ID
		IDIndex=1 					#INDEX USED TO CHOOSE THE NEXT ID
		IDsUsed = {}				#HASH USED TO TRACK IDS USED

		############# GET ID ############
		def  GetID (Index, Type, Length, StripLeadingZero):		
			#NUMERIC
			if(Type == 'NUMBER'):
				Index = QuestionaireMisc.ConvertIDToNum(Index)
				if (not (StripLeadingZero)):					
					Index = str(Index)
					return  (("0"*(Length - len(Index)))+Index)				
				else:
					return (Index)		
			#LETTERS
			elif(Type == 'LETTER'):
				Index = QuestionaireMisc.ConvertNumToID(Index)
				if(not(re.search(r'[a-z]',str(Index), re.IGNORECASE))):
					return (QuestionaireMisc.ConvertNumToID(Index))				
				else: 
					return (Index.upper())

		#POPULATE IDS USED WITH ANY EXISTING IDS
		for	ListItem in Self.ListItems:
			if(ListItem.ListItemID != ""):
				IDsUsed[str(ListItem.ListItemID)] = 1

		#SET HEADING ID IF DEFINED
		if('CHOICE_HEADING_START' in Self.Configs['MAIN_CONFIG'].Config):
			IDHeadingIndex = int(Self.Configs['MAIN_CONFIG'].Config['CHOICE_HEADING_START']) 

		#SET ID FORMAT DEFINED CHOICE ID OR STATEMENT ID DEPENDING ON LIST TYPE
		IDFormat = Self.Configs['MAIN_CONFIG'].Config['CHOICE_ID']  if(Self.ListType == 'CHOICE') else Self.Configs['MAIN_CONFIG'].Config['STATEMENT_ID'] if(Self.ListType == 'STATEMENT') else None			
		if(IDFormat == "" or  IDFormat is None):
			raise Exception("Questionaire List - No List Type defined\n")
		
		#SET ID LENGTH (NOT SURE WHY THIS IS GLOBAL)
		Self.TextContentFlags['ID_LENGTH']= len(IDFormat)

		#SET ID TYPE (LETTER, NUMBER)
		ListItemIDType = 'LETTER' if(re.search(r'^[A-Z]+$',IDFormat)) else 'NUMBER' if(re.search(r'^[0-9]+$',IDFormat)) else None

		#LOOP THROUGH LIST ADDING ID'S AS REQUIRED. 
		for Index, ListEntry in enumerate(Self.ListItems):		
			#ID NOT DEFINED OR IF HEADINGS ARE FOUND IN THIS LIST RESET ALL
			if(ListEntry.ListItemID == "" or ListEntry.ListItemIDType == 'LIST_HEADING'):
				#HEADING
				NewID=""
				if(ListEntry.ListItemIDType == 'LIST_HEADING'):	
					while(str(IDHeadingIndex) in IDsUsed): IDHeadingIndex+=1
					IDsUsed[str(IDHeadingIndex)] = 1		
					NewID= IDHeadingIndex	
				#NOT A HEADING
				else:
					while(str(IDIndex) in IDsUsed): IDIndex+=1
					IDsUsed[str(IDIndex)] = 1
					NewID = IDIndex	
				ListEntry.ListItemID =  NewID


		#LOOP THROUGH LIST ENTRIES, GET LENGTH OF IDS UPDATE LENGTH AS NEEDED		
		for ListEntry in Self.ListItems:	
			if (ListEntry.ListItemID is not None and ListEntry.ListItemID != "" and len(str(ListEntry.ListItemID)) > Self.TextContentFlags['ID_LENGTH']):
				Self.TextContentFlags['ID_LENGTH'] = len(str(ListEntry.ListItemID))

		#LOOP THROUGH LIST ENTRIES, UPDATING IDS WITH LEADING ZEROS
		for ListEntry in Self.ListItems:	
			StripLeadingZero = 1 if ('STRIP_LEADING_ZERO' in Self.Configs['MAIN_CONFIG'].Config and Self.Configs['MAIN_CONFIG'].Config['STRIP_LEADING_ZERO']) else 0
			ListEntry.ListItemID = GetID(ListEntry.ListItemID, ListItemIDType, Self.TextContentFlags['ID_LENGTH'],StripLeadingZero)
			if(len(str(ListEntry.ListItemID)) > Self.IDLength):
					Self.IDLength = len(str(ListEntry.ListItemID))

	

	############# QuestionairProcessCheck:Remove Blank Elemenets #############
	#FUNCTION:   Loops through list items removing anything that doesn't have any text
	#PARAMATERS: Nothing
	#RETURNS:	 Nothing	
	def RemoveBlankElements(Self):
		RemoveCount = 0	
		#LOOP THROUGH LIST ITEMS
		for Index, ListEntry in list(enumerate(Self.ListItems)):
			#REMOVE ALL TAGS
			ListEntryText = QuestionaireMisc.ClearTags(ListEntry.ListItemText)
			#REMOVE ALL WHITESPACE
			ListEntryText = re.sub(r'\s+','',ListEntryText)
			#IF NO TEXT REMOVE OR IF TEXT IS NOT ALPHANUMERIC (SINGLE CHARACTER)			
			if(ListEntryText == "" or re.search(r'^[^a-zA-Z0-9]$',ListEntryText)):				
				del Self.ListItems[Index-RemoveCount]
				RemoveCount+=1
    ############# QuestionaireList:SetListTypeWeight #############
    #FUNCTION:   Add a list item to this list
    #PARAMATERS: ListItem
    #RETURNS:	 Nothing
	def ProcessListFlags (Self):
 		#POPULATE TRACKING STRUCTURES - LIST TRACK AND QUESTION TRACK SHOULD BE CONSITENT ACROSS ALL LIST ITEMS
		Self.ListTrack = Self.ListItems[0].ListTrack	
		#PRINT LIST ITEMS

		#UPDATE LIST TRACK 
		Self.ListTrack.NumericValues['LENGTH'] = len(Self.ListItems)		

		Self.QuestionTrack = Self.ListItems[0].QuestionTrack	
		if(Self.Debug ==2): print("\nPROCESS LIST FLAG:\n")
		#POPULATE TRACKING STRUCTURES - MERGE TRACKS FOUND IN LIST ITEMS FOR LIST LEVEL PROCESSING
		def PopulateAverageTrack (TrackStruct, Type, NumericValues):
			LastTrackStruct = None
			TrackCount = 0
			#DEPENDING ON TYPE BUILD TRACK STRUCTURE
			if(Type == 'LIST_DEF'):
				TrackStruct = QuestionaireListDefTrack()
			elif(Type == 'BLOCK'):
				TrackStruct = QuestionaireBlockTrack()	
			elif(Type == 'TABLE'):
				TrackStruct = QuestionaireTableTrack()

			#LOOP THROUGH LIST ITEMS TO POPULATE TRACKING STRUCTURES
			for ListItem in Self.ListItems:
				SourceTrack = None
				if(Type == 'LIST_DEF'):
					SourceTrack = QuestionaireListDefTrack()
				elif(Type == 'BLOCK'):
					SourceTrack = QuestionaireBlockTrack()	
				elif(Type == 'TABLE'):
					SourceTrack = QuestionaireTableTrack()		
				#CHECK IF TRACK STRUCTURE EXISTS		
				if(ListItem.ListDefTrack != None):
					if(not(SourceTrack is LastTrackStruct)):
						LastTrackStruct = SourceTrack				
						for KeyVal in NumericValues:
							TrackStruct.NumericValues[KeyVal] += SourceTrack.NumericValues[KeyVal]
						TrackCount+=1
			#AVERAGE VALUES
			if(TrackCount > 0):
				for KeyVal in NumericValues:
					TrackStruct.NumericValues[KeyVal] = TrackStruct.NumericValues[KeyVal] / TrackCount	

		PopulateAverageTrack(Self.ListDefTrack, 'LIST_DEF',['LENGTH','LENGTH_AVERAGE','LENGTH_STD_DEV','BREAK_COUNT'])
		PopulateAverageTrack(Self.BlockTrack, 'BLOCK',['LENGTH','LENGTH_AVERAGE','LENGTH_STD_DEV','BREAK_COUNT','COUNT_LIST_DEF'])
		PopulateAverageTrack(Self.TableTrack, 'TABLE',['LENGTH','LENGTH_AVERAGE','LENGTH_STD_DEV','BREAK_COUNT','COUNT_ROW','COUNT_COL','TAB_AVERAGE'])

		#POPULATE OTHER FLAGS - NOT SURE WHAT THIS WAS SUPPOSED TO DO
		#for ListItem in Self.ListItems:
		#	if(re.search(r'^\s*\d+\s*$',QuestionaireMisc.ClearFormatTags(ListItem.Text))):
		#		Self.TextContentFlags['IN_SCALE'] = 1
		
		Self.Text=""
		for ListItem in Self.ListItems:
			Self.Text+=" "+ListItem.Text			
		Self.Text = QuestionaireMisc.ClearFormatTags(Self.Text)

		#PROCESS SCALE WEIGHTS
		for ListType in Self.Configs['MAIN_CONFIG'].Config['LIST_TYPE']:
			#CHECK THAT CONFIG EXISTS AND THEN PROCESS
			if(ListType['ID'] in Self.Configs['LIST_TYPE']):
				if(Self.Debug ==2): print("PROCESS LIST TYPE:"+ListType['ID'])			
				Weight = Self.CheckElements(Self.Configs['LIST_TYPE'][ListType['ID']],Self.Text)
				if(Weight >= int(Self.Configs['LIST_TYPE'][ListType['ID']].Config['THRESHOLD'])):
					Self.StateFlags[ListType['STATE']] = 1
					Self.LogicCodes[ListType['STATE']] = 1
		#CHECK LOGIC FOR REMOVAL TRIGGER
		for Logic in Self.Configs['MAIN_CONFIG'].Config['LOGIC']:
			if('LIST_REMOVE_ON' in Logic):
				#LOOP THROUGH STATES TRIGGERING THIS EVEN
				for State in Logic['LIST_REMOVE_ON']:
					if(State in Self.StateFlags):
						ListValue = []	#VALUE OF LIST ADDITION VALUES 
						#LOOP THROUGH LIST ADDITIONS
						if("LIST_VALUE" in Logic):
							for Value in Logic['LIST_VALUE'].keys():
									ListValue.append(Value)
						#LOOP THROUGH NEXT LIST ADDIOTNS
						if("NEXT_LIST_VALUE" in Logic):
							for Value in Logic['NEXT_LIST_VALUE'].keys():
									ListValue.append(Value)
						for Value in ListValue:
							if(Value in Self.LogicCodes):
								Self.LogicCodes[Value] = 0

		#PROCESS LIST TYPE WEIGHTS
		if(Self.Debug ==2): print("PROCESS CHOICE WEIGHT")					
		Self.ChoiceWeight = Self.CheckElements(Self.Configs['ID_LIST_CHOICE'],Self.Text)
		
    ############# QuestionaireList:SetListTypeWeight #############
    #FUNCTION:   Add a list item to this list
    #PARAMATERS: ListItem
    #RETURNS:	 Nothing
	def SetListTypeWeight (Self):
		Self.ChoiceWeight =Self.CheckElements(Self.Configs['LIST_ID_CHOICE_CONFIG'],Self.Self.Text)

	############# QuestionaireList:MergeLabels #############
	#FUNCTION:   Provided a list of text integrates it into the existing list - used to merge subsequent table heading rows
	#PARAMATERS: LabelList
	#RETURNS:	 Nothing    
	def MergeLabels(Self, AddedLabelList, Line, CurrentListID, DefinedFlags, StateFlags, TrackOutput, Configs, FileName, Debug=0):

		#REMOVE LEADING BLANKS
		FoundText = 0 #USED TO MAINTAINS SPACE
		for ListItem in AddedLabelList:
			if(not(re.search(r"[0-9a-z]",QuestionaireMisc.ClearTags(ListItem),re.IGNORECASE) or FoundText==1) ):
				AddedLabelList.remove(ListItem)
				FoundText = 1
        #IF LISTS EQUAL SIZE:      
		if(len(AddedLabelList) == len(Self.ListItems)):				
			for Index in range(0,len(Self.ListItems)):
				Self.ListItems[Index].ListItemText += AddedLabelList[Index]
		#UN-EQUAL SIZE	
		else:
			#CHECK IF LISTS ARE 0 - I DON'T KNOW HOW THIS WOULD HAPPEN
			#CHECK IF ADDED LIST IS EMPTY AND JUST EXIT FUNCTION IF SO
			if(len(AddedLabelList)==0):
				return()                        
			#IF LIST SIZES ARE EQUAL - MERGE LISTS
			if(len(AddedLabelList)==len(Self.ListItems)):
				for Index in range(0,len(Self.ListItems)):
					Self.ListItems[Index].ListItemText += AddedLabelList[Index]
			#IF UN-EQUAL SIZES
			else:
				LeadingArray = []
				TrailingArray = []

				#LEADING BLANK
				while(len(Self.ListItems)>0 and len(AddedLabelList)>0):
					#REMOVE FIRST AND LAST ELEMENTS FROM LIST IF EMPTY
					if(not(re.search(r"[0-9a-z]",QuestionaireMisc.ClearTags(Self.ListItems[0].ListItemText),re.IGNORECASE))):
						Self.ListItems.pop(0)
					if(not(re.search(r"[0-9a-z]",QuestionaireMisc.ClearTags(AddedLabelList[0]),re.IGNORECASE))):
						AddedLabelList.pop(0)
					if(len(Self.ListItems)>0 and not(re.search(r"[0-9a-z]",QuestionaireMisc.ClearTags(Self.ListItems[-1].ListItemText),re.IGNORECASE))): 
						Self.ListItems.pop(-1)
					if(len(AddedLabelList)>0 and not(re.search(r"[0-9a-z]",QuestionaireMisc.ClearTags(AddedLabelList[-1]),re.IGNORECASE))):
						AddedLabelList.pop(-1)

					#MERGIN LEADING VALUE
					if(len(Self.ListItems)>0 and len(AddedLabelList)>0):
						Self.ListItems[0].ListItemText += AddedLabelList[0]
						LeadingArray.append(Self.ListItems[0])
						Self.ListItems.pop(0)
						AddedLabelList.pop(0)
					#MERGE TRAILING VALUE					
					if(len(Self.ListItems)>0 and len(AddedLabelList)>0):
						Self.ListItems[-1].ListItemText += AddedLabelList[-1]
						TrailingArray.insert(0, Self.ListItems[-1])
						Self.ListItems.pop(-1)
						AddedLabelList.pop(-1)
				
				#CHECK IF NEW LIST IS NOW EMPTY
				if(len(Self.ListItems)==0):
					AddedListItemList = []					
					for ListItem in AddedLabelList:		
						AddedListItemList.append(QuestionaireListItem(Self.Question, Self,  ListItem,  Line.Index, CurrentListID, Line.PrevIDType, Line.ListDefTrack, Line.TableTrack, Line.BlockTrack, Line.QuestionTrack, Self.ListTrack, StateFlags, DefinedFlags, TrackOutput, Configs, FileName, UpdateTracks=False, Debug=Debug))					
					Self.ListItems = LeadingArray + AddedListItemList + TrailingArray						
				#CHECK IF CURRENT LIST IS NOW EMPTY
				elif(len(AddedLabelList)==0):
					Self.ListItems = LeadingArray + Self.ListItems + TrailingArray
				#print ("CURRENTLY NON-FUNCTIONS NEED TO RE-BUILD WITH BETTER LOOPING FROM BOTH SIDES TO THE MIDDLE")

	############# QuestionaireList:GetIdentifierValue #############
	#FUNCTION:   Returns appropriate structure based on provided identifier and index.
	#PARAMATERS: Element Identifier
	#RETURNS:	 Value of provided identifier	
	def GetIdentifierValue(Self, Identifier, Index):		
		#LIST+

		if(Identifier == "LIST"):
			return Self.ListItems
		#LIST ITEM
		elif(Identifier == "INDEX"):
			return (Index+1)
		#ID
		elif(Identifier == "ID"):		
			return Self.ListItems[Index].ListItemID
		#TEXT
		elif(Identifier == "TEXT"):
			return Self.ListItems[Index].ListItemText		
		#LENGTH
		elif(Identifier == "LENGTH"):
			return Self.IDLength
		#FIRST ID
		elif(Identifier == "FIRST_ID"):
			return Self.ListItems[0].ListItemID
		#LAST ID
		elif(Identifier == "LAST_ID"):
			return Self.ListItems[-1].ListItemID	
		#CHECK LOGIC		
		elif(Identifier in Self.LogicCodes):
			return Self.LogicCodes[Identifier]
		#CHECK LIST ITEM LOGIC
		elif(Identifier in Self.ListItems[Index].LogicCodes):
			return Self.ListItems[Index].LogicCodes[Identifier]
		#IF UNKNOW PRINT ERROR AND RETURN BLANK
		else:	
			print ("Error: List - Unrecognized indentifier keyword: "+Identifier)				
			return ("")

	############# QuestionaireList:Finalize #############
	#FUNCTION:   Updates text to prepare for print
	#PARAMATERS: 
	#RETURNS:	 Nothing
	def Finalize(Self, QuestionType):
		for ListItem in Self.ListItems:
			ListItem.Finalize(Self.Scale,QuestionType)
		