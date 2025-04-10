import re
import sys
import os.path
import QuestionaireMisc
from DConfig import DConfig
from Command import Command

########################################################################################################
######################################## EXPORT EXCEL TEMPLATE #########################################
########################################################################################################

########################### EXPR.pl ###########################
#DESCRIPTION: 
#TODO:
#CHANGE LOG:

class QuestionaireExportExcelTemplate():
	CONFIG_COMMANDS = {	#Keywords available in config
		'TRACK_FORMATS': 1,
		'MULTI_MENTION': 1,
		'IMPORTATION_CONFIG':1,
		'EXCEL_EXPORT':1,
		'BLOCK_DEF': 1,
	}
	CONFIG_COMMAND_FIELDS={}
	CONFIG_COMMANDS_REQUIRED_FIELDS={}

############# SurveySetup:Export Excel Block #############
#FUNCTION:   Provided a Config file hash processes it as per programming found within using 
#PARAMATERS: Config, Lookup Structure 
#RETURNS:	 
	def ExportExcelBlock(Self, Config, Question, Index=-1):
		#LOOP THROUGH LINES
		for Line in Config['LINES']:
			#CHECK IF NEXT LINE IS A BLOCK
			if('BLOCK_DEF' in Line):
				Preceed=1		#FLAG DENOTING IF CONDITION MET FOR BLOCK
				#CHECK FOR CONDITION
				if('CONDITION' in Line):
					if(re.search(r"<<(.*)>>",Line['CONDITION'])):
						NewCommand = Command(None, re.search(r"<<(.*)>>",Line['CONDITION']).group(1), None) #COMMAND DATA STRUCTURE
						IDList = NewCommand.GetIDList()														#LIST OF IDS USED BY THIS COMMAND
						IDLookup = {}																		#LOOKUP STRUCTURE USED TO RUN THIS COMMAND
						#BUILD ID LOOKUP TABLE
						for ID in IDList:
							IDLookup[ID] = Question.GetIdentifierValue(ID, Index)
						#CHECK CONDITION TO FLAG PRECCEED, FAILURE IS LIKELY DUE TO UNDIFINED FLAG AND WILL ALSO FAIL
						if(not NewCommand.Execute(None, IDLookup)):
							Preceed=0
					#IF LINE CONDITION IS NOT FORMATED WITH <<>> DIE
					else:
						raise Exception("Misformatted Condition missing wrapping <<>>\n")
				#CHECK IF SHOULD PRECEED
				if (Preceed):
					#CHECK FOR LOOP
					if('REPEAT' in Line):	
						ListIndex=0
						#LOOP THROUGH SPEFICIED ITEM
						for ListItem in Question.GetList(Line['REPEAT']):
							Self.ExportExcelBlock(Line, Question, ListIndex)
							ListIndex+=1
					#IF NO LOOP PRINT TEXT
					else:
						Self.ExportExcelBlock(Line, Question, Index)
			#OTHERWISE WRITE THE LINE
			else:
				#LOOP THORUGH ITEMS IN LINE STRUCTURE
				for LineItem in Line.keys():
					WriteValue = Line[LineItem]
					Col = Self.HEADING_LOOKUP[LineItem.upper()]	#COLUMN TO WRITE TO
					#CHECK IF PROCESSING REQUIRED
					if(re.search(r"<<(.*)>>",WriteValue)):
						NewCommand = Command(None, re.search(r"<<(.*)>>",WriteValue).group(1), None)
						IDList = NewCommand.GetIDList()														#LIST OF IDS USED BY THIS COMMAND
						IDLookup = {}																		#LOOKUP STRUCTURE USED TO RUN THIS COMMAND
						#BUILD ID LOOKUP TABLE
						for ID in IDList:
							IDLookup[ID] = Question.GetIdentifierValue(ID, Index)
						WriteValue = NewCommand.Execute(None, IDLookup)
					Self.OUTSHEET.write(Self.Row,Col,WriteValue)
				Self.Row+=1

	############# SurveySetup:AddLogic #############
	#FUNCTION:   Exports the question to Excel based on the appropriate template
	#PARAMATERS: Question
	#RETURNS:	 Nothing
	def ExportExcel(Self, Question, Config):
		QuestionConfig = Config['QTYPE_EXPORT_CONFIG'][Question['QUESTION_TYPE']] #CONFIG FOR THE CURRENT QUESTION
		Self.ExportExcelBlock(QuestionConfig['Config'], Question) #EXPORT THE BLOCK DEFINIEND BY THE CONFIG

