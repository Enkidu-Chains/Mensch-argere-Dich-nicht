import random
from enum import IntEnum
from typing import Generator


# The code implements all parts of the project, and a bit more. (Python version 3.11)


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


class Vector2D:
	_x: int
	_y: int

	def __init__(self, x: int, y: int):
		self._x = x
		self._y = y

	@property
	def x(self) -> int:
		return self._x

	@property
	def y(self) -> int:
		return self._y

	def __add__(self, other: 'Vector2D') -> 'Vector2D':
		return Vector2D(self.x + other.x, self.y + other.y)

	def __mul__(self, scalar: int) -> 'Vector2D':
		return Vector2D(self.x * scalar, self.y * scalar)

	def __eq__(self, other: 'Vector2D') -> bool:
		return self.x == other.x and self.y == other.y


class Side(IntEnum):
	Top = 0,
	Right = 1,
	Bottom = 2,
	Left = 3


class PieceState(IntEnum):
	InBase = 0
	InPlay = 1
	InHouse = 2


class Piece:
	_state: PieceState
	_distance: int | None  # distance from the start.

	def __init__(self):
		self._state = PieceState.InBase
		self._distance = None

	@property
	def state(self) -> PieceState:
		return self._state

	@property
	def distance(self) -> int | None:
		return self._distance

	def change_state(self, new_state: PieceState):
		self._state, self._distance = (new_state, 0) if new_state is PieceState.InPlay else (new_state, None)

	def move(self, distance: int):
		if self._state is not PieceState.InPlay:
			raise exception('Piece may not be moved if it is not in play.')
		if 0 >= distance:
			raise value_error('Distance to move may not be less or equal to 0')

		self._distance += distance


class Player:
	_pieces: list[Piece]
	_side: Side

	def __init__(self, pieces: list[Piece], side: Side):
		self._set_pieces(pieces)
		self._set_side(side)

	@property
	def pieces(self) -> list[Piece]:
		return self._pieces

	def _set_pieces(self, pieces: list[Piece]):
		if contains_duplicates(pieces):
			raise value_error('Pieces must be unique entities.')
		if len(pieces) < 1:
			raise value_error('Player can\'t have 0 pieces.')

		self._pieces = pieces

	@property
	def side(self) -> Side:
		return self._side

	def _set_side(self, side: Side):
		self._side = side


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
		# But that calculation happens quiet a bit, so I decided to make it a separate property.
		return self.half_size - 1

	@property
	def one_side_length(self):
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

	@property
	def track_length(self) -> int:
		return 4 * self.one_side_length

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


class Dice:
	_max_roll_value: int
	_min_roll_value: int

	def __init__(self, max_roll: int, min_roll: int):
		if max_roll < min_roll:
			raise value_error('Max roll value can\'t be smaller than min roll value.')
		self._max_roll_value = max_roll
		self._min_roll_value = min_roll

	@property
	def get_max_roll_value(self) -> int:
		return self._max_roll_value

	@property
	def get_min_roll_value(self) -> int:
		return self._min_roll_value


class Game:
	_players: list[Player]
	_board: Board
	_dice: Dice

	def __init__(self, board_size: int, players: list[Player], dice: Dice):
		self._set_players(players)
		self._set_board(board_size)
		self._set_dice(dice)

	@property
	def board(self) -> Board:
		return self._board

	def _set_board(self, board_size: int):
		self._board = Board(board_size)

	@property
	def players(self) -> list[Player]:
		return self._players

	def _set_players(self, players: list[Player]):
		if 2 > len(players) or 4 < len(players):
			raise value_error('The number of players should be from 2 to 4.')
		if not self._are_players_unique_entities(players):
			raise value_error('Players should be unique entities and they should be on different sides.')
		self._players = players

	@property
	def dice(self) -> Dice:
		return self._dice

	def _set_dice(self, dice: Dice):
		self._dice = dice

	def _are_players_unique_entities(self, players: list[Player]) -> bool:
		for i in range(len(players)):
			for j in range(i + 1, len(players)):
				if players[i] is players[j] or players[i].side == players[j].side:
					return False

		return True


#  Application


class DiceService:
	def roll(self, dice: Dice) -> int:
		return random.randrange(dice.get_min_roll_value, dice.get_max_roll_value + 1)


