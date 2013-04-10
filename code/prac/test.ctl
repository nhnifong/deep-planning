competition_type = 'playoff'

board_size = 9
komi = 7.5

players = {
    'gnugo-l1' : Player('gnugo --mode=gtp --level=1'),
    'test_play' : Player('players/test_play'),
    }

matchups = [
    Matchup('gnugo-l1', 'test_play',
            alternating=True,
            number_of_games=50),
    ]