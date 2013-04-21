#!/usr/bin/env python
from __future__ import division
import random
import sys

from gomill import gtp_engine
from gomill import gtp_states

from batch_SdA import SdA
from dataset import process_sgf, make_training_example
import numpy as np
import cPickle

class Player(object):
    """Player for use with gtp_state."""

    def __init__(self):
        self.sda = cPickle.load(open(sys.argv[1]))
        self.logfile = open('sda_player.log','a')
    
    def log(self,m):
        self.logfile.write(m+'\n')
        self.logfile.flush()

    def genmove(self, game_state, player):
        """Move generator that reconstructs the board using a pretrained SdA and picks the most desirable empty spot

        game_state -- gtp_states.Game_state
        player     -- 'b' or 'w'

        """
        board = game_state.board
        pts = [0.5] * (19**2 + 2)
        for row, col in board.board_points:
            stone = board.get(row, col)
            if stone is None:
                pass
            if stone == player:
                pts[row*19+col] = 0.25
            else:
                pts[row*19+col] = 0.75

        img = self.sda.reconstruct(pts)
        result = gtp_states.Move_generator_result()
        desired = sorted(enumerate(img[:-2]),key=lambda k: k[1])
        for index,score in desired:
            if score > 0.5:
                result.pass_move = True
                return result
            row = index // 19
            col = index - (row * 19)
            if self.legal(game_state, player, (row,col)):
                result.move = (row,col)
                return result
        result.resign = True
        return result

    def legal(self, game_state, player, move):
        if game_state.board.get(move[0], move[1]) is not None:
            return False
        if move == game_state.ko_point:
            return False
        # flood fill group, sum liberties
        dirnb = [(-1,0),(1,0),(0,-1),(0,1)]
        def onboard(mm):
            return all(map(lambda m: 0<=m<19,mm))
        front = filter(onboard, map(lambda x: map(sum,zip(move,x)), dirnb))
        checked = [list(move)]
        libs = 0
        #self.log('')
        while len(front) > 0:
            spot = front.pop(0)
            h = game_state.board.get(spot[0], spot[1])
            #self.log(str(spot)+' '+str(h))
            if h == player:
                # on-board neighbors
                nb = filter(onboard, map(lambda x: map(sum,zip(spot,x)), dirnb))
                # put any new ones on the front
                #self.log(repr(checked)+' '+repr(nb))
                front.extend(filter(lambda x: (x not in checked) and 
                                    (x not in front), nb))
            elif h is None:
                libs += 1
            checked.append(spot)
        #self.log("%i libs" % libs)
        return libs > 0
        

    def handle_name(self, args):
        return "Trained SdA Player"

    def handle_version(self, args):
        return ""

    def handle_resign_p(self, args):
        try:
            f = gtp_engine.interpret_float(args[0])
        except IndexError:
            gtp_engine.report_bad_arguments()
        self.resign_probability = f

    def get_handlers(self):
        return {
            'name'            : self.handle_name,
            'version'         : self.handle_version,
            'gomill-resign_p' : self.handle_resign_p,
            }


def make_engine(player):
    """Return a Gtp_engine_protocol which runs the specified player."""
    gtp_state = gtp_states.Gtp_state(
        move_generator=player.genmove,
        acceptable_sizes=(9, 13, 19))
    engine = gtp_engine.Gtp_engine_protocol()
    engine.add_protocol_commands()
    engine.add_commands(gtp_state.get_handlers())
    engine.add_commands(player.get_handlers())
    return engine

def main():
    try:
        player = Player()
        engine = make_engine(player)
        gtp_engine.run_interactive_gtp_session(engine)
    except (KeyboardInterrupt, gtp_engine.ControllerDisconnected):
        sys.exit(1)

if __name__ == "__main__":
    main()
