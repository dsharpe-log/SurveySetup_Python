
import re

########################################################################################################
######################################### PARSE EXPORT TEMPLATE ########################################
########################################################################################################


# LANG STRUCTURE

# CONCAT
# OBJECT + OBJECT

# OBJECT
#	TEXT
#	CONDITION
#	LOOP
#	INSERTION

#CONDITION
#	[[CONCAT]]:TEXT

#LOOP
#	{{CONCAT}}:TEXT

#ID
# <<TEXT>>

#TEXT

#VALID IDENTIES
#LOOPS 

#


########################### PROCESS SAMPLE.pl ###########################
#DESCRIPTION: Breaks Provided text into a logic tree - flags 
#TODO:
#CHANGE LOG:

import sys
import QuestionaireMisc


class QuestionaireExportTemplate():
	########################################################################################################
	###################################### CONSTANTS AND GLOBALS ###########################################
	########################################################################################################	
	TOKEN_TEXT           = 1000
	
	TOKEN_IDENTITY_START = 1201
	TOKEN_IDENTITY_END   = 1202
	TOKEN_CONDITION_START= 1203
	TOKEN_CONDITION_END  = 1301
	TOKEN_LOOP_START     = 1204
	TOKEN_LOOP_END       = 1302
	TOKEN_COMMENT        = 1205

	TOKEN_STRUCT_ID      = 0
	TOKEN_STRUCT_TEXT    = 1

	NODE_STRUCT_ID          = 0
	NODE_STRUCT_TEXT        = 1
	NODE_STRUCT_LEFT_CHILD  = 2
	NODE_STRUCT_RIGHT_CHILD = 3

	NODE_CONCATENATE = 10000
	NODE_TEXT        = 10001
	NODE_LOOP        = 10002
	NODE_CONDITION   = 10003
	NODE_IDENTIFIER  = 10004

	KeyTwoChar = {	#KEY TWO CHARACTER STRINGS RESERVED BY PROCESSING
		"<<":201,
		">>":202,
		"[[":203,
		"{{":204,
		#"##":205,
	}

	KeyThreeChar = { #KEY THREE CHARACTER STRINGS RESERVED BY PROCESSING
		"]]:" :301,
		"}}:" :302,
	}

	########################################################################################################
	############################################# INITILIZATION ############################################
	########################################################################################################
	############# QuestionaireExportTemplate:Initialization #############
	#FUNCTION:   Object Constructor - Builds a QuestionaireExportTemplate object, breaks down provided text into tree(s) and generates flags
	#PARAMATERS: FileName
	#RETURNS:	 Nothing
	def __init__ (Self, FileName):
		Self.FileName = FileName
		Self.Text =""
		
		try:
			with open(Self.FileName, 'r') as QuestionFile:
				Self.Text = QuestionFile.read()
		except:
			raise Exception("Failed to load file" + Self.FileName)
		#PARSE TEXT INTO TREE
		Self.Lex()
		Self.Tree = Self.Parse(1)  
		

	########################################################################################################
	########################################## SECONDARY FUNCTIONS #########################################
	########################################################################################################
	############# SurveySetup:AddToken #############
	#FUNCTION:   Builds a Token structure
	#PARAMATERS: ID, Text
	#RETURNS:	 Token
	def AddToken (Self, TokenId, TokenText):
		NewToken = [TokenId, TokenText]
		return NewToken
	
	########################################################################################################
	####################################### MAIN PROCESSING FUNCTIONS ######################################
	########################################################################################################
	
	############# SurveySetup:Lex #############
	#FUNCTION:   Deletes processing data structures and tags cleaning up the structure for future use
	#PARAMATERS: Text to be processed
	#RETURNS:	 List of Tokens
	def Lex (Self):
		Text = Self.Text
		#TEXT BEING PROCESSED
		#LIST OF TOKENS GENERATED
		Tokens = []
		#REMOVE NEW LINE CHARACTERS
		Text = Text.replace("\n","")
		#REPLACE \N WITH NEW LINE CHARACTER	
		Text = Text.replace("\\n","\n")
		#CONTINUE TO LOOK UNTIL ALL TEXT HAS BEEN PROCESSED
		while len(Text) > 0:
			#CHECK FOR A BLOCK OF ALPHA_NUMERIC
			if(re.match(r'^([0-9a-zA-Z_]+)',Text)):
				#ADD NEW TOKEN
				Tokens.append(Self.AddToken(Self.TOKEN_TEXT, re.match(r'^([0-9a-zA-Z_]+)',Text).group(1)))
				#REMOVE ASSOCIATE TEXT
				Text = re.sub(r'^([0-9a-zA-Z_]+)',"",Text)
			#CHECK FOR SPACE
			elif(re.match(r'^(\s+)',Text)):
				#ADD NEW TOKEN
				Tokens.append(Self.AddToken(Self.TOKEN_TEXT, re.match(r'^(\s+)',Text).group(1)))
				#REMOVE ASSOCIATE TEXT
				Text = re.sub(r'^(\s+)',"",Text)
			#CHECK FOR A THREE CHARACTER BLOCK
			elif Text[0:3] in Self.KeyThreeChar:
				Tokens.append(Self.AddToken(Self.KeyThreeChar[Text[0:3]]+1000, ""))
				Text = Text[3:]
			#CHECK FOR A TWO CHARACTER BLOCK
			elif Text[0:2] in Self.KeyTwoChar:
				Tokens.append(Self.AddToken(Self.KeyTwoChar[Text[0:2]]+1000, ""))
				Text = Text[2:]
			#ADD THE NEXT CHARACTER AS TEXT (ANYTHING ELSE SHOULD BE VALID)
			else:
				Tokens.append(Self.AddToken(Self.TOKEN_TEXT, Text[0]))
				Text = Text[1:]
		Self.Tokens = Tokens


	############# SurveySetup:Parse #############
	#FUNCTION:   Takes provided token list and build a binary execution tree
	#PARAMATERS: List of Tokens
	#RETURNS:	 Tree Node
	def Parse (Self, InitialPass = 0):
		LeftChild = None
		RightChild = None
		#CHECK FOR LOOP
		if Self.Tokens[0][Self.TOKEN_STRUCT_ID] == Self.TOKEN_LOOP_START:
			#REMOVE FIRST ELEMENT
			Self.Tokens.pop(0)
			#GET TEXT IN LOOP
			ContentNode = Self.Parse(0)
			#CHECK FOR AND REMOVE ELEMENT
			if(Self.Tokens[0][Self.TOKEN_STRUCT_ID] != Self.TOKEN_LOOP_END):
				raise Exception("TEMPLATE SYNTAX ERROR - CAN'T FIND END OF LOOP: "+ Self.FileName)
			Self.Tokens.pop(0)
			#CHECK FOR AND BUILD IDENTIFIER
			if(Self.Tokens[0][Self.TOKEN_STRUCT_ID] != Self.TOKEN_TEXT):
				raise Exception("TEMPLATE SYNTAX ERROR - CAN'T FIND IDENTIFIER ")
			#BUILD ID NODE
			IDNode = [Self.NODE_TEXT, Self.Tokens[0][Self.TOKEN_STRUCT_TEXT]]
			Self.Tokens.pop(0)
			#SET UP LOOP NODE
			LoopNode = [Self.NODE_LOOP, "", ContentNode, IDNode]	
			LeftChild = LoopNode
		#CHECK FOR CONDITION
		elif(Self.Tokens[0][Self.TOKEN_STRUCT_ID] == Self.TOKEN_CONDITION_START):
			#REMOVE FIRST ELEMENT
			Self.Tokens.pop(0)
			#GET TEXT IN LOOP
			ContentNode = Self.Parse(0)
			#CHECK FOR AND REMOVE ELEMENT
			if(Self.Tokens[0][Self.TOKEN_STRUCT_ID] != Self.TOKEN_CONDITION_END):
				raise Exception("TEMPLATE SYNTAX ERROR - CAN'T FIND END OF CONDITION ")
			Self.Tokens.pop(0)
			#CHECK FOR AND BUILD IDENTIFIER
			if(Self.Tokens[0][Self.TOKEN_STRUCT_ID] != Self.TOKEN_TEXT):
				raise Exception("TEMPLATE SYNTAX ERROR - CAN'T FIND IDENTIFIER ")
			#BUILD ID NODE
			IDNode = [Self.NODE_TEXT, Self.Tokens[0][Self.TOKEN_STRUCT_TEXT]]
			Self.Tokens.pop(0)
			#SET UP CONDITION NODE
			ConditionNode = [Self.NODE_CONDITION, '' ,ContentNode, IDNode]
			LeftChild = ConditionNode
		#CHECK FOR IDENTITY
		elif(Self.Tokens[0][Self.TOKEN_STRUCT_ID] == Self.TOKEN_IDENTITY_START):
			#REMOVE FIRST ELEMENT
			Self.Tokens.pop(0)
			#BUILD IDENTITY NODE
			if(Self.Tokens[0][Self.TOKEN_STRUCT_ID] != Self.TOKEN_TEXT):
				raise Exception("TEMPLATE SYNTAX ERROR - CAN'T FIND IDENTIFIER ")		
			IdentityNode = [Self.NODE_IDENTIFIER, Self.Tokens[0][Self.TOKEN_STRUCT_TEXT]]
			Self.Tokens.pop(0)
			if(Self.Tokens[0][Self.TOKEN_STRUCT_ID]  != Self.TOKEN_IDENTITY_END):	
				raise Exception("TEMPLATE SYNTAX ERROR - CAN'T FIND END OF IDENTITY")				
			Self.Tokens.pop(0)
			LeftChild = IdentityNode
		#CHECK FOR TEXT
		elif(Self.Tokens[0][Self.TOKEN_STRUCT_ID] == Self.TOKEN_TEXT):
			#BUILD TEXT NODE
			TextNode = [Self.NODE_TEXT, Self.Tokens[0][Self.TOKEN_STRUCT_TEXT]]
			Self.Tokens.pop(0)
			#LOOP UNTIL NO MORE TEXT TOKENS FOUND
			while(len(Self.Tokens)>0 and Self.Tokens[0][Self.TOKEN_STRUCT_ID] == Self.TOKEN_TEXT):
				TextNode[Self.NODE_STRUCT_TEXT] += Self.Tokens[0][Self.TOKEN_STRUCT_TEXT]
				Self.Tokens.pop(0)
			LeftChild = TextNode
		elif(InitialPass and Self.Tokens[0][Self.TOKEN_STRUCT_ID] == Self.TOKEN_IDENTITY_END):
			raise Exception("End of loop identifier detected, withouth matching start")
		elif(InitialPass and Self.Tokens[0][Self.TOKEN_STRUCT_ID] == Self.TOKEN_CONDITION_END):
			raise Exception("End of loop identifier detected, withouth matching start")
		elif(InitialPass and Self.Tokens[0][Self.TOKEN_STRUCT_ID] == Self.TOKEN_LOOP_END):
			raise Exception("End of loop identifier detected, withouth matching start")	
		
		#PARSE TO BUILD RIGHT SIDE OF CONCATENATE NODE IF MORE TOKENS TO PROCESS
		if (len(Self.Tokens)>0 and Self.Tokens[0][Self.TOKEN_STRUCT_ID] != Self.TOKEN_IDENTITY_END and Self.Tokens[0][Self.TOKEN_STRUCT_ID] != Self.TOKEN_CONDITION_END and Self.Tokens[0][Self.TOKEN_STRUCT_ID] != Self.TOKEN_LOOP_END):
			
			RightChild = Self.Parse(0)
			#BUILD CONCATENATION NODE
			ConcatNode = [Self.NODE_CONCATENATE, "", LeftChild, RightChild]
			return ConcatNode
		#RETURN LEFT CHILD IF NO MORE TOKENS
		else:
			return LeftChild
		

	############# SurveySetup:ProcessNode #############
	#FUNCTION:   Runs the saved binary execution tree and runs it sourcing data from the provided Question structure
	#PARAMATERS: Tree Node, Question Structure
	#RETURNS:	 Text
	def ProcessNode (Self, Node, Question, ListIndex = -1):
		#PROCESS CURRENT NODE IF CONCATENATE
		if(Node[Self.NODE_STRUCT_ID] == Self.NODE_CONCATENATE):
			LeftChild = Self.ProcessNode(Node[Self.NODE_STRUCT_LEFT_CHILD], Question, ListIndex)
			RightChild = Self.ProcessNode(Node[Self.NODE_STRUCT_RIGHT_CHILD], Question, ListIndex)
			if (LeftChild == None): LeftChild = ''
			if (RightChild == None): RightChild = ''		
			return str(LeftChild) + str(RightChild)
			
		#IF TEXT NODE RETURN TEXT STORED
		elif(Node[Self.NODE_STRUCT_ID] == Self.NODE_TEXT):
			return Node[Self.NODE_STRUCT_TEXT]
		#PROCESS IF LOOP
		elif(Node[Self.NODE_STRUCT_ID] == Self.NODE_LOOP):
			Identifier = Question.GetIdentifierValue(Node[Self.NODE_STRUCT_RIGHT_CHILD][Self.NODE_STRUCT_TEXT],ListIndex)
			Result = ""
			#CHECK IF RETURNED STRUCTURE IS AN ARRAY
			if (isinstance(Identifier, list)):
				#LOOP THROUGH PROVIDED ARRAY CALLING EACH LINE INTO THE LEFT SIDE OF THE TREE
				for Index in range(0, len(Identifier)):
					Result += (Self.ProcessNode(Node[Self.NODE_STRUCT_LEFT_CHILD], Question, Index))
			#TO DO: ADD CODE TO HANDLE DICTIONARIES
			return Result
		#PROCESS IF CONDITION
		elif(Node[Self.NODE_STRUCT_ID] == Self.NODE_CONDITION):
			Identifier = Question.GetIdentifierValue(Node[Self.NODE_STRUCT_RIGHT_CHILD][Self.NODE_STRUCT_TEXT],ListIndex)
			if (Identifier == None): Identifier = ''
			#CHECK IF VALUE OF IDENTIFIER IS VALID
			if (Identifier != None and ((isinstance(Identifier, list) and len(Identifier)>0) or re.match(r'[1-9a-z]',str(Identifier)))):
				LeftChild = Self.ProcessNode(Node[Self.NODE_STRUCT_LEFT_CHILD], Question, ListIndex)
				if(LeftChild == None): LeftChild = ''
				return LeftChild
			else:
				return ''
		#IF IDENTIFIER CALL THE QUESTION WITH THE ID AND RETURN
		elif(Node[Self.NODE_STRUCT_ID] == Self.NODE_IDENTIFIER):
			return Question.GetIdentifierValue(Node[Self.NODE_STRUCT_TEXT],ListIndex)


	
	########################################################################################################
	########################################### EXTERNAL FUNCTIONS #########################################
	########################################################################################################
	
	############# SurveySetup:Export #############
	#FUNCTION:   Runs the saved binary execution tree and runs it sourcing data from the provided Question structure
	#PARAMATERS: Question Structure, File Handle
	#RETURNS:	 Question Text
	def Export(Self, Question, FileHandle):
		ReturnText = ""
		#PROCESS TREE AND RETURN TEXT
		ReturnText = Self.ProcessNode(Self.Tree, Question)
		#ON CASE HAD THESE - cHEDAR COLOR STUDY = THINK IT'S A DASH OF SOME SORT
		ReturnText = re.sub(r'\u221a', '', ReturnText)
		ReturnText = re.sub(r'\uf071', '', ReturnText)
		ReturnText = re.sub(r'\u2751', '', ReturnText)
		ReturnText = re.sub(r'\u25cb', '', ReturnText)
		#REMOVE ANY BLANK LINES
		#ReturnText = re.sub(r'\n\s*\n', '\n', ReturnText) #REMOVED 
		FileHandle.write("\n"+ReturnText +"\n")
