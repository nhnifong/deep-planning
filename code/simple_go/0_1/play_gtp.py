# -*- coding: cp1252 -*-
#! /usr/bin/env python

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This program is distributed with GNU Go, a Go program.        #
#                                                               #
# Write gnugo@gnu.org or see http://www.gnu.org/software/gnugo/ #
# for more information.                                         #
#                                                               #
# Copyright 1999, 2000, 2001, 2002, 2003 and 2004               #
# by the Free Software Foundation.                              #
#                                                               #
# This program is free software; you can redistribute it and/or #
# modify it under the terms of the GNU General Public License   #
# as published by the Free Software Foundation - version 2.     #
#                                                               #
# This program is distributed in the hope that it will be       #
# useful, but WITHOUT ANY WARRANTY; without even the implied    #
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR       #
# PURPOSE.  See the GNU General Public License in file COPYING  #
# for more details.                                             #
#                                                               #
# You should have received a copy of the GNU General Public     #
# License along with this program; if not, write to the Free    #
# Software Foundation, Inc., 59 Temple Place - Suite 330,       #
# Boston, MA 02111, USA.                                        #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# some comments (like above) and
# lots of code copied from twogtp.py from gnugo-3.6-pre4
# additions/changes by Aloril 2004

# minor changes by Blubb Fallo 2004

# Alori modified to work with simple_go.py

try:
    import psyco
    from psyco.classes import *
    psyco.full()
except:
    pass

import simple_go

import popen2
import sys
import string
import time
import random
import os
import traceback

debug = 1

def log(s):
    fp = open("game2.log", "a")
    fp.write(s)
    fp.close()

def coords_to_sgf(size, board_coords):
    global debug
    
    board_coords = string.lower(board_coords)
    if board_coords == "pass":
        return ""
    letter = board_coords[0]
    digits = board_coords[1:]
    if letter > "i":
        sgffirst = chr(ord(letter) - 1)
    else:
        sgffirst = letter
    sgfsecond = chr(ord("a") + int(size) - int(digits))
    return sgffirst + sgfsecond
        


class GTP_controller:

    #
    # Class members:
    #   outfile         File to write to
    #   infile          File to read from

    def __init__(self, infile, outfile):
        self.infile  = infile
        self.outfile = outfile
        # total number of gtpb-logfiles
        for i in range(1000):
            log_name = "gtpb%03i.log" % i
            if not os.path.exists(log_name):
                break
        self.log_fp = open(log_name, "w")

    def get_cmd(self):
        global debug
        result = ""
        while 1:
            line = self.infile.readline()
            if not line: break
            if self.log_fp:
                self.log_fp.write(">" + line)
                self.log_fp.flush()
            if line=="\n": continue
            result = result + line
            break
        return result
        

    def set_result(self, result):
        global debug
        if debug:
            self.log_fp.write("<"+result)
            self.log_fp.flush()
        self.outfile.write(result)
        self.outfile.flush()
        


