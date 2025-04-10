import re
import math
import numpy
import pprint
import random


#LANGUAGE DEFINITION

#EXPRESSIO_LIST
#	EXPRESSION EXPRESSIO_LIST
#	EXPRESSION

#EXPRESSION
#	IF(EXTENSION,EXPRESSION,EXPRESSION)
#	ID = EXTENSION
#	EXTENSION
	
#EXTENSION
#	CONDITION
#	CONDITION AND CONDITION
#	CONDITION OR CONDITION
#	NOT CONDITION

#CONDITION
#	EXPONENT
#	EXPONENT == LIST
#	EXPONENT == EXPONENT
#	EXPONENT != EXPONENT
#	EXPONENT < EXPONENT
#	EXPONENT > EXPONENT
#	EXPONENT <= EXPONENT	
#	EXPONENT >= EXPONENT	

#SUM
#	PRODUCT
#	PRODUCT + SUM
#	PRODUCT - SUM

#PRODUCT
#	EXPONENT
#	EXPONENT * PRODUCT
#	EXPONENT / PRODUCT

#EXPONENT
#	CONCAT
#	CONCAT ** EXPONENT

#CONCAT
#	BRAKET
#	BRAKET & CONCAT

#BRACKET
#	LAMBDA
#	(EXPRESSION)

#LAMBDA
# LOOKUP.FUNCTION
# LOOKUP

#LOOKUP
#THIS
#FUNCTION[EXPRESSION]
#FUNCTION

#FUNCTION
#ID(PARAMATER)
#VALUE

#VALUE
# NUMBER
# STRING
# CONSTANT
# ID


#PARAMATER
# EXTENSION, EXTENSION
# EXTENSION

#CONSTANT
#TRUE
#FALSE

TokenIndex = {
'TOKEN_STRING' 				: 101,
'TOKEN_NUMBER' 				: 102,
'TOKEN_ID' 					: 103,
'TOKEN_THIS'				: 104,  #THIS

'TOKEN_COMMAND_START' 		: 200,
'TOKEN_IF'					: 201, #IF
'TOKEN_ASSIGNMENT'			: 202, #ASSIGN

'TOKEN_EXTENSION_START' 	: 300,
'TOKEN_NOT'					: 301, #NOT
'TOKEN_AND'					: 302, #AMD
'TOKEN_OR'					: 303, #OR

'TOKEN_CONDITION_START'		: 400, 
'TOKEN_EQUAL'				: 401, #==
'TOKEN_NOT_EQUAL'			: 402, #!=
'TOKEN_LESS'				: 403, #<
'TOKEN_GREATER'				: 404, #>
'TOKEN_LESS_EQUAL'			: 405, #<=
'TOKEN_GREATER_EQUAL'		: 406, #>=

'TOKEN_MATH_START'    		: 500, 
'TOKEN_PLUS'    		 	: 501, #+
'TOKEN_MINUS'    		 	: 502, #-
'TOKEN_MULTIPLY' 		 	: 503, #*
'TOKEN_DIVIDE'  		 	: 504, #/
'TOKEN_EXPONENT' 		 	: 505, #**

'TOKEN_STRING_COMMAND'		: 600,
'TOKEN_CONCAT'				: 601, #&

'TOKEN_MISC_OPERATOR_START'	: 700,
'TOKEN_OPEN_BRACKET'		: 701, #(
'TOKEN_CLOSE_BRACKET'		: 702, #)
'TOKEN_OPEN_SQ_BRACKET'		: 703, #[
'TOKEN_CLOSE_SQ_BRACKET'    : 704, #]
'TOKEN_COMMA'				: 705, #,
'TOKEN_PERIOD'              : 706, #.

'TOKEN_FUNCTION_START'		: 800,
'TOKEN_ISNUM'				: 801, #ISNUM
'TOKEN_ISFULL'				: 802, #ISFULL
'TOKEN_ISEMPTY'				: 803, #ISEMPTY
'TOKEN_INC'					: 804, #INC
'TOKEN_TONUMBER'			: 805, #TONUMBER
'TOKEN_INT'					: 806, #INC
'TOKEN_DEC'					: 807, #DEC
'TOKEN_ODATE'				: 808, #ODATE  - NOT USED
'TOKEN_TOUPPER'				: 809, #TOUPPER
'TOKEN_TOUPPER_LEAD'		: 810, #TOLOWER
'TOKEN_TOLOWER'				: 811, #TOLOWER
'TOKEN_EDATE'				: 812, #EDATE
'TOKEN_HDATE'				: 813, #HDATE
'TOKEN_CHAR'				: 814, #CHAR
'TOKEN_EXISTS'				: 815, #EXISTS
'TOKEN_VALUEAT'			   	: 816, #VALUEAT
'TOKEN_TWO_PARAM_FUNC'		: 817,
'TOKEN_TODATE'				: 818, #TODATE
'TOKEN_SEARCH'				: 819, #SEARCH
'TOKEN_MATCH'				: 820, #MATCH
'TOKEN_JOIN'				: 821, #JOIN
'TOKEN_RAND'				: 822, #RAND
'TOKEN_QUESTIONCHOICE'      : 823, #QUESTIONCHOIHCE
'TOKEN_THREE_PARAM_FUNC'	: 824,
'TOKEN_SUBSTR'				: 825, #SUBSTR
'TOKEN_SPLIT'				: 826, #SPLIT
'TOKEN_REPLACE'				: 827, #REPLACE

'TOKEN_CONSTANT_START'		: 900,
'TOKEN_TRUE'				: 901, #TRUE
'TOKEN_FALSE'				: 902, #FALSE
'TOKEN_DATE'				: 903  #DATE
}

