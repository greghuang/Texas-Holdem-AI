from pokereval.card import Card

"""Create a card. Rank is 2-14, representing 2-A,
   while suit is 1-4 representing spades, hearts, diamonds, clubs"""
def getCard(card):
	cardnume_code = card[0]
	card_type = card[1]
	
	card_num = 0
	card_num_type = 0
	
	if card_type == 'S':
		card_num_type = 1
	elif card_type == 'H':
		card_num_type = 2
	elif card_type == 'D':
		card_num_type = 3
	elif card_type == "C":
		card_num_type = 4
	else:
		raise NameError(card_type + " is not defined")

	if cardnume_code == 'T':
		card_num = 10
	elif cardnume_code == 'J':
		card_num = 11
	elif cardnume_code == 'Q':
		card_num = 12
	elif cardnume_code == 'K':
		card_num = 13
	elif cardnume_code == 'A':
		card_num = 14
	else:
		card_num = int(cardnume_code)

	return Card(card_num, card_num_type)