import go, player
import sys
from pprint import pprint

sys.setrecursionlimit(19*19+10)


sgf_header = "(;GM[1]FF[4]AP[qGo:1.5.4]ST[1]\nSZ[19]HA[0]KM[5.5]PW[White]PB[Black]\n\n"
sgf_footer = "\n)"
bw = {-1:'B',1:'W'}
alpha = 'abcdefghijklmnopqrstuvwxyz'

sgf_moves = ""
game = go.State(19)
players = { -1:player.RandomPlayer() ,
             1:player.RandomPlayer() }

while game.passes < 2:
	try:
		pers = game.fromPerspective(game.cp)
		choice = players[game.cp].decideMove(pers)
		game = go.nextGameState(game,choice)
		if choice is None:
			choice = (20,20) # stupid SGF convention
		sgf_moves += ";%s[%s%s]" % (bw[game.cp], alpha[choice[0]], alpha[choice[1]])
	except go.IllegalMove:
		print "%s has made an illegal move and forfeits" % (bw[game.cp])
		
#game has ended
scores, winner = go.scoreGame(game) 

print "writing gameout.sgf"
fo = open('gameout.sgf','w')
fo.write(sgf_header)
fo.write(sgf_moves)
fo.write(sgf_footer)
fo.close()