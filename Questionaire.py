
########################################################################################################
############################################# QUESTIONAIRE #############################################
########################################################################################################
#DESCRIPTION: Class structure used to hold a complete questionaire
#TODO:
#CHANGE LOG:
import os
import sys
import roman
import zipfile
import re
import pandas
import tensorflow as tf
from tensorflow import keras
import numpy
import roman
import codecs

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


import QuestionaireMisc
from DConfig import DConfig

from QuestionaireQuestion import QuestionaireQuestion
from QuestionaireLine import QuestionaireLine
from QuestionaireExportTemplate import QuestionaireExportTemplate
from QuestionaireCleanUp import QuestionaireCleanUp

from QuestionaireProcessCheck import QuestionaireBlockTrack
from QuestionaireProcessCheck import QuestionaireListDefTrack
from QuestionaireProcessCheck import QuestionaireTableTrack
from QuestionaireProcessCheck import QuestionaireQuestionTrack

########################################################################################################
###################################### CONSTANTS AND GLOBALS ###########################################
########################################################################################################
CONFIG_COMMANDS = {								#Keywords available in config
    
    'IMPORTATION_CONFIG':1,                     #DENOTES THIS CONFIG IS A MAIN IMPORTATION CONFIG
    'STRIP_LEADING_ZERO':1,                     #DENOTES NO LEADING ZEROS SHOULD BE ADDED TO IDS

    'REPLACE_CLEAR':1,							#CLEANUP _ REPLACE CLEAR
    'REMVOE_LEADING_ID':1,						#BEHAVCOIRAL - ID REMOVAL FOR TEXT

    'LOGIC_QUESTION':1,	                        #LOGIC - PROCESSED ON A QUESTION LEVEL (LINE AND SEGMENTS)
    'LOGIC_LIST':1,	                            #LOGIC - PROCESSED ON A LIST LEVEL (SEGMENTS)
    'LOGIC_CHECK_QTEXT':1,	                    #LOGIC - CONSIDERS QUESTION TEXT 
    'QUESTION_UNIQUE':1,                        #LOGIC - DENOTES THAT LOGIC SHOULD ONLY BE APPLIED TO A QUESTION ONCE
    'QUESTION_TEXT':1,                          #LOGIC - CONSIDERS QUESTION TEXT
    'QUESTION_TYPE':1,                          #LOGIC - CONSIDERS QUESTION TEXT
    'LIST_TEXT':1,                              #LOGIC - CONSIDERS LIST TEXT
    'STATE' :1,                   	            #LOGIC - USED TO DENOTE THAT THIS LOGIC IS A STATE TRACKER
    'DELETE':1,                                 #LOGIC - DELETE TRIGGERING TEXT FROM INCLUSION IF LOGIC IS TRIGGERED
    'STRIP_TEXT_TAGS':1,                        #LOGIC - STRIPS TAGS FROM TEXT RECALLS INTO CONSTRUCTED LOGIC STRUCTURES
    'SET_QUESTION_ID':1,                             #LOGIC - SETS QUESTION ID
    
    'MULTI_MENTION':1,                          #QUESTION - DENOTES MULTIMENTION TYPING
    'TRACK_FORMATS':1,                          #QUESTION - DENOTES THAT FORMATS SHOULD BE TRACKED WITHIN IN QUESTIONAIRE (NOT YET IMPLEMENTED)
}   

CONFIG_COMMAND_FIELDS={}
CONFIG_COMMANDS_REQUIRED_FIELDS={}


