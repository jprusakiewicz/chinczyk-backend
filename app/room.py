import json
import random
import uuid
from typing import List, Union

import app.color
from .connection import Connection
from .game import Game
from .server_errors import GameIsStarted, ItsNotYourTurn


class Room:
    def __init__(self, room_id):
        self.winners = []  # !use normal id!
        self.id = room_id
        self.active_connections: List[Connection] = []
        self.is_game_on = False
        self.game: Union[None, Game] = None
        self.whos_turn: str
        self.MAX_PLAYERS = 4
        self.MIN_PLAYERS = 1
        self.game_id: str

    async def append_connection(self, connection):
        if len(self.active_connections) <= self.MAX_PLAYERS and self.is_game_on is False:
            connection.player.game_id = self.get_free_player_game_id()
            self.active_connections.append(connection)
            if len(self.active_connections) >= self.MIN_PLAYERS:
                await self.start_game()
        else:
            raise GameIsStarted

    def get_taken_ids(self) -> List[str]:
        taken_ids = [connection.player.game_id for connection in self.active_connections]
        return taken_ids

    def get_player(self, id):
        player = next(
            connection.player for connection in self.active_connections if connection.player.id == id)
        return player

    def get_players_game_ids_in_game(self):
        players = [connection.player.game_id for connection in self.active_connections if
                   connection.player.in_game]
        return players

    def get_free_player_game_id(self):
        taken_ids = self.get_taken_ids()
        for color in app.color.Color:
            if color not in taken_ids:
                return color.value

    async def remove_connection(self, connection_with_given_ws):
        await self.remove_player_by_id(connection_with_given_ws.player.id)
        self.active_connections.remove(connection_with_given_ws)
        if len(self.active_connections) <= 1:
            await self.end_game()

    async def broadcast_json(self):
        for connection in self.active_connections:
            gs = self.get_game_state(connection.player.id)
            await connection.ws.send_text(gs)

    async def restart_game(self):
        await self.start_game()

    async def start_game(self):
        self.is_game_on = True
        self.whos_turn = self.draw_random_player_id()
        self.game = Game(self.get_taken_ids())
        self.put_all_players_in_game()
        self.game_id = str(uuid.uuid4().hex)
        await self.broadcast_json()

    async def end_game(self):
        self.is_game_on = False
        self.whos_turn = 0
        self.game = None
        self.put_all_players_out_of_game()
        await self.broadcast_json()

    async def remove_player_by_game_id(self, game_id):
        player = next(
            connection.player for connection in self.active_connections if connection.player.game_id == game_id)
        if self.game:

            self.game.remove_players_counters(player.game_id)
            if self.whos_turn == player.game_id:
                self.next_person_move()
            player.in_game = False

            # await self.broadcast_json()

    async def remove_player_by_id(self, id):
        player = next(
            connection.player for connection in self.active_connections if connection.player.id == id)
        if self.game is not None:
            self.game.remove_players_counters(player.game_id)
            if self.whos_turn == player.game_id:
                self.next_person_move()
            player.in_game = False
            print(f"kicked player {player.id}")

    def put_all_players_in_game(self):
        for connection in self.active_connections:
            connection.player.in_game = True

    def put_all_players_out_of_game(self):
        for connection in self.active_connections:
            connection.player.in_game = False

    async def handle_players_move(self, client_id, player_move):
        player = next(
            connection.player for connection in self.active_connections if connection.player.id == client_id)
        self.validate_its_players_turn(player.game_id)

        next_person_move = self.game.handle_players_move(player.game_id, player_move)
        if next_person_move:
            self.next_person_move()

    def next_person_move(self):
        current_player = self.whos_turn
        taken_ids = self.get_taken_ids()
        current_idx = taken_ids.index(current_player)
        try:
            next_person = taken_ids[current_idx + 1]
        except IndexError:
            next_person = taken_ids[0]
        self.whos_turn = next_person

        self.game.roll_the_dice()

    def get_game_state(self, client_id) -> str:
        if self.is_game_on:
            player = next(
                connection.player for connection in self.active_connections if connection.player.id == client_id)
            game_state = dict(is_game_on=self.is_game_on, my_color=player.game_id,
                              whos_turn=str(self.whos_turn), dice=self.game.dice,
                              game_data=self.game.get_current_state(player.game_id), nicks=self.get_nicks())
        else:
            game_state = dict(is_game_on=self.is_game_on, nicks=self.get_nicks())

        return json.dumps(game_state)

    def draw_random_player_id(self):
        return random.choice(self.get_taken_ids())

    @property
    def get_stats(self):
        return {'is_game_on': self.is_game_on,
                "whos turn": self.whos_turn,
                "number_of_connected_players": len(self.active_connections),
                "regular": self.game.regular,
                "finnish": self.game.finnish,
                "idle": self.game.idle}

    def get_nicks(self):
        nicks = {}
        for connection in self.active_connections:
            enemy_color = connection.player.game_id
            nicks[enemy_color] = connection.player.nick
        return nicks

    def validate_its_players_turn(self, player_id):
        if player_id != self.whos_turn:
            raise ItsNotYourTurn

    async def kick_player(self, player_id):
        await self.remove_player_by_id(player_id)

    async def check_and_handle_full_finnish(self, player):
        # if len(self.game.players[player.game_id]) == 0:
        #     print(f"player {player.id} has ended")
        #     self.winners.append(player.id)
        #     await self.remove_player_by_game_id(player.game_id)
        ...  # todo