NodeIndex = {
'NODE_EXPRESSION_LIST'				: 9000,

'NODE_EXPRESSION'					: 10000,
'NODE_IF'							: 10201,
'NODE_IF_RESULT'					: 10211,
'NODE_ASSIGN'						: 10202,
		
'NODE_EXTENSION'					: 20000,
'NODE_NOT'							: 20301,
'NODE_AND'							: 20302,
'NODE_OR'							: 20303,
		
'NODE_COMPARISON'					: 30000,
'NODE_EQUAL'						: 30401,
'NODE_NOT_EQUAL'					: 30402,
'NODE_LESS'			    			: 30403,
'NODE_GREATER'						: 30404,
'NODE_LESS_EQUAL'					: 30405,
'NODE_GREATER_EQUAL'       			: 30406,
		
'NODE_LIST'							: 40000,
'NODE_RANGE'						: 40001,
		
'NODE_SUM'							: 50000,
'NODE_ADD'							: 50501,
'NODE_SUB'							: 50502,
		
'NODE_PRODUCT'						: 60000,
'NODE_MULT'							: 60503,
'NODE_DIVIDE'						: 60504,
		
'NODE_EXPONENT'						: 70000,
		
'NODE_STRING_OP'					: 80000,
'NODE_CONCAT'						: 80601,
		
'NODE_BRACKET'						: 90000,
	
'NODE_LAMBDA'                       : 91000,

'NODE_LOOKUP'                       : 92000,

'NODE_PARAMATER'                    : 93000,
	
'NODE_VALUE'						: 100000,
'NODE_STRING'						: 100101,
'NODE_NUMBER'						: 100102,
'NODE_ID'							: 100103,
'NODE_THIS'						    : 100104,
		
'NODE_CONSTANT'						: 110000,
'NODE_TRUE'							: 110901,
'NODE_FALSE'						: 110902,
'NODE_DATE'							: 110903,
	
'NODE_FUNCTION'				    	: 120000,
'NODE_FUNC_RAND'                    : 120801, #PROBABLY NOT USING MOST OF THESE.
'NODE_FUNC_ISNUM'				    : 120802,
'NODE_FUNC_ISFULL'				    : 120803,
'NODE_FUNC_ISEMPTY'			    	: 120804, #INC
'NODE_FUNC_INC'				   		: 120805,
'NODE_FUNC_TONUMBER'			    : 120806,
'NODE_FUNC_INT'				    	: 120807, #DEC
'NODE_FUNC_DEC'				    	: 120808,
'NODE_FUNC_ODATE'				    : 120809,
'NODE_FUNC_TOUPPER'			   	 	: 120810,
'NODE_FUNC_TOUPPER_LEAD'			: 120811,
'NODE_FUNC_TOLOWER'			    	: 120812, #EDATE
'NODE_FUNC_EDATE'				    : 120813, #HDATE
'NODE_FUNC_HDATE'				    : 120814, #CHAR
'NODE_FUNC_CHAR'				    : 120815, #EXISTS
'NODE_FUNC_EXISTS'				    : 120816,
'NODE_FUNC_VALUEAT'			    	: 120840,
'NODE_TWO_PARAM_FUNC'			    : 120841, 
'NODE_FUNC_TODATE'				    : 120842, 
'NODE_FUNC_SEARCH'				    : 120843, 
'NODE_FUNC_MATCH'				    : 120844, 
'NODE_FUNC_JOIN'				    : 120845, #RAND
'NODE_FUNC_RAND'				    : 120860,
'NODE_THREE_PARAM_FUNC'				: 120861, 
'NODE_FUNC_SUBSTR'				    : 120862, 
'NODE_FUNC_SPLIT'				    : 120863,
'NODE_FUNC_REPLACE'					: 120864,				
}

NodeLabelLookup={ 
9000:'NODE_EXPRESSION_LIST',

10000:'NODE_EXPRESSION',				
10201:'NODE_IF',
10211:'NODE_IF_RESULT',
10202:'NODE_ASSIGN',			
		
20000:'NODE_EXTENSION',
20301:'NODE_NOT',					
20302:'NODE_AND',					
20303:'NODE_OR',						
		
30000:'NODE_COMPARISON',
30401:'NODE_EQUAL',					
30402:'NODE_NOT_EQUAL',				
30403:'NODE_LESS',			    	
30404:'NODE_GREATER',				
30405:'NODE_LESS_EQUAL',			
30406:'NODE_GREATER_EQUAL',       	
		
40000:'NODE_LIST',					
40001:'NODE_RANGE',					
		
50000:'NODE_SUM',					
50501:'NODE_ADD',					
50502:'NODE_SUB',					
		
60000:'NODE_PRODUCT',
60503:'NODE_MULT',					
60504:'NODE_DIVIDE',					
		
70000:'NODE_EXPONENT',
		
80000:'NODE_STRING_OP',				
80601:'NODE_CONCAT',
		
90000:'NODE_BRACKET',				
	
91000:'NODE_LAMBDA',                

92000:'NODE_LOOKUP',                 

93000:'NODE_PARAMATER',
	
100000:'NODE_VALUE',
100101:'NODE_STRING',					
100102:'NODE_NUMBER',					
100103:'NODE_ID',						
100104:'NODE_THIS',						
		
110000:'NODE_CONSTANT',
110901:'NODE_TRUE',
110902:'NODE_FALSE',						
110903:'NODE_DATE',						
	
120000:'NODE_FUNCTION',
120801:'NODE_FUNC_ISNUM',				
120802:'NODE_FUNC_ISFULL',				
120803:'NODE_FUNC_ISEMPTY',			    
120804:'NODE_FUNC_INC',
120805:'NODE_FUNC_TONUMBER',			    
120806:'NODE_FUNC_INT',				    
120807:'NODE_FUNC_DEC',				    
120808:'NODE_FUNC_ODATE',				
120809:'NODE_FUNC_TOUPPER',			   	
120810:'NODE_TOUPPER_LEAD',
120811:'NODE_FUNC_TOLOWER',		    
120812:'NODE_FUNC_EDATE',
120813:'NODE_FUNC_HDATE',				
120814:'NODE_FUNC_CHAR',				    
120815:'NODE_FUNC_EXISTS',
120816:'NODE_FUNC_VALUEAT',			    
120840:'NODE_TWO_PARAM_FUNC',
120841:'NODE_FUNC_TODATE',
120842:'NODE_FUNC_SEARCH',				
120843:'NODE_FUNC_MATCH',				
120844:'NODE_FUNC_JOIN',				    
120845:'NODE_FUNC_RAND',				    
120860:'NODE_THREE_PARAM_FUNC',			
120861:'NODE_FUNC_SUBSTR',				
120862:'NODE_FUNC_SPLIT',				
120863:'NODE_FUNC_REPLACE',				
120864:'NODE_FUNC_LOG',				
}