class Questionaire():

    ########################################################################################################
    ####################################### INITIALIZATION FUNCTIONS #######################################
    ########################################################################################################
    
    ############# Questionaire: Initialization  #############
    #FUNCTION:   Object Constructor - Builds a Questionaire object, breaks down provided excel file into usuable datastructure
    #PARAMATERS: Filename, ConfigFile, Trackoutput
    #RETURNS:	 Nothing
    def __init__ (Self, FileName,ConfigFile, TrackOutput, TrackOutputFile, DebugMode ):
                
        #FILES
        Self.FileName = FileName						#QUESTIONAIRE FILE
        Self.ConfigFile = ConfigFile					#MAIL CONFIG FILE
        Self.TrackOutputFile = TrackOutputFile			#FILE OUTPUT ROOT FOR TRACKING
        
        #FLAGS
        Self.TrackOutput = TrackOutput					#FLAG DENOTING THAT 
        Self.DebugMode = DebugMode						#DEBUG MODE
        Self.IsExcelExport = 0                          #FLAG DENOTING THAT THIS IS AN EXCEL EXPORT 

        #STRUCTURES
        Self.Questions = []								#LIST OF ALL QUESTIONS
        Self.Configs = {}								#MAIN LOOKUP STRUCTUR
        Self.QuestionIDTrack = {}						#TRACKS QUESTION IDS USED        
        

        #BUILD CONFIG FILES
        try:	
            Self.InitConfig()	
        except:
            raise Exception("Failed to build config files\n")
        
        #BUILD OUTPUT TRACKER IF REQUIRED
        if(Self.TrackOutput):
            Self.InitTrack()	
                        
        #SET INTI CLEANUP
        Self.InitClean = QuestionaireCleanUp(Self.Configs['CLEANUP'].Config)

        #PARSE NUMBERING
        try:			
            Self.ParseNumbering()         
        except:
            raise Exception('Failed to Parse numbering from Document - Questionaire::New')
            
        #PARSE FORMATS
        try:
               Self.ParseFormats()            
        except:
            raise Exception('Failed to Parse Formats from Document - Questionaire::New')
        
        #PARSE DOCUMENT
        try:
            Self.ParseDoc()	
        except:
            raise Exception('Failed to Parse Document - Questionaire::New')
        
        #PARSE QUESTIONS
        try:
            Self.ParseQuestions()
        except:
            raise Exception('Failed to Parse Questions - Questionaire::New')
        
        #PARSE QUESTIONS
        try:    
            Self.BuildQuestions()
        except:
            raise Exception('Failed to Build Questions - Questionaire::New')

        Self.FillIDs()	 

        #@$Self->DebugPrintElements
  
    ############# Questionaire:InitTrack #############
    #FUNCTION:   Builds structures used to export csv files tracking decision making values
    #PARAMATERS: Nothing
    #RETURNS:	 Nothing
    def InitTrack(Self):	
        return()
    
    ############# Questionaire:InitConfig #############
    #FUNCTION:   Populates config Structures
    #PARAMATERS: FileName
    #RETURNS:	 Nothing
    def InitConfig(Self):
    
        Self.Configs['TRACK_OUTPUT_FILE']=Self.TrackOutputFile
        Self.Configs['DEFUALT_VALUES']={}
        Self.Configs['TEMPLATES']={}
        Self.Configs['QTYPE_CONFIG']={}
        Self.Configs['LOGIC_CONFIG']={}
        Self.Configs['TRACKING_VALUES']={}
        Self.Configs['LIST_TYPE']={}

        Self.Configs['TRACKING_VALUES']['LINE_VALUE'] = []
        Self.Configs['TRACKING_VALUES']['LIST_VALUE'] = []
        Self.Configs['TRACKING_VALUES']['QUESTION_VALUE'] = []
        Self.Configs['TRACKING_VALUES']['LIST_VALUE'] = []

        Self.Configs['MAIN_CONFIG'] = DConfig(Self.ConfigFile, CONFIG_COMMANDS)	
        Self.Configs['ID_LIST'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_LIST_CONFIG'], CONFIG_COMMANDS)
        Self.Configs['ID_LIST_HEADING'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_LIST_HEADING_CONFIG'], CONFIG_COMMANDS)
        Self.Configs['ID_TABLE_HEADING'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_TABLE_HEADING_CONFIG'], CONFIG_COMMANDS)
        Self.Configs['ID_LOGIC'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_LOGIC_CONFIG'], CONFIG_COMMANDS)
        Self.Configs['ID_QUESTION_TEXT'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_QUESTION_TEXT_CONFIG'], CONFIG_COMMANDS)
        Self.Configs['ID_QUESTION_ID'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_QUESTION_ID_CONFIG'], CONFIG_COMMANDS)
        Self.Configs['ID_SECOND_TABLE_HEADING'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_SECOND_TABLE_HEADING_CONFIG'], CONFIG_COMMANDS)

        Self.Configs['ID_LIST_NEW'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_NEW_LIST_CONFIG'], CONFIG_COMMANDS)
       # Self.Configs['ID_LIST_SCALE'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['LIST_ID_SCALE_CONFIG'], CONFIG_COMMANDS)
        Self.Configs['ID_LIST_CHOICE'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['LIST_ID_CHOICE_CONFIG'], CONFIG_COMMANDS)
        Self.Configs['ID_LIST_ID'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['LIST_ID_IDENFICATION_CONFIG'], CONFIG_COMMANDS)

        Self.Configs['ID_SEGMENT_LOGIC'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_SEGMENT_LOGIC_CONFIG'], CONFIG_COMMANDS)
        Self.Configs['ID_SEGMENT_TEXT'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_SEGMENT_TEXT_CONFIG'], CONFIG_COMMANDS)        
        Self.Configs['ID_SEGMENT_ID'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['ID_SEGMENT_ID_CONFIG'], CONFIG_COMMANDS)

        #PROCESS SUB CONFIG FILES - MIGHT WANT TO RESTRUCTURE ALL CLEANUP CONFIGS INTO A SINGLE STRUCTURE 
        if('PROCESS_CLEANUP_CONFIG' in Self.Configs['MAIN_CONFIG'].Config):
            Self.Configs['CLEANUP'] = DConfig(Self.Configs['MAIN_CONFIG'].Config['PROCESS_CLEANUP_CONFIG'], CONFIG_COMMANDS)	
            #LOOK FOR RULES IN ADDITONAL CLEAN UP MERGE WITH DEFAULTS
            #TO DO - MODIFY TO MERGE ADDITIONAL CLEANUP STRUCTURES INTO SPECIFIC CLEANUP SUBSTRUCTURES  INIT_CLEANUP FROM ADD TO INIT_CLEANUP IN BASE
            if('ADDITIONAL_CLEANUP' in Self.Configs['MAIN_CONFIG'].Config):
                Self.Configs['CLEANUP'].Config['ADDITIONAL_CLEANUP'] = Self.Configs['MAIN_CONFIG'].Config['ADDITIONAL_CLEANUP']        #LOOP THROUGH QUESTION TYPES
        else:
            raise Exception("Error: No Cleanup Config Found\n")
        #RE INIT INC VALUES TO INTEGERS
        for IncValue in Self.Configs['MAIN_CONFIG'].Config['INC_VALUES']:        
            Self.Configs['MAIN_CONFIG'].Config['INC_VALUES'][IncValue] = int(Self.Configs['MAIN_CONFIG'].Config['INC_VALUES'][IncValue])

        if('QUESTION_TYPES' in Self.Configs['MAIN_CONFIG'].Config):	
            for QType in Self.Configs['MAIN_CONFIG'].Config['QUESTION_TYPES']:
                if (QType['ID'] in Self.Configs['TEMPLATES']):
                    raise Exception("Error: Duplicate template ID: "+QType['ID']+" found\n")
             
                #CHECK IF EXPORTING TO EXCEL
                if('EXCEL_EXPORT' in Self.Configs['MAIN_CONFIG'].Config):			
                    raise Exception("Error: Excel Export not yet supported\n")
                    #QTypeExportConfigs[QType['ID']] = DConfig(QType['TEMPLATE_CONFIG'], CONFIG_COMMANDS)	
                #PROCESS TEMPLATES FOR TEXT
                else:
                    Self.Configs['TEMPLATES'][QType['ID']]= QuestionaireExportTemplate(QType['TEMPLATE_CONFIG'])
                Self.Configs['QTYPE_CONFIG'][QType['ID']]= DConfig(QType['ID_CONFIG'], CONFIG_COMMANDS)

        #LOOP THROUGH LIST TYPES
        if('LIST_TYPE' in Self.Configs['MAIN_CONFIG'].Config):   
            for ListType in Self.Configs['MAIN_CONFIG'].Config['LIST_TYPE']:
                 if ('CONFIG' in ListType):               
                    Self.Configs['LIST_TYPE'][ListType['ID']] = DConfig(ListType['CONFIG'], CONFIG_COMMANDS)
        #LOOP THROUGH LOGIC
        if('LOGIC' in Self.Configs['MAIN_CONFIG'].Config):	
            for Logic in Self.Configs['MAIN_CONFIG'].Config['LOGIC']:
                if (Logic['ID'] in Self.Configs['TEMPLATES']):
                    raise Exception("Error: Duplicate template ID: "+Logic['ID']+" found\n")
                if('ID_CONFIG' in Logic):
                    Self.Configs['LOGIC_CONFIG'][Logic['ID']]= DConfig(Logic['ID_CONFIG'], CONFIG_COMMANDS)
                #ADD POST QUESTION TEMPLATE
                if('POST_QUESTION_ADD' in Logic):
                    Self.Configs['TEMPLATES']["POST_"+Logic['ID']]= QuestionaireExportTemplate(Logic['POST_QUESTION_ADD'])
                #ADD PRE QUESTION TEMPLATE
                if('PRE_QUESTION_ADD' in Logic):
                    Self.Configs['TEMPLATES']["PRE_"+Logic['ID']]= QuestionaireExportTemplate(Logic['PRE_QUESTION_ADD'])
                for ValueTypeKey in Self.Configs['TRACKING_VALUES']:
                    if(ValueTypeKey in Logic):                      
                        for ValueKey in Logic[ValueTypeKey]:
                            if(ValueKey not in Self.Configs['TRACKING_VALUES'][ValueTypeKey]):
                                Self.Configs['TRACKING_VALUES'][ValueTypeKey].append(ValueKey)
                    #LOOK FOR NEXT FUNCTIONALTIY
                    if("NEXT_"+ValueTypeKey in Logic):
                        for ValueKey in Logic["NEXT_"+ValueTypeKey]:
                            if(ValueKey not in Self.Configs['TRACKING_VALUES'][ValueTypeKey]):
                                   Self.Configs['TRACKING_VALUES'][ValueTypeKey].append(ValueKey)

    ########################################################################################################
    ########################################## PARSE FUNCTIONS #############################################
    ########################################################################################################
    
    ############# Questionaire:ParseNumbering #############
    #FUNCTION:   Breaks the Numbering.xml file in the word ductment into a 
    #PARAMATERS: Nothing
    #RETURNS:	 Nothing
    def ParseFormats(Self):
        try:
            Zip = zipfile.ZipFile(Self.FileName)						#ZIPED EXTRACT OF THE DOC FILE
            Document = Zip.read('word/document.xml') .decode('utf-8')	#PRIMARY DOCUMENT 
        except:
            raise Exception('Failed to add question - Questionaire::ParseDoc')	
        
        def ProcessFormatList(Regex):
            List={}
            for Code in re.findall(Regex,Document):
                if(Code in List):
                    List[Code]+=1
                else:
                    List[Code]=1
            HighCount=0
            SelectedVal=""
            for Index in List.keys():
                if(List[Index] > HighCount):
                    SelectedVal=Index
                    HighCount = List[Index] 
            return (SelectedVal)
            
        Self.Configs['DEFUALT_VALUES']["Font"] = ProcessFormatList(r'\<w\:rFonts w\:ascii\="([^"]+)"')
        Self.Configs['DEFUALT_VALUES']["Size"] = ProcessFormatList(r'\<w\:sz w\:val="(\d+)"')
        Self.Configs['DEFUALT_VALUES']["Color"] = "000000"

    ############# Questionaire:ParseNumbering #############
    #FUNCTION:   Breaks the Numbering.xml file in the word ductment into a 
    #PARAMATERS: Nothing
    #RETURNS:	 Nothing
    def ParseNumbering (Self):	
        Self.ListEntry={}
        
        try:
            Zip = zipfile.ZipFile(Self.FileName)						#ZIPED EXTRACT OF THE DOC FILE			
        except:
            raise Exception("Failed to open Word Document")
        Path = zipfile.Path(Self.FileName,'word/numbering.xml')
        if(Path.exists()):
            Document = Zip.read('word/numbering.xml').decode('utf-8')	#PRIMARY DOCUMENT 

            ListStructure={}											#HASH CONTAINING ALL LIST DEFINITIONS					
            #LOOP THORUGH EACH LOOP DEFINITION
            for ListText in re.findall(r'w:abstractNum(.*?>.*?)<\/w:abstractNum>',Document):			
                #CHECK FOR LIST STRUCTURE ID
                NumID = re.search(r'w:abstractNumId="(\d+)"',ListText).group(1)
                if(NumID):
                    ListStructure[NumID]={}
                    #LOOP THROUGH LAYER DEFINTIONS
                    for LayerText in re.findall(r'(<w:lvl.*?>.*?<\/w:lvl>)',ListText):
                        NewLayerStructure={}		#VALUES USED TO DEFINE THE CURRENT LAYER
                        LayerId = re.search(r'w:ilvl="(\d+)"',LayerText).group(1)
                        if(LayerId):
                            NewLayerStructure['LEVEL']=LayerId
                            NewLayerStructure['START']=0
                            ListStructure[NumID][LayerId]=NewLayerStructure
                            #GET NUMBER FORMAT
                            NumFormat = re.search(r'w:numFmt w:val="([^"]+)"', LayerText).group(1)
                            if(NumFormat): NewLayerStructure['FORMAT']=NumFormat
                            #GET LEVEL TEXT
                            if(re.search(r'w:lvlText w:val="([^"]+)"', LayerText)):
                                NewLayerStructure['LEVEL_TEXT']= re.search(r'w:lvlText w:val="([^"]+)"', LayerText).group(1)							
                            #GET START
                            if(re.search(r'w:start w:val="([^"]+)"', LayerText)):
                                NewLayerStructure['START'] = re.search(r'w:start w:val="([^"]+)"', LayerText).group(1)
            #GET NUMBERING - ABSTRACT LINKAGES:
            for LinkText in re.findall(r'(<w:num .*?>.*?<\/w:num>)',Document): 
                #FIND NUMBERING DEFINTION
                NumId = re.search(r'w:num w:numId="(\d+)"', LinkText).group(1)
                if(NumId):
                    #FIND ABSTRACT ID
                    LinkID = re.search(r'w:abstractNumId w:val="(\d+)"', LinkText).group(1)
                    if(LinkID):
                        NewListEntry={}			#STRCUTRUE FOR THIS LIST ENTRY
                        #POPULATE LIST ENTRY STRUCTURE
                        NewListEntry['LIST_STRUCTURE']=ListStructure[LinkID]
                        NewListEntry['COUNTERS']={}
                        #LOOP THROUGH EACH LAYER IN THE ASSOCIATED LIST STRUCTURE
                    for Key, Value in NewListEntry['LIST_STRUCTURE'].items():
                        NewListEntry['COUNTERS'][int(Key)]=int(Value['START'])
                    Self.ListEntry[NumId]=NewListEntry


    ############# Questionaire:ParseDoc #############
    #FUNCTION:   Breaks the Docx file into lines modifing text
    #PARAMATERS: Nothing
    #RETURNS:	 List of Lines
    def ParseDoc (Self):	
        try:
            Zip = zipfile.ZipFile(Self.FileName)						#ZIPED EXTRACT OF THE DOC FILE
            Document = Zip.read('word/document.xml') .decode('utf-8')	#PRIMARY DOCUMENT 
        except:
            raise Exception('Failed to add question - Questionaire::ParseDoc')	
    
        LineList = []											#LIST OF ALL LINES IN THE QUESTIONAIRE
        
        #TRACKING VARIABLES TO POPUATE PROCESS TAGS
        BlockCount=1
        ListDefIDTrack={}
                
        def ListAppend(Value):
            nonlocal BlockCount
            UpdateValue = Self.InitClean.UpdateText(Value,'INIT_CLEANING')	
            CleanValue = QuestionaireMisc.ClearTags(UpdateValue)
            if(CleanValue != "" and CleanValue != "~"):
                LineList.append('<<BLOCK='+str(BlockCount)+'>>'+str(UpdateValue))
                BlockCount+=1
            else:
                LineList.append(UpdateValue)
                BlockCount=1
        #CONFIRM EXTRACTION FROM WORD DOCUMENT

        #BREAK ANY TABLES FROM THE REST OF THE TEXT
        Document = re.sub(r'<w\:tbl>','%%<w:tbl>',Document)  	#ADDS %% BEFORE <W:TBL> TAGS
        Document = re.sub(r'<\/w\:tbl>',r'<\/w:tbl>%%',Document)	#ADDS %% AFTER <\W:TBL> TAGS
        
        #BREAKUP QUESTION TEXT INTO LINES
        #LOOP THROUGH BREAKS		
        for Break in Document.split('%%'):
            #CHECK IF TABLE
            if (re.search(r'<w:tbl>',Break)):
                #ADD TABLE ENTRY TAG
                ListAppend('<<TABLE>>')
                #LOOP THROUGH ROWS
                TableLineIndex=1				
                for RowText in re.findall(r'<w:tr.*?>(.*?)<\/w:tr>',Break):
                    LineText='<<TABL_IND='+str(TableLineIndex)+'>>' 	#TEXT FROM THE CURRENT LINE
                    #CLEAR TABS IN TABLE
                    RowText = re.sub(r'<w\:tab\/\>','',RowText)
                    #LOOP THROUGH COLUMNS
                    for ColText in re.findall(r'<w:tc.*?>(.*?)<\/w:tc>',RowText):
                        #LOOP THROUGH LINE DEFINITIONS
                        for WPText in re.findall(r'<w:p.*?>(.*?)<\/w:p>',ColText):						
                            #LOOP THROUGH SEGMENTS
                            for WRText in re.findall(r'<w:r[ >](.*?)<\/w:r>',WPText):
                                #CHECK IF TEXT IS STRUCK THROUGH
                                if (not (re.search(r'<w\:strike\/>',WRText))):									
                                    LineText += Self.ReformatSegment(WRText)										
                            LineText+=" "							
                        LineText+= "<<t>>"			
                    #CLEAN UP TEXT				
                    ListAppend(LineText)					
                    TableLineIndex+=1
                #ADD TABLE END TAG
                ListAppend('<</TABLE>>')					
            #PROCESS IF NOT TABLE
            else:
                #LOOP THROUGH LINE DEFINITIONS
                for WPText in re.findall(r'(<w:p.*?>.*?)<\/w:p>',Break):		                					
                    LineText="" 	#TEXT FROM THE CURRENT LINE
                    Level=0			#LIST LEVEL
                    ListID=0		#LIST ID
                    IDValue=""		#VALUE OF THIS ID
                    #CHECK FOR SELF TERMING PARGRAPH TAG - IF FOUNDED ADD A BLANK LINE
                    if(re.search(r'(\<w\:p\s+[^<]+\/\>)',WPText)):	
                        LineList.append('')
                        BlockCount=1
                    #CHECK FOR LIST DEFINITION	
                    if (re.search(r'<w:numPr.*?>(.*?)<\/w:numPr>',WPText)):				
                        ListText = re.search(r'<w:numPr.*?>(.*?)<\/w:numPr>',WPText).group(1)	#TEXT DEFINING LIST
                        if("<w:ilvl" in ListText):                            
                            Level = re.search(r'<w:ilvl w:val=\"(\d+)"\/>',ListText).group(1)		#CURRENT LIST LEVEL
                        if("<w:numId" in ListText):
                            ListID =re.search(r'<w:numId w:val=\"(\d+)"\/>',ListText).group(1)	 	#CURRENT LIST ID
                        IDValue = Self.GetID(ListID, Level)
                        #GET A LIST DEF ID COUTNER
                        ListCount=1
                        if( ListID in ListDefIDTrack):
                            ListDefIDTrack[ListID]+=1
                            ListCount = ListDefIDTrack[ListID]
                        else:
                            ListDefIDTrack[ListID]=ListCount						
                        #CHECK IF AN ID VALUE HAS BEEN COMPUTED FOR THIS LEVEL
                        if(re.search(r'\S',IDValue)):
                            LineText += "<<LIST_ID="+str(ListID)+" LIST_LEVEL="+str(Level)+" LIST_COUNT="+str(ListCount)+" ID_VALUE="+str(IDValue)+">>"
                        else:						
                            LineText += "<<LIST_ID="+str(ListID)+" LIST_LEVEL="+str(Level)+" LIST_COUNT="+str(ListCount)+">>"

                    #CHECK FOR FORMATTED LIST DEFINTION
                    elif(re.search(r'<w:pPr.*?>(.*?)<\/w:pPr>',WPText)):											
                        ListText = re.search(r'<w:pPr.*?>(.*?)<\/w:pPr>',WPText).group(1)#TEXT DEFINING LIST
                        #CHECK OF LINE TEXT
                        if(re.search(r'<w:pStyle w:val="([^"]+)"\/>',ListText)):	
                            ListID = re.search(r'<w:pStyle w:val="([^"]+)"\/>',ListText).group(1) #CURRENT LIST IDE
                            #GET A LIST DEF ID COUTNER
                            ListCount=1
                            if( ListID in ListDefIDTrack):
                                ListDefIDTrack[ListID]+=1
                                ListCount = ListDefIDTrack[ListID]
                            else:
                                ListDefIDTrack[ListID]=ListCount	
                            
                            LineText += "<<LIST_ID="+str(ListID)+" LIST_COUNT="+str(ListCount)+">>"
                            
                    #LOOP THROUGH TEXT SEGMENTS SEGMENTS
                    for WRText in re.findall(r'<w:r[ >](.*?)<\/w:r>',WPText):	
                        #CHECK IF TEXT IS STRUCK THROUGH
                        if (not(re.search(r'<w\:strike\/>',WRText)) or re.search(r'\~',WRText)):							
                            AddText = ""		#ADD TEXT USED TO ADD ~ IF FOUND IN STRIKETHROUGH
                            #IF TAB DETECTED ADD A SPACE							
                            if (re.search(r'<w:tab/>',WRText)):
                                AddText=" "
                            #IF SYMBOL DETECTED ADD A SPACE
                            if (re.search(r'<w:sym',WRText)):
                                AddText=" "
                            #LOOK FOR BR TAG AND REPLACEK
                            WRText = re.sub(r'\<w\:br\/\>','%n%',WRText)
                            LineText += Self.ReformatSegment(WRText) + AddText	

                    
                    #CLEAN UP TEXT	- DISABLED FOR NOW				 	
#					LineText = Self.CleanText(LineText)		
                    #CHECK FOR EMBEDED NEWLINE		
                    if(re.search(r'\%N\%',LineText,re.IGNORECASE)) :
                        List = LineText.split('%N%')
                        for ListItem in List: ListAppend(ListItem) 
                    #IF NO EMBEDDED NEW LINE ADD ENITRE TEXT TO LINE LIST                  
                    else:
                        ListAppend(LineText)	
        
        Self.Lines = LineList
                                      
    ############# Questionaire:ParseQuesitons #############
    #FUNCTION:   Breaks the provided lines into questions, collecting data for 
    #PARAMATERS: Lines
    #RETURNS:	 Nothing					
    def ParseQuestions (Self):	
        #CONTROL VARIBLES
        NewQuestionFlag=0                                  #FLAG DENOTING THAT THIS LINE REQUIRES A NEW QUESTION 
        QuestionLine=0                                     #INDEX OF THE CURRENT LINE WITHIN THE CURRENT QUESTION
        TableValues = None                                 #QUESTIONAIRE TABLE VALUES STRUCTURE
        ListDefValues = None                               #QUESTIONAIRE LIST DEF VALUES STRUCTURE
        BlockValues = None                                 #QUESTIUONAIRE BLOCK VALUES STRUCTURE
        QuestionValues= QuestionaireQuestionTrack()        #QUESTIONAIRE QUESTION VALUES STRUCTURE
        PrevIDType = "None"                                #TRACKING VARIABLE FOR THE PREVIOUS ID TYPE - SET AFTER EACH LINE ASSIGNMENT
        PrevListDefID = ""                                 #TRACKS ASSOCIATED LIST DEF ID FROM PREVIOUS LINE
        StateFlags = {}                                    #HASH USED TO TRACK STATE FLAGS
        QuestionLines= []			                       #TEXT FOR THE CURRENT QUESTION
        ListDefValueTrack = {}                             #TRACKING LIST DEF VALUES
        ListDefQuestionTrack = {}                          #TRACKING LIST DEF QUESTIONS
        #LOOP THROUG LINES 
        for LineText in Self.Lines:
            #IF TABLE PROCESS TABLE VALUES	
            if(re.search(r'<<TABLE>>',LineText)):	
                TableValues = QuestionaireTableTrack()
                StateFlags['IN_TABLE']=1
                StateFlags['IN_TABLE_DEF']=1       

                LineText = re.sub(r'<<TABLE>>','',LineText)         
            #CHECK FOR THE END OF TABLE	
            elif(re.search(r'<</TABLE>>',LineText)):				                
                TableValues=None
                StateFlags.pop('IN_TABLE' ,None)
                StateFlags['IN_POST_TABLE']=1
                StateFlags['IN_TABLE_DEF']=1                    

                LineText = re.sub(r'<<TABLE>>','',LineText)         
            #CHECK FOR BLANK LINE
            elif(QuestionaireMisc.ClearTags(LineText) == "" or not(re.search(r'\S',QuestionaireMisc.ClearTags(LineText)))):                
                StateFlags['IN_BLANK_LINE']=1  	                	
            else:
                QuestionLine+=1                      
                #REMOVE TILDE IF NOT ONLY VALUE
                if(re.search(r'^\s*~',QuestionaireMisc.ClearTags(LineText))):
                    NewQuestionFlag = 1
                    LineText = re.sub(r'~','',LineText)	
                #CHECK FOR FIRST BLOCK ENTRY OR RESET IF FIRST LINE IN QUESTION
                if(re.search(r'<<BLOCK=1>>',LineText) or  QuestionLine == 1 or NewQuestionFlag == 1):                    
                    BlockValues= QuestionaireBlockTrack()                          
                #LIST DEF FUNCTIONALTIY
                if(re.search(r'<<LIST_ID=',LineText)):
                    ListID = re.search(r'<<LIST_ID=(\S+)',LineText).group(1)                   
                    ListDefQuestionIndex=0
                    #UPDATE LIST DEF FLAGS IF FIRST LINE IN ASSOCIATED LIST DEF
                    if(ListID in ListDefValueTrack and (ListDefValues is None or ListDefValues != ListDefValueTrack[ListID])):
                        ListDefValues = ListDefValueTrack[ListID]                        
                        ListDefValues.Flags['BROKEN']=1
                        ListDefValues.AddBreak()
                    elif(ListDefValues is None or re.search(r'LIST_COUNT=1>',LineText) or QuestionLine == 1):									
                        ListDefValues = QuestionaireListDefTrack()         
                        ListDefValueTrack[ListID] = ListDefValues
                        ListDefQuestionIndex=1
                    #SET QUESTION LIST COUNTER
                    if(ListID in ListDefQuestionTrack):
                        ListDefQuestionIndex = ListDefQuestionTrack[ListID]+1
                    else:
                        ListDefQuestionIndex=1
                    CurrentCount = ListDefValues.NumericValues['LENGTH'] + 1                    
                    ListDefQuestionTrack[ListID] = ListDefQuestionIndex
                    LineText = re.sub(r'LIST_COUNT=(\d+)',r'LIST_COUNT=\1 LIST_INDEX='+str(CurrentCount)+' QUESTION_LENGTH='+str(ListDefQuestionIndex),LineText)
                    #LOOP THROUGH LINES AND UPDATE WITH NEW QUESTION LIST VALUE
                    for Line in QuestionLines:
                        Line.SetListDefQuestionTrack(ListID,ListDefQuestionIndex)
                else:   
                        ListDefValues = None                                                
                

                #REMOVE WEIRD CHARACTERS
                LineText = LineText.replace('','')
                                                  
                #CREATE LINE OBJECT        
                CurrentLine = QuestionaireLine(None, LineText, QuestionLine, PrevIDType ,ListDefValues,TableValues,BlockValues, None, None, StateFlags, None, Self.TrackOutput,Self.Configs, Self.FileName,Debug=Self.DebugMode)
                PrevIDType = CurrentLine.GetIDType()
                #UPDATE LIST DEF ID LABELING
                CurrentLine.NumericValuesText['LIST_DEF_ID_PREV'] = PrevListDefID 
                if(CurrentLine.NumericValuesText['LIST_DEF_ID_CURR'] !=""):
                    PrevListDefID = CurrentLine.NumericValuesText['LIST_DEF_ID_CURR']


                #CHECK IF NEW QUESTION IS NEEDED
                if(not(NewQuestionFlag)):
                    NewQuestionFlag = CurrentLine.CheckNewQuestion()	

                #IF NEW QUESTION IS NEEDED GENERATE PREVIOUS QUESTION AND RESET VARIABLES
                if(NewQuestionFlag):                    
                    #CHECK THAT ACTUAL LINES EXIST
                    if (len(QuestionLines)>0):
                        CurrentLine.SetValuesNewQuestions()
                        Self.Questions.append(QuestionaireQuestion(Self.FileName, QuestionLines, Self.Configs, Self.QuestionIDTrack, Self.TrackOutput, Debug=Self.DebugMode))
                    #RESET FLAGS
                    QuestionValues= QuestionaireQuestionTrack()    
                    NewQuestionFlag=0
                    QuestionLines=[]  
                    StateFlags={}
                    ListDefQuestionTrack={}
                    CurrentLine.ResetListDefQuestionTrack()
                    QuestionLine=0
                    PrevIDType = "None" 


                #ADD THIS STRUCTURE TO THE CURRENT QUESTION          
                

                #SKIP LINE ASSIGNMENT IF LIN IS A NEW QUESTION MARKER
                if(QuestionaireMisc.ClearTags(LineText) != "~" and QuestionaireMisc.ClearTags(LineText) != ""):                        
                    QuestionLines.append(CurrentLine)                           
                    CurrentLine.SetQuestionTrack(QuestionValues)  
                #RESET SINGLE LINE STATE FLAGS             
                StateFlags.pop('IN_TABLE_DEF' ,None)               
                StateFlags.pop('IN_BLANK_LINE' ,None)                     
                StateFlags.pop('IN_LIST_DEF' ,None)                         
        #ADD FINAL QUESTION
        if (len(QuestionLines)>0):
            Self.Questions.append(QuestionaireQuestion(Self.FileName, QuestionLines, Self.Configs, Self.QuestionIDTrack, Self.TrackOutput, Debug=Self.DebugMode))

    ############# Questionaire:BuildQuestions #############
    #FUNCTION:   Runs secondary functions to build questions
    #PARAMATERS: Lines
    #RETURNS:	 Nothing	
    def BuildQuestions (Self):  
        for Question in Self.Questions:
            Question.BuildQuestion()    

    ########################################################################################################
    ########################################### MISC FUNCTIONS #############################################
    ########################################################################################################

    ############# Questionaire:ReformatSegment #############
    #FUNCTION:   Reformats elements on a segment level, looking at other tags in the text segment definition
    #PARAMATERS: Text
    #RETURNS:	 Updated Text
    def ReformatSegment (Self, Text):	
        UpdatedSegment = ""	#UPDATED LINE TEXT			
        DisplayTags={}		#STRUCTURE USED TO HOLD FLAGS DENOTING FLAGS
        if (re.search(r'<w:b\/>',Text)): DisplayTags['BOLD']=1 
        if (re.search(r'<w:u w:val=\"single\"\/>',Text)): DisplayTags['UNDERLINE']=1
        if (re.search(r'<w:i\/>',Text)): DisplayTags['ITALIC']=1
        
        if(re.search(r'\<w\:rFonts w\:ascii\="([^"]+)"',Text)):
            if(re.search(r'\<w\:rFonts w\:ascii\="([^"]+)"',Text).group(1) != Self.Configs['DEFUALT_VALUES']["Font"]): DisplayTags['ALT_FONT']=1
        if(re.search(r'\<w\:sz w\:val="(\d+)"',Text)):
            if(re.search(r'\<w\:sz w\:val="(\d+)"',Text).group(1) != Self.Configs['DEFUALT_VALUES']["Size"]): DisplayTags['ALT_SIZE']=1
        if(re.search(r'<w:color w:val="([^"]+)"',Text)):
            if(re.search(r'<w:color w:val="([^"]+)"',Text).group(1) != Self.Configs['DEFUALT_VALUES']["Color"]): DisplayTags['ALT_COLOR']=1

        if('BOLD' in DisplayTags):      UpdatedSegment+='<<B>>' 
        if('UNDERLINE' in DisplayTags): UpdatedSegment+='<<U>>' 
        if('ITALIC' in DisplayTags):    UpdatedSegment+='<<I>>' 
        if('ALT_FONT' in DisplayTags):      UpdatedSegment+='<<F>>' 
        if('ALT_SIZE' in DisplayTags): UpdatedSegment+='<<S>>' 
        if('ALT_COLOR' in DisplayTags):    UpdatedSegment+='<<C>>' 

        #LOOK FOR TABS AND ADD TO PROCESSED TEXT
        Text = re.sub(r'<w\:tab\/><w\:t>','<w:t> <<T>> ', Text)
        Text = re.sub(r'<w\:tab\/>',r'<w:t> <<T>> <\/w:t>', Text)
        #LOOP THORUGH TEXT	
        for WTText in  re.findall(r'<w:t.*?>(.*?)<\/w:t>',Text):
            WTText = re.sub(r'<\\\/w:t><w:t','<w:t', WTText)
            WTText = re.sub(r'<w:t[^<]*>','',WTText) 				 #STRIP LEADING W:T TAG IF STILL PRESENT		
            UpdatedSegment += WTText	
            
        if('ALT_COLOR' in DisplayTags): UpdatedSegment += '<</C>>' 
        if('ALT_SIZE' in DisplayTags): UpdatedSegment += '<</S>>' 
        if('ALT_FONT' in DisplayTags): UpdatedSegment += '<</F>>' 		
        if('ITALIC' in DisplayTags): UpdatedSegment += '<</I>>' 
        if('UNDERLINE' in DisplayTags): UpdatedSegment += '<</U>>' 
        if('BOLD' in DisplayTags): UpdatedSegment += '<</B>>' 		
                
        #NEW LINETAG
        if(re.search(r'\%N\%.*<w:t.*?>', Text, re.IGNORECASE)):
            UpdatedSegment = '%N%' + UpdatedSegment 
    
        elif(re.search(r'%n%',Text, re.IGNORECASE)):
            UpdatedSegment +='%N%'           			
        return(UpdatedSegment)			 
        
    ############# Questionaire:ConvertCount #############
    #FUNCTION:   Converts provided count to specified type
    #PARAMATERS: Type, Count
    #RETURNS:	 Nothing
    def ConvertCount(Self,Type,Count):     
        #DECIMAL TYPE
        if(Type == 'decimalZero'):
            if (Count < 10): return '0' + str(Count)
            return Count;	
        #DECIMAL
        elif(Type == 'decimal'):
            return (Count)        
        #UPPER LETTER
        elif(Type == 'upperLetter'):
                return QuestionaireMisc.ConvertNumToID(Count).upper()           
        #UPPER ROMAN
        elif(Type == 'upperRoman'):
            return roman.toRoman(Count).upper()        
        #LOWER LETTER
        elif(Type == 'lowerLetter'):
            return QuestionaireMisc.ConvertNumToID(Count).lower();    
        #LOWER ROMAN
        elif(Type == 'lowerRoman'):
            return roman.toRoman(Count).lower()

    ############# Questionaire:GetID #############
    #FUNCTION:  Generates a computed ID for a list element
    #PARAMATERS: List ID,  Current List Level
    #RETURNS:	 Nothing
    def GetID(Self,ListID,ListLevel):
        ID=""					#COMPUTED ID 
        #print(Self.ListEntry)
        if(not ListID in Self.ListEntry or not ListLevel in Self.ListEntry[ListID]['LIST_STRUCTURE']):
            return("")
 
        IDText = Self.ListEntry[ListID]['LIST_STRUCTURE'][ListLevel]['LEVEL_TEXT']  #ID TEXT FOR THIS ID
        IDFormat = Self.ListEntry[ListID]['LIST_STRUCTURE'][ListLevel]['FORMAT']    #ID FORMAT FOR THIS ID

        #CHECK THAT FORMAT IS NOT BULLET
        if(IDFormat != 'bullet'):
            ID = IDText;
            #LOOP THROUGH EACH LAYER AND REPLACE ASSCOIATED		
            for NumberingIndex in range(1,len(Self.ListEntry[ListID]['LIST_STRUCTURE'])+1):	
                CurrentLayerVal = Self.ListEntry[ListID]['COUNTERS'][NumberingIndex -1]
                if ((NumberingIndex-1) < int(ListLevel)): CurrentLayerVal = CurrentLayerVal - 1
                ReplaceValue = Self.ConvertCount(IDFormat,CurrentLayerVal)
                if (ReplaceValue):
                    ID = re.sub(r'\%'+str(NumberingIndex),str(ReplaceValue),str(ID))
        #INCREMENT COUNTER
        Self.ListEntry[ListID]['COUNTERS'][int(ListLevel)]+=1       

        return (ID)
   
    ############# Questionaire:FillIDs #############
    #FUNCTION:   Loops through all questions looking for questions without ids and adds them.
    #PARAMATERS: Nothing
    #RETURNS:	 Nothing                
    def FillIDs(Self):
		#CLASS VARIABLE
        CurrentQuestionID=""							#ID OF THE CURRENT QUETION ID
        PreviousQuestionID=""							#ID OF THE CURRENT QUETION ID		IDUsed=set()									#HASH USED TO TRACK IDS USED
        IDCount=0										#COUNTER USED TO POPULATE MISSING IDS
        IDUsed = set()									#HASH USED TO TRACK IDS USED    

		#LOOP THROUGH QUESTIONS GENERATING A LIST OF ALL IDS USED	
        for Question in Self.Questions:
            #CHECK IF ID IS ALDREADY USED ANC CLEAR IF FOUND
            if(Question.QuestionID in IDUsed):
                Question.QuestionID=""
            if(Question.QuestionID != "" and Question.QuestionID != "Q"):
                IDUsed.add(Question.QuestionID)

        for Question in Self.Questions:
            PreviousQuestionID = CurrentQuestionID
            CurrentQuestionID=Question.QuestionID
            #CHECK FOR EMPTY ID
            if(CurrentQuestionID == 'Q' or CurrentQuestionID == ""):	
                #CHECK IF LIST DEFINTIN - ASSOCICITED FLAGS ARE NEVER SET WAS NEVER EXECUTED             
                if(PreviousQuestionID != ""):
                    defID = re.sub(r'Q','', PreviousQuestionID)
                    defID = re.sub(r"\D", "", defID)
                    if(defID == ""): defID = 0
                    #LOOP INCREMENTING COUNTER UNTIL UNSED QUESTION ID IS FOUND
                    while ('Q'+str(defID) in IDUsed):
                        defID = int(defID)+1
                    CurrentQuestionID='Q'+str(defID)
                    IDUsed.add('Q'+str(defID))
                    Question.QuestionID=CurrentQuestionID
                #OTHERWISE DEFAULT TO Q0
                else:
                    CurrentQuestionID="Q0"
                    Question.QuestionID="Q0"
                    IDUsed.add("Q0")

    ############# Questionaire:Export Text #############
    #FUNCTION:   Calls each question to return text, per export question. 
    #PARAMATERS: None
    #RETURNS:	 Text of all questions
    def ExportText(Self, OutputFile):	
        FileOutHandle = open(OutputFile, 'w')	#OUTPUT FILE HANDLE
        
        #CHECK FOR STARTING TEXT AND ADD TO EXPORT TEXT
        if ("START_TEXT" in Self.Configs["MAIN_CONFIG"].Config):                
            StartTextFileHandle = open(Self.Configs["MAIN_CONFIG"].Config["START_TEXT"], 'r')
            for TextLine in StartTextFileHandle:
                FileOutHandle.write(TextLine)
            StartTextFileHandle.close()
            
        #LOOP THROUGH QUESTIONS
        for Question in Self.Questions:
            Question.ExportQuestion(FileOutHandle)


        #CHECK FOR STARTING TEXT AND ADD TO EXPORT TEXT
        if ("END_TEXT" in Self.Configs["MAIN_CONFIG"].Config):                
            EndTextFileHandle = open(Self.Configs["MAIN_CONFIG"].Config["END_TEXT"], 'r')
            for TextLine in EndTextFileHandle:
                FileOutHandle.write(TextLine)
            EndTextFileHandle.close()
        
        FileOutHandle.close()    #CLOSE FILE HANDLE
