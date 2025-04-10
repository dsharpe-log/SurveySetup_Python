
import re

########################################################################################################
########################################## QUESTIONAIRE MISC #######################################
########################################################################################################
#DESCRIPTION: Miscellaneous functions used to process questionnaires
#TODO:
# SEGMENTER - NEED TO MAINTAIN AN UNALTERED VERSION OF EACH SEGMENT FOR RE-INTEGRATION?s
#CHANGE LOG:

#INDEX FOR FORMATTING ARRAYS
FORMAT_ALT_FONT			= 'F'
FORMAT_ALT_COLOR      	= 'C'
FORMAT_ALT_SIZE      	= 'S'
FORMAT_VAL_ALL_CAP  	= 'CAP'
FORMAT_VAL_CRLY_BRK 	= 'CRL'
FORMAT_VAL_SQ_BRK   	= 'SQ'
FORMAT_VAL_BOLD     	= 'B'	
FORMAT_VAL_ITTALIC 		= 'I'
FORMAT_VAL_UNDERLINE	= 'U'

#LIST OF CHARACTERS WHICH DELIMIT TEXT
Delimiters={'(':1,'[':2,'{':3,'<':4,'FORMAT_OFFSET':10,'<<B>>':11,'<<I>>':12,'<<U>>':13,'<<F>>':14, '<<S>>':15, '<<C>>':16,"CLOSING_OFFSET":50,')':51,']':52,'}':53,'>':54,'<</B>>':61,'<</I>>':62,'<</U>>':63,'<</F>>':64,'<</S>>':65,'<</C>>':66,"TERMINAL_OFFSET":100,'<<T>>':101,'...':102,'.':103,'?':104,'!':105,}

#LIST OF OVERRIDES
Override= [r'^\.\s*\d']
#LIST OF TEXT UPDATE PERFORMED VEFORE SEGMENTAITON
SegmentReplace={r'&lt;':r'<',r'&gt;':r'>',r'&amp;':'&'}

#LIST OF SPECIFC VALUES TO REPLACE IN TEXT
Replace  = {r'e\.g':'eg', r'i\.e':'ie', r'I d ':'Id ', r'I m ':'Im ', r'don t':'dont', r'Q (\d+)':r'Q\1', r'Q\.(\d+)':r'Q\1',r'^Q ([a-z])':r'Q\1',r'^Q ([a-z]) ':r'Q\1 ',r'u\.s\.':'us', r'e\. .':'eg',r'(s)':'s',r' s ':'s ',r'(\d+)\s?pm ':'\1 _TIME_ ',r'(\d+)\s?am ':'\1 _TIME_ ',r'(\d+)\s?yrs ':'\1 _TIME_ ',r'(\d+)\s?hrs ':'\1 _TIME_ ',r'(\d+)\s?mins ':'\1 _TIME_ ',r'(\d+)\s?m ':'\1 _DIST_ ',r'(\d+)\s?km ':'\1 _DIST_ ',r'(\d+)\s?pm$':'\1 _TIME_ ',r'(\d+)\s?am$':'\1 _TIME_ ',r'(\d+)\s?yrs$':'\1 _TIME_ ',r'(\d+)\s?hrs$':'\1 _TIME_ ',r'(\d+)\s?mins$':'\1 _TIME_ ',r'(\d+)\s?m$':'\1 _DIST_ ',r'(\d+)\s?km$':'\1 _DIST_ ',r'é':'e',r'â':'a',r'ê':'e',r'î':'i',r'ô':'o',r'û':'u',r'à':'a',r'è':'e',r'ì':'i',r'ò':'o',r'ù':'u'}

############# SurveySetup:GetWord Array #############
#FUNCTION:  Breaks a line fo text into a series of words
#PARAMATERS: Number A-1 B-2 C-3 ... Z-26 AA-27 AB-28
#RETURNS:	 Alpha ID
def GetWordArray(Text, CleanSymbols=1):	
	#CLEAN UP
	for FindKey in Replace.keys():
		Text = re.sub (FindKey,Replace[FindKey], Text, flags=re.IGNORECASE)

	Text =  re.sub(r"['’]","" ,Text)
	Text =  re.sub(r"\<\<[^<>]+\>\>","" ,Text)
	Text =  re.sub(r"(\d),(\d)",r'\1\2' ,Text)	                  #REMOVE COMMAS FROM NUMBERS
	Text =  re.sub(r"(\d).(\d)",r'\1\2' ,Text)	                  #REMOVE DECIMALS FROM NUMBERS

	#REPLACE ANY ACCENTED CHARACTERS WITH STANDARD CHARACTERS
 	#ARRAY OF ALL ACCENTED CHARACTERS
	AccentChars = ['é','â','ê','î','ô','û','à','è','ì','ò','ù']
	#ARRAY OF STANDARD CHARACTERS
	StandardChars = ['e','a','e','i','o','u','a','e','i','o','u']
	#LOOP THROUGH EACH CHARACTER REPLACING ACCENTED WITH STANDARD
	for Index, AccentChar in enumerate(AccentChars):
		Text =  re.sub(AccentChar,StandardChars[Index] ,Text)
	
	Text =  re.sub(r"([^A-Z0-9_$%!?.,#:])"," " ,Text, flags=re.IGNORECASE) #REPLACE ANY NON-ALPHA NUMERIC IGNORED CHARACTERS

	#ARRAY OF VALID NON-ALPHA NUMERIC CHARACTERS
	ValidChars = ['_','$','%','?','!','.',',','#',':']
	#LOOP THROUGH EACH VALID CHARACTER (ESCAPING PASSED STRING)  ADDING SPACES BEFORE AND AFTER EACH CHARACTER 
	for ValidChar in ValidChars:
		Text =  re.sub(re.escape(ValidChar)," "+ValidChar+" " ,Text, flags=re.IGNORECASE) #REPLACE ANY NON-ALPHA NUMERIC IGNORED CHARACTERS

	Text =  re.sub(r"\n"," ", Text)   		                      #REPLACE NEWLINE WITH SPACE
	Text =  re.sub(r" +"," ", Text)                                #REMOVE MULTIPLE SPACES
	Text =  re.sub(r"^\s*_+","", Text)  		                      #REMOVE LEADINGG _	
	Text =  re.sub(r"_+","_", Text)  		                      #REMOVE MULTIPLE UNDERSCORES	
	Text = re.sub(r"_ +tab +_","_TAB_ ", Text, flags=re.IGNORECASE)			              #CLEAN UP TAB TAG
	Text = re.sub(r"_ +list +_ +break +_","_LIST_BREAK_ ", Text, flags=re.IGNORECASE)	      #CLEAN UP LIST BREAK TAG
	Text = re.sub(r"\s+"," ", Text)			                      #REMOVE MULITPLE SPACES
	Text = re.sub(r"\n","", Text)			                      #REMOVE NEW LINES (SHOULDN'T EXIST ANYWAY)
 
	return(Text.split(" "));
	
