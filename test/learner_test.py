import pytest
import random
from pathlib import Path
import mancala
from mancala import learner

def test_single_play():
    sut = learner.Play()
    sut.set_stones([0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0])
    sut.set_moves([5])
    sut.play()
    assert sut.board.is_end()
    assert sut.board.get_score() == (1, 0)
    assert sut.board.winner() == 0

def test_logging():
    sut = learner.MemoryLogger()
    play = learner.Play()
    play.set_logger(sut)
    play.set_stones([0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0])
    play.set_moves([4, 7, 5])
    play.play()
    assert sut.events[0] == ("sow", [0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0], 0, 4)
    assert sut.events[1] == ("sow", [0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0], 1, 7)
    assert sut.events[2] == ("sow", [0, 0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0], 0, 5)
    assert sut.events[3] == ("end", (1, 0), 0)

def test_learning():
    cycle = 10
    logger = learner.MemoryLogger()
    learner.play_cicles(cycle, logger, learner.random_moves)

    database, wins, moves_count = learner.build_database(logger.events)

    print(len(database), len(database) / moves_count)
    assert len(database) > 0
    assert moves_count > 0
    assert wins[0] > 0 and wins[1] > 0

    print(wins)
    wins_ratio_before = wins[0] / sum(wins)

    logger = learner.MemoryLogger()
    def clever_moves_for_player1(play):
        while True:
            player, candidates = play.board.valid_moves()
            if player == 0:
                stones = tuple(play.board.holes)
                key = repr((player, stones))
                waited_candidates = []
                if key in database:
                    base = 24
                    for c in candidates:
                        if c not in database[key]:
                            waited_candidates += [c] * (0 + base)
                        else:
                            total, count = database[key][c]
                            wait = total / count
                            if wait + base > 0:
                                waited_candidates += [c] * int(wait + base)
                    yield random.choice(waited_candidates)
                else:
                    yield random.choice(candidates)
            else:
                yield random.choice(candidates)
    learner.play_cicles(10, logger, clever_moves_for_player1)

    wins = [0, 0]
    for e in logger.events:
        sows = []
        if e[0] == "end":
            winner = e[2]
            if winner is not None:
                wins[winner] += 1

    print(wins)
    wins_ratio_after = wins[0] / sum(wins)


