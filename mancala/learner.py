import os
import random
import pathlib
from sqlitedict import SqliteDict
from mancala import Board, learner

class NullLogger:
        def on_sow(self, stones, player, move):
            pass
        def on_end(self, score, winner):
            pass


class MemoryLogger:
    def __init__(self):
        self.events = []
    def on_sow(self, stones, player, move):
        self.events.append(("sow", stones[:], player, move))
    def on_end(self, score, winner):
        self.events.append(("end", score, winner))


class FileLogger:
    def __init__(self, outs):
        self.outs = outs
    def on_sow(self, stones, player, move):
        self.outs.write(repr(("sow", stones[:], player, move)) + "\n")
    def on_end(self, score, winner):
        self.outs.write(repr(("end", score, winner)) + "\n")
    @classmethod
    def read(self, ins):
        for l in ins:
            try:
                yield eval(l.strip())
            except:
                assert False


class Play:
    def __init__(self):
        self.board = Board()
        self._stones = None
        self._moves = None
        self._logger = NullLogger()

    def set_stones(self, stones):
        self._stones = stones

    def set_moves(self, moves):
        if type(moves) == list:
            self._moves = iter(moves)
        else:
            self._moves = moves

    def set_logger(self, logger):
        self._logger = logger

    def play(self):
        if self._stones:
            self.board.reload(self._stones)

        while not self.board.is_end():
            player = self.board.next_player()
            next_move = next(self._moves)
            self._logger.on_sow(self.board.holes, player, next_move)
            self.board.sow(player, next_move)

        self._logger.on_end(self.board.get_score(), self.board.winner())


def random_moves(play):
    while True:
        _, candidates = play.board.valid_moves()
        yield random.choice(candidates)

def play_cicles(cycle, logger, moves_generator):
    for i in range(cycle):
        play = learner.Play()
        play.set_logger(logger)
        play.set_moves(moves_generator(play))
        play.play()


def build_database(events, dbname="mancala.db"):
    moves_count = 0
    wins = [0, 0]
    database = SqliteDict(dbname)
    sows = []
    for e in events:
        if e[0] == "sow":
            sows.append(e)
            moves_count += 1
        elif e[0] == "end":
            winner = e[2]
            if winner is not None:
                wins[winner] += 1
            diff = e[1][0] - e[1][1]
            for _, stones, player, hole_idx in sows:
                stones = tuple(stones)
                key = repr((player, stones))
                if key not in database:
                    database[key] = {}
                if hole_idx not in database[key]:
                    entry = database[key]
                    entry[hole_idx] = (0, 0)
                    database[key] = entry
                entry = database[key]
                total, count = entry[hole_idx]
                entry[hole_idx] = (total + diff, count + 1)
                database[key] = entry
            sows.clear()
    database.commit()
    return database, wins, moves_count


class Main:
    @staticmethod
    def run(argv):
        if argv[1] == "stat":
            dbname = argv[2]
            Main.stat(dbname)
        elif argv[1] == "record":
            cycle = int(argv[2])
            dbname = argv[3]
            Main.record(cycle, dbname)
        elif argv[1] == "match":
            cycle = int(argv[2])
            dbname = argv[3]
            Main.match(cycle, dbname)
        else:
            print("usage:")
            print("  python -m mancala.learner record {cycle} {dbname}")
            print("  python -m mancala.learner stat {dbname}")
            print("  python -m mancala.learner match {cycle} {dbname}")

    @staticmethod
    def record(cycle, dbname):
        import time
        start = time.time()
        for i in range(cycle):
            last = time.time()
            logger = MemoryLogger()
            play_cicles(10, logger, random_moves)
            build_database(logger.events, dbname)
            print(f"Cycle {i+1}: elapsed {time.time() - start} sec, interval {time.time() - last} sec")

    @staticmethod
    def match(cycle, dbname):
        database = SqliteDict(dbname)
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
                        top = (float('-inf'), 0)
                        for c in candidates:
                            if c not in database[key]:
                                val = (0, c)
                            else:
                                total, count = database[key][c]
                                wait = total / count
                                val = (total / count, c)
                            if top[0] < val[0]:
                                top = val
                        yield top[1]
                    else:
                        yield random.choice(candidates)
                else:
                    yield random.choice(candidates)
        learner.play_cicles(cycle, logger, clever_moves_for_player1)

        wins = [0, 0]
        for e in logger.events:
            sows = []
            if e[0] == "end":
                winner = e[2]
                if winner is not None:
                    wins[winner] += 1

        print(f"{wins[0]} wins, {wins[1]} losses, {cycle-wins[0]-wins[1]} draws after {cycle} matches.  Winning ratio is {wins[0]/cycle}")


    @staticmethod
    def stat(dbname):
        database = SqliteDict(dbname)
        print(f"{len(database)} records")
        counts = {}
        l = 0
        for key in database.keys():
            player, stones = eval(key)
            val = database[key]
            for hole_idx in val:
                diff_total, count = val[hole_idx]
                if count not in counts:
                    counts[count] = 0
                counts[count] += 1

#            l += 1
#            if l > 10:
#                break

        print("distribution of moves ever played")
        for a, b in sorted(list(counts.items()), key = lambda v: v[1]):
            print(f"  {b} {a}")


def main(argv):
    Main.run(argv)

if __name__=='__main__':
    import sys
    main(sys.argv)
