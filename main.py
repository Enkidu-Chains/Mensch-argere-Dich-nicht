import random
from enum import IntEnum, Enum
from typing import Generator

# The code implements all parts of the project, and a bit more. (Python version 3.11)

# All the exception cases were made for debugging purposes.

#  Additional stuff


def contains_duplicates(l: list) -> bool:
	"""
	Checks the list on duplicates.
	:param l: A list to check
	:return: True if the list contains duplicates, otherwise False.
	"""
	for i in range(len(l)):
		for j in range(i + 1, len(l)):
			if l[i] is l[j] or l[i] == l[j]:
				return True

	return False


def value_error(note: str) -> ValueError:
	"""
	Makes a value error with the note string.
	:param note: A note to add to an error.
	:return: A ValueError with the note.
	"""
	error: ValueError = ValueError()
	error.add_note(note)
	return error


def exception(note: str) -> Exception:
	"""
	Makes a general exception with the note.
	:param note: A note to add to an exception.
	:return: An Exception with the note.
	"""
	ex: Exception = Exception()
	ex.add_note(note)
	return ex


#  Domain


class Vector2D:
	_x: int
	_y: int

	def __init__(self, x: int, y: int):
		"""
		:param x: x coordinate.
		:param y: y coordinate.
		"""
		self._x = x
		self._y = y

	@property
	def x(self) -> int:
		return self._x

	@property
	def y(self) -> int:
		return self._y

	def __add__(self, other: 'Vector2D') -> 'Vector2D':
		"""
		Adds two vectors.
		:param other: A vector to add.
		:return: A new vector that is the result of adding two vectors.
		"""
		return Vector2D(self.x + other.x, self.y + other.y)

	def __mul__(self, scalar: int) -> 'Vector2D':
		"""
		Multiplies a vector by the scalar.
		:param scalar: A scalar to multiply a vector by.
		:return: A new vector with scaled coordinates.
		"""
		return Vector2D(self.x * scalar, self.y * scalar)

	def __eq__(self, other: 'Vector2D') -> bool:
		"""
		Checks whether two vectors are equal.
		:param other: Another vector
		:return: True if two vectors have the same coordinates, otherwise False.
		"""
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
		"""
		Sets a state of a piece to a new state, also changes the distance property based on new state.
		:param new_state: A new states to set a piece to.
		"""
		self._state, self._distance = (new_state, 0) if new_state is PieceState.InPlay else (new_state, None)

	def move(self, distance: int):
		"""
		Increases the distance from the start. The piece should be in play.
		:param distance: A distance to increase. Should be bigger than 0.
		"""
		if self._state is not PieceState.InPlay:
			raise exception('Piece may not be moved if it is not in play.')
		if 0 >= distance:
			raise value_error('Distance to move may not be less or equal to 0')

		self._distance += distance


class Player:
	_pieces: list[Piece]
	_side: Side

	def __init__(self, pieces: list[Piece], side: Side):
		"""
		:param pieces: A set of piece the new player has.
		:param side: A side of the new player.
		"""
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
	def k(self) -> int:  # I haven't made up a better name.
		# But that calculation happens quiet a bit (7 times), so I decided to make it a separate property.
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
		"""
		Checks if the cell with the coordinates x, y is an empty cell.
		:param x: x coordinates.
		:param y: y coordinates.
		:return: True if the cell is empty, otherwise False.
		"""
		return x not in self.middle_range and y not in self.middle_range

	def is_it_center(self, x: int, y: int):
		"""
		Checks if the cell is the center of the board.
		:param x: x coordinates.
		:param y: y coordinates.
		:return: True if the cell is the center, otherwise False.
		"""
		return x == y == self.half_size

	def is_it_house(self, x: int, y: int):
		"""
		Checks if the cell is a house.
		:param x: x coordinates.
		:param y: y coordinates.
		:return: True if the cell is a house, otherwise False.
		"""
		return (x == self.half_size or y == self.half_size) and x not in [0, self.size - 1] and y not in [0, self.size - 1]


class Dice:
	_max_roll_value: int
	_min_roll_value: int

	def __init__(self, max_roll: int, min_roll: int):
		"""
		:param max_roll: The maximal number on the dice.
		:param min_roll: The minimal number on the dice.
		"""
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
		"""
		:param board_size: A size of the board.
		:param players: A list of players.
		:param dice: Dice.
		"""
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
		"""
		Rolls the dice.
		:param dice: Dice to roll.
		:return: A random number on the dice. (from min roll to max roll including)
		"""
		return random.randrange(dice.get_min_roll_value, dice.get_max_roll_value + 1)


