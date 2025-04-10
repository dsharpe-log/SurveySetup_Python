
import sys
import roman
import re


import QuestionaireMisc

from QuestionaireProcessCheck import QuestionaireProcessCheck

class QuestionaireSegment (QuestionaireProcessCheck):



    StateFlags = ['IN_LIST','IN_TEXT']
    NumericLineValues=['TEXT_LENGTH','SEGMENT_COUNT','SEGMENT_CURRENT']
    TextFlags=['TEXT_START_UNDERSCORE','TEXT_START_NUMBER','TEXT_START_SINGLE_CHAR','TEXT_START_CHECK','TEXT_START_TAB','TEXT_START_UNDERSCORE_NUMBER','TEXT_END_UNDERSCORE','TEXT_END_NUMBER','TEXT_END_SINGLE_CHAR','TEXT_END_CHECK','TEXT_END_TAB','TEXT_FIRST_WORD_NUM','TEXT_FIRST_WORD_LETTER','TEXT_FIRST_WORD_PERIOD','TEXT_FIRST_WORD_ID','TEXT_FIRST_WORD_IS_WORD','TEXT_FIRST_WORD_UNDERSCORE']
    FormatFlags = ['F','C','S','CAP','CRL','SQ','B','I','U']	  

    ##################################################################################################################
    ########################################## QUESTIONAIRE SEGMENT - INIT ###########################################
    ##################################################################################################################
    ############# QuestionaireSegment:Init #############
    #FUNCTION:   Object Constructor - Builds a Question object
    #PARAMATERS: Question Text Array, Segment Index, Previous Id Type, List Def Track, Table Track, Block Track, State Flags, Track Output, Track Output File, Configs, Word Document File Name
    #RETURNS:	 Nothing
    def __init__ (Self, Question, Text, SegmentIndex, SegmentCount, ListDefTrack, TableTrack, BlockTrack, QuestionTrack, ListTrack, TrackOutput, Configs, Debug=0):
        
        def PopulateValues(DefaultList):
            ReturnList={}
            for Key in DefaultList:
                ReturnList[Key] =0
            return (ReturnList)
        
        QuestionaireProcessCheck.__init__(Self, Question, Debug)	
        Self.ProcessType = "SEGMENT"
        
        Self.Text = Text
        Self.Type =""
        Self.Configs = Configs
        Self.TrackOutput = TrackOutput
        
        Self.TableTrack = TableTrack
        Self.BlockTrack = BlockTrack    
        Self.QuestionTrack = QuestionTrack
        Self.ListTrack = ListTrack
        Self.ListDefTrack = ListDefTrack

        Self.FormatFlags = PopulateValues(QuestionaireSegment.FormatFlags)
        Self.StateFlags = PopulateValues(QuestionaireSegment.StateFlags)
        Self.NumericValuesText = PopulateValues(QuestionaireSegment.NumericLineValues)
        Self.TextContentFlags = PopulateValues(QuestionaireSegment.TextFlags) 
        
        Self.NumericValuesText['SEGMENT_COUNT']= SegmentCount
        Self.NumericValuesText['SEGMENT_CURRENT']= SegmentIndex
        Self.NumericValuesText['TEXT_LENGTH']= len(QuestionaireMisc.ClearTags(Text))
        
        Self.SetType()
    ############# QuestionaireSegment:Set Type #############
    #FUNCTION:   Sets the segment type
    #PARAMATERS: Nothing
    #RETURNS:	 Nothing
    def SetType (Self):
        Line = Self.Text
        Self.FormatFlags = QuestionaireMisc.GetTextFormattingFlags(Line)
        
        UnformmatedLine = QuestionaireMisc.ClearFormatTags(Line) 
        CleanLine = QuestionaireMisc.ClearTags(Line) 

        FirstWord = CleanLine.split(' ')[0] 

        #STARING CHARACTER      
        Self.TextContentFlags['TEXT_START_UNDERSCORE'] = int(bool(re.search(r'^\s*_',CleanLine)))
        Self.TextContentFlags['TEXT_START_NUMBER'] = int(bool(re.search(r'^\s*\d+',CleanLine)))
        Self.TextContentFlags['TEXT_START_SINGLE_CHAR'] = int(bool(re.search(r'^\s*[a-z]\s',CleanLine,re.IGNORECASE)))
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
        Self.TextContentFlags['TEXT_FIRST_WORD_NUM'] = int(bool(re.search(r'[0-9]',FirstWord)))
        Self.TextContentFlags['TEXT_FIRST_WORD_LETTER'] = int(bool(re.search(r'/[A-Z]',FirstWord,re.IGNORECASE)))
        Self.TextContentFlags['TEXT_FIRST_WORD_PERIOD'] = int(bool(re.search(r'\.',FirstWord)))
        Self.TextContentFlags['TEXT_FIRST_WORD_ID'] = int(bool(re.search(r'^[A-Z]\.?[0-9]+(A-Z)*\.?',FirstWord,re.IGNORECASE)))
        Self.TextContentFlags['TEXT_FIRST_WORD_IS_WORD'] = int(bool(re.search(r'/[BCDFGHJKLMNPQRSTVWX]',FirstWord, re.IGNORECASE)) and bool(re.search(r'[AEIOUY]',FirstWord, re.IGNORECASE)) and not bool(re.search(r'[0-9]',FirstWord, re.IGNORECASE)))
        Self.TextContentFlags['TEXT_FIRST_WORD_UNDERSCORE'] = int(bool(re.search(r'_',FirstWord)))


        Weights = {}
        #BUILD WEIGHTS FOR EACH ELEMENT		
        if(Self.Debug == 2): 
            print("\n\n###############################################################")
            print("SEGMENT: "+Self.Text)   


            
        Weights["LOGIC"] =Self.CheckElements(Self.Configs['ID_SEGMENT_LOGIC'],Self.Text)
        Weights["TEXT"] = Self.CheckElements(Self.Configs['ID_SEGMENT_TEXT'],Self.Text)
        Weights["ID"] = Self.CheckElements(Self.Configs['ID_SEGMENT_ID'],Self.Text)

        if(Self.Debug == 2): 
            print("\n\nSELECTED:"+Self.Text)

        Self.Type = QuestionaireMisc.SelectHigh(Weights,Self.Debug)
        

        return(0)
