import re
import sys
import json
from collections import OrderedDict, defaultdict
import random
import itertools
from copy import copy

f = open(sys.argv[1], "r")

def newBullet():
	bullet = OrderedDict()
	bullet["headingLevel"] = -1;
	bullet["definitions"] = OrderedDict()
	bullet["bullets"] = []
	bullet["list"] = []
	bullet["types"] = {}
	return bullet	

doc = {
	"headings": [],
	"bullets": []
}

def parseNotes():
	def createBullet(line, blevel, currSection):
		TERM_OR_DEF = '\*?\*\*(\w.+?\w)\*\*\*?'
		# IDEA: Terms could be tagged with the part of speech: verb, noun, name, adjective
		#  already tagged with name
		#  This would allow easy assembly of mc options that are more plausible
		#  Can use NTLK library for python

		# IDEA: For lists, ask user to list the terms following the list owner text
		#  Terms are just like other terms so we can assemble lists of 
		#  other terms as mc options


		bullet = newBullet()
		bullet["parentSection"] = currSection
		hashes = re.search('^(#+)', line)
		if hashes:
			bullet["headingLevel"] = len(hashes.group(1))
			currSection = bullet
			doc["headings"].append(bullet)

		bullet["rawtext"] = line
		# for nameSent in re.finditer('(\.\s+)?\*\*@(.+?)\*\*(.*?\.)', line):
			# bullet["names"][nameSent.group(2)] = nameSent.group(3)

		# have a list of ('type', 'term') where type indicates the typeof the term (Person, Place, etc.)
		# want to group by type later so we should have a structure like:
		# type -> (terms, context) where 'terms' is all terms tagged with type in the bullet

		for type, term in re.findall('\*\*([!@#$%\^&?\\/\-_])(.+?)\*\*', line):
			bullet["types"].setdefault(type, {}).setdefault("terms", []).append(term)
			bullet["types"][type]["context"] = re.sub('\*\*'+ type +'(.+?)\*\*', type + "_____", line)
		
		# TODO: Refactor below to remove duplication with above
				# find terms and termscontext
		bullet["terms"] = re.findall(TERM_OR_DEF, line)
		if bullet["terms"]:
			bullet["termscontext"] = re.sub(TERM_OR_DEF, "_____", line)
				# record definitions

		bullet["tags"] = re.findall('.#(\w+)', line)

		while True:
			last_pos = f.tell()
			line = f.readline()
			if not line:
				break

			if line == '\n':
				continue
				# if heading assign heading blevel
			child = newBullet()
			hashes = re.search('^(#+)', line)
			spaces = re.search('^(\s*)', line)
			if hashes:
				if len(hashes.group(1)) > currSection["headingLevel"] and blevel is -1:
					child = createBullet(line, -1, currSection)
				else:
					f.seek(last_pos)
					break
			elif len(spaces.group(1)) > blevel:
				child = createBullet(line, len(spaces.group(1)), currSection)
			else: # not a child
				f.seek(last_pos)
				break;

					# process text
						# rawtext
						# find names and namescontext

			if re.search('^\s*\d+\.', child["rawtext"]):
				bullet["list"].append(child["rawtext"])
			# else:
			# 	bullet["bullets"].append(child)

			child["parent"] = bullet["rawtext"]

		doc["bullets"].append(bullet)
		return bullet

	return createBullet(f.readline(), -1, {"headingLevel": -1})
				# add child bullet if starts with '- + *' or is a definition or header
					# add bullet to list if it's numbered
doc["root"] = parseNotes()

with open("debug_output.json", "w") as fp:
	json.dump(doc["bullets"], fp, indent=4)

def emptyQuestion(bullet):
	q = {
		"answer": [],
		"text"  : "",
		"section": "",
		"parent": "",
		"tags": [],
		"multipleChoice": True
	}
	try:
		q["section"] = bullet["parentSection"]["rawtext"]
		q["parent"] = bullet["parent"]
		q["tags"] = bullet["tags"]
	except KeyError:
		pass
	return q

def termQuestion(bullet):
	q = emptyQuestion(bullet)
	try:
		q["answer"] = bullet["terms"]
		q["text"] = bullet["termscontext"]
	except KeyError:
		pass
	return [q]

def defQuestion(bullet):
	q = emptyQuestion(bullet)
	defs = bullet["definitions"].items()
	if defs:
		answer, q["text"] = random.choice(defs)
		q["answer"] = [answer]
	return [q]

def listQuestion(bullet):
	q = emptyQuestion(bullet)
	if bullet["list"]:
		q["text"] = bullet["rawtext"]
		q["answer"] = bullet["list"]
		q["multipleChoice"] = False
	return [q]

def typedQuestion(bullet):
	qs = []
	try:
		for values in bullet["types"].values():
			q = emptyQuestion(bullet)
			q["answer"] = values["terms"]
			q["text"] = values["context"]
			qs.append(q)
	except KeyError:
		pass
	return qs


questionTypes = [
	termQuestion,
	defQuestion,
	typedQuestion,
	listQuestion
]

def anyQuestion(bullet):
	qTypes = copy(questionTypes)
	random.shuffle(qTypes)
	for qType in qTypes:
		q = qType(bullet)
		if q["answer"]:
			return q
	return emptyQuestion(bullet)

# find a random section plus term, name, definition, or list
# find up to 4 others of the same type if possible
def makeQuestions():
	pool = [q for bullet in doc["bullets"] for qType in questionTypes for q in qType(bullet)]
	pool = [question for question in pool if question["answer"]]
	# random.shuffle(pool)
	# pool = [bullet for bullet in doc["bullets"] if questionFor(bullet)["answer"]]
	# mcQuestions = []
	# for i, question in enumerate(pool):
	# 	rest = pool[:i] + pool[i+1:]
	# 	questions = [question]
	# 	# if a multiple fill in the blank, don't need to sample, just provide
	# 	#  the different permutations up to a certain number
	# 	answers = [question["answer"]]
	# 	if question["multipleChoice"]:
	# 		if len(question["answer"]) > 1:
	# 			if "swap" in question["tags"]:
	# 				perms = [list(p) for p in itertools.permutations(question["answer"])]
	# 				perms.remove(question["answer"])
	# 				answers += perms[:4]
	# 			else:
	# 				choices = [a for q in pool for a in q["answer"]]
	# 				for _ in range(4):
	# 					answers += [a for a in random.sample(choices, min(len(question["answer"]), len(choices)))]
	# 		else:
	# 			# questions.extend(random.sample(rest, min(4, len(rest))))
	# 			singleTermed = [q for q in rest if len(q["answer"]) is 1]
	# 			answers += [q["answer"] for q in random.sample(singleTermed, min(4, len(singleTermed)))]

	# 	correctAnswer = answers[0]
	# 	random.shuffle(answers)
	# 	text = questions[0]["text"]
	# 	section = questions[0]["section"]
	# 	parent = questions[0]["parent"]
	# 	mcQuestions.append({
	# 		"text": text,
	# 		"answers": answers,
	# 		"correctAnswer": correctAnswer,
	# 		"section": section,
	# 		"parent": parent
	# 	})

	# for question in listPool:
	# 	mcQuestions.append({
	# 			"text": question["text"],
	# 			"answers": question["answer"],
	# 			"correctAnswer": False,
	# 			"section": question["section"],
	# 			"parent": question["parent"]
	# 	})

	# random.shuffle(mcQuestions)
	# return mcQuestions
	# random.shuffle(pool)
	return pool
