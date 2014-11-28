import random
from NoteParser import makeQuestions, getTypes, typedQuestion


class MatchingGame(object):
	def __init__(self, questions):
		self.questions = questions
		self._termGroups = [q["answer"] for q in self.questions]

		random.shuffle(self.questions)

	def termGroups(self):
		return self._termGroups

	def contexts(self):
		return [q["parent"] + q["text"] for q in self.questions]

	def isFinished(self):
		return len(self._termGroups) is 0

	def play(self, tid, cid):
		q = self.questions[cid]
		tg = self._termGroups[tid]
		if q["answer"] == tg:
			self._termGroups.remove(tg)
			q["text"] = q["rawtext"]
			return True
		else:
			return False

def makeGames(type, partition=None):
	questions = makeQuestions([typedQuestion(type)])
	random.shuffle(questions)
	games = []
	if partition is None:
		partition = len(questions)
	start = 0
	end = partition
	while start < len(questions):
		games.append(MatchingGame(questions[start:end]))
		start += partition
		end += partition
	return games
