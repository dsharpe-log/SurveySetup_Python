
import pprint
import re
import io

#CHANGE LOG
#2023-05-09 - Modified hash interaction with defined command list to only allow for value defition but not require it


TOKEN_TYPE_COLON		  		= 0
TOKEN_TYPE_TILDE		  		= 1
TOKEN_TYPE_OPEN_SQ_BRACKET  	= 2
TOKEN_TYPE_CLOSE_SQ_BRACKET  	= 3
TOKEN_TYPE_OPEN_CR_BRACKET  	= 4
TOKEN_TYPE_CLOSE_CR_BRACKET  	= 5
TOKEN_TYPE_ESCAPE				= 6
TOKEN_TYPE_COMMENT				= 7
TOKEN_TYPE_CONTINUE				= 8
TOKEN_TYPE_STRING				= 9

TokenCharacters = {					#Key characters found in config
	':' : TOKEN_TYPE_COLON,
	'~' : TOKEN_TYPE_TILDE,
	'[' : TOKEN_TYPE_OPEN_SQ_BRACKET,
	']' : TOKEN_TYPE_CLOSE_SQ_BRACKET,
	'{' : TOKEN_TYPE_OPEN_CR_BRACKET,
	'}' : TOKEN_TYPE_CLOSE_CR_BRACKET,
	'`' : TOKEN_TYPE_ESCAPE,
	'---' : TOKEN_TYPE_COMMENT,
	'...' : TOKEN_TYPE_CONTINUE,
}

CharacterReturn =[ #LINKS TOKEN INDEX TO CHARACTER
	':',
	'~',
	'[',
	']',
	'{',
	'}',
	'`',
	'---',
	'...',
	'STRING'
]

#TOKEN CLASS
#Used by the lexer to break strings into formal types while preserving data and 
class Token:
	#CONSTRUCTOR CLASS 
	#PARAMATERS: File Name
	#RETURNS: NOTHING:
	def __init__(Self, Type, Value, LineNum):
		Self.Type = Type
		Self.Value = Value
		Self.LineNum = LineNum
	