class PositionService:
	def get_piece_position(self, board: Board, piece: Piece, side: Side) -> Vector2D:
		if piece.state != PieceState.InPlay:
			raise value_error('Piece must be in play to get it\'s position.')

		rotation_coefficient: int = piece.distance // board.one_side_length + side.value
		direction: Vector2D = self._get_direction_from_distance(board, piece.distance % board.one_side_length)
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

	def _get_direction_from_distance(self, board: Board, distance: int):
		if distance >= (2 * board.k):
			return Vector2D(board.k, board.k + distance % board.k)

		if distance > board.k:
			return Vector2D(distance % board.k, board.k)

		return Vector2D(0, distance % board.half_size)

	def _rotate_90_counter_clockwise(self, vector: Vector2D) -> Vector2D:
		return Vector2D(-vector.y, vector.x)


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
			char: str = self._board_side_to_piece_char(player.side)

			for piece in player.pieces:
				if piece.state is PieceState.InPlay:
					position: Vector2D = self._position_service.get_piece_position(board, piece, player.side)
					yield position, char

				if piece.state is PieceState.InHouse:
					position: Vector2D = self._position_service.get_piece_position_in_house(
						board,
						player.side,
						house_number=player.pieces.index(piece) + 1)
					yield position, char

	def _print_board_matrix(self, board_matrix: list[list[str]]):
		print(end='\n')
		for row in board_matrix:
			for element in row:
				print(element, end=' ')
			print(end='\n')
		print(end='\n')

	def _put_pieces_onto_board(self, pieces: list[tuple[Vector2D, str]], board_matrix: list[list[str]]):
		for position, char in pieces:
			board_matrix[position.y][position.x] = char

	def _get_board_element_on(self, board: Board, x: int, y: int) -> str:
		if board.is_it_empty_cell(x, y):
			return ' '
		if board.is_it_center(x, y):
			return 'X'
		if board.is_it_house(x, y):
			return 'O'

		return '*'

	def _board_side_to_piece_char(self, side: Side) -> str:
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
	def put_in_the_base(self, piece: Piece):
		piece.change_state(PieceState.InBase)

	def put_in_the_play(self, piece: Piece):
		piece.change_state(PieceState.InPlay)

	def put_in_the_house(self, piece: Piece):
		piece.change_state(PieceState.InHouse)

	def move_by(self, piece: Piece, distance: int):
		try:
			piece.move(distance)
		except BaseException as ex:
			print(ex)


class PlayerService:
	_dice_service: DiceService
	_piece_service: PieceService

	def __init__(self):
		self._dice_service = DiceService()
		self._piece_service = PieceService()

	def play(self, player: Player, dice: Dice):
		for i in range(3):
			dice_number: int = self._dice_service.roll(dice)

			if dice_number != dice.get_max_roll_value:
				self._try_to_move_piece_by(self._chose_piece(player), dice_number)
				return

			move_or_put_piece: int = random.randrange(2)

			if move_or_put_piece == 0 and not self._try_to_put_piece_in_the_play(player):
				self._try_to_move_piece_by(self._chose_piece(player), dice_number)
			if move_or_put_piece == 1 and not self._try_to_move_piece_by(self._chose_piece(player), dice_number):
				self._try_to_put_piece_in_the_play(player)

	def _try_to_put_piece_in_the_play(self, player: Player) -> bool:
		for piece in player.pieces:
			if piece.state == PieceState.InBase:
				self._piece_service.put_in_the_play(piece)
				return True

		return False

	def _try_to_move_piece_by(self, piece: Piece | None, distance: int) -> bool:
		if piece is None:
			return False

		self._piece_service.move_by(piece, distance)
		return True

	def _chose_piece(self, player: Player) -> Piece | None:
		pieces_in_play: list = [piece for piece in player.pieces if piece.state == PieceState.InPlay]
		if len(pieces_in_play) == 0:
			return None

		index: int = random.randrange(0, len(pieces_in_play))

		return pieces_in_play[index]


class GameService:
	_board_renderer: BoardRenderer
	_piece_service: PieceService
	_player_service: PlayerService
	_position_service: PositionService

	def __init__(self):
		self._piece_service = PieceService()
		self._player_service = PlayerService()
		self._position_service = PositionService()
		self._board_renderer = BoardRenderer()

	def create_game(self, board_size: int, number_of_players: int) -> Game:
		sides: list[Side] = [Side.Top, Side.Bottom, Side.Right, Side.Left]
		dice: Dice = Dice(6, 1)
		number_of_pieces_per_player: int = (board_size - 3) // 2
		players: list[Player] =\
			[Player([Piece() for _ in range(number_of_pieces_per_player)], sides[i]) for i in range(number_of_players)]
		return Game(board_size, players, dice)

	def run(self, game: Game):
		while True:
			self._board_renderer.render_board(game.board, game.players)
			
			for player in game.players:
				if self._did_player_win(player):
					return

				self._player_service.play(player, game.dice)
				self._attack(game, player)
				self._put_pieces_in_the_house(game, player)

	def _attack(self, game: Game, attacker: Player):
		for piece_attacker in attacker.pieces:
			if piece_attacker.state != PieceState.InPlay:
				continue

			position1: Vector2D = self._position_service.get_piece_position(
				game.board, piece_attacker, attacker.side
			)
			for attacked in game.players:
				if attacked is attacker:
					continue

				for attacked_piece in attacked.pieces:
					if attacked_piece.state != PieceState.InPlay:
						continue

					position2: Vector2D = self._position_service.get_piece_position(
						game.board, attacked_piece, attacked.side
					)

					if position1 == position2:
						self._piece_service.put_in_the_base(attacked_piece)

	def _put_pieces_in_the_house(self, game: Game, player: Player):
		for piece in player.pieces:
			if piece.state == PieceState.InPlay and piece.distance > game.board.track_length:
				self._piece_service.put_in_the_house(piece)

	def _did_player_win(self, player: Player):
		for piece in player.pieces:
			if piece.state != PieceState.InHouse:
				return False
		
		return True


#  Run script


if __name__ == '__main__':
	board_size: int = int(input('Type a board size (should be an odd number bigger than or equal to 5):\n'))
	number_of_players: int = int(input('Type a number of players (from 2 to 4):\n'))

	game_service: GameService = GameService()
	game: Game = game_service.create_game(board_size, number_of_players)
	game_service.run(game)
