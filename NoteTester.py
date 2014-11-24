import re
import sys
import json
from collections import OrderedDict, defaultdict
import random
import itertools
from copy import copy

from NoteParser import makeQuestions

statsFile = sys.argv[2]

def quit():
	with open(statsFile, "w") as fp:
		json.dump(stats, fp, indent=4)
	exit()

# print the section text
# print the definition and ask user to select from possible definitions
# print the termscontext and ask user to select from possible terms and
#  orders of terms
# print the name and ask to pick the context
# print the namecontext and ask to pick the name
# print the list and ask to select the corresponding bullet
# print the bullet and ask to select the right things to make up the list

stats = {}
with open(statsFile, "r") as fp:
	stats = json.load(fp)

questions = makeQuestions()

for question in copy(questions):
	text = question["text"].decode("utf-8")
	if text not in stats.keys():
		stats[text] = {
			"right": 0,
			"wrong": 0,
			"keep": 0
		}
	if stats[text]["right"] + stats[text]["wrong"] > 5:
		bottom = stats[text]["wrong"] + stats[text]["keep"]
		if bottom and stats[text]["right"] / bottom > 1:
			questions.remove(question)

while questions:
	for question in copy(questions):
		try:
			section = question["section"]
			text = question["text"]
			# answers = question["answers"]
			answers = question["answer"]
			# correctAnswer = question["correctAnswer"]
			parent = question["parent"]

			if "keep" not in stats[text].keys():
				stats[text]["keep"] = 0

			print
			print section
			print parent
			print text
			s = raw_input("Press any key to continue")
			for i, ans in enumerate(answers):
				print i + 1, ans
			# if question["multipleChoice"]:
			# s = raw_input("answer > ")
			# s = int(s)
			# if answers[s] == correctAnswer:
				# stats[text]["right"] += 1
				# s = raw_input("Correct! Press enter to remove this question or k to keep > ")
			s = raw_input("Press enter to remove this question or k to keep > ")
			if s is not 'k':
				questions.remove(question)
			else:
				stats[text]["keep"] += 1
			# else:
			# 	print "Sorry, correct answer was", correctAnswer
			# 	stats[text]["wrong"] += 1

			print len(questions), "left"

		except EOFError:
			print "\nGoodbye"
			quit()
		except Exception as e:
			print "Unexpected error:", sys.exc_info()[0]
			print e
			s = raw_input("Press enter to continue or q to quit > ")
			questions.remove(question)
			if s is 'q':
				quit()
quit()