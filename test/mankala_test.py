import pytest
import mancala

@pytest.fixture
def board():
    return mancala.Board()

@pytest.fixture
def me(board):
    me, _ = board.players()
    return me

@pytest.fixture
def opponent(board):
    _, opponent = board.players()
    return opponent

class TestLegalMoves:
    def test_sow_only_one_stone(self, board, me):
        board.reload([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        board.sow(me, 0)
        assert board.holes == [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def test_sow_five_stones(self, board, me):
        board.reload([0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        board.sow(me, 4)
        assert board.holes == [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0]

    def test_dont_drop_opponents_store(self, board, me):
        board.reload([0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        board.sow(me, 4)
        assert board.holes == [1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0]

    def test_opponent_dont_drop_my_store(self, board, opponent):
        board.reload([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0])
        board._next_player = opponent
        board.sow(opponent, 10)
        assert board.holes == [1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1]

    def test_initial_stones(self, board):
        board.reload()
        assert board.holes == [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]


class TestInvalidMoves:
    def test_cannot_sow_from_store(self, board, me):
        board.reload([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
        with pytest.raises(mancala.InvalidMoveError):
            board.sow(me, 6)

    def test_cannot_sow_from_store_opponent(self, board, opponent):
        board.reload([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
        board._next_player = opponent
        with pytest.raises(mancala.InvalidMoveError):
            board.sow(opponent, 13)

    def test_cannot_sow_from_empty_hole(self, board, me):
        board.reload([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        with pytest.raises(mancala.InvalidMoveError):
            board.sow(me, 0)

    def test_cannot_sow_from_opponent_side(self, board, me):
        with pytest.raises(mancala.InvalidMoveError):
            board.sow(me, 7)

    def test_cannot_sow_from_my_side(self, board, opponent):
        with pytest.raises(mancala.InvalidMoveError):
            board._next_player = opponent
            board.sow(opponent, 5)

class TestTakingTurns:
    def test_me_first_then_opponent(self, board, me, opponent):
        board.reload()
        board.sow(me, 0)
        board.sow(opponent, 7)

    def test_me_first(self, board, opponent):
        board.reload()
        with pytest.raises(mancala.WrongTurnError):
            board.sow(opponent, 7)

    def test_opponent_next(self, board, me):
        board.reload()
        board.sow(me, 0)
        with pytest.raises(mancala.WrongTurnError):
            board.sow(me, 7)

    class TestFreeMove:
        def test_free_move(self, board, me):
            board.reload([6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            board.sow(me, 0)
            assert board._next_player == me

        def test_free_move_by_opponent(self, board, opponent):
            board.reload([6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            board._next_player = opponent
            board.sow(opponent, 12)
            assert board._next_player == opponent


class TestScoringAndWinning:
    def test_score_initial(self, board):
        assert (0, 0) == board.get_score()

    def test_score(self, board, me):
        board.reload([1, 1, 1, 1, 1, 1, 10, 1, 1, 1, 1, 1, 1, 20])
        assert (10, 20) == board.get_score()

    def test_end_of_game(self, board):
        board.reload([0, 0, 0, 0, 0, 0, 10, 1, 1, 1, 1, 1, 1, 20])
        assert board.is_end()

    def test_end_of_game_opponent_side(self, board):
        board.reload([0, 0, 0, 0, 0, 1, 10, 0, 0, 0, 0, 0, 0, 20])
        assert board.is_end()

    def test_not_end_of_game(self, board):
        board.reload([0, 0, 0, 0, 2, 0, 10, 1, 1, 1, 1, 1, 1, 20])
        assert not board.is_end()

    def test_winner_is_opponent(self, board, opponent):
        board.reload([0, 0, 0, 0, 0, 0, 10, 1, 1, 1, 1, 1, 1, 20])
        assert board.winner() == opponent

    def test_winner_is_me(self, board, me):
        board.reload([0, 0, 0, 0, 0, 0, 30, 1, 1, 1, 1, 1, 1, 20])
        assert board.winner() == me

    def test_winner_is_not_decided(self, board, me):
        board.reload([0, 0, 0, 1, 0, 0, 30, 1, 1, 1, 1, 1, 1, 20])
        assert board.winner() == None

    def test_draw(self, board, me):
        board.reload([0, 0, 0, 0, 0, 0, 20, 1, 1, 1, 1, 1, 1, 20])
        assert board.winner() == None
