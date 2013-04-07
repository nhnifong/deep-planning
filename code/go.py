from __future__ import division
from copy import copy, deepcopy
import sys
from pprint import pprint
from random import randint

sys.setrecursionlimit(19*19+10)

class IllegalMove(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class State:
	def __init__(self, size):
		# 0 blank, -1 black, 1 white
		# stored from black's perspective
		self.size = size
		self.board = [[0]*size for i in range(size)]
		self.cp = -1 # current player black
		self.passes = 0 # consecutive passes
		self.movecount = 0
		# the following are necessary to implement the ko rule (Japanese variant) but may also be useful to the SdA players.
		self.prevmove = None
		self.prevnumcap = 0 # number of stones captured on previous move
		self.captures = {-1:0, 1:0}
		
	def fromPerspective(self, perspective):
		s = deepcopy(self)
		for i in range(s.size):
			for j in range(s.size):
				s.board[i][j] *= -1
		s.cp *= -1
		d = s.captures[-1]
		s.captures[-1] = s.captures[1]
		s.captures[1] = d
		return s
		
	def serialize(self, perspective):
		bb = itertools.chain(*(deepcopy(self.board)))
		if perspective == 1: # white
			bb = map(lambda x: -x, bb) # swap -1s and 1s
			bb.append(-1*self.cp)
		else:
			bb.append(self.cp)
		return bb

def nextGameState(gamestate,move):
	# transforms gamestate to next gamestate.
	# if move is illegal, throws IllegalMove with an explanation
	# move is assumed to be of current player's color
	gs = deepcopy(gamestate)
	
	if gs.passes == 2:
		raise IllegalMove("Cannot move or pass again after game is over")
	
	if move == None: # pass
		gs.passes    += 1
		gs.cp        *= -1
		gs.movecount += 1
		return gs
	
	else:
		if type(move) != tuple:
			raise IllegalMove("Move is not a tuple. %r" % (move,))
		if len(move) != 2:
			raise IllegalMove("Move is not a pair . %r" % (move,))
		if any([type(x) != int for x in move]):
			raise IllegalMove("Move not a pair of ints. %r" % (move,))
		if any([not (0 <= x < gs.size) for x in move]):
			raise IllegalMove("Move location was not on board. %r" % (move,))
		if gs.board[ move[0] ][ move[1] ] != 0:
			raise IllegalMove("Chosen location is already occupied. %r" % (move,))
		gs.passes = 0
		
		# with that out of the way, place the stone and begin re-calculating the status of any groups claiming that as a liberty.
		gs.board[move[0]][move[1]] = gs.cp
		
		
		# suicide rule
		mygrp = findGroups(gs.board, move, gs.size)
		if mygrp is not None:
			if len(mygrp[2]) == 0:
				raise IllegalMove("Cannot make a group with no liberties. %r" % (move,))
			
		# the board locations adjacent to the place that just changed
		cardinals = filter(
			lambda mv: all([0 <= x < gs.size for x in mv]),
			[
				(move[0]-1, move[1]),
				(move[0]+1, move[1]),
				(move[0], move[1]-1),
				(move[0], move[1]+1)
			]
		)
		
		# the set of groups that may occupy the cardinals.
		others = set()
		for card in cardinals:
			others.add( findGroups(gs.board, card, gs.size) )
			
		# find and remove captures from the board
		numCaptured = 0
		singlecap = None
		for eg in others:
			if eg is not None:
				c_color, c_stones, c_libs = eg
				if c_color == (-1*gs.cp):
					if len(c_libs) == 0: # capture!
						numCaptured += len(c_stones)
						for cx,cy in c_stones:
							gs.board[cx][cy] = 0
							singlecap = (cx,cy)
		gs.captures[gs.cp] += numCaptured
				
		# if the suicide rule is checked first, then the ko rule can be checked in the following way:
		# One may not capture just one stone, if that stone was played on the previous move, and that move also captured just one stone.
		if (numCaptured == 1) and (gs.prevmove == singlecap) and (gs.prevnumcap == 1):
			raise IllegalMove("Ko rule violation. %r" % (move,))
			
		gs.cp        *= -1
		gs.movecount += 1
		gs.prevmove = move
		gs.prevnumcap = numCaptured
		return gs

def findGroups(board, loc, size):
	# returns (color, stones, liberties)
	# where stones and liberties are sets of locations
	sx = len(board)
	sy = len(board[0])
	if board[loc[0]][loc[1]] == 0:
		return None
	color = board[loc[0]][loc[1]]
	stones = set()
	liberties = set()
	front = set()
	checked = set()
	front.add(loc)
	# flood fill
	while not len(front)==0:
		(x,y) = front.pop()
		if board[x][y] == color:
			stones.add((x,y))
			cardinals = filter(
				lambda mv: all([0 <= k < size for k in mv]),
				[ (x-1, y), (x+1, y), (x, y-1), (x, y+1) ])
			for cloc in cardinals:
				# if this potential location is not in any of the other sets
				if all([cloc not in z for z in [front,stones,liberties,checked]]):
					front.add(cloc)
		elif board[x][y] == 0:
			liberties.add((x,y))
		else:
			checked.add((x,y))
	return (color, frozenset(stones), frozenset(liberties))
	
def scoreGame(gs):
	scores = copy(gs.captures)
	# remove dead
	
	# count territory that is totally surrounded by one color
	
	
	winner = scores
	return scores,winner

if __name__ == "__main__":
	begin = State(19)
	pprint(begin.board)
	moo = "(;GM[1]FF[4]AP[qGo:1.5.4]ST[1]\nSZ[19]HA[0]KM[5.5]PW[White]PB[Black]\n\n"
	while True:
		try:
			
			cho = (randint(0,18), randint(0,18))
			begin = nextGameState(begin,cho)
			#print ''
			#print repr(cho)
			#print '' 
			#pprint(begin.board)
			bw = {-1:'B',1:'W'}
			alpha = 'abcdefghijklmnopqrstuvwxyz'
			moo+= ";%s[%s%s]" % (bw[begin.cp], alpha[cho[0]], alpha[cho[1]])
		except IllegalMove:
			pass
		except KeyboardInterrupt:
			pprint(begin)
			moo += "\n)"
			print "writing gameout.sgf"
			fo = open('gameout.sgf','w')
			pprint(begin.captures)
			fo.write(moo)
			fo.close()
			sys.exit(0)
















			