############# SurveySetup:Write Excel #############
	#FUNCTION:   Writes a provided structure to provided excel worksheet
	#PARAMATERS: Output structure File
	#RETURNS:	 Nothing
	def WriteExcelBlock(Self,ConfigFileName):
		#CHECK THAT CONFIG FILE EXISTS
		if(not(os.path.isfile(ConfigFileName))):
			raise Exception("Config file not found. Name: "+ConfigFileName)
		Config = DConfig(ConfigFileName, Self.CONFIG_COMMANDS, Self.CONFIG_COMMAND_FIELDS, Self.CONFIG_COMMANDS_REQUIRED_FIELDS, 1) #BUILD CONFIG STRUCTURE		
		#LOOP THROUGH LINES
		for Line in Config['LINES']:
			#LOOP THROUGH ITEMS IN LINE STRUCTURE
			for LineItem in Line.keys():
				WriteValue = Line[LineItem]	#VALUE TO WRITE
				Col = Self.HEADING_LOOKUP[LineItem.upper()]	#COLUMN TO WRITE TO
				#CHECK IF COMPUTED FORMAT
				if(re.search(r"<<(.*)>>",WriteValue)):
					FormatText = re.search(r"<<(.*)>>",WriteValue).group(1)	#TEXT FOR PROCESSING
					#CHECK FOR VALUES
					if(FormatText in Self.QUESTIONAIRE):
						WriteValue = Self.QUESTIONAIRE[FormatText]
				Self.Outsheet.write(Self.Row,Col,WriteValue)	#WRITE TO EXCEL SHEET
			Self.Row+=1	#INCREMENT ROW

	########################################################################################################
	############################################## CONSTRUCTOR #############################################
	########################################################################################################
	def _init_ (Self, FileName, Questionnaire):
		Self.FileName = FileName				#FILE NAME	
		Self.Questionnaire = Questionnaire #QUESTIONAIRE STRUCTURE
		Self.Outsheet = None					#WORKSHEET TO OUTPUT TO
		Self.Row=0								#INDEX CONTROLLED ROW TO OUTPUT TO
		Self.HeadingLookup={}					#STRUCTURE USED TO LOOKUP HEADINGS -> ROWS


	########################################################################################################
	########################################### EXTERNAL FUNCTIONS #########################################
	########################################################################################################

	############# SurveySetup:Export #############
	#FUNCTION:   Runs the saved binary execution tree and runs it sourcing data from the provided Question structure
	#PARAMATERS: Question Structure
	#RETURNS:	 Question Text
	def Export (Self):
		Config = Self.Questionnaire.Configs['MAIN_CONFIG'].Config	#MAIN CONFIGURATION FILE

		OutWorkBook = None		#WORKBOOK FOR EXPORT
		HeadingList = None		#LIST OF HEADINGS
		OutWorksheet = None		#WORKSHEET
		BoldFormat = None		#FORMAT STRUCTURE
		Col=0					#CURRENT COLUMN




		

	sub Export {
		my $Self = $_[0];				#CLASS VARIABLE	
		
		my $Config =  $Self->{QUESTIONAIRE}->{CONFIGS}->{MAIN_CONFIG}->{Config};

		#BUILD WORKBOOK
		my $OutWorkbook;		#WORKBOOK FOR EXPORT	
		my $HeadingList;		#LIST OF HEADINGS	
		my $OutWorksheet;		#WORKSHEET
		my $BoldFormat;			#FORMAT STRUCTURE	
		my $Col=0;				#CURRENT COLUMN
		
		$OutWorkbook = Excel::Writer::XLSX->new($Self->{FILE_NAME});
		$HeadingList = $Config->{EXPORT_HEADINGS};
		#BUILD WORKSHEET
		
		$Self->{OUTSHEET} =  $OutWorkbook->add_worksheet("Questionnaire");
		#BOLD FORMAT
		$BoldFormat = $OutWorkbook->add_format();
		$BoldFormat->set_bold(); 
		#LOOP THROUGH HEADINGS
		foreach my $Heading (@$HeadingList){		
			$Self->{OUTSHEET}->write($Self->{ROW},$Col,$Heading->{'NAME'},$BoldFormat);
			$Self->{OUTSHEET}->set_column($Col,$Col,$Heading->{'WIDTH'});
			$Self->{HEADING_LOOKUP}->{uc($Heading->{'NAME'})} = $Col;
			$Col++;
		}
		
		#INCREMENT ROW
		$Self->{ROW}++;	
		$Self->__WriteExcelBlock($Config->{START_TEXT});
		
		#LOOP THROUGH QUESTIONS
		foreach my $Question (@{$Self->{QUESTIONAIRE}->{QUESTIONS}}){		
			$Self->__ExportExcelQuestion($Question, $Self->{QUESTIONAIRE}->{CONFIGS});		
		}
		
		$Self->__WriteExcelBlock($Config->{END_TEXT});
		$OutWorkbook->close();
		
	}