TokenCharacters = {
'**':'TOKEN_EXPONENT',
'=':'TOKEN_ASSIGNMENT',
'==':'TOKEN_EQUAL',
'!=':'TOKEN_NOT_EQUAL',
'<':'TOKEN_LESS',
'>':'TOKEN_GREATER',			
'<=':'TOKEN_LESS_EQUAL',		
'>=':'TOKEN_GREATER_EQUAL',
'&':'TOKEN_CONCAT',
'+':'TOKEN_PLUS',
'-':'TOKEN_MINUS',
'*':'TOKEN_MULTIPLY',
'/':'TOKEN_DIVIDE',
'(':'TOKEN_OPEN_BRACKET',
')':'TOKEN_CLOSE_BRACKET',
'[':'TOKEN_OPEN_SQ_BRACKET',
']':'TOKEN_CLOSE_SQ_BRACKET',
'.':'TOKEN_PERIOD',
',':'TOKEN_COMMA',
}

TokenKeywords = {
'not':'TOKEN_NOT',	
'and':'TOKEN_AND',
'or':'TOKEN_OR',	
'if':'TOKEN_IF',
'this':'TOKEN_THIS'
}

################################# LEX ################################# 
############# CHECK PASS #############
#FUNCTION:   Checks the token list against the provided value removing it if true
#PARAMATERS: TokenList,Value,OptionalFlag
#RETURNS:	Boolean
def CheckPass(Tokens, CheckValue, Optional):
	if(len(Tokens)>0):
		if(Tokens[0]['TOKEN_TYPE'] == CheckValue):
			del Tokens[0]
			return(1)
	if(not Optional):
		raise Exception ("Error: Unexpected Token Ecountered expected:"+ str(CheckValue)+" found: "+ str(Tokens[0]['TOKEN_TYPE']))
		return(0)
	return(1)


################################# LEX #################################
#Function:  LEXER - BREAKS PROVIDED STRING INTO TOKENS
#Input:  Text String
#Output: Token List	 
def Lex(EntryText):
	Text = EntryText
	Tokens=[]
	Text = str(Text)
	#CLEAN UP INPUT STRING 
	Text = re.sub(r'\n',' ',Text)		#REMOVE NEW LINES
	Text = re.sub(r'\s+$','',Text)		#REMOVE TRAILING SPACES
	Text = re.sub(r'^\s+','',Text)		#REMOVE LEADING SPACES
	Text = re.sub(r'\&amp\;','&',Text)   #REPLEACE &amp; WITH &	

	while(re.match(r'\s*\S',Text)):
		NewToken = {}  #NEW TOKEN CREATED IN THIS PASS		
		#REMOVE ANY LEADING SPACE
		Text = re.sub(r'^\s+','',Text)		#REMOVE LEADING SPACES	
		#CHECK FOR NUMBER
		if(re.match(r'^(\-?[0-9]+(\.[0-9]+)?)',Text)):
			#NEGATIVE SIGN
			if(re.match(r'^\-',Text) and len(Tokens)>0 and (Tokens[-1]['TOKEN_TYPE'] < TokenIndex['TOKEN_COMMAND_START'] or Tokens[-1]['TOKEN_TYPE'] == TokenIndex['TOKEN_CLOSE_BRACKET'] or Tokens[-1]['TOKEN_TYPE'] > TokenIndex['TOKEN_CONSTANT_START'])):
				NewToken['TOKEN_TYPE'] = TokenIndex['TOKEN_MINUS']
				Text = Text[1:]				
			#NUMBER
			else :				
				NewToken['TOKEN_TYPE'] = TokenIndex['TOKEN_NUMBER']	
				NewToken['TOKEN_VALUE'] = re.search(r'^(\-?[0-9]+(\.[0-9]+)?)',Text).group(1)
				Text = re.sub(r'^(\-?[0-9]+(\.[0-9]+)?)','',Text)
		#CHECK FOR STRING
		elif(re.match(r'^\"([^"]*)\"', Text)):
			NewToken['TOKEN_TYPE'] = TokenIndex['TOKEN_STRING']	
			NewToken['TOKEN_VALUE'] = re.search(r'^\"([^"]*)\"',Text).group(1)
			NewToken['TOKEN_VALUE'] = NewToken['TOKEN_VALUE'].replace('"', '')
			Text = re.sub(r'^\"([^"]*)\"','',Text)
		#CHECK FOR OPERATOR - FIRST TWO CHARACTERS
		elif (len(Text)>1 and Text[:2] in TokenCharacters):
			NewToken['TOKEN_TYPE'] = TokenIndex[TokenCharacters[Text[:2]]]
			Text = Text[2:]	
		#CHECK FOR OPERATOR - FIRST CHARACTER
		elif (len(Text)>0 and Text[:1] in TokenCharacters):
			NewToken['TOKEN_TYPE'] = TokenIndex[TokenCharacters[Text[:1]]]
			Text = Text[1:]		
		#GET STRING
		elif(re.match(r'^([a-zA-Z0-9_]+)',Text)):
			IDText = re.search(r'^([a-zA-Z0-9_]+)',Text).group(1) #TEXT FOR NEXT TOKEN
			#CHECK FOR KEYWORD
			if(IDText.lower() in TokenKeywords):
				NewToken['TOKEN_TYPE'] = TokenIndex[TokenKeywords[IDText.lower()]]
			#SET AS ID
			else:
				NewToken['TOKEN_TYPE'] = TokenIndex['TOKEN_ID']
				NewToken['TOKEN_VALUE'] = IDText
			Text = re.sub(r'^([a-zA-Z0-9_]+)','',Text)	
		#ERROR UNRECOGNIZED TOKEN
		else:
			raise Exception (EntryText+"\nError: Unrecognized Token "+ Text[1:] +" detected, skipping and continueing\n")
			Text = Text[1:]	
		#ADD TOKEN TO LIST
		Tokens.append(NewToken)

	return(Tokens)
	

