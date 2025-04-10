import sys, getopt
import os
import zipfile

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from Questionaire import Questionaire

########################################################################################################
############################################# SURVEY SETUP #############################################
########################################################################################################
#DESCRIPTION: Provided a questionnaire file name invokes the Parse Questionnaire library with a template, 
#default or designated by switch to build a textfile formatted for import.  
#PARAMATERS: Questionnaire File Name,  Text File Name
#USAGE: SurveySetup -d -l -t Template  Word_Questionaire_File_Name Text_Output_File_Name )
#SWITCHES
#	-d = Debug Mode
#	-l = Lists available Templates
#	-t = Designate specific Template
#	-x = Export Tracking Data 

#TO DO: 
#	- Might want to look at using list level in List Def tag for decision making - currently ignored


#LOGIC VARIABLES
#	VALUE TRACK (SETS FOR BLOCKS, LISTS, LIST DEFS, TABLES. QUESTIONS)
#		NUMERIC VALUES: 'LENGTH','LENGTH_AVERAGE','LENGTH_STD_DEV','BREAK_COUNT'
#
#   LINE VALUES
#	LIST DEF TRACKING VALUES

#CHANGE LOG:  

########################################################################################################
####################################### CONSTANTS AND VARIABLES ########################################
########################################################################################################

QuestionaireFileName=""																	#QUESTIONAIRE FILE NAME
TextFileName = ""																		#FILE NAME OF THE OUTPUT FILE
StudyQuestionaire = "" 																	#QUESTIONAIRE DATA STRUCTURE
Configs = ""																			#LIST OF AVAILABLE CONFIG
ConfigDir = r'K:\Programs\Development\SurveySetup Ver2/CONFIGS/'								#DIRECTORY CONTAINING CONFIG FILES                
ConfigFile = r'K:\Programs\Development\SurveySetup Ver2/CONFIGS/QFI_IMPORT_DEFAULT.config'		#CONFIG FILE NAME

#DEBUGGING
TrackOutput = 0																			#BOOLEAN DENOTING THAT TRACKOUTPUT IS ACTIVE
TrackOutputFile = "" 																	
DebugMode = 0																			#DEBUG MODE	

#PROGRAM PARAMATERS
argv = sys.argv[1:]

#FILE TO TRACK OUTPUT
OptionsList={}		#OPTION LIST
ConfigList={}		#LIST OF PRIMARY PLATFORM CONFIGS

#LOOP THROUGH OPTIONS POPULATING OPTIONLIST
Options, Arguments = getopt.getopt(argv,"dxlt:",["Template="])		
for Option, Argument in Options:
	OptionsList[Option] = Argument   

#CHECK FOR TEMPLATE OR LIST OPTION - BUILD LIST OF PRIMARY PLATFORM CONFIGS
if ('-l' in OptionsList or '-t' in OptionsList):		
	#LOOP THROUGH THE DIRECTOR
	for ConfigFileName in os.listdir(ConfigDir):
		ConfigFileName = os.path.join(ConfigDir, ConfigFileName)
		#CHECK IF A FILE
		if os.path.isfile(ConfigFileName):
			with open(ConfigFileName) as FileHandler:					
				Line = FileHandler.readline()
				#CHECK IF FIRST LINE IS IMPORTATION CONFIG
				if('IMPORTATION_CONFIG' in Line):
					ConfigName = ConfigFileName
					ConfigName = ConfigName.replace(ConfigDir,'')
					ConfigName = ConfigName.replace("_IMPORT.config",'')
					ConfigList[ConfigName] = ConfigFileName

#IF LIST FLAG, LIST ALL TEMPLATES AND EXIT
if ('-l' in OptionsList):
	#LOOP THROUGH AND PRINT EACH CONFIG
	for Config in ConfigList.keys():
		print (Config)
#IF NOT LIST BEGIN QUESTIONAIRE PROCESSING
else:
	#CHECK FOR VALID PARAMATERS
	if (len(Arguments) <2):
		print ("USAGE: SurveySetup -l -t Template  Word_Questionaire_File_Name Text Output_File_Name \n\t-l: List available Templates\n\t-t: Designate a specific template")		
	else:	
		QuestionaireFileName = Arguments[0]
		TextFileName = Arguments[1]
		
		#BUILD TRACKING OUTPUT FILE
		if('-x' in OptionsList):
			TrackOutput=1
			TrackOutputFile = QuestionaireFileName.replace('.docx','')
		#DEBUG MODE
		if ('-d' in OptionsList):
			DebugMode = 1

		#CHECK IF TEMPLATE HAS BEEN SELECTED
		if('-t' in OptionsList):
			#CHECK IF SELECTED CONFIG HAS BEEN DEFINED
			if (OptionsList['-t'] in ConfigList):
				ConfigFile = ConfigList[OptionsList['-t']]
			#IF DENOTED TEMPLATE DOESN'T EXIST - ERROR AND LIST AVAILABLE CONFIG
			else:
				print ("Error - Unrecognized Template selected. "+OptionsList['-t']+" \n Available Tempates:")
				#LOOP THROUGH AND PRINT EACH CONFIG
				for Config in ConfigList.keys():
					print (Config)
		if(not(zipfile.is_zipfile(QuestionaireFileName))):
			raise Exception("Provided questionaire doesn't seem to be a Word Document.")

		#BUILD QUESTIONAIRE OBJECT
		StudyQuestionaire = Questionaire(QuestionaireFileName, ConfigFile, TrackOutput, TrackOutputFile, DebugMode)

		#PRINT TO TEXT FILE
		if (StudyQuestionaire.IsExcelExport):
			StudyQuestionaire.ExportExcel(TextFileName)	
		else:
			StudyQuestionaire.ExportText(TextFileName)		


