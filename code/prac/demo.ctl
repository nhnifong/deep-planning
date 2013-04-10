competition_type = 'playoff'

board_size = 9
komi = 7.5

players = {
    'gnugo-l1' : Player('gnugo --mode=gtp --level=1'),
    'gnugo-l2' : Player('gnugo --mode=gtp --level=2'),
    }

matchups = [
    Matchup('gnugo-l1', 'gnugo-l2',
            alternating=True,
            number_of_games=50),
    ]