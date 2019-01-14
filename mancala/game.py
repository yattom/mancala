class InvalidMoveError(Exception):
    pass

class WrongTurnError(Exception):
    pass

class Board:
    PLAYER1 = 0
    PLAYER2 = 1

    def __init__(self):
        self.holes = [0 for i in range((6 + 1) * 2)]
        self._players = 2
        self.reload()

    def reload(self, stones=[4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]):
        for i in range(len(self.holes)):
            self.holes[i] = stones[i]
        self._next_player = Board.PLAYER1

    def players(self):
        return range(self._players)

    def next_player(self):
        return self._next_player

    def is_valid_move(self, player, hole_idx):
        if self.is_store(hole_idx):
            return False
        if not self.is_side(hole_idx, player):
            return False
        if self.holes[hole_idx] == 0:
            return False
        return True

    def sow(self, player, hole_idx):
        if player != self._next_player:
            raise WrongTurnError
        if not self.is_valid_move(player, hole_idx):
            raise InvalidMoveError

        free_move = False
        grabbed = self.holes[hole_idx]
        self.holes[hole_idx] = 0
        idx = hole_idx + 1
        while grabbed > 0:
            if self.is_store(idx) and player != self.whose_store(idx):
                pass
            else:
                if grabbed == 1 and self.is_store(idx, player):
                    free_move = True
                self.holes[idx % len(self.holes)] += 1
                grabbed -= 1
            idx += 1
            if idx == len(self.holes):
                idx = 0

        if not free_move:
            self.switch_player()

    def switch_player(self):
        self._next_player = ((self._next_player) + 1) % self._players

    def is_store(self, hole_idx, player=None):
        if hole_idx == 6 or hole_idx == 13:
            if player == None or player == self.whose_store(hole_idx):
                return True
        return False

    def whose_store(self, hole_idx):
        if hole_idx == 6:
            return Board.PLAYER1
        if hole_idx == 13:
            return Board.PLAYER2
        raise ValueError("not a store")

    def is_side(self, hole_idx, player):
        if player == Board.PLAYER1 and 0 <= hole_idx <= 6:
            return True
        if player == Board.PLAYER2 and 7 <= hole_idx <= 13:
            return True
        return False

    def get_score(self):
        return (self.holes[6], self.holes[13])

    def is_end(self):
        return sum(self.holes[0:6]) == 0 or sum(self.holes[7:13]) == 0

    def winner(self):
        if not self.is_end(): return None
        s1, s2 = self.get_score()
        if s1 > s2:
            return Board.PLAYER1
        elif s1 < s2:
            return Board.PLAYER2
        else:
            return None

    def valid_moves(self):
        player = self._next_player
        if player == 0:
            candidates = [0, 1, 2, 3, 4, 5]
        else:
            candidates = [7, 8, 9, 10, 11, 12]
        moves = []
        for c in candidates:
            if self.is_valid_move(player, c):
                moves.append(c)

        return (player, moves)


