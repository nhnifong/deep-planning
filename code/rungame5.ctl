competition_type = 'playoff'

board_size = 19
komi = 7.5

players = {
    'gnugo-l1' : Player('gnugo --mode=gtp --level=1'),
    'sda_play' : Player('python sda_play.py winners_SdA_ley3.pickle'),
    }

matchups = [
    Matchup('gnugo-l1', 'sda_play',
            alternating=True,
            number_of_games=50),
    ]