############# PARSE EXPRESSION LIST #############
#FUNCTION: Parse Extension
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseExpressionList(Tokens):
	LeftChild=''		   #LEFT CHILD OF NEW NODEa
	NewNode = {}		   #NODE GENERATED HERE
	#PARSE LEFT CHILD 
	LeftChild = ParseExpression(Tokens)
	#CHECK FOR ADDITIONAL STATEMENT
	if(len(Tokens)>0):
		RightChild = ParseExpressionList(Tokens)
		return(Node(NodeIndex['NODE_EXPRESSION_LIST'], "", LeftChild, RightChild))
	#RETURN LEFT CHILD IF NOT LIST
	return(LeftChild)

############# PARSE EXPRESSION #############
#FUNCTION: Parse Extension
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseExpression(Tokens):
	#PROCESS IF
	if(len(Tokens)>0):
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_IF']):		
			NodeType = int(NodeIndex['NODE_EXPRESSION']) + int(Tokens[0]['TOKEN_TYPE'])
			del Tokens[0]
			CheckPass(Tokens, TokenIndex['TOKEN_OPEN_BRACKET'],0)
			#GET CONDITION 
			LeftChild=ParseExtension(Tokens)				
			CheckPass(Tokens, TokenIndex['TOKEN_COMMA'],0)
			#GET TRUE RESULT
			ResultLeftChild=ParseExpression(Tokens)		
			#CHECK FOR ELSE RESULT
			ResultRightChild=''
			if (Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_COMMA']):
				del Tokens[0]
				ResultRightChild =ParseExpression(Tokens)		
			CheckPass(Tokens, TokenIndex['TOKEN_CLOSE_BRACKET'],0)
			ResultNode = Node(NodeIndex['NODE_IF_RESULT'],"",ResultLeftChild,ResultRightChild)				
			return (Node(NodeIndex['NODE_IF'],"",LeftChild,ResultNode))	
	#CHECK FOR ASSIGNMENT
	LeftChild = ParseExtension(Tokens)	
	if(len(Tokens)>0):		
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_ASSIGNMENT']):
			if (LeftChild.Type != NodeIndex['NODE_ID']):
				raise Exception ("ERROR - Found assigment with a non-identifier as left paramater.\n")
			del Tokens[0]
			RightChild = ParseExtension(Tokens)
			return(Node(NodeIndex['NODE_ASSIGN'],"",LeftChild, RightChild))
	#PARSE EXTENSION IF NOT EXPRESSION
	return (LeftChild)

############# PARSE EXTENSION #############
#FUNCTION: Parse Extension
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseExtension(Tokens):
	#CHECK FOR NOT
	if(len(Tokens)>0):
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_NOT']):
			del Tokens[0]
			#PROCESS CHILD
			LeftChild=ParseCondition(Tokens)
			LeftChild=Node(NodeIndex['NODE_NOT'],'',LeftChild,'')	
		else:
			LeftChild = ParseCondition(Tokens)
		#CHECK FOR AND OR OR
		if(len(Tokens)>0):	
			if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_AND'] or Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_OR']):
				NodeType= int(NodeIndex['NODE_EXTENSION']) + int(Tokens[0]['TOKEN_TYPE'])
				del Tokens[0]
				#SET CHILDREN
				RightChild = ParseExtension(Tokens)
				return (Node(NodeType,'',LeftChild,RightChild))
	#RETURN LEFT CHILD IF NOT CONDITION
	return(LeftChild)

############# PARSE CONDITION #############
#FUNCTION: Parse Condition
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseCondition(Tokens):
	#PARSE LEFT CHILD 
	LeftChild = ParseSum(Tokens)
	#CHECK FOR CONDITION OPERATOR
	if(len(Tokens)>0):
		if(Tokens[0]['TOKEN_TYPE']>=TokenIndex['TOKEN_CONDITION_START'] and Tokens[0]['TOKEN_TYPE']<TokenIndex['TOKEN_MATH_START']):	
			NodeType=int(NodeIndex['NODE_COMPARISON']) + int(Tokens[0]['TOKEN_TYPE'])
			del Tokens[0]
			#SET CHILDREN
			RightChild = ParseSum(Tokens)
			return (Node(NodeType,'',LeftChild,RightChild))

	#RETURN LEFT CHILD IF NOT CONDITION
	return(LeftChild)

