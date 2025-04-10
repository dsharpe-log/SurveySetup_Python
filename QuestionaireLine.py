import sys
import roman
import re

import QuestionaireMisc

from QuestionaireProcessCheck import QuestionaireProcessCheck
from QuestionaireProcessCheck import QuestionaireBlockTrack
from QuestionaireProcessCheck import QuestionaireTableTrack
from QuestionaireProcessCheck import QuestionaireListDefTrack
from QuestionaireProcessCheck import QuestionaireQuestionTrack
from QuestionaireProcessCheck import QuestionaireListTrack
#from QuestionaireSegment import QuestionaireSegment

MODEL_LINE_TYPE = {
    '0':"ID",
    '1':"TEXT",
    '2':"LIST",
    '3':"LIST_HEADING",
    '4':"TABLE_HEADING",
    '5':"SECOND_TABLE_HEADING",
    '6':"LOGIC"
}

LINE_TYPE_ID                    = 0
LINE_TYPE_TEXT                  = 1
LINE_TYPE_LIST                  = 2
LINE_TYPE_LIST_HEADING          = 3
LINE_TYPE_TABLE_HEADING         = 4
LINE_TYPE_SECOND_TABLE_HEADING  = 5
LINE_TYPE_LOGIC                 = 6

SEGMENT_TYPE_TEXT               = 0
SEGMENT_TYPE_ID                 = 1
SEGMENT_TYPE_LOGIC              = 2
SEGMENT_TYPE_LEADING_ID         = 3
SEGMENT_TYPE_TRAILING_ID        = 4
SEGMENT_TYPE_LIST               = 5

LIST_LINE_TYPE_TEXT             = 0 
LIST_LINE_TYPE_HEADING          = 1
LIST_LINE_TYPE_OTHER            = 2
LIST_LINE_TYPE_EXCLUSIVE        = 3


#TRACKED VALUE NOTES
# DEFINED FLAGS - DENOTES THAT THESE ELEMENTS HAVE BEEN FOUND IN CURRENT QUESTION3
# STATE FLAGS - DENOTE THAT THESE VALUES WERE RECENTLY PRESENT (USUALLY THE PREVIOUS LINE, OR AS IN TABLE / POST TABLE WITHIN A SPECIFIED SUBSTRUCTURE
# FORMAT FLAGS - DENOTES THE FORMATTING OF THE CURRENT LINE
# TEXT FLAGS - ALL VALUES SHOULD BE 0 OR 1
#       TEXT_START_ = DENOTE ELMENTS THAT START WITH SPECIFIED CHARACTER FORM
#       TEXT_END_ = DENOTE ELEMENTS THAT END WITH SPECIFIED CHARACTER FORM
#       TEXT_FIRST_WORD_ = DENOTE ELEMENTS WHERE THE FIRST SPACE SEPERATED WORD HAS A SPECIFIED CHARACTER FORM
#       LINE_ID_ = DENOTE TYPE OF ID FOUND IN LINE
#       PREV_ID_TYPE_ = DENOTE TYPE OF ID FOUND IN PREVIOUS LINE
# NUMERIC LINE VALUES - DENOTE NUMERIC VALUES ASSOCIATED WITH THE LINE
#         LIST_DEF_ID_PREV - ID OF THE LAST LIST DEF LINE ENCOUNTERED
#         LIST_DEF_ID_CURR - ID OF THE CURRENT LIST (IF IN LIST DEF)

#    NumericLineValues=['Length','TEXT_COUNT_SPACED_NUMERIC','TEXT_COUNT_TAB','TEXT_COUNT_TABED_BLANK','TEXT_COUNT_TABED_FULL','TEXT_COUNT_TABED_TEXT','TEXT_COUNT_TABED_NUMERIC','TEXT_LENGTH_TABED_AVERAGE''ListDefLevel','LengthFirstTab','TEXT_FIRST_WORD_LENGTH','Index','IndexBlock','IndexListDef','IndexTable', 'IndexList']

