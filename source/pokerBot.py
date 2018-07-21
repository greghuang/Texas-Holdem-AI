from treys import Card
import sys, traceback

def getCard(card):
	return Card.new(card[0] + card[1].lower())

# 2018.07.17
# Total games:40 total chips:130178 avg.chips:3254.0625
# Total rounds:415, win rounds:100, win rate:0.240964
class PokerBot(object):
	def initRound(self, data):
		err_msg = self.__build_err_msg("init round")
		raise NotImplementedError(err_msg)

	def showAction(self, data):
		err_msg = self.__build_err_msg("init round")
		raise NotImplementedError(err_msg)

	def declareAction(self, data, isBet=False):
		err_msg = self.__build_err_msg("declare action")
		raise NotImplementedError(err_msg)

	def endRound(self, data):
		err_msg = self.__build_err_msg("round over")
		raise NotImplementedError(err_msg)

	def endGame(self, data):
		err_msg = self.__build_err_msg("game over")
		raise NotImplementedError(err_msg)