############# PARSE SUM #############
#FUNCTION: Parse Condition
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseSum(Tokens):
	#PARSE LEFT CHILD 
	LeftChild = ParseProduct(Tokens)
	#CHECK FOR + OR -
	if(len(Tokens)>0):
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_PLUS'] or Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_MINUS']):
			NodeType=int(NodeIndex['NODE_SUM']) + int(Tokens[0]['TOKEN_TYPE'])
			del Tokens[0]
			#SET CHILDREN
			RightChild = ParseSum(Tokens)		
			return (Node(NodeType,'',LeftChild,RightChild))
	#RETURN LEFT CHILD IF NOT SUM
	return(LeftChild)
	
############# PARSE PRODUCT #############
#FUNCTION: Parse Product
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree	
def ParseProduct(Tokens):
	#PARSE LEFT CHILD 
	LeftChild = ParseExponent(Tokens)
	#CHECK FOR * OR /	
	if(len(Tokens)>0 ):
		if (Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_MULTIPLY'] or Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_DIVIDE']):
			NodeType=int(NodeIndex['NODE_PRODUCT']) + int(Tokens[0]['TOKEN_TYPE'])
			del Tokens[0]
			#SET CHILDRENS
			RightChild = ParseProduct(Tokens)
			return (Node(NodeType,'',LeftChild,RightChild))
	#RETURN LEFT CHILD IF NOT PRODUCT
	return(LeftChild)	

############# PARSE EXPONENT #############
#FUNCTION: Parse Exponent
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseExponent(Tokens):
	#PARSE LEFT CHILD 
	LeftChild = ParseConcat(Tokens)
	#CHECK FOR **
	if(len(Tokens)>0):
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_EXPONENT']):
			NodeType=NodeIndex['NODE_EXPONENT']	
			del Tokens[0]
			#SET CHILDREN
			RightChild = ParseExponent(Tokens)
			return (Node(NodeType,'',LeftChild,RightChild))
	#RETURN LEFT CHILD IF NOT EXPONEANT
	return(LeftChild)

############# PARSE CONCAT #############
#FUNCTION: Parse Concatenate
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseConcat(Tokens):
	#PARSE LEFT CHILD 
	LeftChild = ParseBracket(Tokens)
	#CHECK FOR &
	if(len(Tokens)>0):
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_CONCAT']):
			NodeType=int(NodeIndex['NODE_CONCAT'])
			del Tokens[0]
			#SET CHILDREN			
			RightChild = ParseConcat(Tokens)
			return (Node(NodeType,'',LeftChild,RightChild))
	#RETURN LEFT CHILD IF NOT EXPONEANT
	return(LeftChild)
	
############# PARSE BRAKET #############
#FUNCTION: Parse Bracket
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseBracket(Tokens):
	#CHECK FOR (
	if(len(Tokens)>0):
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_OPEN_BRACKET']):
			del Tokens[0]				
			#GET COMMAND WITHIN BRAKET
			NewNode = ParseExpression(Tokens)
			CheckPass(Tokens, TokenIndex['TOKEN_CLOSE_BRACKET'],0)
			return NewNode;
	#RETURN LEFT CHILD IF NOT EXPONEANT
	return(ParseLambda(Tokens))

