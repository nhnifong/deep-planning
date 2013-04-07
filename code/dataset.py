from __future__ import division
import sys, os
from gomill import sgf, sgf_moves
from zipfile import ZipFile
import numpy

other = {'w':'b','b':'w'}

def read_all_zips(data_dir,prefix):
    meg = []
    nn = 0
    for zipfilename in os.listdir( data_dir ):
        if zipfilename.startswith('.') or zipfilename.startswith('__MACOSX'):
            continue
        zfpath = os.path.join(data_dir, zipfilename)
        print "Opening zip file: %s" % (zfpath)
        zf = ZipFile(zfpath)
        for filech in zf.filelist:
            if filech.filename.endswith( '.sgf' ):
                #print("processing SGF file: %s" % filech.filename)
                sgf_src = zf.open(filech).read()
                try:
                    moves = process_sgf( sgf_src )
                    meg.extend(moves)
                    if len(meg) >= 100000:
                    	foutname = "../data/moves/%s-%i.np" % (prefix, nn)
                    	print "Writing %i new records to %s" % (len(meg), foutname)
                    	fout = open(foutname, 'wb')
                    	numpy.array(meg).tofile(fout)
                    	fout.close()
                    	meg = []
                    	nn += 1
                except StandardError as e:
                    #print str(e)
                    continue
        foutname = "../data/moves/%s-%i.np" % (prefix, nn)
        print "Writing %i new records to %s" % (len(meg), foutname)
        fout = open(foutname, 'wb')
        numpy.array(meg).tofile(fout)
        fout.close()
        


def process_sgf(sgf_src):
    moves = []
    try:
        sgf_game = sgf.Sgf_game.from_string(sgf_src)
    except ValueError:
        raise StandardError("bad sgf file")
    
    if not sgf_game.size == 19:
        return
    lastmove = {}
    try:
        board, plays = sgf_moves.get_setup_and_moves(sgf_game)
    except ValueError, e:
        raise StandardError(str(e))
        
    mn = 0
    for colour, move in plays:
        if move is None:
            continue
        row, col = move
        lastmove[colour] = move
        try:
            board.play(row, col, colour)
            mn += 1
            x = make_training_example(board, sgf_game, mn, colour, len(plays), lastmove)
            moves.append(x)
        except ValueError:
            raise StandardError("illegal move in sgf file")
    return moves

def make_training_example(board, game, move_number, who_just_moved, tot_moves, lastmove):
    pts = [0.5] * (19**2 + 2) #. 0.5 means empty, 0 means black, 1 means white
    # represent board as if it is always black's move
    for i in range(19):
        for j in range(19):
            color = board.get(i,j)
            if color == None:
                pts[i*19+j] = 0.5
            elif color == who_just_moved:
                pts[i*19+j] = 0.25 # one of mine
            else:
                pts[i*19+j] = 0.75 # one of his
    
    try:
        myrow,mycol = lastmove[who_just_moved]
        pts[myrow*19+mycol] = 0.0
    except KeyError:
        pass
    try:
        herow,hecol = lastmove[other[who_just_moved]]
        pts[herow*19+hecol] = 0.0
    except KeyError:
        pass
    
    pts[361] = move_number / tot_moves # move number normalized to length of game
    
    # 1 for a win for the player who just moved
    # 0 for a win for the other player
    # 0.5 for an unknown outcome
    winner = game.get_winner()
    if winner == who_just_moved:
        reward = 1.0
    elif winner == other[who_just_moved]:
        reward = 0.0
    else:
        reward = 0.5
    
    pts[362] = reward # ultimate normalized reward for black
    
    #print reward,winner
    return pts
            
if __name__ == "__main__":
    read_all_zips(sys.argv[1],sys.argv[2])






