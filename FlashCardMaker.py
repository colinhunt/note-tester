from NoteParser import makeQuestions

for i, question in enumerate(makeQuestions()):
	section = question["section"]
	text = question["text"]
	# answers = question["answers"]
	answers = question["answer"]
	# correctAnswer = question["correctAnswer"]
	parent = question["parent"]

	print "=" * 50
	print i + 1
	print section
	print parent
	print text
	print "-" * 50
	print
	for i, ans in enumerate(answers):
		print i + 1, ans