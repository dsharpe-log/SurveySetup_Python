
import QuestionaireMisc as Misc
from QuestionaireList import QuestionaireList 
from QuestionaireList import QuestionaireListItem

print("\nTesting: ConvertNumToID")
print("1 - "+Misc.ConvertNumToID(1))
print("27 - "+Misc.ConvertNumToID(27))
print("36 - "+Misc.ConvertNumToID(36))
print("52 - "+Misc.ConvertNumToID(52))

print("\nTesting: ConvertIDToNum")
print("A - "+str(Misc.ConvertIDToNum('A')))
print("AA - "+str(Misc.ConvertIDToNum('AA')))
print("AZ - "+str(Misc.ConvertIDToNum('AZ')))
print("BG - "+str(Misc.ConvertIDToNum('BG')))

print("\nTesting: ClearFormatTags")
print ("<<B>>SCREENER<</B>><<N>> <<T>> What is your gender?<<N>>")
print (Misc.ClearFormatTags("<<B>>SCREENER<</B>><<N>> <<T>> What is your gender?<<N>>"))
print ("<<LIST_ID=2 LIST_LEVEL=0 ID_VALUE=12.>>Do not reside in Canada <<T>> [TERMINATE]")
print (Misc.ClearFormatTags("<<LIST_ID=2 LIST_LEVEL=0 ID_VALUE=12.>>Do not reside in Canada <<T>> [TERMINATE]"))
print ("<<T>> For this survey, we would like to better understand your general <<B>>media habits and usage<</B>>.<<N>>Approximately how many hours in an average week do you spend doing each of the following?<<N>>")
print (Misc.ClearFormatTags("<<T>> For this survey, we would like to better understand your general <<B>>media habits and usage<</B>>.<<N>>Approximately how many hours in an average week do you spend doing each of the following?<<N>>"))

print("\nTesting: ClearTags")
print ("<<B>>SCREENER<</B>><<N>> <<T>> What is your gender?<<N>>")
print (Misc.ClearTags("<<B>>SCREENER<</B>><<N>> <<T>> What is your gender?<<N>>"))
print ("<<LIST_ID=2 LIST_LEVEL=0 ID_VALUE=12.>>Do not reside in Canada <<T>> [TERMINATE]")
print (Misc.ClearTags("<<LIST_ID=2 LIST_LEVEL=0 ID_VALUE=12.>>Do not reside in Canada <<T>> [TERMINATE]"))
print ("<<T>> For this survey, we would like to better understand your general <<B>>media habits and usage<</B>>.<<N>>Approximately how many hours in an average week do you spend doing each of the following?<<N>>")
print (Misc.ClearTags("<<T>> For this survey, we would like to better understand your general <<B>>media habits and usage<</B>>.<<N>>Approximately how many hours in an average week do you spend doing each of the following?<<N>>"))

print("\nTesting: GetTextFormatting")
print ("<<B>>TEXT<</B>>")
print (Misc.GetTextFormatting("<<B>>TEXT<</B>>"))
print ("<<B>><<I>>Text<</I>><</B>>")
print (Misc.GetTextFormatting("[{<<B>><<I>>Text<</I>><</B>>}]"))
print ("<<U>>TEXT<</U>>")
print (Misc.GetTextFormatting("<<U>>TEXT<</U>>"))

