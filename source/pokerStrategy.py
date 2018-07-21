from treys import Card
from treys import Evaluator
from treys import Deck

class PokerStrategy(object):
	def evaluate(self, hands, boards):
		err_msg = self.__build_err_msg("evaluate")
		raise NotImplementedError(err_msg)

class WinRateStrategy(PokerStrategy):
	evaluator = Evaluator()
	
	def evaluate(self, hands, boards):		
		rank = self.evaluator.evaluate(boards, hands)
		percentage = 1.0 - self.evaluator.get_five_card_rank_percentage(rank)
		r_class = self.evaluator.get_rank_class(rank)
		print("My hand rank = %f (%s)" % (percentage, self.evaluator.class_to_string(r_class)))
		return percentage

class CardCounting(WinRateStrategy):
	def evaluate(self, hands, boards):
		win_rate = super(CardCounting, self).evaluate(hands, boards)

		deck = Deck()
		draw_cards = []

		for card in deck.draw(52):
			if card in hands or card in boards:
				continue
			boards.append(card)
			new_win_rate = super(CardCounting, self).evaluate(hands, boards)
			if new_win_rate - win_rate > 0.1:
				print('old:{}'.format(win_rate) + ' new:{}'.format(new_win_rate))
				draw_cards.append(card)
			boards.remove(card)
		
		print("Draw cards:")
		Card.print_pretty_cards(draw_cards)
		return draw_cards

