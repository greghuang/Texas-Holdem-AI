from dummyPokerBot import DummyPokerBot
from switch import switch
from poker import Stage

class CardCountingBot(DummyPokerBot):
	def declareAction(self, data, isBet=False):
		# super(DummyPokerBot, self).initAction(data)
		self.initAction(data)
		amount = 0
		action = Action.Check

		for case in switch(self.stage):
			if case(Stage.PreFlop):
				withPreFlop(data)
				break
			if case(Stage.Flop):
				withFlop(data)
				break
			if case(Stage.Turn):
				withTurn(data)
				break
			if case(Stage.River):
				withRiver(data)
				break
			if case(Stage.HandOver):
				print('game over')
				break

		return super(CardCountingBot, self).declareAction(data, isBet)

	def withPreFlop(self, data):
		print("preFlop")

	def withFlop(self, data):
		print("Flop")

	def withTurn(self, data):
		print("Turn")

	def withRiver(self, data):
		print("River")