print("\nTesting: SegmentText")
print ("S5. <<T>> Which of the following <<B>>best describes<</B>> your <<B>>main ancestry<</B>> or <<B>>ethnic background<</B>>? Please select one option only.")
print (Misc.SegmentText("S5. <<T>> Which of the following <<B>>best describes<</B>> your <<B>>main ancestry<</B>> or <<B>>ethnic background<</B>>? Please select one option only."))
print ("ASK IF MORE THAN ONE SELECTED AT S8 [SHOW ONLY THOSE SELECTED AT S8], OTHERWISE FORCE PUNCH S9', S9. <<T>> And, which of the following language(s) is your <<B>>mother tongue<</B>> (that is the language you grew up speaking from early childhood)?")
print (Misc.SegmentText("ASK IF MORE THAN ONE SELECTED AT S8 [SHOW ONLY THOSE SELECTED AT S8], OTHERWISE FORCE PUNCH S9', S9. <<T>> And, which of the following language(s) is your <<B>>mother tongue<</B>> (that is the language you grew up speaking from early childhood)?"))
print ("S10. <<T>> Do you currently have a <<B>><<U>>paid<</U>><</B>> cable, satellite or IPTV television package (for example, Bell, Rogers, EastLink, Shaw, Telus, TV Box, Ethnic IPTV, etc.)?'")
print (Misc.SegmentText("S10. <<T>> Do you currently have a <<B>><<U>>paid<</U>><</B>> cable, satellite or IPTV television package (for example, Bell, Rogers, EastLink, Shaw, Telus, TV Box, Ethnic IPTV, etc.)?'"))
print ("G1. <<T>> We would now like to get your opinions <<B>>in general<</B>> and <<B>><<U>>not<</U>><</B>> those related to television programming or media.")
print (Misc.SegmentText("G1. <<T>> We would now like to get your opinions <<B>>in general<</B>> and <<B>><<U>>not<</U>><</B>> those related to television programming or media."))
print ("( ) Democratic primary TERMINATE")
print (Misc.SegmentText("( ) Democratic primary TERMINATE"))
print ("– THANK &amp; TERMINATE*")
print (Misc.SegmentText("– THANK &amp; TERMINATE*"))
print ("(DO NOT READ) DK/REF TERMINATE")
print (Misc.SegmentText("(DO NOT READ) DK/REF TERMINATE"))
print ("(DON'T KNOW = 0000) (YEAR MUST BE FOUR DIGITS) (TERMINATE IF BORN 2005 OR LATER)")
print (Misc.SegmentText("(DON'T KNOW = 0000) (YEAR MUST BE FOUR DIGITS) (TERMINATE IF BORN 2005 OR LATER)"))
print ("[e.g. Teststuff] Stuf. (I like<<T>> More stuff)")
print (Misc.SegmentText("[e.g. Teststuff] Stuf. (I like<<T>> More stuff)"))
print ("TEst 1<<t>> TEST 2<<T>>{test 3  <<T>> TEST 4} THIS IS AN AWSOME TEST Testing is neat")
print (Misc.SegmentText("TEst 1<<t>> TEST 2<<T>>{test 3  <<T>> TEST 4} THIS IS AN AWSOME TEST Testing is neat"))
print ("ASK IF MORE THAN ONE SELECTED AT S8 [SHOW ONLY <<B>>THOSE SELECTED<</B>> AT S8], OTHERWISE FORCE PUNCH S9', S9.")
print (Misc.SegmentText("ASK IF MORE THAN ONE SELECTED AT S8 [SHOW ONLY <<B>>THOSE SELECTED<</B>> AT S8], OTHERWISE FORCE PUNCH S9', S9.")) 
print ("ASK IF MORE THAN ONE SELECTED AT S8 [SHOW ONLY. THOSE SELECTED AT S8], OTHERWISE FORCE PUNCH S9', S9.")
print (Misc.SegmentText("ASK IF MORE THAN ONE SELECTED AT S8 [SHOW ONLY. THOSE SELECTED AT S8], OTHERWISE FORCE PUNCH S9', S9.")) 
print ("Where have you seen, read or heard about the <<B>>Canada Dental Benefit<</B>>?  Please select all that apply.  <<B>>[PN:  ROTATE ITEMS.  OTHER SPECIFY ANCHORED AT END OF LIST.]<</B>>")
print (Misc.SegmentText("Where have you seen, read or heard about the <<B>>Canada Dental Benefit<</B>>?  Please select all that apply.  <<B>>[PN:  ROTATE ITEMS.  OTHER SPECIFY ANCHORED AT END OF LIST.]<</B>>"))



print("\nTesting: SelectHigh")
print([1,2,5,6,7,8,3,4])
print(Misc.SelectHigh([1,2,5,6,7,8,3,4]))
print({'A':34,'B':36,'k':14})
print(Misc.SelectHigh({'A':34,'B':36,'k':14}))

print ("\nTesting: GetWords")
print ("S5. <<T>> Which of the following <<B>>best describes<</B>> your <<B>>main ancestry<</B>> or <<B>>ethnic background<</B>>? Please select one option only.")
print (Misc.GetWords("S5. <<T>> Which of the following <<B>>best describes<</B>> your <<B>>main ancestry<</B>> or <<B>>ethnic background<</B>>? Please select one option only."))

