import random
from enum import IntEnum
from typing import Generator


#  Additional stuff


def is_null_or_empty(string: str) -> bool:
	return string.strip() == '' or string.strip() is None


def contains_duplicates(l: list) -> bool:
	for i in range(len(l)):
		for j in range(i + 1, len(l)):
			if l[i] is l[j] or l[i] == l[j]:
				return True

	return False


def value_error(note: str) -> ValueError:
	error: ValueError = ValueError()
	error.add_note(note)
	return error


def exception(note: str) -> Exception:
	ex: Exception = Exception()
	ex.add_note(note)
	return ex


#  Domain


class Dice:
	@staticmethod
	def roll():
		return random.randrange(1, 7, 1)


class Vector2D:
	x: int
	y: int

	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y

	def __add__(self, other: 'Vector2D') -> 'Vector2D':
		return Vector2D(self.x + other.x, self.y + other.y)

	def __mul__(self, other: int) -> 'Vector2D':
		return Vector2D(self.x * other, self.y * other)


class Side(IntEnum):
	Top = 0,
	Right = 1,
	Bottom = 2,
	Left = 3


class PieceState(IntEnum):
	OutOfTheGame = 0
	InTheGame = 1
	InTheHouse = 2


class Piece:
	_state: PieceState
	_distance: int | None

	def __init__(self):
		self._state = PieceState.OutOfTheGame
		self._distance = None

	def get_state(self) -> PieceState:
		return self._state

	def get_distance(self) -> int | None:
		return self._distance

	def change_state(self, new_state: PieceState):
		self._state, self._distance = (new_state, 0) if new_state is PieceState.InTheGame else (new_state, None)

	def move(self, distance: int):
		if self._state is not PieceState.InTheGame:
			raise exception('Piece may not be moved if it is not in the game.')
		if 0 >= distance or distance > 6:
			raise value_error('Distance to move may not be less or equal to 0 or greater than 6.')\

		self._distance += distance


class Player:
	_nickname: str
	_pieces: list[Piece]
	_side: Side

	def __init__(self, nickname: str, pieces: list[Piece], side: Side):
		self._set_nickname(nickname)
		self._set_pieces(pieces)
		self._set_side(side)

	def get_nickname(self) -> str:
		return self._nickname

	def _set_nickname(self, nickname: str):
		if is_null_or_empty(nickname):
			raise value_error('Nickname can\'t be empty.')

		self._nickname = nickname

	def get_pieces(self) -> list[Piece]:
		return self._pieces

	def _set_pieces(self, pieces: list[Piece]):
		if contains_duplicates(pieces):
			raise value_error('Pieces must be unique entities.')
		if len(pieces) < 1:
			raise value_error('Player can\'t have 0 pieces.')

		self._pieces = pieces

	def get_side(self) -> Side:
		return self._side

	def _set_side(self, side: Side):
		self._side = side

	pass


# todo redo a bit
class Game:
	_board_size: int
	_players: list[Player]

	def __init__(self, board_size: int, players: list[Player]):
		self._set_board_size(board_size)
		self._set_players(players)

	def get_board_size(self) -> int:
		return self._board_size

	def _set_board_size(self, size: int):
		if size % 2 == 0 or size < 5:
			raise value_error('Size should be an odd number and grater than or equal to 5.')

		self._size = size

	def get_players(self) -> list[Player]:
		return self._players

	def _set_players(self, players: list[Player]):
		if 2 < len(players) <= 4:
			raise value_error('The number of players should be from 2 to 4.')
		if not self.are_players_unique_entities(players):
			raise value_error('Players should be unique entities.')

	@staticmethod
	def are_players_unique_entities(players: list[Player]) -> bool:
		for i in range(len(players)):
			for j in range(i + 1, len(players)):
				if players[i] is players[j]:
					return False

		return True


class Board:
	_size: int

	def __init__(self, size: int):
		self._set_size(size)

	@property
	def size(self) -> int:
		return self._size

	@property
	def half_size(self) -> int:
		return self.size // 2

	@property
	def k(self) -> int:  # I haven't made up a better name due to the lack of proficiency.
		return self.half_size - 1

	@property
	def max_one_quarter_dist(self):
		return self.size - 1

	@property
	def start_position(self) -> Vector2D:
		return Vector2D(1, -self.half_size)

	@property
	def start_house_position(self) -> Vector2D:
		return Vector2D(0, -1)

	@property
	def position_shift(self) -> Vector2D:
		return Vector2D(self.half_size, self.half_size)

	@property
	def middle_range(self) -> range:
		return range(self.half_size - 1, self.half_size + 2)

	def _set_size(self, size: int):
		if size % 2 == 0 or size < 5:
			raise value_error('Size should be an odd number and grater than or equal to 5.')

		self._size = size

	def is_it_empty_cell(self, x: int, y: int):
		return x not in self.middle_range and y not in self.middle_range

	def is_it_center(self, x: int, y: int):
		return x == y == self.half_size

	def is_it_house(self, x: int, y: int):
		return (x == self.half_size or y == self.half_size) and x not in [0, self.size - 1] and y not in [0, self.size - 1]


