from enum import Enum, unique

@unique
class Action(Enum):
	Bet = 'bet'
	Call = 'call'
	Raise = 'raise'
	Check = 'check'
	Fold = 'fold'
	Allin = 'allin'
	def __str__(self):
		return str(self.value)