class GTP_player:

    # Class members:
    #    slave          GTP_connection
    #    master         GTP_controller

    def __init__(self):
        self.engine = simple_go.Game(19)
        self.master = GTP_controller(sys.stdin, sys.stdout)
        self.version = "0.1.6"
        self.name = "SimpleBot: at end of game I will pass once your stones are so safe that you can pass FOREVER: my info contains links to my source code: "
        self.komi = 0.0
        self.handicap = 0
        # total number of gtpc-logfiles
        for i in range(1000):
            log_name = "gtpc%03i.log" % i
            if not os.path.exists(log_name):
                break
        self.log_fp = open(log_name, "w")

    def ok(self, result=None):
        if result==None: result = ""
        return "= " + result + "\n\n"

    def error(self, msg):
        return "? " + msg + "\n\n"

    def boardsize(self, size):
        if size > simple_go.max_size:
            return self.error("Too big size")
        self.engine = simple_go.Game(size)
        self.handicap = 0.0
        return self.ok("")

    def clear_board(self):
        return self.boardsize(self.engine.size)

    def check_side2move(self, color):
        if (self.engine.current_board.side==simple_go.BLACK) != (string.upper(color[0])=="B"):
            if self.handicap==0:
                handicap_change = 2
            else:
                handicap_change = 1
            if string.upper(color[0])=="B":
                self.handicap = self.handicap + handicap_change
            else:
                self.handicap = self.handicap - handicap_change
            self.engine.make_move(simple_go.PASS_MOVE)

    def genmove_plain(self, color, remove_opponent_dead=False, pass_allowed=True):
        self.check_side2move(color)
        move = self.engine.generate_move(remove_opponent_dead, pass_allowed)
        move = simple_go.move_as_string(move, self.engine.size)
        self.play_plain(color, move)
        return move

    def genmove(self, color):
        return self.ok(self.genmove_plain(color, remove_opponent_dead=False, pass_allowed=True))

    def play_plain(self, color, move):
        self.check_side2move(color)
        self.engine.make_move(simple_go.string_as_move(string.upper(move), self.engine.size))
        log(str(self.engine.current_board))
        log(self.engine.current_board.as_string_with_unconditional_status())
        log("move: " + move + "\n")
        log("score: %s unconditional score: W:%i B:%i\n" % (
            self.final_score_as_string(),
            self.engine.current_board.unconditional_score(simple_go.WHITE),
            self.engine.current_board.unconditional_score(simple_go.BLACK)))

    def play(self, color, move):
        return self.ok(self.play_plain(color, move))

    def place_free_handicap(self, count):
        self.handicap = count
        result = []
        for move in self.engine.place_free_handicap(count):
            move = simple_go.move_as_string(move, self.engine.size)
            result.append(move)
        return self.ok(string.join(result))

    def set_free_handicap(self, stones):
        self.handicap = len(stones)
        for i in range(len(stones)):
            if i: self.play_plain("white", "PASS")
            self.play_plain("black", stones[i])
        return self.ok("")

    def final_status_list(self, status):
        lst = self.engine.final_status_list(status)
        str_lst = []
        for pos in lst:
            str_lst.append(simple_go.move_as_string(pos, self.engine.size))
        return self.ok(string.join(str_lst, "\n"))

    def final_score_as_string(self):
        score = self.engine.current_board.score_position()
        if self.engine.current_board.side==simple_go.BLACK:
            score = -score
        score = score + self.komi + self.handicap
        if score>=0:
            result = "W+%.1f" % score
        else:
            result = "B+%.1f" % -score
        return result

    def final_score(self):
        return self.ok(self.final_score_as_string())

    def genmove_cleanup(self, color):
        return self.ok(self.genmove_plain(color, remove_opponent_dead=True))

    def showboard(self):
        return self.ok(str(self.engine.current_board))

    def list_commands(self):
        result = string.join(("list_commands",
                              "boardsize",
                              "name",
                              "version",
                              "quit",
                              "clear_board",
                              "place_free_handicap",
                              "set_free_handicap",
                              "play",
                              "final_status_list",
                              "kgs-genmove_cleanup",
                              "showboard",
                              "protocol_version",
                              "komi",
                              "final_score",
                              ), "\n")
        return self.ok(result)
        
    def relay_cmd_and_reply(self):
        cmd_line = self.master.get_cmd()
        if not cmd_line: return 0
        cmd_lst = string.split(cmd_line)
        cmd = cmd_lst[0]     #Ctrl-C cancelling shows "list index out of range" error here in the log (keep this comment)
        if cmd=="version":                              
            result = "= " + self.version + "\n\n"
        elif cmd=="name":
            result = "= " + self.name + "\n\n"
        elif cmd=="protocol_version":
            result = "= 2\n\n"
        elif cmd=="komi":
            self.komi = float(cmd_lst[1])
            result = "=\n\n"
        elif cmd=="genmove_white":
            result = self.genmove("white")
        elif cmd=="genmove_black":
            result = self.genmove("black")
        elif cmd=="genmove":
            result = self.genmove(cmd_lst[1])
        elif cmd=="boardsize":
            result = self.boardsize(int(cmd_lst[1]))
        elif cmd=="list_commands":
            result = self.list_commands()
        elif cmd=="play":
            result = self.play(cmd_lst[1], cmd_lst[2])
        elif cmd=="clear_board":
            result = self.clear_board()
        elif cmd=="place_free_handicap":
            result = self.place_free_handicap(int(cmd_lst[1]))
        elif cmd=="set_free_handicap":
            result = self.set_free_handicap(cmd_lst[1:])
        elif cmd=="final_status_list":
            result = self.final_status_list(cmd_lst[1])
        elif cmd=="kgs-genmove_cleanup":
            result = self.genmove_cleanup(cmd_lst[1])
        elif cmd=="showboard":
            result = self.showboard()
        elif cmd=="final_score":
            result = self.final_score()
        elif cmd=="quit":
            result = "=\n\n"
        else:
            self.log_fp.write("Unhandled command:" + cmd_line)
            self.log_fp.flush()
            result = self.error("Unknown command")
        self.master.set_result(result)
        return cmd!="quit"
    def loop(self):
        try:
            while self.relay_cmd_and_reply():
                pass
        except:
            traceback.print_exc(None, self.log_fp)
            self.log_fp.flush()
            raise

if __name__=="__main__":
    player = GTP_player()
    player.loop()
    