print ("\nTesting: KeywordID")
Keyword =["Do you",  "currently", "paid", "satellite", "IPTV television"]
print ("S5. <<T>> Which of the following <<B>>best describes<</B>> your <<B>>main ancestry<</B>> or <<B>>ethnic background<</B>>? Please select one option only.")
print(Misc.KeywordID("S5. <<T>> Which of the following <<B>>best describes<</B>> your <<B>>main ancestry<</B>> or <<B>>ethnic background<</B>>? Please select one option only.", Keyword))
print ("S10. <<T>> Do you currently have a <<B>><<U>>paid<</U>><</B>> cable, satellite or IPTV television package (for example, Bell, Rogers, EastLink, Shaw, Telus, TV Box, Ethnic IPTV, etc.)?'")
print(Misc.KeywordID("S10. <<T>> Do you currently have a <<B>><<U>>paid<</U>><</B>> cable, satellite or IPTV television package (for example, Bell, Rogers, EastLink, Shaw, Telus, TV Box, Ethnic IPTV, etc.)?'", Keyword))
print ("S10. <<T>>  <<B>><<U>>paid<</U>><</B>>?'")
print(Misc.KeywordID("S10. <<T>>  <<B>><<U>>paid<</U>><</B>>?'", Keyword))
print("<<B>>SCREENER<</B>><<N>> <<T>> What is your gender?<<N>>")
print(Misc.KeywordID("<<B>>SCREENER<</B>><<N>> <<T>> What is your gender?<<N>>", Keyword))
print("<<B>>SCREENER<</B>><<N>> <<T>> What is your gender?<<N>> Do you")
print(Misc.KeywordID("<<B>>SCREENER<</B>><<N>> <<T>> What is your gender?<<N>> Do you", Keyword))

print ("\nTesting: GetPrevCode")
print ("A")
print (Misc.GetPrevCode("A"))
print ("1")
print (Misc.GetPrevCode("1"))
print ("Z")
print (Misc.GetPrevCode("Z"))
print ("99")
print (Misc.GetPrevCode("99"))

print ("\nTesting: GetNextCode")
print ("A")
print (Misc.GetNextCode("A"))
print ("1")
print (Misc.GetNextCode("1"))
print ("AB")
print (Misc.GetNextCode("AB"))
print ("3245")
print (Misc.GetNextCode("3245"))

print ("\nTesting: KeywordSearch")
Keyword ={"select one option":1,"appropriate":1,"currently":1,"Please":1,"Are you":1,"Currently":1,"Prefer not":-1,"to answer":-1}
print("Which of the following best describes your main ancestry or ethnic background? Please select one option only.")
print(Misc.KeywordSearch("Which of the following best describes your main ancestry or ethnic background? Please select one option only.",Keyword))
print("Please select the province in which you live.")
print(Misc.KeywordSearch("Please select the province in which you live.",Keyword))
print("Please check the appropriate boxes.")
print(Misc.KeywordSearch("Please check the appropriate boxes.",Keyword))
print("Are you currently")
print(Misc.KeywordSearch("Are you currently",Keyword))
print("What is your current marital status? ")
print(Misc.KeywordSearch("What is your current marital status? ",Keyword))
print("Prefer not to answer")
print(Misc.KeywordSearch("Prefer not to answer",Keyword))

print ("\nTesting: GetNumbers")
print("1 xasdf 3 asdfxzcv 345 sadfasdfa 1 asdfasdf 10 asdfasdf 34")
print(Misc.GetNumbers("1 xasdf 3 asdfxzcv 345 sadfasdfa 1 asdfasdf 10 asdfasdf 34"))
#NOT SURE WHAT THIS IS FOR


print ("\nTesting: RunReformat")
#TO DO
#def RunReformat (Text, Config):



def AddItemsList(Values):
    List = QuestionaireList(1, "", "", "")
    for Value in Values:
        List.ListItems.append(QuestionaireListItem(len(List.ListItems),Value,"","",0))
    return(List)

def PrintValues(List):
    for Value in List.ListItems:
        print(Value.Text)
        
print("\n\nTESTING LISTS")
#QUESTIONAIRE LIST FUNCTIONS
ValuesListAA = ["VERY GOOD","GOOD","NEUTRAL","BAD","VERY BAD"]
ValuesListBA = ["1","2","3","4","5"]
ValuesListBB = ["1","3","5"]
ValuesListBC = ["1","5"]

ListAA = AddItemsList(ValuesListAA)
ListBA = AddItemsList(ValuesListBA)
ListBB = AddItemsList(ValuesListBB)
ListBC = AddItemsList(ValuesListBC)

ListAA.CombineList(ListBA)
print ("\nListAddition A")
PrintValues(ListAA)

ListAA = AddItemsList(ValuesListAA)
ListAA.CombineList(ListBB)
print ("\nListAddition B")
PrintValues(ListAA)


ListAA = AddItemsList(ValuesListAA)
ListAA.CombineList(ListBC)
print ("\nListAddition C")
PrintValues(ListAA)