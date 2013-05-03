import string, simple_go

def diagram2game(str):
    g = None
    for line in string.split(str, "\n"):
        line = string.strip(line)
        if not line: continue
        if line[0]=="A" and not g:
            g = simple_go.Game(len(line))
        elif line[0] in string.digits:
            y, line, rest = string.split(line, "|")
            y = int(y)
            for x in range(len(line)):
                stone = line[x]
                x = x + 1
                if stone in simple_go.WHITE+simple_go.BLACK:
                    if g.current_board.side!=stone:
                        g.make_move(simple_go.PASS_MOVE)
                    g.make_move((x, y))
    return g

def test_unconditional(str):
    g = diagram2game(str)
    print g.current_board.as_string_with_unconditional_status()