#DCONFIG CLASS
class DConfig:		
	#CONSTRUCTOR CLASS 
	#PARAMATERS: File Name
	#RETURNS: NOTHING:
	def __init__(Self, FileName, Commands):
		Self.Config = {}
		Self.FileName = FileName		
		Self.Commands = Commands
		if not(isinstance(Self.Commands, dict)):
			raise Exception(Self.FileName + '\nCommand list must be a dictionary');
		Self.Tokens = []		
		Self.ProcessConfig()
		
	#PROCESS CONFIG
	#FUNCTION: Opens and processes a cofnig file populating the config data structure
	#PARAMATER: Nothing
	#RETURNS: Nothing
	def ProcessConfig(Self):		
		
		with io.open(Self.FileName,mode="r", encoding="utf-8") as InputFile:
			#LOOP THROUGH EACH LINE
			for LineNumber, Line in enumerate(InputFile): 	
				Line = Line.rstrip("\n\r")			
				Self.Lex(Line,LineNumber)			
			InputFile.close()			
			Self.CleanTokens();
			Self.Parse();	
	#LEX
	#FUNCTION: Breaks provided string into a list of tokens
	#PARAMATER: Line of text, Line number of text
	#RETURNS: Nothing
	def Lex(Self, Line, LineNumber):
		CurrentLine = Line 		#CURRENT LINE 
		InEscape = 0			#DENOTES ESCAPE CHARACTER HAS BEEN ENCOUNTERED			
		CurrentToken = None		#CURRENT TOKEN USED FOR STRINGS
	
		#CHECK FOR THRE CHARACTER LIMIT
		while CurrentLine:
			if(CurrentToken is None):
				CurrentLine.strip();
			OneChar = CurrentLine[0:1] 	#FIRST CHARACTERS OF THE LINE
			TwoChar = CurrentLine[0:2] 	#FIRST TWO CHARACTERS OF THE LINE
			ThreeChar = CurrentLine[0:3] 	#FIRST THREE CHARACTERS OF THE LINE
			
			#CHECK FOR ESCAPE
			if(TokenCharacters.get(OneChar) == TOKEN_TYPE_ESCAPE):
				#FLIP ESCAPE FLAG
				if InEscape:
					InEscape = 0
				else:
					InEscape = 1
				CurrentLine = CurrentLine[1:]
				CurrentToken = None
			#CHECK IF FIRST THREE CHARACTERS MATCH A RESERVED CHARACTER SET
			elif(not(InEscape) and ThreeChar in TokenCharacters and len(CurrentLine)>2):
				#CHECK FOR COMMENT - EXIT LOOP EFFECTIVELY ADDING NOTHING ELSE TO TOKEN LIST
				if TokenCharacters[ThreeChar] == TOKEN_TYPE_COMMENT:
					break;	
				#CONTINUE TAG - IGNORED (DEPRECATED SYNTAX)
				elif TokenCharacters[ThreeChar] == TOKEN_TYPE_CONTINUE:
					CurrentLine = CurrentLine[3:]
				#OTHER THREE CHARACTER RESERVED WORDS
				else:
					Self.Tokens.append(Token(TokenCharacters[ThreeChar],ThreeChar,LineNumber))
					CurrentLine = CurrentLine[3:]
				CurrentToken = None
			#CHECK IF FIRST TWO CHARACTERS MATCH A RESERVED CHARACTER SET
			elif (not(InEscape) and TwoChar in TokenCharacters and len(CurrentLine)>1):
				Self.Tokens.append(Token(TokenCharacters[TwoChar],TwoChar,LineNumber))
				CurrentLine = CurrentLine[2:]
				CurrentToken = None
			#CHECK IF FIRST CHARACTER MATCH A RESERVED CHARACTER SET
			elif (not(InEscape) and OneChar in TokenCharacters):
				Self.Tokens.append(Token(TokenCharacters[OneChar],OneChar,LineNumber))
				CurrentLine = CurrentLine[1:]
				CurrentToken = None
			#ANYTHING ELSE				
			else:
				#BUILD NEW STRING TOKEN
				if CurrentToken is None:
					#CHECK THAT FIRST CHARACTER IS NON-BLANK
					if not(OneChar.isspace()):
						CurrentToken = Token(TOKEN_TYPE_STRING,OneChar,LineNumber)
						Self.Tokens.append(CurrentToken)
				#OTHERWISE ADD CHARACTER TO CURRENT STRING
				else:
					CurrentToken.Value = CurrentToken.Value + CurrentLine[0:1]
				CurrentLine = CurrentLine[1:]	
				
	#CLEAN TOKENS
	#FUNCTION: Removes leading and trailing spaces from token values if string and space as value removes
	#PARAMATERS: Nothing
	#RETURNS: Nothing			
	def CleanTokens(Self):
		for Index, Token in enumerate(Self.Tokens):			
			Self.Tokens[Index].Value = Self.Tokens[Index].Value.lstrip()
			Self.Tokens[Index].Value = Self.Tokens[Index].Value.rstrip()
			#CHECK IF EMPTY STRING
			if Self.Tokens[Index].Value.isspace():
				Self.Tokens.pop(Index)

	#CHECK PASS
	#FUNCTION: Checks the next token against provided ID, if the next token is not the provided ID raises and exception, otherwise removes the next token 
	#PARAMATERS: Token ID
	#RETURNS: Nothing
	def CheckPass (Self, ID):
		if Self.Tokens[0].Type == ID:
			Self.Tokens.pop(0)
		else:
			raise Exception(Self.FileName + '\nLINE: '+str(Self.Tokens[0].LineNum)+' : Unexpected Token ecountered: ' + Self.Tokens[0].Value + ' expected: '+str(ID));
			
	
	#NOT CHECK
	#FUNCTION: Checks the next token against provided ID, if the next token is the provided ID raises and exception
	#PARAMATERS: Token ID
	#RETURNS: Nothing
	def NotCheck (Self, ID):
		if Self.Tokens[0].Type == ID:
			raise Exception(Self.FileName + '\nLINE: '+str(Self.Tokens[0].LineNum)+' : Illegal Token ecountered: '+ str(Self.Tokens[0].Type));		
			
	#PARSE
	#FUNCTION: Breaks tokens into a data structure
	#PARAMATERS: Nothing
	#RETURNS: Nothing
	def Parse(Self):
		Self.Config = Self.ParseHash()
		
	#PARSE HASH
	#FUNCTION: Breaks tokens into a hash
	#PARAMATERS: Nothing
	#RETURNS: Nothing	
	def ParseHash(Self):
		NewHash = {}		
		#LOOP UNTIL NO TOKENS REMAIN OR END BRACKET ENCOUNTERED			
		while Self.Tokens and not (Self.Tokens[0].Type == TOKEN_TYPE_CLOSE_CR_BRACKET):
			#GET IDENTITY
			if(Self.Tokens[0].Type == TOKEN_TYPE_STRING):				
				#GET LEFT SIDE OF IDENTITY				
				NewKey = Self.Tokens[0].Value 
				Self.Tokens.pop(0)				
				if (Self.Tokens[0].Type == TOKEN_TYPE_COLON):
					#CHECK FOR COLON
					Self.CheckPass(TOKEN_TYPE_COLON)
					#CHECK IF HASH
					if (Self.Tokens[0].Type == TOKEN_TYPE_OPEN_CR_BRACKET):
						Self.Tokens.pop(0)
						NewHash[NewKey] = Self.ParseHash()
						Self.CheckPass( TOKEN_TYPE_CLOSE_CR_BRACKET)					
					#CHECK IF ARRAY
					elif (Self.Tokens[0].Type == TOKEN_TYPE_OPEN_SQ_BRACKET):
						Self.Tokens.pop(0)
						NewHash[NewKey] = Self.ParseArray()
						Self.CheckPass(TOKEN_TYPE_CLOSE_SQ_BRACKET)				
					elif (Self.Tokens[0].Type == TOKEN_TYPE_STRING):
						NewHash[NewKey] = Self.Tokens[0].Value
						Self.Tokens.pop(0)		
				elif(NewKey in Self.Commands):
					NewHash[NewKey] = 1		
				else:
					raise Exception(Self.FileName + '\nLINE: '+str(Self.Tokens[0].LineNum)+' : Malformed Hash defitions, miisng ":" found: ' + Self.Tokens[0].Value+" -  Current Key: "+NewKey);
			#ELSE ERROR
			elif(Self.Tokens[0].Type != TOKEN_TYPE_STRING):
				raise Exception(Self.FileName + '\nLINE: '+str(Self.Tokens[0].LineNum)+' : Unexpected Token ecountered: ' + Self.Tokens[0].Value + "");
			if(Self.Tokens and Self.Tokens[0].Type == TOKEN_TYPE_TILDE):
					Self.Tokens.pop(0)
		return NewHash
		
	#PARSE ARRAY
	#FUNCTION: Breaks tokens into a array
	#PARAMATERS: Nothing
	#RETURNS: Nothing	
	def ParseArray(Self):
		NewArray = []
		#LOOP UNTIL 
		while Self.Tokens and not (Self.Tokens[0].Type == TOKEN_TYPE_CLOSE_SQ_BRACKET):	
			#CHECK IF STRING
			if(Self.Tokens[0].Type == TOKEN_TYPE_STRING):
				NewArray.append(Self.Tokens[0].Value )
				Self.Tokens.pop(0)
				#CHECK FOR TILDE - REMOVE IF FOUND
				if (Self.Tokens[0].Type == TOKEN_TYPE_TILDE):
					Self.Tokens.pop(0)
				#IF NOT TILDE OR CLOSE BRACKET RAISE EXCEPTION
				elif(Self.Tokens[0].Type != TOKEN_TYPE_CLOSE_SQ_BRACKET):
					raise Exception(Self.FileName + '\nLINE: '+str(Self.Tokens[0].LineNum)+' : Unexpected Token ecountered: ' + Self.Tokens[0].Value + ' expected either ~ or ]');	
			#CHECK IF HASH
			elif (Self.Tokens[0].Type == TOKEN_TYPE_OPEN_CR_BRACKET):
				Self.Tokens.pop(0)
				NewArray.append(Self.ParseHash())
				Self.CheckPass( TOKEN_TYPE_CLOSE_CR_BRACKET)	
				#CHECK FOR TILDE - REMOVE IF FOUND
				if (Self.Tokens[0].Type == TOKEN_TYPE_TILDE):
					Self.Tokens.pop(0)		
			#CHECK IF ARRAY
			elif (Self.Tokens[0].Type == TOKEN_TYPE_OPEN_SQ_BRACKET):
				Self.Tokens.pop(0)
				NewArray.append(Self.ParseArray())
				Self.CheckPass(TOKEN_TYPE_CLOSE_SQ_BRACKET)	
				#CHECK FOR TILDE - REMOVE IF FOUND
				if (Self.Tokens[0].Type == TOKEN_TYPE_TILDE):
					Self.Tokens.pop(0)					
			#ELSE ERROR
			else:
				Self.PrintTokens()		
				raise Exception(Self.FileName + '\nLINE: '+str(Self.Tokens[0].LineNum)+' : Unexpected Token ecountered: ' + Self.Tokens[0].Value);	
		return NewArray

	#PRINT
	#FUNCTION: Prints out the entire data structure
	#PARAMATERS: Nothing
	#RETURNS: Nothing		
	def Print (Self):
		Self.PrintHash(Self.Config,"")
	
	#PRINT HASH
	#FUNCTION: Prints out the entire data structure
	#PARAMATERS: Hash to Print, Indent
	#RETURNS: Nothing		
	def PrintHash (Self, H, I):
		CurrentHash = H
		print (I + "{");
		Indent = I + "\t"
		for CurrentKey in CurrentHash:		
			if  isinstance(CurrentHash[CurrentKey],dict):
				print (Indent + str(CurrentKey)+" : ")
				Self.PrintHash(CurrentHash[CurrentKey], Indent)
			elif isinstance(CurrentHash[CurrentKey],list):
				print (Indent + str(CurrentKey)+" : ")
				Self.PrintArray(CurrentHash[CurrentKey], Indent)
			else:
				print (Indent + str(CurrentKey) + " : "+ str(CurrentHash[CurrentKey]))
		print (I + "}\n");

	#PRINT ARRAY
	#FUNCTION: Prints out the entire data structure
	#PARAMATERS: Nothing
	#RETURNS: Nothing		
	def PrintArray (Self, H, I):
		CurrentArray = H
		print (I + "[");
		Indent = I + "\t"
		for CurrentValue in CurrentArray:
			if isinstance(CurrentValue,dict):
				Self.PrintHash(CurrentValue, Indent)
			elif isinstance(CurrentValue,list):
				Self.PrintArray(CurrentValue, Indent)
			else:
				print (Indent + CurrentValue)
		print (I + "]\n");
	#PRINT TOKENS
	#FUNCTION: Prints out the list of tokens
	#PARAMATERS: Nothing
	#RETURNS: Nothing		
	def PrintTokens (Self):	
		print ("***************************************\n")
		for CurrentToken in Self.Tokens:
			print (CurrentToken.Value);
	