############# SurveySetup:ConvertNumToID #############
#FUNCTION:   Converts Alphabetical ids to numeric equivalent, otherwise strips all non-numeric
#PARAMATERS: Number A-1 B-2 C-3 ... Z-26 AA-27 AB-28
#RETURNS:	 Alpha ID
def ConvertNumToID (Dividend):
	Return = Dividend			#RETURN STRING
	Modulo =0			#MODULO FOR CALCULATION
	if(re.search(r"[0-9]", str(Dividend), re.IGNORECASE)):
		Return = ""	#RETURN STRING
		Dividend = int(Dividend) #CONVERT TO INTEGER
		#CHECK THAT THERE ARE NO LETTERS PRESENT IN NUM
		if(not(re.search(r"[a-z]", str(Dividend), re.IGNORECASE))):
			while (Dividend > 0):			
				Modulo = (Dividend - 1) % 26
				Return = chr(65 + Modulo) + str(Return)
				Dividend = int((Dividend - Modulo) / 26)
	return (Return)

############# SurveySetup:ConvertIDtoNum #############
#FUNCTION:   Converts Alphabetical ids to numeric equivalent, otherwise strips all non-numeric
#PARAMATERS: Text
#RETURNS:	 Updated ID
def ConvertIDToNum(ID):
	#CHECK IF ID IS ONLY COMPOSED OF LETTERS
	if(re.search(r"^[a-z]+$", str(ID), re.IGNORECASE)):	
		Return=0		
		#LOOP THROUGH EACH LETTER
		for Letter in list(ID.upper()):
			Return=Return*26+(ord(Letter)-64)
		return(Return)
	
	#CHECK IF ID IS BLANK
	if(ID == ""): return 0  
	ID = re.sub(r"[^0-9]","",str(ID)) #REMOVE NON-NUMERIC
	return (int(ID))

