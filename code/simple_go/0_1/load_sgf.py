import string, simple_go, re, sys

def sgf_to_coords(size, sgf_coords):
    #print sgf_coords
    if len(sgf_coords)==0: return "PASS"
    letter = string.upper(sgf_coords[0])
    if letter>="I":
        letter = chr(ord(letter)+1)
    digit = str(ord('a') + int(size) - ord(sgf_coords[1]))
    return letter+digit

def sgf2tuple(size, move):
    coords = sgf_to_coords(size, move)
    return simple_go.string_as_move(coords, size)

def load_file(name):
    s = open(name).read()
    parts = string.split(s, ";")
    header = parts[1]
    moves = parts[2:]
    sz = re.match(r".*SZ\[(\d+)\].*", header, re.DOTALL)
    if sz:
        g = simple_go.Game(int(sz.group(1)))
    else:
        raise ValueError, "no size tag"
    ha = re.match(r".*AB(.*?)P.*", header, re.DOTALL)
    if ha:
        for move in string.split(ha.group(1)[1:-1], "]["):
            if g.current_board.side==simple_go.WHITE:
                g.make_move(simple_go.PASS_MOVE)
            g.make_move(sgf2tuple(g.size, move))
    for move_str in moves:
        m = re.match(r".*?(.)\[(.*?)\].*", move_str, re.DOTALL)
        if m:
            color = m.group(1)
            move = m.group(2)
            if (g.current_board.side==simple_go.BLACK) != (string.upper(color[0])=="B"):
                g.make_move(simple_go.PASS_MOVE)
            g.make_move(sgf2tuple(g.size, move))
    return g

if __name__=="__main__":
    g = load_file(sys.argv[1])