#  Application


class PositionService:
	def get_piece_position(self, board: Board, piece: Piece, side: Side) -> Vector2D:
		rotation_coefficient: int = piece.get_distance() // board.max_one_quarter_dist + side.value
		direction: Vector2D = self._get_direction_from_distance(board, piece.get_distance() % board.max_one_quarter_dist)
		position: Vector2D = board.start_position + direction

		for _ in range(rotation_coefficient):
			position = self._rotate_90_counter_clockwise(position)

		return position + board.position_shift

	def get_piece_position_in_house(self, board: Board, side: Side, house_number: int):
		if house_number >= board.half_size or house_number < 1:
			raise value_error(
				f'The house number must be between 0 and {board.half_size} excluded. (0, {board.half_size})')

		rotation_coefficient: int = side.value
		position: Vector2D = board.start_house_position * house_number

		for _ in range(rotation_coefficient):
			position = self._rotate_90_counter_clockwise(position)

		return position + board.position_shift

	@staticmethod
	def _get_direction_from_distance(board: Board, distance: int):
		if distance >= (2 * board.k):
			return Vector2D(board.k, board.k + distance % board.k)

		if distance > board.k:
			return Vector2D(distance % board.k, board.k)

		return Vector2D(0, distance % board.half_size)

	@staticmethod
	def _rotate_90_counter_clockwise(vector: Vector2D) -> Vector2D:
		return Vector2D(-vector.y, vector.x)

	pass


class BoardRenderer:
	_position_service: PositionService

	def __init__(self):
		self._position_service = PositionService()

	def render_board(self, board: Board, players: list[Player]):
		board_matrix: list[list[str]] = list(self._default_board(board))
		pieces: list[tuple[Vector2D, str]] = list(self._get_renderable_pieces(board, players))
		self._put_pieces_onto_board(pieces, board_matrix)
		self._print_board_matrix(board_matrix)

	def _default_board(self, board: Board) -> Generator[list[str], None, None]:
		for y in range(board.size):
			row: list[str] = [self._get_board_element_on(board, x, y) for x in range(board.size)]
			yield row

	def _get_renderable_pieces(self, board: Board, players: list[Player]) -> Generator[tuple[Vector2D, str], None, None]:
		for player in players:
			char: str = self._board_side_to_piece_char(player.get_side())

			for piece in player.get_pieces():
				if piece.get_state() is PieceState.InTheGame:
					position: Vector2D = self._position_service.get_piece_position(board, piece, player.get_side())
					yield position, char

				if piece.get_state() is PieceState.InTheHouse:
					position: Vector2D = self._position_service.get_piece_position_in_house(
						board,
						player.get_side(),
						house_number=player.get_pieces().index(piece) + 1)
					yield position, char

	@staticmethod
	def _print_board_matrix(board_matrix: list[list[str]]):
		for row in board_matrix:
			for element in row:
				print(element, end='')
			print(end='\n')

	@staticmethod
	def _put_pieces_onto_board(pieces: list[tuple[Vector2D, str]], board_matrix: list[list[str]]):
		for position, char in pieces:
			board_matrix[position.y][position.x] = char

	@staticmethod
	def _get_board_element_on(board: Board, x: int, y: int) -> str:
		if board.is_it_empty_cell(x, y):
			return ' '
		if board.is_it_center(x, y):
			return 'X'
		if board.is_it_house(x, y):
			return 'O'

		return '*'

	@staticmethod
	def _get_colour_of_char(side: Side) -> str:
		match side:
			case Side.Top:
				return 'red'
			case Side.Right:
				return 'yellow'
			case Side.Bottom:
				return 'blue'
			case side.Left:
				return 'green'
			case _:
				raise exception('There is no such side.')

	@staticmethod
	def _board_side_to_piece_char(side: Side) -> str:
		match side:
			case Side.Top:
				return 'A'
			case Side.Right:
				return 'B'
			case Side.Bottom:
				return 'C'
			case side.Left:
				return 'D'
			case _:
				raise exception('There is no such side.')


class PieceService:
	pass


class PlayerService:
	pass


class GameService:
	pass


#  Run script


if __name__ == '__main__':
	players: list[Player] = [
		Player('hello', [Piece(), Piece(), Piece(), Piece(), Piece()], Side.Top),
		Player('hello2', [Piece(), Piece(), Piece(), Piece(), Piece()], Side.Bottom),
		Player('hello3', [Piece(), Piece(), Piece(), Piece(), Piece()], Side.Right)
	]
	for i in range(5):
		for player in players:
			state: PieceState = PieceState(random.randrange(0, 3, step=1))

			player.get_pieces()[i].change_state(state)

			if player.get_pieces()[i].get_state() is PieceState.InTheGame:
				player.get_pieces()[i].move(Dice().roll())

	BoardRenderer().render_board(Board(13), players)
