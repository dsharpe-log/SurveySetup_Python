import sys
import roman
import re

import QuestionaireMisc

from QuestionaireLine import QuestionaireLine
from QuestionaireProcessCheck import QuestionaireProcessCheck

class QuestionaireLogic (QuestionaireLine):
      
    ##################################################################################################################
    ########################################## QUESTIONAIRE LOGIC - INIT #############################################
    ##################################################################################################################
    ############# QuestionaireLogic:Init #############
    #FUNCTION:   Object Constructor - Builds a Question object
    #PARAMATERS: Question Text Array, Line Index, Previous Id Type, List Def Track, Table Track, Block Track, State Flags, Track Output, Track Output File, Configs, Word Document File Name
    #RETURNS:	 Nothing
    def __init__ (Self, Source, Line, List, Question, Text, Index, PrevIDType, ListDefTrack, TableTrack, BlockTrack, QuestionTrack, ListTrack, StateFlags, DefineFlags, TrackOutput, Configs, FileName, UpdateTracks=True, Debug=0, Logic=None):    
        QuestionaireLine.__init__(Self, Question, Text, Index, PrevIDType, ListDefTrack, TableTrack, BlockTrack, QuestionTrack, ListTrack, StateFlags, DefineFlags, TrackOutput, Configs, FileName, UpdateTracks, Debug)	
        Self.ProcessType = "LOGIC" 
        Self.Source = Source            #SOURCE OBJECT TYPE
        Self.Line = Line
        Self.List = List
        Self.LogicType = ""	#LOGIC TYPE

        if Logic is not None:
            for LogicValue in Logic.keys():
                Self.LogicCodes[LogicValue] = Logic[LogicValue]

        #MINOR CLEANUP OF LOGIC TEXT
        Self.Text = re.sub(r'^\s+', ' ', Self.Text)
        Self.Text = re.sub(r'\s+$', ' ', Self.Text)


        Self.ProcessLogic()
    ##################################################################################################################
    ###################################### QUESTIONAIRE LOGIC - PROCEESSING ##########################################
    ##################################################################################################################	
    ############# QuestionaireLogic:ProcessLogic #############
    #FUNCTION:   Executes functions
    #PARAMATERS: 
    #RETURNS:	 Nothing
    def ProcessLogic(Self):
        #UPDATE TEXT - KEWORD REPLACEMENT
        def UpdateText(Text, StripTags):
            #REPLACES _TEXT_ WITH THE PROVIDED LOGIC TEXT - ALLOWS FOR PROVIDED LOGIC TEXT TO BE INCLUDE IN QUESTION SETUP
            if("_TEXT_" in Text):                
                if(StripTags):
                    Text= Text.replace("_TEXT_",QuestionaireMisc.ClearTags(Self.Text))         
                else:
                    Text= Text.replace("_TEXT_",Self.Text)         
            return(Text)
    
        #UPDATE FIELD VALUES
        def UpdateField(Target,ValueStruct,StripTags,CleanCommands):
            if(not(Target is None)):
                for LogicValue in ValueStruct.keys():
                    WriteText = ValueStruct[LogicValue]
                    WriteText = UpdateText(WriteText,StripTags)
                    for Command in CleanCommands:
                        WriteText = re.sub(Command, '', WriteText)

                    #CHECK IF VALUE IS AND INC REFERENCE
                    if(WriteText in Self.Configs['MAIN_CONFIG'].Config['INC_VALUES']):
                        Target.LogicCodes[LogicValue] = Self.Configs['MAIN_CONFIG'].Config['INC_VALUES'][WriteText]
                    else:
                        Target.LogicCodes[LogicValue] = WriteText

        #BUILD WEIGHTS FOR EACH ELEMENT
        if(Self.Debug == 2): 
            print("\n\n###############################################################")
            print("\nLOGIC IDENTIFIER\n\n")
            print("LOGIC: "+Self.Text)   
            print(Self.Source)
        #BUILD WEIGHTS FOR EACH ELEMENT
        for Element in Self.Configs['MAIN_CONFIG'].Config['LOGIC']:
            StripTags = 0   #FLAG DENOTING CLEANUP ON TAGS UPON USE
            CleanCommands = []  #CLEAN COMMANDS
            if('STRIP_TEXT_TAGS' in Element):
                StripTags = 1   
            if('CLEAN_TEXT' in Element):
                CleanCommands = Element['CLEAN_TEXT']
            #CHECK TYPE AGAINST LOGIC EXECUTION TYPE     
            if(("LOGIC_QUESTION" in Element and Self.Source == "QUESTION") or ("LOGIC_LIST" in Element and Self.Source == "LIST") or ("LIST_TEXT" in Element and Self.Source == "LIST_TEXT") or ("QUESTION_TEXT" in Element and Self.Source == "QUESTION_TEXT")):
                Pass = 0
                LogicID = Element['ID']
                if(Self.Debug == 2):  print("CHECKING:" + LogicID)                
                if LogicID in Self.Configs['LOGIC_CONFIG']:
                    Weight  = Self.CheckElements(Self.Configs['LOGIC_CONFIG'][LogicID],Self.Text)
                    if(Weight > int(Self.Configs['LOGIC_CONFIG'][LogicID].Config['THRESHOLD'])):
                        Pass = 1
                #CHECK IF WORD IN TEXT
                elif('WORDS' in Element):
                    for Word in Element['WORDS']:
                        if(Word in Self.Text):
                          Pass=1  
                #CHECK IF UNIQUE
                if('QUESTION_UNIQUE' in Element and Element['ID'] in Self.Question.LogicCodes):
                    Pass = 0
                if(Pass):
                    if(Self.Debug == 2): 
                        print("ADDED LOGIC")       
                    Self.LogicType = LogicID
                    #LINE VALUES                
                    if('LINE_VALUE' in Element):
                        UpdateField(Self.Line,Element['LINE_VALUE'],StripTags,CleanCommands)
                        Self.Line.LogicCodes[Element['ID']] = 1
                    #LIST VALUES
                    if('NEXT_LINE_VALUE' in Element):            
                        Self.Question.AddNextLineLogic(Element['NEXT_LINE_VALUE'])    
                    #INSERT VALUES INLINE
                    if('LINE_INLINE_TEXT' in Element):
                        TextValue = UpdateText(Element['LINE_INLINE_TEXT'],StripTags)
                        if(Self.Source == "QUESTION"):
                            Self.Question.SetInlineText(TextValue)
                        else:
                            Self.Line.SetInlineText(TextValue)
                    #LIST VALUES
                    if('LIST_VALUE' in Element and not(Self.List is None)):
                        UpdateField(Self.List,Element['LIST_VALUE'],StripTags,CleanCommands)                 
                        Self.List.LogicCodes[Element['ID']] = 1
                    if('NEXT_LIST_VALUE' in Element):                               
                        Self.Question.AddNextListLogic(Element['NEXT_LIST_VALUE'])
                    #LIST ID                    
                    if('LIST_ITEM_ID' in Element):                        
                        Self.Line.ListItemID = Element['LIST_ITEM_ID']
                    #LIST PREPPEND TEXT
                    if('LIST_ITEM_PREPEND_TEXT' in Element):
                        TextValue = Element['LIST_ITEM_PREPEND_TEXT']
                        TextValue = TextValue.replace("\s"," ") 
                        Self.Line.ListPrepend.append(TextValue)        
                    #LIST APPEND TEXT
                    if('LIST_ITEM_APPEND_TEXT' in Element):
                        TextValue = Element['LIST_ITEM_APPEND_TEXT']
                        TextValue = TextValue.replace("\s"," ") 
                        Self.Line.ListAppend.append(TextValue)                    
                    #LIST APPEND TEXT
                    if('LIST_ITEM_CLEAR' in Element):
                        Values = Element['LIST_ITEM_CLEAR']
                        Self.Line.ListClear = Self.Line.ListClear + Values
                    #QUESTION VALUES
                    if('QUESTION_VALUE' in Element):
                        UpdateField(Self.Question,Element['QUESTION_VALUE'],StripTags,CleanCommands)
                        Self.Question.LogicCodes[Element['ID']] = 1
                    #INC VALUE
                    if('INC_VALUES' in Element):
                        for Value in Element['INC_VALUES']:
                            Self.Configs['MAIN_CONFIG'].Config['INC_VALUES'][Value] += 1      
                    #SET_QUESTION_ID
                    if('SET_QUESTION_ID' in Element):
                        Text = QuestionaireMisc.ClearTags(Self.Text)
                        #TAG IMPLISES RECALL FROM TEXT
                        for Command in CleanCommands:
                            Text = re.sub(Command, '', Text)                        
                        Self.Question.ID =Text
                    #LIST ITEM ID 
                    #    Self.List.ListItemID = Element['LIST_ITEM_ID']          
        
                    #if('LIST_ITEM_ID' in Element):  
    ##################################################################################################################
    ##################################### QUESTIONAIRE LOGIC - SET VALUES ############################################
    ##################################################################################################################	
    ############# QuestionaireLogic:SetType #############
    #FUNCTION:   DETERMINES THE TYPE OF THE QUESTION
    #PARAMATERS: 
    #RETURNS:	 Nothing
    #def SetType(Self):

        
