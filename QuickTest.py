import QuestionaireMisc

#QuestionaireMisc.CleanupNestedTags("<<B>><<S>><<C>>DEMOGRAPHICS<</B>><</S>><</C>><<N>><<C>>The last few questions are for classification purposes only.<</C>><<N>><<C>>What is your current marital status?<</C>>>")
QuestionaireMisc.CleanupOrphanTags("<<C>><<S>><<B>>DEMOGRAPHICS<</B>><</S>><</C>><<N>><<C>>The last few questions are for classification purposes only.<</C>><<N>><<C>>What is your current marital status?<</C>>")