class QuestionaireLine (QuestionaireProcessCheck):

    DefineFlags = ['DEFINED_LIST','DEFINED_LIST_HEADING','DEFINED_LOGIC','DEFINED_QUESTION_ID','DEFINED_QUESTION_TEXT','DEFINED_TABLE_HEADING','DEFINED_SECOND_TABLE_HEADING','DEFINED_CHOICE','DEFINED_STATEMENTS','DEFINED_INSTRUCTIONS']
    StateFlags = ['IN_ID_LINE','IN_LIST','IN_TABLE_DEF','IN_TABLE','IN_POST_TABLE','IN_TEXT','IN_LOGIC','IN_LIST_HEADING','IN_TABLE_HEADING','IN_LIST_DEF','IN_BLANK_LINE','IS_ID_LINE','IS_LIST','IS_TEXT','IS_LOGIC','IS_LIST_HEADING','IS_TABLE_HEADING']
    FormatFlags = ['F','C','S','CAP','CRL','SQ','B','I','U']	
    TextFlags=['TEXT_START_UNDERSCORE','TEXT_START_NUMBER','TEXT_START_SINGLE_CHAR','TEXT_START_CHECK','TEXT_START_TAB','TEXT_FIRST_TAB_EMPTY','TEXT_START_UNDERSCORE_NUMBER','TEXT_END_UNDERSCORE','TEXT_END_NUMBER','TEXT_END_SINGLE_CHAR','TEXT_END_CHECK','TEXT_END_TAB','LINE_ID_USED','LINE_ID_AT_END','LINE_ID_TYPE_ID','LINE_ID_TYPE_NUMERIC','LINE_ID_TYPE_ALPHA','LINE_ID_TYPE_LIST_DEF','LINE_ID_FIRST_VAL','PREV_ID_TYPE_ID','PREV_ID_TYPE_NUMERIC','PREV_ID_TYPE_ALPHA','PREV_ID_TYPE_LIST_DEF','TEXT_FIRST_WORD_NUM','TEXT_FIRST_WORD_LETTER','TEXT_FIRST_WORD_PERIOD','TEXT_FIRST_WORD_ID','TEXT_FIRST_WORD_IS_WORD','TEXT_FIRST_WORD_UNDERSCORE']       
    NumericLineValues=['LINE_ID_TYPE','PREV_ID_TYPE','TEXT_LENGTH','TEXT_COUNT_SPACED_NUMERIC','TEXT_COUNT_TAB','TEXT_COUNT_TABED_BLANK','TEXT_COUNT_TABED_FULL','TEXT_COUNT_TABED_TEXT','TEXT_COUNT_TABED_NUMERIC','TEXT_LENGTH_TABED_AVERAGE','LIST_DEF_LEVEL','FIRST_TAB_LENGTH','TEXT_FIRST_WORD_LENGTH','QUESTION_CURRENT_LINE','BLOCK_CURRENT_LINE','LIST_DEF_ID','LIST_DEF_CURRENT_LINE','LIST_DEF_LENGTH_IN_QUESTION','TABLE_CURRENT_LINE', 'LIST_CURRENT_LINE','LIST_DEF_ID_CURR','LIST_DEF_ID_PREV']
  
    ##################################################################################################################
    ##################################### QUESTIONAIRE PROCESS CHECK LINE- INIT ######################################
    ################################################################################1#################################
    ############# QuestionaireLine:Init #############
    #FUNCTION:   Object Constructor - Builds a Question object
    #PARAMATERS: Question Text Array, Line Index, Previous Id Type, List Def Track, Table Track, Block Track, State Flags, Track Output, Track Output File, Configs, Word Document File Name
    #RETURNS:	 Nothing
    def __init__ (Self, Question, Text, Index, PrevIDType, ListDefTrack, TableTrack, BlockTrack, QuestionTrack, ListTrack, StateFlags, DefinedFlags, TrackOutput, Configs, FileName, UpdateTracks=True, Debug=0):
        QuestionaireProcessCheck.__init__(Self, Question, Debug)	
        Self.ProcessType = "LINE"
        def PopulateValues(DefaultList):
            ReturnList={}
            for Key in DefaultList:
                ReturnList[Key] =0
            return (ReturnList)
        Self.FileName = FileName
        Self.Configs = Configs
        Self.TrackOutput = TrackOutput
        Self.LineType = None        
        Self.PrevIDType =PrevIDType

        #SET NUMERIC TRACKING  - THESE MAY BE NONE - NEED TO CONFIRM REFERENCING FUNCTIONS WILL COMPENSATE
        
        Self.TableTrack = TableTrack
        Self.BlockTrack = BlockTrack    
        Self.QuestionTrack = QuestionTrack      #SET LATER
        Self.ListTrack = ListTrack              #SET LATER
        Self.ListDefTrack = ListDefTrack

        #ADD THE CURRENT TEXT TO EACH OF THE ABOVE STRUCTURES TO UPDATE THERE VALUES - ENTIRE PROCESS IS SKIPPED ON COMMAND
        if(UpdateTracks):
            if not (Self.ListDefTrack == None):
                Self.ListDefTrack.AddText(Text)
            if not (Self.TableTrack == None):
                Self.TableTrack.AddText(Text)
            if not (Self.BlockTrack == None):
                Self.BlockTrack.AddText(Text)            

            if not (Self.ListTrack == None):
                Self.ListTrack.AddText(Text)            
        #DON'T WANT TO TRIGGER THIS HERE, INSTEAD AFTER ASSOCIATED QUESTION IS CONFIRMED - OTHER ELEMENTS SHOULDN'T BREAK ACROSS QUESTIONS ANYWAY
            #if not (Self.QuestionTrack == None):
            #    Self.QuestionTrack.AddText(Text)
        #SET STATE FLAGS BASED ON PARAMATER         
        Self.MaxWords=200		

        
        Self.StateFlags = PopulateValues(QuestionaireLine.StateFlags)
        if(not(StateFlags is None)):                    
            Self.SetFlagValues(StateFlags)
        Self.DefinedFlags = PopulateValues(QuestionaireLine.DefineFlags)
        if(not(DefinedFlags is None)):        
            Self.SetFlagValues(DefinedFlags)

        Self.FormatFlags = PopulateValues(QuestionaireLine.FormatFlags)
        Self.TextContentFlags = PopulateValues(QuestionaireLine.TextFlags) 
        Self.NumericValuesText= PopulateValues(QuestionaireLine.NumericLineValues)   

        for Value in Self.Configs['TRACKING_VALUES']['LINE_VALUE']:
            Self.LogicCodes[Value]=0

        #SET VALUES
        Self.Text = Text
        Self.CleanText = re.sub(r'<<[tT]>>','_TAB_ ',Text)  #PRSERVE TABS         
        Self.CleanText = QuestionaireMisc.ClearTags(Self.CleanText)
        
        Self.Index = Index
        
        #POPULATE NUMERIC VALUES
        Self.InitLogicCodes(Configs,'LINE_VALUE')        
        Self.SetLineValues(Self.Text, Self.Index, PrevIDType)        

    ##################################################################################################################
    ####################################### QUESTIONAIRE LINE - PROCEESSING ##########################################
    ##################################################################################################################	
    ############# QuestionaireLine:CheckNewQuestion #############
    #FUNCTION:   Executes AI model to determine if the current line is the start of a new question 
    #PARAMATERS: Nothing
    #RETURNS:	 Boolean
    def CheckNewQuestion (Self):
        #CHECK FOR TILDE - WILL NEVER TRIGGER UPDATED PRIOR TO EXECTTION
        if(re.search(r"^\s*(<<[^>]+>>\s*)*\s*~",Self.Text)):
            return(True)
        else:
            return(False)

    ##################################################################################################################
    ###################################### QUESTIONAIRE LINE - SET VALUES ############################################
    ##################################################################################################################	
    ############# QuestionaireLine:SetType #############
    def SetType (Self):
        Weights = {}
        #BUILD WEIGHTS FOR EACH ELEMENT		
        if(Self.Debug == 2): 
            print("\n\n###############################################################")
            print("LINE: "+Self.Text)   

        Weights["LOGIC"] =Self.CheckElements(Self.Configs['ID_LOGIC'],Self.Text)
        Weights["ID"] = Self.CheckElements(Self.Configs['ID_QUESTION_ID'],Self.Text)
        Weights["TEXT"] = Self.CheckElements(Self.Configs['ID_QUESTION_TEXT'],Self.Text)
        Weights["LIST"] = Self.CheckElements(Self.Configs['ID_LIST'],Self.Text)
        Weights["LIST_HEADING"] = Self.CheckElements(Self.Configs['ID_LIST_HEADING'],Self.Text)
        Weights["TABLE_HEADING"] = Self.CheckElements(Self.Configs['ID_TABLE_HEADING'],Self.Text)
        Weights["SECOND_TABLE_HEADING"] = Self.CheckElements(Self.Configs['ID_SECOND_TABLE_HEADING'],Self.Text)

        if(Self.Debug == 2): 
            print("\n\nSELECTED:"+Self.Text)

        Self.LineType = QuestionaireMisc.SelectHigh(Weights,Self.Debug)
        

        return(0)
        
    ############# QuestionaireLine:SetLineValues #############
    #FUNCTION:   Provided a line of text processes a set of variables associated with it. 
    #PARAMATERS: Line
    #RETURNS:	 Nothing	
    def SetLineValues (Self, Line, Index, PrevIDType):   
        Self.FormatFlags = QuestionaireMisc.GetTextFormattingFlags(Line)

        Self.ClearValues(Self.NumericValuesText, QuestionaireLine.NumericLineValues)
        Self.ClearValues(Self.TextContentFlags, QuestionaireLine.TextFlags)				
        UnformmatedLine = QuestionaireMisc.ClearFormatTags(Line) 
        
        CleanLine = QuestionaireMisc.ClearTags(Line) 
        FirstWord = CleanLine.split(' ')[0] 

        TabbedLine = re.sub(r'<<t>>','XXXTABXXX',Line, flags=re.IGNORECASE)
        TabbedLine = QuestionaireMisc.ClearTags(TabbedLine) 	
        TabbedLine = re.sub(r'XXXTABXXX','<<T>>',TabbedLine, flags=re.IGNORECASE)
        Tabs = TabbedLine.split('<<T>>')
        FirstTab = Tabs[0]
        FirstTab = QuestionaireMisc.ClearTags(FirstTab) 
        #NUMERIC VALUES
        Self.NumericValuesText['TEXT_LENGTH'] = len(CleanLine)
        Self.NumericValuesText['TEXT_COUNT_SPACED_NUMERIC'] = len(re.findall(r'\s\d+\s',CleanLine)) + bool(re.search(r'\s\d+$',CleanLine)) + bool(re.search(r'^\d+\s',CleanLine))		
        Self.NumericValuesText['TEXT_FIRST_WORD_LENGTH'] = len(FirstWord)
        
        #TABBED VALUES		
        Self.NumericValuesText['TEXT_COUNT_TAB'] = len(Tabs)
        Self.NumericValuesText['FIRST_TAB_LENGTH'] = len(Tabs[0])
        for Tab in Tabs:
            if(Tab ==""): Self.NumericValuesText['TEXT_COUNT_TABED_BLANK'] += 1
            Self.NumericValuesText['TEXT_COUNT_TABED_FULL'] += int(bool(re.search(r'\S',Tab)))
            
            Self.NumericValuesText['TEXT_COUNT_TABED_TEXT'] += int(bool(re.search(r'[a-z]',Tab,re.IGNORECASE)))		
            Self.NumericValuesText['TEXT_COUNT_TABED_NUMERIC'] += int(bool(re.search(r'^[0-9_. ]+$',Tab,re.IGNORECASE)))		
            Self.NumericValuesText['TEXT_LENGTH_TABED_AVERAGE'] += len(Tab)
        Self.NumericValuesText['TEXT_LENGTH_TABED_AVERAGE'] =Self.NumericValuesText['TEXT_LENGTH_TABED_AVERAGE']/Self.NumericValuesText['TEXT_COUNT_TAB']
        #INDEX
        Self.NumericValuesText['QUESTION_CURRENT_LINE']=Index

        #BLOCKS TYPICALLY INCLUDE THE BREAK AT THE START - AND MAY INCLUDE MORE IF LINE CONTAIN DELETED CHARACTERS
        if(re.search(r'<<BLOCK=(\d+)>>',Line)):		            
            Self.NumericValuesText['BLOCK_CURRENT_LINE']=int(re.search(r'<<BLOCK=(\d+)>>',Line).group(1))
            if not (Self.BlockTrack == None) and (Self.StateFlags['IN_BLANK_LINE']):                 
                Self.BlockTrack.AddBreak()
        #IF LIST DEF
        if(re.search(r'<<LIST_ID=(\S+)',Line)):
        		
            ListID = re.search(r'<<LIST_ID=(\S+)',Line).group(1)      
            Self.StateFlags['IN_LIST_DEF'] = 1
            Self.NumericValuesText['LIST_DEF_CURRENT_LINE']=int(re.search(r'LIST_INDEX=(\d+)',Line).group(1))
            Self.NumericValuesText['LIST_DEF_LENGTH_IN_QUESTION']=int(re.search(r'QUESTION_LENGTH=(\d+)',Line).group(1))
            #LIST LEVEL
            if(re.search(r'<<LIST_ID[^<>]+LIST_LEVEL',Line)):
                Self.NumericValuesText['LIST_DEF_LEVEL'] = int(re.search(r'<<LIST_ID[^<>]+LIST_LEVEL=(\d+)',Line).group(1))
            if not (Self.ListDefTrack == None) and(Self.StateFlags['IN_BLANK_LINE']):
                Self.ListDefTrack.AddBreak()
            Self.NumericValuesText['LIST_DEF_ID_CURR'] = ListID 
            if(re.search(r'ID_VALUE',Line)): 
                #NUMERIC
                if(re.search(r'<<LIST_ID[^<>]+ID_VALUE=(\d+)',Line)):
                    Self.NumericValuesText['LIST_DEF_ID'] = int(re.search(r'<<LIST_ID[^<>]+ID_VALUE=(\d+)',Line).group(1))
                #NON-NUMERIC
                else:
                    Self.NumericValuesText['LIST_DEF_ID'] = re.search(r'<<LIST_ID[^<>]+ID_VALUE=([^ ><]+)',Line).group(1)
        if(re.search(r'<<TABL_IND=(\d+)',Line)):		
            Self.NumericValuesText['TABLE_CURRENT_LINE']=int(re.search(r'<<TABL_IND=(\d+)',Line).group(1))
            if not (Self.TableTrack == None) and(Self.StateFlags['IN_BLANK_LINE']):
                Self.TableTrack.AddBreak()

        #BOOLEAN VALUES
        #STARING CHARACTER      
        Self.TextContentFlags['TEXT_START_UNDERSCORE'] = int(bool(re.search(r'^\s*_',CleanLine)))
        Self.TextContentFlags['TEXT_START_NUMBER'] = int(bool(re.search(r'^\s*\d+',CleanLine)))
        Self.TextContentFlags['TEXT_START_SINGLE_CHAR'] = int(bool(re.search(r'^\s*[a-z][^A-Z]\s',CleanLine,re.IGNORECASE)))
        Self.TextContentFlags['TEXT_START_CHECK'] = int(bool(re.search(r'^\s*',CleanLine, re.UNICODE)) or bool(re.search(r'^\s*☐',UnformmatedLine, re.UNICODE)))
        Self.TextContentFlags['TEXT_START_TAB'] =int(bool(re.search(r'^\s*(<<[^<>]+>>\s*)*\s*<<T>>',Line)))
        Self.TextContentFlags['TEXT_START_UNDERSCORE_NUMBER'] = int(bool(re.search(r'^\s*_+\s*\d',CleanLine)))
        
        #ENDING CHARACTER
        Self.TextContentFlags['TEXT_END_UNDERSCORE'] = int(bool(re.search(r'_\s*$',CleanLine)))
        Self.TextContentFlags['TEXT_END_NUMBER'] = int(bool(re.search(r'\d+\s*$',CleanLine)))
        Self.TextContentFlags['TEXT_END_SINGLE_CHAR'] = int(bool(re.search(r'\s[a-z]\s*$',CleanLine,re.IGNORECASE)))
        Self.TextContentFlags['TEXT_END_CHECK'] = int(bool(re.search(r'\s*$',UnformmatedLine,re.UNICODE)) or bool(re.search(r'☐\s*$',UnformmatedLine, re.UNICODE)))
        Self.TextContentFlags['TEXT_END_TAB'] = int(bool(re.search(r'<<T>>\s*$',Line,re.IGNORECASE)))

        #FIRST WORD
        Self.TextContentFlags['TEXT_FIRST_WORD_NUM'] = int(bool(re.search(r'[0-9]',FirstWord)) and (not(bool(re.search(r'[-+]',FirstWord))) or (bool(re.search(r'^\s*[0-9]+\s*-\s*[a-zA-Z]',CleanLine)))))
        Self.TextContentFlags['TEXT_FIRST_WORD_LETTER'] = int(bool(re.search(r'^[A-Z][^A-Z]*$',FirstWord,re.IGNORECASE)))
        Self.TextContentFlags['TEXT_FIRST_WORD_PERIOD'] = int(bool(re.search(r'\.',FirstWord)))
        Self.TextContentFlags['TEXT_FIRST_WORD_ID'] = int(bool(re.search(r'^[A-Z]\.?[0-9]+(A-Z)*\.?',FirstWord,re.IGNORECASE)))
        Self.TextContentFlags['TEXT_FIRST_WORD_IS_WORD'] = int(bool(re.search(r'[BCDFGHJKLMNPQRSTVWX]',FirstTab, re.IGNORECASE)) and bool(re.search(r'[AEIOUY]',FirstWord, re.IGNORECASE)) and not bool(re.search(r'[0-9]',FirstWord, re.IGNORECASE)))
        Self.TextContentFlags['TEXT_FIRST_WORD_UNDERSCORE'] = int(bool(re.search(r'_',FirstWord)))
        
        #FIRST TAB
        Self.TextContentFlags['TEXT_FIRST_TAB_EMPTY']  = int(bool(re.search(r'^\s*$',FirstTab,re.IGNORECASE)))        
        #SET PREVIOUS ID TYPE
        Self.NumericValuesText['PREV_ID_TYPE']= PrevIDType
        
        if(PrevIDType=="ListDef"):
            Self.TextContentFlags['PREV_ID_TYPE_LIST_DEF'] = 1
        elif(PrevIDType=="ID"):
            Self.TextContentFlags['PREV_ID_TYPE_ID'] = 1
        elif(PrevIDType=="Numeric"):
            Self.TextContentFlags['PREV_ID_TYPE_NUMERIC'] = 1
        elif(PrevIDType=="Alpha"):
            Self.TextContentFlags['PREV_ID_TYPE_ALPHA]'] = 1
        
        #SET CURRENT ID TYPE	        
        #LEADING IDS (PRESUMED OVER TRAILING)
        Self.NumericValuesText['LINE_ID_TYPE']= 'None'
        if(re.search(r'<<LIST_ID=([^ >]+)',Line, re.IGNORECASE)):	
            Self.TextContentFlags['LINE_ID_TYPE_LIST_DEF'] = 1
            Self.NumericValuesText['LINE_ID_TYPE']= 'ListDef'           
        elif(Self.TextContentFlags['TEXT_FIRST_WORD_ID']==1):
            Self.TextContentFlags['LINE_ID_TYPE_ID'] = 1
            Self.NumericValuesText['LINE_ID_TYPE']= 'ID'                
        elif(Self.TextContentFlags['TEXT_FIRST_WORD_NUM']==1):
            #ONLY POPULATE IF LIKELY ID - LESS FORGIVING THAN OTHER ID IDENTIFICATION	
            if(re.search(r'^1$',re.sub("[^a-zA-Z0-9]","",FirstWord)) or re.search(r'^0$',re.sub("[^a-zA-Z0-9]","",FirstWord))):
                Self.TextContentFlags['LINE_ID_FIRST_VAL'] = 1    
            Self.TextContentFlags['LINE_ID_TYPE_NUMERIC'] = 1
            Self.NumericValuesText['LINE_ID_TYPE']= 'Numeric'                      
        elif(Self.TextContentFlags['TEXT_START_SINGLE_CHAR']==1):	
            #ONLY POPULATE IF LIKELY ID - LESS FORGIVING THAN OTHER ID IDENTIFICATION
            if(re.search(r'A',re.sub("[^a-zA-Z0-9]","",FirstWord),re.IGNORECASE)):
                Self.TextContentFlags['LINE_ID_FIRST_VAL'] = 1    
            Self.TextContentFlags['LINE_ID_TYPE_ALPHA'] = 1
            Self.NumericValuesText['LINE_ID_TYPE']= 'Alpha'                

        #TRAILING IDS
        elif(Self.TextContentFlags['TEXT_END_NUMBER']==1):	
            #ONLY POPULATE IF LIKELY ID - LESS FORGIVING THAN OTHER ID IDENTIFICATION
            if(PrevIDType=="Numeric" or re.search(r'\d$',CleanLine)):
                Self.TextContentFlags['LINE_ID_AT_END'] = 1                
                Self.TextContentFlags['LINE_ID_TYPE_NUMERIC'] = 1
                Self.NumericValuesText['LINE_ID_TYPE']= 'Numeric'            
        elif(Self.TextContentFlags['TEXT_END_SINGLE_CHAR']==1):
            #ONLY POPULATE IF LIKELY ID - LESS FORGIVING THAN OTHER ID IDENTIFICATION
            if(PrevIDType=="Alpha" or re.search(r'A$',CleanLine,re.IGNORECASE)):
                Self.TextContentFlags['LINE_ID_AT_END'] = 1
                Self.TextContentFlags['LINE_ID_TYPE_ALPHA'] = 1
                Self.NumericValuesText['LINE_ID_TYPE']= 'Alpha'     


    ############# QuestionaireQuestion:SetValuesNewQuestions #############
    #FUNCTION:   Denotes that this line is the start of a new quesiton - clears and modifies several tags apporpriately
    #PARAMATERS: Nothing
    #RETURNS:	 Nothing	
    def SetValuesNewQuestions (Self):
        def PopulateValues(DefaultList):
            ReturnList={}
            for Key in DefaultList:
                ReturnList[Key] =0
            return (ReturnList)        
        Self.DefineFlags = PopulateValues(QuestionaireLine.DefineFlags)
        Self.StateFlags = PopulateValues(QuestionaireLine.StateFlags)
        Self.TextContentFlags['QuestionCurrentLine']=1
        Self.TextContentFlags['PrevIDTypeID']=0
        Self.TextContentFlags['PrevIDTypeNumeric']=0
        Self.TextContentFlags['PrevIDTypeAlpha']=0
        Self.TextContentFlags['PrevIDTypeListDef']=0
  
   ############# QuestionaireQuestion:SetBlockTrack #############
    #FUNCTION:   Sets the refernce of the list track object
    #PARAMATERS: Block Track object
    #RETURNS:	 Nothing	
    def SetBlockTrack (Self, BlockTrack):        
        Self.BlockTrack = BlockTrack
        BlockTrack.AddText(Self.Text)

    ############# QuestionaireQuestion:SetTableTrack #############
    #FUNCTION:   Sets the refernce of the list track object
    #PARAMATERS: Table Track object
    #RETURNS:	 Nothing
    def SetTableTrack (Self, TableTrack):    
        Self.TableTrack = TableTrack
        TableTrack.AddText(Self.Text)

   ############# QuestionaireQuestion:SetListDefTrack #############
    #FUNCTION:   Sets the refernce of the list Def track object
    #PARAMATERS: List Def Track object
    #RETURNS:	 Nothing	
    def SetListDefTrack (Self, ListDefTrack):  
        Self.ListDefTrack = ListDefTrack
        ListDefTrack.AddText(Self.Text)

    ############# QuestionaireQuestion:SetQuestionTrack #############
    #FUNCTION:   Sets the refernce of the list track object       
    #PARAMATERS: Question Track object
    #RETURNS:	 Nothing
    def SetQuestionTrack (Self, QuestionTrack):              
        Self.QuestionTrack = QuestionTrack
        QuestionTrack.AddText(Self.Text)
   ############# QuestionaireQuestion:SetListTrack #############
    #FUNCTION:   Sets the refernce of the list track object
    #PARAMATERS: List Track object
    #RETURNS:	 Nothing	
    def SetListTrack (Self, ListTrack):  
        Self.ListTrack = ListTrack
        ListTrack.AddText(Self.Text)

    ############# QuestionaireQuestion:SetListDefQuestionTrack #############
    #FUNCTION:   Sets the List def question track value and modifies the question text to match
    #PARAMATERS: List Value, Value to update to
    #RETURNS:	 Nothing	    
    def SetListDefQuestionTrack (Self, ListValue, Value):          
        if(Self.StateFlags['IN_LIST_DEF'] and re.search(r'<<LIST_ID='+str(ListValue),Self.Text)):            
            Self.NumericValuesText['LIST_DEF_LENGTH_IN_QUESTION']=Value
            Self.Text = re.sub(r'QUESTION_LENGTH=(\d+)','QUESTION_LENGTH='+str(Value),Self.Text)


    ############# QuestionaireQuestion:ResetListDefQuestionTrack #############
    #FUNCTION:   Resets the List def question track value to 1 and modifies the question text to match
    #PARAMATERS: Nothing
    #RETURNS:	 Nothing	    
    def ResetListDefQuestionTrack (Self):          
        if(Self.StateFlags['IN_LIST_DEF']):            
            Self.NumericValuesText['LIST_DEF_LENGTH_IN_QUESTION']=1
            Self.Text = re.sub(r'QUESTION_LENGTH=(\d+)','QUESTION_LENGTH=1',Self.Text)


    ##################################################################################################################
    ################################ QUESTIONAIRE PROCESS CHECK LINE - GET VALUES ####################################
    ##################################################################################################################	
  
    ############# QuestionaireLine:Get ID Type #############
    #FUNCTION:   Returns the ID Type of the current line
    #PARAMATERS: Nothing
    #RETURNS:	 ID Type
    def GetIDType (Self):
        return (Self.NumericValuesText['LINE_ID_TYPE'])        
        
