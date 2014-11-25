from Matching import MatchingGame

# get a dictionary of {terms: context}
# print the contexts out in random order enumerated
# print the terms' out in order enumerated
# get input from user as a pair: (#:#)
#  where (terms'[#],contexts[#]) is a key,value pair into the fist dictionary
# if this pair exists in the first dict then the user is right, else wrong
#   if right, remove the corresponding terms and context from consideration

types = getTypes()

for i, type in enumerated(types):
	print i, type

s = raw_input("Please select from the above types > ")

game = MatchingGame(types[int(s)])

while not game.isFinished():
	try:
		for i, termGroup in enumerated(game.termGroups()):
			print i, termGroups
		print
		for i, context in enumerated(game.contexts()):
			print i, context

		s = raw_input("Match the terms with their context by typing #,#<enter> > ")

		tid, cid = s.split(',');

		if game.play(tid, cid):
			print "Correct!"
		else:
			print "Incorrect, please try again"
	except EOFError:
		print "\nGoodbye"
		quit()
	except Exception as e:
		print "Unexpected error:", sys.exc_info()[0]
		print e
