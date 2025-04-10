
import sys
import roman
import re


import QuestionaireMisc

####################################### QUESTIONAIRE CLEAN UP #########################################
class QuestionaireCleanUp:

    ########################################################################################################
	##################################### QUESTIONAIRE CLEAN UP - INIT #####################################
	########################################################################################################
	############# QuestionaireCleanUp:Init #############
	#FUNCTION:   Object Constructor - Builds a Question Cleanup object
	#PARAMATERS: 
	#RETURNS:	 Nothing
	def __init__ (Self, Rules):
		Self.Rules = Rules


	############# SurveySetup:CleanupNestedTags #############
	#FUNCTION:   Looks for tags nested within other tags in an incorrect format and reformats them	
	#PARAMATERS: Text
	#RETURNS:	 Nothing
	def CleanupNestedTags(Self, Text):
		#NOT USED - USE QUESTIONAIRE MISC VERSION
		Found=True  #VARIABLE USED TO TRACK IF RULE HAS BEEN SUCCESSFULLY APPLIED
		if(not("<<" in Text)): return(Text)
		#print("\n\nUPDATING TEXT")
		#SEARCH TAG VALUES
		WrappingTags =["B","I","U","F","S","C"]
		#LOOP THROUGH WRAPIING TAGS, WITH INDEX
		while(Found):
			Found=False
			for Tag in WrappingTags:
				#print("TAG:"+Tag)	
				#TEST WITH THIS REGEX INSTEAD FOR LOOP /<<$Tag>>(([^<]*(<<\/?[^$Tag]>>)*)+)<<\/$Tag>>/gm) {			 - WOULD NEED TO MOIDFY FONT/SIZE/COLOR TO SINGLE CHANGER TAGS
				#LOOP THROUGH INSTANCES OF TAG
				for TagText in re.findall(r"(<<"+Tag+">>(?:(?:[^<]*(<<\/?[^"+Tag+"]>>)*)+)<<\/"+Tag+">>)",Text):	
					#print("START:"+Text)
					TagText = TagText[0]																					
					InternalTagText = re.search(r"<<"+Tag+">>(([^<]*(<<\/?[^"+Tag+"]>>)*)+)<<\/"+Tag+">>",TagText).group(1) #TEXT IN TAG
					#print("LOOPED TEXT:"+InternalTagText)				
					#CHECK IF STARTS WITH TAG
					if(re.search(r"^<<[^>]+>>",InternalTagText)):
						LeadTag = re.search(r"^<<([^>]+)>>",InternalTagText).group(1)
						#print("INTERNAL TAG FOUND: "+LeadTag)
						#IF A TRAILING TAG
						if(re.search(r"^\/",LeadTag) and LeadTag.replace("/","") in WrappingTags):						
							UpdateText = InternalTagText.replace("^<<"+LeadTag+">>","<<"+LeadTag+">><<"+Tag+">>")
							+">><<"+Tag+">>"
							#print("UPDATE LEADING_TRAIL:"+UpdateText)
							Text = Text.replace("<<"+Tag+">>"+InternalTagText,UpdateText)
							Found=True		
						#IF A LEADING TAG				
						elif(LeadTag in WrappingTags and not(re.search(r"<<\/"+LeadTag+">>",InternalTagText))):						
							UpdateText = re.sub(r"^<<"+LeadTag+">>","<<"+LeadTag+">><<"+Tag+">>",InternalTagText)						
							#print("UPDATE LEADING_LEAD:"+UpdateText)
							Text = Text.replace("<<"+Tag+">>"+InternalTagText,UpdateText)				
							Found=True		
					#CHECK IF TRAILS WITH TAG
					if(re.search(r"<<[^>]+>>$",InternalTagText)):
						TrailTag = re.search(r"<<([^>]+)>>$",InternalTagText).group(1)
						#print("INTERNAL TAG FOUND: "+TrailTag)
						#IF A LEADING TAGss
						if(not(re.search(r"^\/",TrailTag)) and TrailTag in WrappingTags):						
							UpdateText = InternalTagText.replace("<<"+TrailTag+">>$","<</"+Tag+">><<"+TrailTag+">>")
							#print("UPDATE TRAILING_LEAD:"+UpdateText)
							Text = Text.replace(InternalTagText+"<</"+Tag+">>",UpdateText)
							Found=True		
						#IF A TRAILING TAG					
						elif(TrailTag.replace("/","")  in WrappingTags and not(re.search(r"<<"+TrailTag.replace("/","")+">>",InternalTagText))):						
							UpdateText = re.sub(r"<<"+TrailTag+">>$","<</"+Tag+">><<"+TrailTag+">>",InternalTagText)						
							#print("UPDATE TRAILING_TRAIL:"+UpdateText)
							Text = Text.replace(InternalTagText+"<</"+Tag+">>",UpdateText)
							Found=True		
				#print(Text)	
		return(Text)



	############# QuestionaireCleanUp:UpdateText #############
	#FUNCTION:   Provided some text is updated based on the set of rules provided at object instantiation
	#PARAMATERS: Text
	#RETURNS:	 Updated Text
	def UpdateText (Self, Text, Ruleset):	
		if Ruleset in Self.Rules:
			for Rule in Self.Rules[Ruleset]:
				Success=True #VARIABLE USED TO TRACK IF RULE HAS BEEN SUCCESSFULLY APPLIED
				#LOOP TO MANAGE REPETED INSTRUCTIONS
				while(Success):
					Success=False
					#SET REPLACE VALUE			
					Replace = ""
					if('REPLACE' in Rule):
						if(Rule['REPLACE'] == '_SPACE_'):
							Replace=" "
						elif(Rule['REPLACE'] == '_FIRST_'):
							Replace="\\1"												
						elif(Rule['REPLACE'] != '_BLANK_'):							
							Replace = Rule['REPLACE']

					#CHECK FOR LOOP IN RULE
					if('LOOP' in Rule):                
						for LoopValue in Rule['LOOP']:
							if('IGNORECASE' in Rule):
								if(re.search(Rule['SEEK'].replace('_LOOP_',LoopValue),Text,flags=re.IGNORECASE)): 
									Success=True
									Text = re.sub(Rule['SEEK'].replace('_LOOP_',LoopValue), Replace.replace('_LOOP_',LoopValue),Text,flags=re.IGNORECASE)                    
							else:
								if(re.search(Rule['SEEK'].replace('_LOOP_',LoopValue),Text)): 
									Success=True						
									Text = re.sub(Rule['SEEK'].replace('_LOOP_',LoopValue), Replace.replace('_LOOP_',LoopValue),Text)                    
					else:
						if('IGNORECASE' in Rule):
							if(re.search(Rule['SEEK'],Text,flags=re.IGNORECASE)): 
								Success=True
								Text = re.sub(Rule['SEEK'],Replace,Text,flags=re.IGNORECASE)   
						else:
							if(re.search(Rule['SEEK'],Text)): 
								Success=True										
								Text = re.sub(Rule['SEEK'],Replace,Text)
					#CLEAR SUCCESS MARKER IF NOT REPEATED				
					if(not('REPEAT' in Rule)): Success=False	
			#Text = Self.CleanupNestedTags(Text)
		return(Text)

		

 