import uuid
from random import Random
from typing import List

from .color import Color

r = Random()


class Game:
    def __init__(self, taken_ids: List[str]):
        self.person_turn = 1
        self.idle: dict = self.new_game_idle(taken_ids)
        self.regular: dict = {
            "Red": [],
            "Green": [],
            "Blue": [],
            "Yellow": []}
        self.finnish: dict = {
            "Red": [],
            "Green": [],
            "Blue": [],
            "Yellow": []}
        self.dice: int = 1
        self.turn_id = str(uuid.uuid4())


    def handle_players_move(self, player_color, player_move: dict):
        try:
            if player_move['other']:
                return True

        except KeyError:
            is_finnish: bool = player_move['isFinnish']
            is_idle: bool = player_move['isIdle']
            number: int = player_move['number']

            if player_color != player_move['fieldColor']:
                return False

            if is_idle == True and self.idle[player_color] >= 1 and 1 not in self.regular[player_color] \
                    and self.dice in [1, 6]:
                self.idle[player_color] -= 1
                self.try_remove_counter(1, player_color)
                self.regular[player_color].append(1)
                self.roll_the_dice()
                return False

            elif is_finnish == True and number in self.finnish[player_color]:
                new_finnish = number + self.dice
                if new_finnish > 4 or new_finnish in self.finnish[player_color]:
                    return False
                self.finnish[player_color].append(new_finnish)
                self.finnish[player_color].remove(number)
                return True

            elif is_finnish == False and is_idle == False and number in self.regular[player_color]:
                new_number = number + self.dice
                if new_number > 44 or new_number in self.regular[player_color]:
                    return False
                elif new_number > 40:
                    final_number = new_number - 40
                    if final_number in self.finnish[player_color]:
                        return False
                    self.finnish[player_color].append(final_number)
                else:
                    self.try_remove_counter(new_number, player_color)
                    self.regular[player_color].append(new_number)

                try:
                    self.regular[player_color].remove(number)
                except ValueError:
                    pass
                return True

    def roll_the_dice(self):
        self.dice = r.randint(1, 6)
        self.turn_id = str(uuid.uuid4())

    def get_current_state(self):
        return {
            "idle": self.idle,
            "finnish": self.finnish,
            "regular": self.regular
        }

    def new_game_idle(self, taken_ids: List[str]):
        idle = {
            "Red": 0,
            "Green": 0,
            "Blue": 0,
            "Yellow": 0}
        for taken_id in taken_ids:
            idle[taken_id] = 4
        return idle

    def try_remove_counter(self, number, player_color: str):
        global_number = Game.local_number_to_global(number, Color(player_color))
        for color in Color:
            a = self.get_global_regular_counters()[color.value]
            if global_number in a:
                self.regular[color.value].remove(Game.global_number_to_local(global_number, color))
                self.idle[color.value] += 1

    def get_global_regular_counters(self):
        global_regular_counters = {Color.Red.value: [Game.local_number_to_global(counter, Color.Red) for counter in
                                                     self.regular[Color.Red.value]],
                                   Color.Green.value: [Game.local_number_to_global(counter, Color.Green) for counter in
                                                       self.regular[Color.Green.value]],
                                   Color.Yellow.value: [Game.local_number_to_global(counter, Color.Yellow) for counter
                                                        in self.regular[Color.Yellow.value]],
                                   Color.Blue.value: [Game.local_number_to_global(counter, Color.Blue) for counter in
                                                      self.regular[Color.Blue.value]]}
        return global_regular_counters

    @staticmethod
    def local_number_to_global(number: int, color: Color) -> int:
        RED_OFFSET = 30
        GREEN_OFFSET = 20
        YELLOW_OFFSET = 10

        if color == Color.Yellow:
            number += YELLOW_OFFSET
        elif color == Color.Green:
            number += GREEN_OFFSET
        elif color == Color.Red:
            number += RED_OFFSET

        if number > 40:
            number -= 40
        return number

    @staticmethod
    def global_number_to_local(number: int, color: Color) -> int:
        RED_OFFSET = 30
        GREEN_OFFSET = 20
        YELLOW_OFFSET = 10

        if color == Color.Yellow:
            number -= YELLOW_OFFSET
        elif color == Color.Green:
            number -= GREEN_OFFSET
        elif color == Color.Red:
            number -= RED_OFFSET
        if number < 0:
            number += 40
        return number

    def remove_players_counters_from_regular_and_idle_fields(self, game_id):
        self.regular[game_id] = []
        self.idle[game_id] = 0