############# SurveySetup:Clear Format Tags #############
#FUNCTION:   Removes Formatting tags left in the survey
#PARAMATERS: Text
#RETURNS:	 Updated text
def ClearFormatTags (Text):	
	Text = re.sub(r"<<\/?B>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<\/?I>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<\/?U>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<\/?F>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<\/?S>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<\/?C>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<T>>"," ",Text, flags=re.IGNORECASE)
	Text = re.sub(r"^\s+","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"\s+$","",Text, flags=re.IGNORECASE)
	return (Text)

############# SurveySetup:Clear Tags #############
#FUNCTION:   Removes tags left in the survey
#PARAMATERS: Text
#RETURNS:	 Updated text
def ClearTags(Text):	
	Text = re.sub(r"<<\/?B>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<\/?I>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<\/?U>>","",Text, flags=re.IGNORECASE)

	Text = re.sub(r"<<\/?F>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<\/?S>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<\/?C>>","",Text, flags=re.IGNORECASE)
	
	Text = re.sub(r"<<T>>"," ",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<N>>"," ",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<\/?TABLE>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<VALUE\:\d+>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<BLOCK=\d+>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<LIST_ID[^>]+>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<TABL_IND=\d+>>","",Text, flags=re.IGNORECASE)

	Text = re.sub(r"  "," ",Text, flags=re.IGNORECASE)
	Text = re.sub(r"^\s+","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"\s+$","",Text, flags=re.IGNORECASE)
	
	return (Text)
	
############# SurveySetup:Clear Wrapping Tags #############
#FUNCTION:   Provided a line text removes and tags that completely wrap it
#PARAMATERS: Text
#RETURNS:	 Updated text	
def ClearWrappingTags(Text):
	
	MainSearch = [r"^\s*<<B>>(.*)<<\/B>>\s*$", r"^\s*<<I>>(.*)<<\/I>>\s*$", r"^\s*<<U>>(.*)<<\/U>>\s*$", r"^\s*<<F>>(.*)<<\/F>>\s*$", r"^\s*<<S>>(.*)<<\/S>>\s*$", r"^\s*<<C>>(.*)<<\/C>>\s*$"  ]
	Restriction = [r"<<\/B>>", r"<<\/I>>", r"<<\/U>>", r"<<\/F>>", r"<<\/S>>", r"<<\/C>>"]
	Found=1
	#LOOP UNTIL NOT FOUND
	while(Found ==1):
		Found = 0 
		#LOOP THROUGH SEARCH FUNCTIONS
		for Index,SearchText in enumerate(MainSearch):
			
			#CHECK IF SEARCH IS PRESENT
			if(re.search(SearchText,Text)):
				CheckString = re.search(SearchText,Text).group(1)
				if(not(re.search(Restriction[Index],CheckString))):
					Text = CheckString
					Text = ClearLeadingTrailingSpace(Text)
					Found=1
	return(Text)
		
############# SurveySetup:Save Wrapping Tags #############
#FUNCTION:   Provided a line text returns tags wrapping the text with __TEXT__ replacing any text in the middle
#PARAMATERS: Text
#RETURNS:	 Wrapping Tags	
def SaveWrappingTags(Text):		
	MainSearch = [r"^\s*<<B>>(.*)<<\/B>>\s*$", r"^\s*<<I>>(.*)<<\/I>>\s*$", r"^\s*<<U>>(.*)<<\/U>>\s*$", r"^\s*<<F>>(.*)<<\/F>>\s*$", r"^\s*<<S>>(.*)<<\/S>>\s*$", r"^\s*<<C>>(.*)<<\/C>>\s*$"  ]
	Restriction = [r"<<\/B>>", r"<<\/I>>", r"<<\/U>>", r"<<\/F>>", r"<<\/S>>", r"<<\/C>>"]
	LeadVals=[r'<<B>>', r'<<I>>', r'<<U>>', r'<<F>>', r'<<S>>', r'<<C>>']
	TrailVals=[r'<</B>>', r'<</I>>', r'<</U>>', r'<</F>>', r'<</S>>', r'<</C>>']
	Found=1
	LeadReturn=""
	TrailReturn=""
	#LOOP UNTIL NOT FOUND
	while(Found ==1):
		Found = 0 
		#LOOP THROUGH SEARCH FUNCTIONS
		for Index,SearchText in enumerate(MainSearch):
			#CHECK IF SEARCH IS PRESENT
			if(re.search(SearchText,Text)):
				CheckString = re.search(SearchText,Text).group(1)
				if(not(re.search(Restriction[Index],CheckString))):
					Text = CheckString
					Text = ClearLeadingTrailingSpace(Text)
					LeadReturn += LeadVals[Index]
					TrailReturn = TrailReturn + TrailVals[Index]
					Found=1
	return(LeadReturn+"__TEXT__"+TrailReturn)
		
		
############# SurveySetup:Clear Unmatched Tags #############
#FUNCTION:   Provided a line text removes any tags that are missing there matching start or end - Adds the apporpraite tag to either the start or the end
#PARAMATERS: Text
#RETURNS:	 Updated text	
def ClearUnmatchedTags(Text):
	SearchPairs = {r'<<B>>':r'<</B>>',r'<<I>>':r'<</I>>',r'<<U>>':r'<</U>>',r'<<F>>':r'<</F>>',r'<<S>>':r'<</S>>',r'<<C>>':r'<</C>>'} #SEARCH VALUES
	#LOOP THROUGH THE SEARCH PAIRS
	for StartVal, EndVal in SearchPairs.items():
		#CHECK START -MISISNG END
		if(re.search(EndVal,Text) and not(re.search(StartVal,Text))):
			Text = StartVal + Text
		#CHECK END - MISSING START
		if(re.search(StartVal,Text) and not(re.search(EndVal,Text))):
			Text += EndVal
	return(Text)

############# SurveySetup:Clear Leading Trailing Space #############
#FUNCTION:   Provided a line text removes any tags trailing or leading blank space (including tabs)
#PARAMATERS: Text
#RETURNS:	 Updated text	
def ClearLeadingTrailingSpace(Text):
	Text = re.sub(r'^\s+',"",Text)
	Text = re.sub(r'\s+$',"",Text)			
	Text = re.sub(r'^<<T>>',"",Text, flags=re.IGNORECASE)	
	Text = re.sub(r'<<T>>$',"",Text, flags=re.IGNORECASE)		
	Text = re.sub(r'^\s+',"",Text)
	Text = re.sub(r'\s+$',"",Text)
	return(Text)

############# SurveySetup:GetTextFormatting #############
#FUNCTION:   Provided a line of text looks through the text for formatting tags which affect the whole text line building a hash denoting all values
#PARAMATERS: Text
#RETURNS:	 Text hash denoting formatting
def GetTextFormatting(Text):	
	Formats=[]		#ARRAY USED TO TRACK FORMATS FOUND
	NewFormat = 1	#FLAG DENOTING THAT A NEW FORMAT HAS BEEN FOUND IN THE LATEST PASS THROUGH THE LOOP
	
	#CLEAR BLANK TAGS
	Text = re.sub(r"<<B>>\s*<<\/B>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<I>>\s*<<\/I>>","",Text, flags=re.IGNORECASE)
	Text = re.sub(r"<<U>>\s*<<\/U>>","",Text, flags=re.IGNORECASE)
	
	Text = re.sub(r"<<T>>"," ",Text, flags=re.IGNORECASE)

	#REMOVE LIST DEF
	Text = re.sub(r"<<LIST_ID=[^>]+>>","",Text, flags=re.IGNORECASE)
	#REMOVE BLOCK
	Text = re.sub(r"<<BLOCK[^>]+>>","",Text, flags=re.IGNORECASE)
	#REMOVE TABLE TAGS
	Text = re.sub(r"<<\/?TABLE>>","",Text, flags=re.IGNORECASE)	
	Text = re.sub(r"<<TABL_IND=\d+>>","",Text, flags=re.IGNORECASE)
	
	#LOOP UNTIL NO NEW FORMATS ARE FOUND, IF A FORMAT IS FOUND TEXT DENOTING SAID FORMAT IS REMOVED
	while(NewFormat):
		#CHECK IF THE ENTIRE LINE IS BOLDED
		if(re.search(r"^\s*<<B>>.*<<\/B>>\s*$",Text,re.IGNORECASE)):
			Formats.append(FORMAT_VAL_BOLD)
			Text=re.sub(r"^\s*<<B>>","",Text, flags=re.IGNORECASE)
			Text=re.sub(r"<<\/B>>\s*$","",Text, flags=re.IGNORECASE)
		#CHECK IF THE ENTIRE LINE IS CAPITILIZED (NO LOWER CASE)
		elif(not(re.search(r"[a-z]",Text)) and re.search(r"[A-Z]",Text) and (not(FORMAT_VAL_ALL_CAP in Formats))):	
			Formats.append(FORMAT_VAL_ALL_CAP)
		#TEXT IS WRAPPED BY SQUARE BRACKETS
		elif(re.search(r"^\s*\[.*\]\s*$",Text,re.IGNORECASE)):
			Formats.append(FORMAT_VAL_SQ_BRK)   
			Text = re.sub(r"^\s*\[","",Text, flags=re.IGNORECASE)
			Text = re.sub(r"\]\s*$","",Text, flags=re.IGNORECASE)			
		#TEXT IS WRAPPED BY CURLY BRACKETS
		elif(re.search(r"^\{.*\}$",Text,re.IGNORECASE)):
			Formats.append(FORMAT_VAL_CRLY_BRK) 
			Text = re.sub(r"^\s*\{","",Text, flags=re.IGNORECASE)
			Text = re.sub(r"\}\s*$","",Text, flags=re.IGNORECASE)

		#CHECK IF THE ENTIRE LINE IS ITTALIC
		elif(re.search(r"^\s*<<U>>.*<<\/U>>\s*$",Text,re.IGNORECASE)):
			Formats.append(FORMAT_VAL_UNDERLINE)  
			Text = re.sub(r"^\s*<<U>>","",Text, flags=re.IGNORECASE)
			Text = re.sub(r"<<\/U>>\s*$","",Text, flags=re.IGNORECASE)
		#CHECK IF THE ENTIRE LINE IS UNDERLINED
		elif(re.search(r"^\s*<<I>>.*<<\/I>>\s*$",Text,re.IGNORECASE)):
			Formats.append(FORMAT_VAL_ITTALIC)   
			Text = re.sub(r"^\s*<<I>>","",Text, flags=re.IGNORECASE)
			Text = re.sub(r"<<\/I>>\s*$","",Text, flags=re.IGNORECASE)
		#SET FLAG TO END THE LOOP
		#CHECK FOR ALT COLOR
		elif(re.search(r"^\s*<<C>>.*<<\/C>>\s*$",Text,re.IGNORECASE)):
			Formats.append(FORMAT_ALT_COLOR)   
			Text = re.sub(r"^\s*<<C>>","",Text, flags=re.IGNORECASE)
			Text = re.sub(r"<<\/C>>\s*$","",Text, flags=re.IGNORECASE)			
		#CHECK FOR ALT SIZE
		elif(re.search(r"^\s*<<S>>.*<<\/S>>\s*$",Text,re.IGNORECASE)):		
			Formats.append(FORMAT_ALT_SIZE)   
			Text = re.sub(r"^\s*<<S>>","",Text, flags=re.IGNORECASE)
			Text = re.sub(r"<<\/S>\s*$","",Text, flags=re.IGNORECASE)			
		#CHECK FOR ALT FONT
		elif(re.search(r"^\s*<<F>>.*<<\/F>>\s*$",Text,re.IGNORECASE)):
			Formats.append(FORMAT_ALT_FONT)   
			Text = re.sub(r"^\s*<<F>>","",Text, flags=re.IGNORECASE)
			Text = re.sub(r"<<\/F>>\s*$","",Text, flags=re.IGNORECASE)			
		else:
			NewFormat=0		
	Formats.sort()	
	if(len(Formats) >0):
		return ("_".join(Formats))
	else:
		return("")

############# SurveySetup:GetTextFormattingFlags #############
#FUNCTION:   Provided a line of text looks through the text for formatting tags which affect the whole text line building a hash denoting all values
#PARAMATERS: Text
#RETURNS:	 List of Zeros and Ones denoting formating
def GetTextFormattingFlags(Text):
	FormatText = GetTextFormatting(Text)	#FORMATING TEXT
	FormatList = {}						 	#LIST RETURNED
	#LOOP THROUGH FORMATS	
	for Index, Format in enumerate(['F','CAP','CRL','C','SQ','S','B','I','U']):
		#CHECK IF FORMAT TEXT IS IN THE LIST IF SO SET TO 1 ELSE SET TO 0
		if(re.search(Format,FormatText,re.IGNORECASE)):			
			FormatText = re.sub(Format,"",FormatText, flags=re.IGNORECASE)	
			FormatList[Format]=1
		else:
			FormatList[Format]=0
	return(FormatList)

############# SurveySetup:SegmentText #############
#FUNCTION:   Breaks functions into logical segments
#PARAMATERS: Text
#RETURNS:	 Array of segments
def SegmentText (Text):	
	
	#SUB FUNCTION TO APPEND SEGMENTS
	def AppendSegments(Segments,Text):
		#CHECK IF TEXT IS ONE CHARACTER OR TAB OR DOES NOT CONTAIN A ALPHANUMERIC IF SO APPEND TO LAST SEGMENT
		if((len(Text) == 1 or Text.replace(" ","") == '_TAB_' or Text.replace(" ","") == '<<T>>' or not(re.search(r"[a-zA-Z0-9]",Text))) and len(Segments) > 0):
			#REVERT REPLACE
			Segments[-1] += Text	
		#OTHERWISE ADD TO LIST	
		else:
			Segments.append(Text)
	Segments=[]			#ARRAY STORING SEGMENTS THE LIST ITEM IS COMPRIZED OF
	CapFlag = -1		#DENOTES THAT THE CURRENT SEGMENT IS ALL CAPITALS (-1 - UNKNOWN, 0 - CAPITALIZED, 1 - MIXED)
	CurrentTag=0		#STARTING TAG
	FormatTag=0			#USED TO TRACK A FORMAT TAG IF SPLIT BY INTERNAL BRACKET
	CurrentSegment=''   #CURRENT SEGMENT BEING BUILD
	OtherTextFound = 0	#FLAG DENOTING OTHER TEXT HAS BEEN ADDED TO THE SEGMENT
	InBracket = 0		#FLAG DENOTING THAT THE CURRENT SEGMENT IS IN A BRACKET
	Text = re.sub(r"<<LIST_ID=[^>]+>>","",Text, flags=re.IGNORECASE)	#STRIP LEADING LINE TYPE DEFINITIONS:
	Text = re.sub(r"<<BLOCK[^>]+>>","",Text, flags=re.IGNORECASE)	#REMOVE LIST DEF
	Text = re.sub(r"<<TABL_IND=[^>]+>>","",Text, flags=re.IGNORECASE)	#STRIP LEADING TABLE DEFINITIONS:
	#CHARACTER REPLACEMENT
	Text = re.sub(r''," - ",Text)  #SOH

	#CLEAR UNMATCHED TAGS
	Text = ClearUnmatchedTags(Text)
	Text = ClearLeadingTrailingSpace(Text)

	#CLEAN UP	
	WrappingText = SaveWrappingTags(Text)
	Text = ClearWrappingTags(Text)
	#RUN THROUGH REPLACEMENT CODES TO SIMPLIFY SEGMENTATION
	#for FindKey in SegmentReplace.keys():
	#	Text = re.sub (FindKey,SegmentReplace[FindKey], Text, flags=re.IGNORECASE)
	#print("Segment: "+Text)
	#CONTINUE TO LOOP UNTIL TEXT IS EMPTY
	while (re.search(r"\S",Text)):	
		
		First = Text[0:1]	#FIRST CHARACTER IN THE CURRENT STRING					
		#IF TEXT IS LED BY A TAG REPLACE WITH TAG
		if(re.search(r"^(<<[^>]+>>)",Text)): First = re.search(r"^(<<[^>]+>>)", Text).group(0)
		#print("First: "+First)	
		#CHECK FOR LEADING SPACE		
		if (re.search(r"^(\s+)",Text)):
			CurrentSegment += re.search(r"^(\s+)", Text).group(0)
			Text = re.sub(r"^(\s+)", "", Text, flags=re.IGNORECASE)	
		#CHECK LEADING TEXT		
		elif (First in Delimiters):		
			TagID = Delimiters[First]	#ID OF THE CURRENT TAG			
			#CHECK FOR OPENING TAG
			if (TagID < Delimiters['CLOSING_OFFSET']) :
				#print("Opening Tag: "+First + " - "+ str(OtherTextFound) + " - "+ str(InBracket) + " - "+ str(TagID) + " - "+ str(CurrentTag))
				#CHECK IF CURRENTLY IN BOUND TEXT SEGEMENT				
				if(CurrentTag == 0 or (OtherTextFound==1 and InBracket==0 and TagID < Delimiters['FORMAT_OFFSET'])):
					#print("ADDED")
					#ADD CURRENT SEGMENT TO LIST IF NOT BLANK		
					if(CurrentSegment != ''): AppendSegments(Segments,CurrentSegment)
					if (TagID > Delimiters['FORMAT_OFFSET']):
						FormatTag= FormatTag
					CurrentTag=TagID 
					CurrentSegment = ''	
					OtherTextFound=0					
					CapFlag = -1						
				#CHECK IF IN BRAKET AND SET FLAG
				if(TagID < Delimiters['FORMAT_OFFSET']):
					InBracket = 1					
				CurrentSegment += First				
			#CHECK FOR CLOSING TAG
			elif(TagID > Delimiters['CLOSING_OFFSET'] and TagID < Delimiters['TERMINAL_OFFSET']):		
				#print("Closing Tag: "+First)	
				#IF ENDING searchES CURRENT TAG
				CurrentSegment += First
				if(CurrentTag+Delimiters['CLOSING_OFFSET'] == TagID):
					#print("ADDED")
					#ADD CURRENT SEGMENT TO LIST IF NOT BLANK							
					if(CurrentSegment != ''):  AppendSegments(Segments,CurrentSegment)
					if(FormatTag+Delimiters['CLOSING_OFFSET'] == TagID):
						FormatTag=0
					#SET CURRENT TAG NOT TAB  
					if(FormatTag != 0):
						CurrentTag=FormatTag
					else:
						CurrentTag=0
					CapFlag = -1	
					InBracket = 0			
					CurrentSegment = ''													 
			#CHECK FOR TABS / OTHER BREAKS
			elif(TagID > Delimiters['TERMINAL_OFFSET'] and CurrentTag == 0):	
				#print("OTHER BREAK: "+First)				
				#ADD CURRENT SEGMENT TO LIST IF NOT BLANK		
				CurrentSegment += First		
				#CHECK FOR OVERRIDE
				OverrideFound = False
				for OverrideCheck in Override:
					if (re.search(OverrideCheck, Text, flags=re.IGNORECASE)):
						OverrideFound=True
				if(not(OverrideFound)):
					if(CurrentSegment != ''): AppendSegments(Segments,CurrentSegment)
					#SET CURRENT TAG NOT TAB  
					CurrentTag=0 
					FormatTag=0
					CapFlag = -1				
					CurrentSegment = ''		
			#OTHERWISE ADD TO CURRENT SEGMENT (NOT TERMINAL)			
			else:
				#print("TEXT")
				CurrentSegment += First
				#IF IN TAG SET OTHER TEXT 
				if(CurrentTag != 0): 
					OtherTextFound = 1
			Text = re.sub(r"^"+re.escape(First),"",Text, flags=re.IGNORECASE)		

		#CHECK IF TEXT IS LED BY ALPHA NUMERIC
		elif(re.search(r"^[a-z]+", Text, re.IGNORECASE)):				
			NextWord =  re.search(r"^([a-z]+)", Text, re.IGNORECASE).group(0)	#LEADING TEXT FROM THIS LINE
			if ((CurrentTag == 0 and CapFlag == 1 and re.search(r"[a-z]",NextWord)) or (CurrentTag == 0 and CapFlag==0 and len(NextWord)>2 and not(re.search(r"[a-z]",NextWord)))):
				if(CurrentSegment != ''): AppendSegments(Segments,CurrentSegment)						
				CurrentSegment = ''						
			#SET CAP FLAG
			if (len(NextWord)>=2 ):				 
				if(re.search(r"[a-z]", NextWord)):
					CapFlag = 0 
				elif(re.search(r"[A-Z]", NextWord)):
					CapFlag = 1		
			CurrentSegment += NextWord	
			Text = re.sub(r"^"+re.escape(NextWord),"",Text, flags=re.IGNORECASE)		
			if(CurrentTag != 0): 
				OtherTextFound = 1						
		#ANY NUMBER
		elif(re.search(r"^[0-9]+", Text)):
			NextWord =  re.search(r"^([0-9]+)", Text).group(0)	#LEADING TEXT FROM THIS LINE
			CurrentSegment += NextWord					
			Text = re.sub(r"^([0-9]+)","",Text)			
			if(CurrentTag != 0): 
				OtherTextFound = 1						
		#ANY OTHER CHARACTER		
		else:	
			CurrentSegment += First										
			Text = re.sub(r"^"+re.escape(First),"",Text, flags=re.IGNORECASE)			
			if(CurrentTag != 0): 
				OtherTextFound = 1						
	#ADD LAST SEGMENT TO LIST		
	if(CurrentSegment != ''): AppendSegments(Segments,CurrentSegment)
	#LOOP THROUGH SEGMENTS ADDING WRAPPING TEXT BACK TO 
	if (WrappingText != "__TEXT__"):
		for Index, Segment in enumerate(Segments):
			Segments[Index] = WrappingText.replace('__TEXT__',Segment)
	#LOOP THROUGH SEGMENTS ADDING TAGS THAT ENCLOSE A SEGMENT  - CORRECTING SOME ISSUES AROUND THE BRACKETS NESTED WITHIN FORMATTING	
	for SegIndex, Segment in enumerate(Segments):
		if(SegIndex > 0 and SegIndex < len(Segments)-1):
			Start=['(','[','{','<<B>>','<<I>>','<<U>>','<<F>>', '<<S>>', '<<C>>','<']
			End=[')',']','}','<</B>>','<</I>>','<</U>>','<</F>>','<</S>>','<</C>>','>']
			#CHECK EACH TAG PAIR
			for TagIndex, Tag in enumerate(Start):
				if(re.search(re.escape(Start[TagIndex])+r"\s*(<<T>>)*$",str(Segments[SegIndex-1])) and re.search(r"^(<<T>>)*\s*"+re.escape(End[TagIndex]),str(Segments[SegIndex+1]))):
					Segments[SegIndex] = Start[TagIndex]+Segments[SegIndex]+End[TagIndex]
					Segments[SegIndex+1] = re.sub(r"^\s*(<<T>>)*"+re.escape(End[TagIndex]),"",Segments[SegIndex+1])
					Segments[SegIndex-1] = re.sub(re.escape(Start[TagIndex])+"\s*(<<T>>)*$","",Segments[SegIndex-1]) 
	#REMOVE ANY EMPTY SEGMENTS
	for Index, Segment in enumerate(Segments):
		if(not(re.search(r"\S",str(Segment)))): 
			del Segments[Index]
	return (Segments)

############# SurveySetup:SelectHigh #############
#FUNCTION:   Passed a hash where each key points to a number returns the key with the highest associated value
#PARAMATERS: Hash or Array, Debug Flag 
#RETURNS:	 Key of Highest value, or Index of highest Value
def SelectHigh (List, DebugFlag=0):
	SelectedElement = ""		#KEY SELECTED	
	#CHECK IF LIST IS REFERENCING A HASH
	if (type(List) is dict):
		#SELECT HIGHEST WEIGHT
		for Key in List.keys():
			if (DebugFlag): print (str(Key)+" - "+str(List[Key]))
			#IF NOTHING SELECTED SELECT
			if (SelectedElement == ""): SelectedElement = Key 
			#IF WEIGHT OF CURRENT ITEM IS GREATER THAN SELECTED ITM			
			if(List[Key] > List[SelectedElement]): SelectedElement = Key 
		if (DebugFlag): print (SelectedElement)
		return (SelectedElement)
	elif(type(List) is list):	
		#SELECT HIGHEST WEIGHT
		for Index, Value in enumerate(List):
			if (DebugFlag): print (str(Index)+" - "+str(Value)) 
			#IF NOTHING SELECTED SELECT
			if (SelectedElement == ""): SelectedElement = Index 
			#IF WEIGHT OF CURRENT ITEM IS GREATER THAN SELECTED ITM
			if(Value > List[SelectedElement]): SelectedElement = Index 

		if (DebugFlag): print (SelectedElement)
		return (SelectedElement)

	#DIE IF INVALID REFERNCE PROVIDED
	else:
		raise Exception("Invalid reference povided\n")


############# SurveySetup:GetWords #############
#FUNCTION:   Passed a line of text breaks text into word
#PARAMATERS: Hash or Array, Debug Flag
#RETURNS:	 Pointer to Array
def GetWords(Text):
	Text = re.sub(r"([^A-Z0-9_]+)",r" \1 ",Text, flags=re.IGNORECASE) #ADD SPACES BEFORE AND AFTER ANY NON-ALPHA NUMERIC CHARACTER	
	Text = re.sub(r" +"," ",Text)              #REMOVE MULTIPLE SPACES

	#BREAK TEXT INTO WORDS - RETURN
	return (Text.split(' '))
	

############# SurveySetup:KeywordID #############
#FUNCTION:   Provided a string and an array of keywords returns a 1 or 0 depending on if one of the keywords is found in the text
#PARAMATERS: Text, Array of Keywords
#RETURNS:	 1 or 0 depening on if a keyword has been found
def KeywordID (Text, Keywords):	
	Found=0						#RETURN FLAG
	#BREAK TEXT INTO WORDS
	TextList = GetWords(Text)	#LIST OF WORDS 	
	#LOOP THROUGH KEYWORDS
	Keywords.sort()
	for Keyword in (Keywords):
		#LOOP THROUGH TEXT WORDS
		for Index, Value in enumerate(TextList):		
			#CHECK IF KEYWORD IS MULTIPLE WORDS			
			if(" " in Keyword): 
				SpaceCount = Keyword.count(" ") 	#NUMBER OF SPACES IN KEYWORKD
				MergedWords = ""					#WORDS
				#LOOP MERGING WORDS			
				WordIndex=0
				while(WordIndex <= SpaceCount):					
					if(Index+WordIndex < len(TextList)): MergedWords += TextList[Index+WordIndex]+" "
					WordIndex +=1
				MergedWords = re.sub(r" $","",MergedWords) #REMOVE TRAILING SPACE
				#CHECK IF KEYWORD IS THE SAME AS MERGED WORD
				if (Keyword.upper() == MergedWords.upper()):
					Found=1				
			#CHECK IF TEXT WORD EQUAL TO KEYWORD
			elif(Value.upper() == Keyword.upper()):		
					Found=1
	return Found

############# SurveySetup:GetPrevCode #############
#FUNCTION:   Provided a statement/choice code (alpha or numeric) and generates the code which preceeded this one
#PARAMATERS: Code (alpha or numeric)
#RETURNS:	 Previous alpha or numeric code
def GetPrevCode (Code):
	#CHECK IF CODE IS NUMERIC
	if(re.search(r"\(?(\d+)\)?",Code)):
		return int(re.sub(r"\D+","",Code)) - 1	
	#IF CODE IS ALPHA
	else:
		return ConvertNumToID(ConvertIDToNum(Code)-1)

############# SurveySetup:GetNextCode #############
#FUNCTION:   Provided a statement/choice code (alpha or numeric) and generates the code which follows this one
#PARAMATERS: Code (alpha or numeric)
#RETURNS:	Next Numeric of Alpha code
def GetNextCode (Code):
	#CHECK IF CODE IS NUMERIC
	if(re.search(r"\(?(\d+)\)?",Code)):
		return int(re.sub(r"\D+","",Code)) + 1	
	#IF CODE IS ALPHA
	else:
		return ConvertNumToID(ConvertIDToNum(Code)+1)	

############# SurveySetup:GetDelimiter #############
#FUNCTION:   Currently just defaults to tab - holding point for more complex delimiter identification fucntion
#PARAMATERS: LineText
#RETURNS:	Value used to subdivide the text
def GetDelimiter(LineText):
	return "<<t>>"

############# SurveySetup:Keyword Search #############
#FUNCTION:   Provided a string and an hash of keywords pointing to weights this script sums all keywords found and returns this value, 
# three referenced variables are also updated denoting that the text consisted of only positive keywords, only negative keywords or any keyword. 
# The program assumes these flags are true (1) on execution and updates them to false (0) if determine that they are not true.
#PARAMATERS: Text, Keyword Hash, Only Positive Reference, Only Negative Reference, Only Keywords reference
#RETURNS:	 Sum of weights of Keywords found
def KeywordSearch (Text, Keywords):
	AllPositiveUsed = 1	   #REFERENCE TO FLAG DENOTING THAT THE TEXT IS ALL POSITIVE KEYWORDS
	AllNegativeUsed = 1    #REFERENCE TO FLAG DENOTING THAT THE TEXT IS ALL NEGATIVE KEYWORDS 
	AllUsed = 1            #REFERENCE TO FLAG DENOTING THAT THE TEXT IS ALL KEYWORDS
	KeywordCount = 0	   #REFERENCE TO FLAG COUNTING THE NUMBER OF KEYWORDS IN THE FILE
	Weight=0			   #SUMMED WEIGHT OF ALL KEYWORDS
		
	#SORTS THE KEYWORDS BY LENGTH
	def SortFunc(Element):
		return -1 * len(Element)	
	#BREAK TEXT INTO WORDS
	Text = ClearTags(Text);
	TextList = GetWords(Text) 
	#LOOP THROUGH KEYWORDS
	Keys = list(Keywords.keys())
	Keys.sort(key=SortFunc)
	for Keyword in Keys:
		#LOOP THROUGH TEXT WORDS
		for Index,Text in enumerate(TextList):
			#CHECK IF KEYWORD IS MULTIPLE WORDS
			if(" " in Keyword): 
				SpaceCount = Keyword.count(' ') 		#NUMBER OF SPACES IN KEYWORKD
				MergedWords = ""					  	#WORDS
				#LOOP MERGING WORDS			
				WordIndex=0
				while(WordIndex <= SpaceCount):
					if(Index+WordIndex < len(TextList)): MergedWords += TextList[Index+WordIndex]+" "
					WordIndex += 1
					
				MergedWords = re.sub(r" $","",MergedWords) #REMOVE TRAILING SPACE
				#CHECK IF KEYWORD IS THE SAME AS MERGED WORD				
				if (Keyword.upper() == MergedWords.upper()):
					Weight += int(Keywords[Keyword])
					#LOOP THROUGH WORDS
					WordIndex=0
					while(WordIndex <= SpaceCount):
						TextList[Index+WordIndex]="";
						WordIndex +=1
					#UPDATE FLAGS
					if(int(Keywords[Keyword]) <0): AllPositiveUsed=0
					if(int(Keywords[Keyword]) >0): AllNegativeUsed=0
					KeywordCount+= 1
			#CHECK IF TEXT WORD EQUAL TO KEYWORD
			elif(TextList[Index].upper() == Keyword.upper()):			
				Weight+=int(Keywords[Keyword])
				TextList[Index]=""
				#UPDATE FLAGS
				if(int(Keywords[Keyword]) <0): AllPositiveUsed=0
				if(int(Keywords[Keyword]) >0): AllNegativeUsed=0
				KeywordCount += 1
				
	RemainingText = " ".join(TextList)	
	if(re.search(r"[a-z]", RemainingText, re.IGNORECASE) or KeywordCount==0): 
		AllUsed=0 
		AllPositiveUsed=0 
		AllNegativeUsed=0 
	return (Weight, AllPositiveUsed, AllNegativeUsed, AllUsed, KeywordCount)


############# SurveySetup:GetNumbers #############
#FUNCTION:   Provided a line of text finds each unique number in the text and returns a sorted list
#PARAMATERS: Text
#RETURNS:	 Sorted list of numbers
def GetNumbers (Text):	
	TrackUnique = {}				#HASH USED TO TRACK UNIQUE VALUES
	ReturnList =[]					#ARRAY RETURNED FROM THIS FUNCTION
		
	for (RegRet) in re.findall(r"[^a-z](\d+)[^a-z]", Text, re.IGNORECASE):
		if(not(RegRet in TrackUnique)):
			ReturnList.append(RegRet)
			TrackUnique[RegRet]=1
	return(ReturnList)


############# SurveySetup:RunReformatting #############
#FUNCTION:   Provided a Config Structure and a text returns reformatted text  - NOT USED ANYMORE
#PARAMATERS: Text, Config
#RETURNS:	 Reforamtted Text
def RunReformat (Text, Config):

	Found=1
	First=1	
	if (not(Text)):return(Text)
	while(Found):
		Found=0
		#CLEAN UP TEXT AROUND FORMATTING
		for CleanupText in Config:			
			if(First == 1 or "CYCLIC" in CleanupText):
				ToReplace = CleanupText["SEARCH"]		
				LeadReplace = '^'+ToReplace	 #TEXT TO CHECK LEADING
				TrailReplace = ToReplace+'$' #TEXT TO CHECK TRAILING				
				Pass =0  #PASS FOUND

				if("LEADING" in CleanupText):
					if (re.search(LeadReplace,Text, re.IGNORECASE)): Pass=1 

				elif("TRAILING" in CleanupText):
					if (re.search(TrailReplace,Text, re.IGNORECASE)): Pass=1

				else:			
					if (re.search(ToReplace,Text, re.IGNORECASE)): Pass=1								

				if (Pass):
					#REPLACE WITH FIRST FOUND SUBSTRING
					if ("REPLACE_FIRST" in CleanupText):
						Text = re.sub(ToReplace,"\1",Text, flags=re.IGNORECASE)
						Found=1
					elif ("CLEAR" in CleanupText):
						if("LEADING" in CleanupText):
							Text = re.sub(LeadReplace,"",Text, flags=re.IGNORECASE)
						elif("TRAILING" in CleanupText):
							Text = re.sub(TrailReplace,"",Text, flags=re.IGNORECASE)
						else:
							Text = re.sub(ToReplace,"",Text, flags=re.IGNORECASE)
						Found=1
						
					elif("REPLACE" in CleanupText):
						ReplaceWith = CleanupText["REPLACE"]
						Text = re.sub(ToReplace,ReplaceWith,Text, flags=re.IGNORECASE)
						Found=1
					elif("REPLACE_SPACE" in CleanupText):
						Text = re.sub(ToReplace," ",Text, flags=re.IGNORECASE)
						Found=1
					elif("PRE_SPACE" in CleanupText):
						Text = re.sub(ToReplace," $1",Text, flags=re.IGNORECASE)
						Found=1
					elif("POST_SPACE" in CleanupText):
						Text = re.sub(ToReplace,"$1 ",Text, flags=re.IGNORECASE)
						Found=1

		First=0	
	return(Text)



############# SurveySetup:CleanupNestedTags #############
#FUNCTION:   Looks for tags nested within other tags in an incorrect format and reformats them	
#PARAMATERS: Text
#RETURNS:	 Updated Text
def CleanupNestedTags (Text):	
	Found=1				#FLAG DENOTING THAT A TAG HAS BEEN FOUND - USED TO LOOP UNTIL NO ISSUES FOUND	
	WrappingTags = ["B","I","U","F","S","C"]	#WRAPPING TAGS	
	#print(Text)
	#SEARCH TAG VALUES
	#LOOP UNTIL NO ISSUES FOUND
	while (Found):
		Found=0
		
		#LOOP THROUGH WRAPIING TAGS, WITH INDEX
		for Tag in WrappingTags:			
			#print("\nTAG:"+Tag) #tracking				
			#LOOP THROUGH INSTANCES OF TAG	- NEED TO MODIFY THIS IF IMPLEMENT COLOR/SIZE/FONT ECT OR USE SING CHARACTER FOR EACH	
			#SET INSTANCE SPLITS FOR PROCESSING
			RemergeText = []
			SplitText = Text
			SplitText = re.sub(r"<<"+Tag+">>","%^%<<"+Tag+">>",SplitText)
			SplitText = re.sub(r"<<\/"+Tag+">>","<</"+Tag+">>%^%",SplitText)
			Splits = SplitText.split("%^%")
			#print("SPLIT:"+SplitText) #tracking
#TO DO - REPLACE THE INTERATOR GENERATION WITH A FUNCTION - THIS SEEMS TO BREAK UNDER CERTAIN CONDITIONS RESULTING IN AN INFINITE LOOP
			for Match in Splits:
				if(not(re.search(r"^<<"+Tag+">>",Match, re.IGNORECASE))): continue
				#print("MATCH:"+Match) #tracking
				InternalTagText = Match	#TEXT BETWEEN TAGS		
				InternalTagText = re.sub(r"<<\/?"+Tag+">>","",InternalTagText)	#REMOVE LEADING TAG+TRAILING TAG
				#CHECK IF STARTS WITH TAGsuINSERT SINGLE VARIETY IMAGE
				if(re.search(r"^<<([^>])+>>",InternalTagText, re.IGNORECASE)):
					LeadTag= re.search(r"^<<([^>])+>>",InternalTagText, re.IGNORECASE).group(1)	#LEADING TAG IN THE TEXT
					LeadTagType = LeadTag	                                                    #TYPE OF TAG (REMOVES THE CLOSING CHARACTER IF PRESET)
					LeadTagType = re.sub(r"/","",LeadTagType)
					#print("LEADING TAG FOUND:"+LeadTag)	
					#IF A TRAILING TAG			
					if(re.search(r"^\/",LeadTag) and LeadTagType in WrappingTags):	
						#UPDATE TEXT
						UpdateText = InternalTagText
						UpdateText = re.sub(r"^<<"+LeadTag+">>","<<"+LeadTag+">><<"+Tag+">>",UpdateText)
						#print("UPDATE LEADING_TRAIL:"+UpdateText) #tracking
						Text = re.replace ("<<"+Tag+">>"+re.escape(InternalTagText), UpdateText, Text, flags=re.IGNORECASE)
						Found = 1				
					#IF A LEADING TAG								
					elif(LeadTagType in WrappingTags and not(re.search(r"<<\/"+LeadTag+">>", InternalTagText, re.IGNORECASE))):			
						#UPDATE TEXT
						UpdateText = InternalTagText
						UpdateText = re.sub(r"^<<"+LeadTag+">>","<<"+LeadTag+">><<"+Tag+">>",UpdateText)
						#print("UPDATE LEADING_LEAD:"+UpdateText) #tracking
						Text = re.sub ("<<"+Tag+">>"+re.escape(InternalTagText), UpdateText, Text, flags=re.IGNORECASE)						
						Found = 1
					#print("TEXT:"+InternalTagText) #tracking
				#CHECK IF TRAILS WITH TAG
				if(re.search(r"/<<([^>]+)>>$", InternalTagText, re.IGNORECASE)):				
					TrailTag = re.search(r"/<<([^>]+)>>$", InternalTagText, re.IGNORECASE).group(1)
					TrailTagType = TrailTag	#TYPE OF TAG (REMOVES THE CLOSING CHARACTER IF PRESET)
					TrailTagType = re.sub(r"/","",TrailTagType)					
					#print("INTERNAL TAG FOUND: "+TrailTag)	 #tracking				
					#IF A LEADING TAGss
					if(not(re.search(r"^\/", TrailTag, re.IGNORECASE)) and TrailTagType in WrappingTags):	
						#UPDATE TEXT
						UpdateText = InternalTagText
						UpdateText = re.sub(r"/<<"+TrailTag+">>$","<<"+Tag+">><<"+TrailTag+">>",UpdateText)
						#print("UPDATE TRAILING_LEAD:"+UpdateText)	 #tracking					
						Text = re.sub (re.escape(InternalTagText)+"/<<"+TrailTag+">>", UpdateText, Text, flags=re.IGNORECASE)
						Found = 1
					elif(TrailTagType in WrappingTags and not(re.search(r"<<"+TrailTag+">>", InternalTagText, re.IGNORECASE))):
						#UPDATE TEXT
						UpdateText = InternalTagText
						UpdateText = re.sub(r"/<<"+TrailTag+">>$","<<"+Tag+">><<"+TrailTag+">>",UpdateText)
						#print("UPDATE TRAILING_TRAIL:"+UpdateText)	 #tracking					
						Text = re.sub (re.escape(InternalTagText)+"/<<"+TrailTag+">>", UpdateText, Text, flags=re.IGNORECASE)
						Found = 1				
			#print("DONE:"+Text) #tracking
	return(Text)

############# SurveySetup:CleanupListTags #############
#FUNCTION:   Looks for tags in the list entries that ecompose the whole source string (this function presumes that said list was split from a singl line) and projects those tags into each entry in the list
#PARAMATERS: List
#RETURNS:	 Updated List
def CleanupListTags (List):
	for Tag in ['B','I','U']:
		#LOOP THROUGH LIST
		for InitIndex, InitEntry in enumerate(List):
			if(re.search(r"<<"+Tag+">>",List[InitIndex], re.IGNORECASE) and not(re.search(r"<<\/"+Tag+">>",List[0], re.IGNORECASE)) and (re.search(r"<<\/"+Tag+">>",List[-1], re.IGNORECASE))):
				#LOOP THROUGH LIST
				for Index, Entry in enumerate(List):
					if(Index<InitIndex): continue
					#IF NOT FIRST ELEMENT ADD TAG TO START
					if(not(Index == InitIndex)):
						List[Index] = "<<"+Tag+">>"+Entry
					#IF NOT LAST ELEMENT ADD TAG TO END
					if(not(Index == len(List)-1)):
						List[Index] = Entry+"<</"+Tag+">>"
				break
	return(List)
############# SurveySetup:CleanupOrphanTags #############
#FUNCTION:   Looks for tags without matching opening/closing and removes
#PARAMATERS: Text
#RETURNS:	 Updated Text
def CleanupOrphanTags (Text):	
	WrappingTags = ["B","I","U","F","S","C"]	#WRAPPING TAGS
	#LOOP THROUGH WRAPPING TAGS
	for Tag in WrappingTags:		
		#print("\nTAG:"+Tag)
		#CHECK LEADING IN TEXT
		if(re.search(r"<<\/?"+Tag+">>",Text, re.IGNORECASE)):
			SplitText = Text.split("<<"+Tag+">>")
			#REMOVE FIRST BREAK IF BLANK
			if(SplitText[0] == ""): SplitText = SplitText[1:]
			UpdateText = ""
			#print("LEADING SPLIT TEXT:"+str(SplitText))			
			#LOOP THROUGH SPLITS			
			for Index, Split in enumerate(SplitText):
				#CHECK IF CURRENT SPLIT TEXT WITHOUT TAG (NOT LEADING TAG FOUND)
				if(Index == 0 and not(re.search(r"^<<"+Tag+">>" ,Text, re.IGNORECASE))):
					UpdateText = Split
				#LOOK FOR LEADING TAG
				elif(re.search(r"<<\/?"+Tag+">>" ,Split, re.IGNORECASE)):
					UpdateText += "<<"+Tag+">>" + Split
				else:
					UpdateText += Split

			Text = UpdateText
			#print(Text)
			#RESET FOR TRAILING
			SplitText = Text.split("<</"+Tag+">>")
			if(SplitText[0-1] == ""): SplitText = SplitText[:-1]	
			UpdateText = ""
			#print("TRALING SPLIT TEXT:"+str(SplitText))			
			#CHECK TRAILING IN TEXT
			for Index, Split in reversed(list(enumerate(SplitText))):				
				#CHECK IF TRAILING TEXT WITHOUT TAG (NOT TRAILING TAG FOUND)
				if(Index == len(SplitText)-1 and not(re.search(r"<<\/"+Tag+">>$" ,Text, re.IGNORECASE))):
					UpdateText = Split
				#LOOK FOR LEADING TAG
				elif(re.search(r"<<\/?"+Tag+">>" ,Split, re.IGNORECASE)):
					UpdateText = Split +"<</"+Tag+">>"+ UpdateText
				#NOT TRAILING TAG FOUND REMOVE LEADING
				else:
					UpdateText = Split + UpdateText

			Text = UpdateText
			#print(Text)
		#print(Text)
	return(Text)