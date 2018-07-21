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

class Stage(Enum):
	PreFlop = 'preFlop'
	Flop = 'Flop'
	Turn = 'Turn'
	River = 'River'
	Showdown = 'Showdown'
	HandOver = 'HandOver'

def GetStage(stage):
	if stage == 'Deal':
		return Stage.PreFlop
	elif stage == 'Flop':
		return Stage.Flop
	elif stage == 'Turn':
		return Stage.Turn
	elif stage == 'River':
		return Stage.River
	elif stage == 'Showdown':
		return Stage.Showdown
	else:
		return Stage.HandOver