############# PARSE LAMBDA #############
#FUNCTION: Parse Lambda
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseLambda(Tokens):
	LeftChild = ''		   #LEFT CHILD OF NEW NODE
	NewNode = {}	   #NODE GENERATED HERE
	#PARSE LEFT CHILD 
	LeftChild = ParseLookup(Tokens)
	#CHECK FOR * OR /	
	if(len(Tokens)>0):
		if (Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_PERIOD']):
			del Tokens[0]
			#SET CHILDRENS		
			RightChild = ParseFunction(Tokens)
			return (Node(NodeIndex['NODE_LAMBDA'],'',LeftChild,RightChild))
	#RETURN LEFT CHILD IF NOT PRODUCT
	return(LeftChild)

	
############# PARSE LOOKUP #############
#FUNCTION: Parse LOOKUP
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseLookup(Tokens):
	#PARSE LEFT CHILD 
	LeftChild = ParseFunction(Tokens)
	#CHECK FOR * OR /	
	if(len(Tokens)>0 ):
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_OPEN_SQ_BRACKET']):
			del Tokens[0]		
			#GET COMMAND WITHIN BRAKET		
			RightChild = ParseExpression(Tokens)
			CheckPass(Tokens, TokenIndex['TOKEN_CLOSE_SQ_BRACKET'],0)
			return (Node(NodeIndex['NODE_LOOKUP'],'',LeftChild,RightChild))
		#RETURN LEFT CHILD IF NOT PRODUCT
	return(LeftChild)
	
############# PARSE FUNCTION #############
#FUNCTION: Parse LOOKUP
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseFunction(Tokens):
	#PARSE LEFT CHILD 
	LeftChild = ParseValue(Tokens)
	#CHECK FOR * OR /	
	if(len(Tokens)>0 ):
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_OPEN_BRACKET']):
			del Tokens[0]		
			#GET COMMAND WITHIN BRAKET	
			RightChild=''
			if(Tokens[0]['TOKEN_TYPE']!=TokenIndex['TOKEN_CLOSE_BRACKET']):
				RightChild = ParseParamater(Tokens)		
			CheckPass(Tokens, TokenIndex['TOKEN_CLOSE_BRACKET'],0)			
			LeftChild.Type = NodeIndex['NODE_FUNCTION']
			LeftChild.LeftChild = RightChild
			return (LeftChild)
		#RETURN LEFT CHILD IF NOT PRODUCT
	return(LeftChild)
	
	
############# PARSE Paramater #############
#FUNCTION: Parse Value
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseParamater(Tokens):
	#PARSE LEFT CHILD 
	LeftChild = ParseExpression(Tokens)
	#CHECK FOR * OR /	
	if(len(Tokens)>0 ):
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_COMMA']):
			del Tokens[0]		
			#GET COMMAND WITHIN BRAKET	
			RightChild = ParseParamater(Tokens)
			return (Node(NodeIndex['NODE_PARAMATER'],'',LeftChild,RightChild))
		#RETURN LEFT CHILD IF NOT PRODUCT
	return(LeftChild)

############# PARSE VALUE #############
#FUNCTION: Parse Value
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseValue(Tokens):
	#CHECK FOR ONE OF THE THREE TYPE OF VALUES
	if(len(Tokens)>0):	
		if(Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_STRING'] or Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_NUMBER'] or Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_ID'] or Tokens[0]['TOKEN_TYPE']==TokenIndex['TOKEN_THIS']):	
			NodeType = int(NodeIndex['NODE_VALUE']) + int(Tokens[0]['TOKEN_TYPE'])
			if(Tokens[0]['TOKEN_TYPE']!=TokenIndex['TOKEN_THIS']):
				NodeValue = Tokens[0]['TOKEN_VALUE']
			else:
				NodeValue="THIS"
			del Tokens[0]				
			return (Node(NodeType,NodeValue,'',''))
		return(ParseConstant(Tokens))	
	raise Exception("Error, expected token, none found.\n")

############# PARSE CONSTANT #############
#FUNCTION: Parse Constant
#PARAMATERS: TokenList
#RETURNS:	 Binary Execution Tree
def ParseConstant(Tokens):
	if(len(Tokens)>0):	
		if(int(Tokens[0]['TOKEN_TYPE']) > TokenIndex['TOKEN_CONSTANT_START']):
			NodeType=NodeIndex['NODE_CONSTANT'] + Tokens[0]['TOKEN_TYPE'];				
			del Tokens[0]			
			return (Node(NodeType,'','',''))
	#CONSTANTS ARE PARSED DIRECTLY TO THEIR ASSOCIATED VALUE AND STORED AS APPROPRIATE
	raise Exception ("Error, expected token, none found.\n "+str(Tokens[0]['TOKEN_TYPE']))
	

class Node:
	################################# NODE - INITIALIZATION #################################
	#Function:  Creates a new Nation
	#Input:  TYPE, VALUE, LEFTCHILD, RIGHT CHILD
	#Output: object	
	def __init__(Self, Type, Value, LeftChild, RightChild):				
		Self.Type       = Type
		Self.Value      = Value
		Self.LeftChild  = LeftChild
		Self.RightChild = RightChild

	################################# NODE - PRINT #################################
	#Function:  Prints current nods Ids -= values and repeates for children
	#Input:  Tab Offset
	#Output: Nothing
	def Print(Self, Tabs=0):
		for i in range(0,Tabs):
			print("\t", end = '')
		print (str(Self.Type) + " - " + str(Self.Value))
		if(Self.LeftChild != ''):
			Self.LeftChild.Print(Tabs+1)
		if(Self.RightChild != ''):
			Self.RightChild.Print(Tabs+1)	

	################################# NODE - EXECUTE #################################
	#Function:  Executes the node function based on type
	#Input:  TYPE, LOOKUP  
	#Output: VARIES
	def Execute (Self, Lookup):
		#EXPRESSION LIST
		if(Self.Type == NodeIndex['NODE_EXPRESSION_LIST']):
			ReturnLeft = Self.LeftChild.Execute(Lookup)			
			ReturnRight = Self.RightChild.Execute(Lookup)
			return([ReturnLeft,ReturnRight])
		#IF
		elif(Self.Type == NodeIndex['NODE_IF']):
			if(Self.LeftChild.Execute(Lookup)):
				return (Self.RightChild.LeftChild.Execute(Lookup))
			else:
				if(Self.RightChild.RightChild != ''):
					return (Self.RightChild.RightChild.Execute(Lookup))
		#ASSIGNMENT
		if(Self.Type == NodeIndex['NODE_ASSIGN']):
			#GET TARGET			
			temp=1
	
		#EXTENSION
		#NOT
		elif(Self.Type == NodeIndex['NODE_NOT']):			
			return(not(Self.LeftChild.Execute(Lookup)))	
		#AND
		elif(Self.Type == NodeIndex['NODE_AND']):			
			return(Self.LeftChild.Execute(Lookup) and Self.RightChild.Execute(Lookup))				
		#OPR
		elif(Self.Type == NodeIndex['NODE_OR']):
			#TODO - ADD CHECK FOR VARIABLE TYPE
			return(Self.LeftChild.Execute(Lookup) or Self.RightChild.Execute(Lookup))				
			
		#COMPARISONS
		#EQUAL
		elif(Self.Type == NodeIndex['NODE_EQUAL']):
			#TODO - ADD CHECK FOR VARIABLE TYPE
			LeftResult = Self.LeftChild.Execute(Lookup)
			RightResult = Self.RightChild.Execute(Lookup)	
			if((not(isinstance(LeftResult, str)) or re.search(r"^(\-?[0-9]+\.?[0-9]*)$",str(LeftResult))) and (not(RightResult, str) or re.search(r"^(\-?[0-9]+\.?[0-9]*)$",str(RightResult)))):				
				return(float(LeftResult) == float(RightResult))			
			else:
				return(LeftResult == RightResult)		
			
		#NOT EQUAL
		elif(Self.Type == NodeIndex['NODE_NOT_EQUAL']):
			#TODO - ADD CHECK FOR VARIABLE TYPE		
			LeftResult = Self.LeftChild.Execute(Lookup)
			RightResult = Self.RightChild.Execute(Lookup)	
			if((not(isinstance(LeftResult, str)) or re.search(r"^(\-?[0-9]+\.?[0-9]*)$",str(LeftResult))) and (not(RightResult, str) or re.search(r"^(\-?[0-9]+\.?[0-9]*)$",str(RightResult)))):				
				return(float(LeftResult) != float(RightResult))			
			else:
				return(str(LeftResult) != str(RightResult))			
		#LESS
		elif(Self.Type == NodeIndex['NODE_LESS']):			
			return(float(Self.LeftChild.Execute(Lookup)) < float(Self.RightChild.Execute(Lookup)))			
		#GREATER
		elif(Self.Type == NodeIndex['NODE_GREATER']):
			return(float(Self.LeftChild.Execute(Lookup)) > float(Self.RightChild.Execute(Lookup)))		
		#LESS EQUAL
		elif(Self.Type == NodeIndex['NODE_LESS_EQUAL']):
			return(float(Self.LeftChild.Execute(Lookup)) <= float(Self.RightChild.Execute(Lookup)))					
		#GREATER EQUAL
		elif(Self.Type == NodeIndex['NODE_GREATER_EQUAL']):
			return(float(Self.LeftChild.Execute(Lookup)) >= float(Self.RightChild.Execute(Lookup)))				
		
		#MATH
		#ADDTION
		elif(Self.Type == NodeIndex['NODE_ADD']):
			return(float(Self.LeftChild.Execute(Lookup)) + float(Self.RightChild.Execute(Lookup)))		
		#SUBTRACTION
		elif(Self.Type == NodeIndex['NODE_SUB']):
			return(float(Self.LeftChild.Execute(Lookup)) - float(Self.RightChild.Execute(Lookup)))		
		#MULTIPLICATION
		elif(Self.Type == NodeIndex['NODE_MULT']):
			return(float(Self.LeftChild.Execute(Lookup)) * float(Self.RightChild.Execute(Lookup)))		
		#DIVISION
		elif(Self.Type == NodeIndex['NODE_DIVIDE']):
			return(float(Self.LeftChild.Execute(Lookup)) / float(Self.RightChild.Execute(Lookup)))
		#EXPONENT
		elif(Self.Type == NodeIndex['NODE_EXPONENT']):
			return(float(Self.LeftChild.Execute(Lookup)) ** float(Self.RightChild.Execute(Lookup)))
		#CONCAT
		elif(Self.Type == NodeIndex['NODE_CONCAT']):
			return(str(Self.LeftChild.Execute(Lookup)) + str(Self.RightChild.Execute(Lookup)))
			
		#LOOK UP
		elif(Self.Type == NodeIndex['NODE_LOOKUP']):				
			#CHECK IF ID PROVIDED TO LEFT SIDE - NOT SURE WHAT ALTS WILL NEED TO EXIST
			if(Self.LeftChild.Type == NodeIndex['NODE_ID']):
				return (Lookup.GetReference(Self.LeftChild.Value, Self.RightChild.Execute(Lookup)))
			else:
				raise Exception ("Error, unexpected node, found in Lookup Left Child.\n "+str(Self.LeftChild.Type))
	
		#LAMBDA
		elif(Self.Type == NodeIndex['NODE_LAMBDA']):
			#ID
			if (Self.RightChild.Type == NodeIndex['NODE_ID']):
				return (Self.LeftChild.GetEntity(Lookup).GetValue(Self.RighChild.Value))
			#FUNCTION CALL
			elif (Self.RightChild.Type == NodeIndex['NODE_FUNCTION']):
				SelectedEntity = Self.LeftChild.Execute(Lookup)
				Paramaters = []

				if(Self.RightChild.LeftChild != ''):	
					ParamaterReturns = Self.RightChild.LeftChild.Execute(Lookup)
					if(isinstance(ParamaterReturns, list)):
						Paramaters = Paramaters + ParamaterReturns
					else:
						Paramaters.append(ParamaterReturns)						
				return(SelectedEntity.Processor(Self.RightChild.Value,Paramaters))
			else:
				raise Exception ("Error, unexpected node, found in Lambda Right Child.\n "+str(Self.RightChild.Type))
		#FUNCTION
		elif(Self.Type >= NodeIndex['NODE_FUNCTION']):			
			Paramaters = []
			if(Self.LeftChild != ''):				
				ParamaterReturns = Self.LeftChild.Execute(Lookup)		
				if(isinstance(ParamaterReturns, list)):
					Paramaters = Paramaters + ParamaterReturns
				else:
					Paramaters.append(ParamaterReturns)	
				#ISNUM
				if(Self.Value.lower() == "isnum"):
					return(re.search(r"^(\-?[0-9]+\.?[0-9]*)$",str(Paramaters[0])))					
				#ABS
				elif(Self.Value.lower() == "abs"):
					return(abs(Paramaters[0]))				
				#LOG
				elif(Self.Value.lower() == "log"):
					return(math.log(Paramaters[0],10))	
				#SQRT
				elif(Self.Value.lower() == "sqrt"):					
					return(math.sqrt(Paramaters[0]))	
				#TO UPPER LEAD
				elif(Self.Value.lower() == "toupperlead"):
					#CHECK IF CORRECT NUMBER OF PARAMTERS
					if(len(Paramaters) == 1):						
						return(Paramaters[0].capitalize())
					raise Exception ("Error, Inccorect number of paramaters for toupperlead")		
				#INT 
				elif(Self.Value.lower() == "int"):
					#CHECK IF CORRECT NUMBER OF PARAMTERS
					if(len(Paramaters) == 1):						
						return(int(Paramaters[0]))
					raise Exception ("Error, Inccorect number of paramaters for int")
				#ROUND 
				elif(Self.Value.lower() == "round"):
					#CHECK IF CORRECT NUMBER OF PARAMTERS
					if(len(Paramaters) == 1):						
						return(round(Paramaters[0]))
					raise Exception ("Error, Inccorect number of paramaters for int")									
				#SPLIT FUNCTION
				elif(Self.Value.lower() == "split"):
					#CHECK IF CORRECT NUMBER OF PARAMTERS
					if(len(Paramaters) != 3):
						raise Exception ("Error, Inccorect number of paramaters for split")
					return(Paramaters[0].split(Paramaters[1])[Paramaters[2]])
				#SEARCH
				elif(Self.Value.lower() == "search"):
					#CHECK IF CORRECT NUMBER OF PARAMTERS
					if(len(Paramaters) != 2):
						raise Exception ("Error, Inccorect number of paramaters for search")
					return(re.search(Paramaters[1],Paramaters[0]))				
				#RAND
				elif(Self.Value.lower() == "rand"):
					#CHECK IF CORRECT NUMBER OF PARAMTERS
					if(len(Paramaters) != 2):
						raise Exception ("Error, Inccorect number of paramaters for rand")
					return(random.randint(int(Paramaters[0]),int(Paramaters[1])))		
				#RANDFLOAT
				elif(Self.Value.lower() == "randfloat"):
					#CHECK IF CORRECT NUMBER OF PARAMTERS
					if(len(Paramaters) != 2):
						raise Exception ("Error, Inccorect number of paramaters for randfloat")
					return(random.uniform(float(Paramaters[0]),float(Paramaters[1])))
				else:	
					return (Lookup.Processor(Self.Value, Paramaters))
		#ID
		elif(Self.Type == NodeIndex['NODE_ID']):	
			return (Lookup.GetValue(Self.Value))			
		#PARMATERS		
		elif(Self.Type == NodeIndex['NODE_PARAMATER']):		
			ParamaterList = []
			ParamaterList.append(Self.LeftChild.Execute(Lookup))
			if(Self.RightChild != ''):
				RightReturn = Self.RightChild.Execute(Lookup)
				if(type(RightReturn) == list):
					ParamaterList = ParamaterList + RightReturn
				else:
					ParamaterList.append(RightReturn)
			return(ParamaterList)
		#VALUE
		elif(Self.Type == NodeIndex['NODE_STRING'] or Self.Type == NodeIndex['NODE_NUMBER']):
			return(Self.Value)
		#THIS
		elif(Self.Type == NodeIndex['NODE_THIS']):	
			if(not Lookup.ThisRef is None):
				return (Lookup.ThisRef)
	
	################################# NODE - GET NODES BY VALUE #################################
	#Function:  Returns a list of nodes that contain a value matching the provided value(s)
	#Input:  Value(s) to look for
	#Output: List of Values				
	def GetNodesbyValue(Self, Value, List):
		if(Self.Value in Value):
			List.append(Self)
		if(Self.LeftChild != ''):
			List = Self.LeftChild.GetNodesbyValue(Value, List)
		if(Self.RightChild != ''):
			List = Self.RightChild.GetNodesbyValue(Value, List)
		return(List)
				
class Command():
	################################# COMMAND - INITIALIZATION #################################
	#Function:  Creates a new Command Object
	#Input:  Text
	#Output: object	
	def __init__(Self, Text):		
		Self.Text = Text
		try:
			Tokens = Lex(Text)
		except Exception as Message: 
			raise Exception (str(Text)+"Text\nLex Failed\n"+str(Message))
		try:
			Self.Tree = ParseExpressionList(Tokens)	
		except Exception as Message: 
			raise Exception (Text+"\nParse Failed\n"+str(Message))
		Self.ThisRef = None
		
	################################# COMMAND - EXECUTE #################################
	#Function:  Executes this functionh
	#Input:  LOOKUP STRUCTURE
	#Output: object	
	def Execute(Self, Lookup, This=None):		
		Lookup.ThisRef = This
		try:
			return(Self.Tree.Execute(Lookup))
		except Exception as Message: 
			if(not(This is None)):
				print("Command: This Value:")
				print(This.Name)
			Self.Tree.Print()			
			raise Exception ("Execution Failed\n"+str(Message))		
		
	
	
	################################# COMMAND - GET NODES BY VALUE #################################
	#Function:  Returns a list of nodes that contain a value matching the provided value(s)
	#Input:  Value(s) to look for
	#Output: List of Values
	def GetNodesbyValue(Self, Value): 
		#CHECK IF VALUE IS NOT LIST
		if(not isinstance(Value, list)):
			Value = [Value]
		List = []
		List = Self.Tree.GetNodesbyValue(Value, List)
		return(List)
	
	################################# COMMAND - PRINT TREE #################################
	#Function:  PRINTS THE COMMAND TREE
	#Input:  LOOKUP STRUCTURE
	#Output: object		
	def PrintTree(Self):
		Self.Tree.Print()
	