class PositionService:
	def get_piece_position(self, board: Board, piece: Piece, side: Side) -> Vector2D:
		"""
		Gets piece position on the board.
		:param board: A board
		:param piece: A piece
		:param side: The side of the piece (stores in player)
		:return: A vector with its coordinates on the board.
		"""
		if piece.state != PieceState.InPlay:
			raise value_error('Piece must be in play to get it\'s position.')

		rotation_coefficient: int = piece.distance // board.one_side_length + side.value
		direction: Vector2D = self._get_direction_from_distance(board, piece.distance % board.one_side_length)
		position: Vector2D = board.start_position + direction

		for _ in range(rotation_coefficient):
			position = self._rotate_90_counter_clockwise(position)

		return position + board.position_shift

	def get_piece_position_in_house(self, board: Board, side: Side, house_number: int):
		"""
		Gets a piece position in a house.
		:param board: A board.
		:param side: The side of the piece. (Stores in player)
		:param house_number: A house number. (Preferably the index of a piece)
		:return: A vector with its coordinates in the house.
		"""
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
		"""
		Prints the board with the pieces of the players.
		:param board: A board to print.
		:param players: Players to print on the board.
		"""
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
			char: str = self.board_side_to_piece_char(player.side)

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

	def board_side_to_piece_char(self, side: Side) -> str:
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
		"""
		Puts the piece in the base by changing its state to InBase.
		:param piece: A piece to put in the base.
		"""
		piece.change_state(PieceState.InBase)

	def put_in_the_play(self, piece: Piece):
		"""
		Puts the piece in play by changing its state to InPlay.
		:param piece: A piece to put in play.
		"""
		piece.change_state(PieceState.InPlay)

	def put_in_the_house(self, piece: Piece):
		"""
		Puts the piece in a house by changing its state to InHouse.
		:param piece: A piece to put in a house.
		"""
		piece.change_state(PieceState.InHouse)

	def move_by(self, piece: Piece, distance: int):
		"""
		Moves the piece by the distance.
		:param piece: A piece to move.
		:param distance: A distance to move the piece by.
		"""
		piece.move(distance)


class PlayerService:
	_dice_service: DiceService
	_piece_service: PieceService
	_board_render: BoardRenderer

	def __init__(self):
		self._dice_service = DiceService()
		self._piece_service = PieceService()
		self._board_render = BoardRenderer()

	def play(self, player: Player, dice: Dice):
		"""
		A turn of the player.
		:param player: A player which a turn is.
		:param dice: Dice to roll by the player.
		"""
		for i in range(3):
			dice_number: int = self._dice_service.roll(dice)
			move_or_put_piece: int = random.randrange(2)
			piece_in_play: Piece | None = self._chose_piece_with_state(player, PieceState.InPlay)
			piece_in_base: Piece | None = self._chose_piece_with_state(player, PieceState.InBase)

			print(f"The number on the dice for player {self._board_render.board_side_to_piece_char(player.side)}: {dice_number}", end=" ")

			if dice_number != dice.get_max_roll_value and piece_in_play is not None:
				self._piece_service.move_by(piece_in_play, dice_number)
				print("- move", end="\n")
				return
			elif dice_number != dice.get_max_roll_value and piece_in_play is None:
				print("- no piece to move", end="\n")
				return

			if (move_or_put_piece == 0 and piece_in_play is not None) or (move_or_put_piece == 1 and piece_in_base is None):
				self._piece_service.move_by(piece_in_play, dice_number)
				print("- move", end="\n")

			if (move_or_put_piece == 0 and piece_in_play is None) or (move_or_put_piece == 1 and piece_in_base is not None):
				self._piece_service.put_in_the_play(piece_in_base)
				print("- put a piece on the board", end="\n")

	def _chose_piece_with_state(self, player: Player, state: PieceState) -> Piece | None:
		pieces_in_play: list = [piece for piece in player.pieces if piece.state == state]
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
		"""
		Creates a game with the particular size of the board.
		:param board_size: A number of how long is on side of the board should be. (Only odd values bigger than 3)
		:param number_of_players: A number of players to play.
		:return: A game.
		"""
		sides: list[Side] = [Side.Top, Side.Bottom, Side.Right, Side.Left]
		dice: Dice = Dice(6, 1)
		number_of_pieces_per_player: int = (board_size - 3) // 2
		players: list[Player] = [Player([Piece() for _ in range(number_of_pieces_per_player)], sides[i]) for i in range(number_of_players)]
		return Game(board_size, players, dice)

	def run(self, game: Game):
		"""
		Runs the game simulation.
		:param game: A game to run a simulation for.
		"""
		while True:
			self._board_renderer.render_board(game.board, game.players)

			for player in game.players:
				if self._did_player_win(player):
					print(f"Player {self._board_renderer.board_side_to_piece_char(player.side)} won!!!", end="\n")
					return

				self._player_service.play(player, game.dice)
				self._attack(game, player)
				self._put_pieces_in_the_house(game, player)

	def _attack(self, game: Game, attacker: Player):
		for piece_attacker in attacker.pieces:
			if piece_attacker.state != PieceState.InPlay:
				continue

			position1: Vector2D = self._position_service.get_piece_position(game.board, piece_attacker, attacker.side)

			for attacked in game.players:
				if attacked is attacker:
					continue

				for attacked_piece in attacked.pieces:
					if attacked_piece.state != PieceState.InPlay:
						continue

					position2: Vector2D = self._position_service.get_piece_position(game.board, attacked_piece, attacked.side)

					if position1 == position2:
						self._piece_service.put_in_the_base(attacked_piece)
						print(f"Player {self._board_renderer.board_side_to_piece_char(attacker.side)} attacked player {self._board_renderer.board_side_to_piece_char(attacked.side)}", end="\n")

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
