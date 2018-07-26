from treys import Card
from treys import Evaluator
from treys import Deck
from pokerBot import getCard

class PokerStrategy(object):
	def evaluate(self, hands, boards):
		err_msg = self.__build_err_msg("evaluate")
		raise NotImplementedError(err_msg)

class CardEvaluator(PokerStrategy):
	evaluator = Evaluator()
	
	def evaluate(self, hands, boards, showRank = True):		
		rank = self.evaluator.evaluate(boards, hands)
		percentage = 1.0 - self.evaluator.get_five_card_rank_percentage(rank)
		if showRank:
			r_class = self.evaluator.get_rank_class(rank)
			print("My hand rank = %f (%s)" % (percentage, self.evaluator.class_to_string(r_class)))
		return percentage

class CardCounting(CardEvaluator):
	def evaluate(self, hands, boards, threshold):
		win_rate = super(CardCounting, self).evaluate(hands, boards, False)

		deck = Deck()
		draw_cards = []

		for card in deck.draw(52):
			if card in hands or card in boards:
				continue
			
			boards.append(card)
			if len(boards) == 5: # River
				new_win_rate = super(CardCounting, self).evaluate(hands, boards, False)
				if new_win_rate >= threshold and new_win_rate - win_rate > 0.1:
					draw_cards.append(card)
					# print('old:{}'.format(win_rate) + ' new:{}'.format(new_win_rate))
			elif len(boards) == 4: # Turn			
				cards = self.evaluate(hands, boards, threshold)
				for dc in cards:
					if dc not in draw_cards:
						draw_cards.append(dc)
			boards.remove(card)
		
		return draw_cards

class HoleEvaluator(CardEvaluator):
	def evaluate(self, hands, num_draw, count):
		deck = Deck()
		draw_cards = []
		boards = []
		win_rate = 0.0

		for i in range(0, count):
			deck.shuffle()
			j = 0
			while j < num_draw:
				card = deck.draw(1)
				if card in hands :
					continue
				else:
					boards.append(card)
					j+=1
			win_rate += super(HoleEvaluator, self).evaluate(hands, boards, False)
			boards.clear()

		hole_win_rate = win_rate / float(100)
		print('hole win rate:{}'.format(hole_win_rate))
		return hole_win_rate



if __name__ == '__main__':
	# Hand card:
 # 	[7♦],[5♠]
	# Board card:
 # 	[4♠],[3♦],[Q♣]
 	hole = [getCard('7d'), getCard('5s')]
 	boards = [getCard('4s'), getCard('3d'), getCard('Qc')]
 	print("Hole:")
 	Card.print_pretty_cards(hole)
 	print("Boards:")
 	Card.print_pretty_cards(boards)
 	print("Draw:")
 	drawCard = CardCounting().evaluate(hole, boards, 0.7)
 	Card.print_pretty_cards(drawCard)
 	# Hand card:
	# [J♦],[6♦]
	# Board card:
	# [7♣],[3♣],[A♦]
 	hole = [getCard('Jd'), getCard('6d')]
 	boards = [getCard('7c'), getCard('3c'), getCard('Ad')]
 	print("Hole:")
 	Card.print_pretty_cards(hole)
 	print("Boards:")
 	Card.print_pretty_cards(boards)
 	print("Draw:")
 	drawCard = CardCounting().evaluate(hole, boards, 0.75)
 	Card.print_pretty_cards(drawCard)

 	hole = [getCard('Ts'), getCard('Th')]
 	pot = []
 	HoleEvaluator().evaluate(hole, pot, 0.5)

 	hole = [getCard('2c'), getCard('2d')]
 	pot = []
 	HoleEvaluator().evaluate(hole, pot, 0.5)
