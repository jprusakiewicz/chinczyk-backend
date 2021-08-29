from random import Random
from typing import List

r = Random()  # todo


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

    #     self.is_blocked = False
    #     self.stack: List[Card] = self.set_full_deck()
    #     self.pile: List[str] = [self.get_nonfunctional_card().code]
    #     self.players: dict = self.get_new_game_cards(number_of_players)

    # def shuffle_deck(self):
    #     shuffle(self.stack)
    #
    # @staticmethod
    # def set_full_deck() -> List[Card]:
    #     cards = []
    #     prod = list(product(Figure, Color))
    #     for p in prod:
    #         card = Card(p[0], p[1])
    #         cards.append(card)
    #     cards.remove(
    #         next(c for c in cards if c.figure == Figure.Joker and c.color == Color.Spades))  # theres no spades joker
    #     shuffle(cards)
    #     return cards
    #
    # def get_new_game_cards(self, number_of_players: int):
    #     players = {}
    #     if number_of_players > 4 or number_of_players <= 1:
    #         raise ValueError  # todo except this
    #     for player_id in range(number_of_players):
    #         player_cards = []
    #         while len(player_cards) != 4:
    #             player_cards.append(self.get_card().code)
    #         players[str(player_id + 1)] = player_cards
    #     return players  # todo

    def handle_players_move(self, player_color, player_move: dict):
        is_finnish: bool = player_move['isFinnish']
        is_idle: bool = player_move['isIdle']
        number: int = player_move['number']

        if is_idle == True and self.idle[player_color] >= 1 and 1 not in self.regular[player_color]:
            self.idle[player_color] -= 1
            self.regular[player_color].append(1)
            return True

        elif is_finnish == True:
            new_finnish = number + self.dice
            if new_finnish > 4 or new_finnish in self.finnish[player_color]:
                return False
            self.finnish[player_color].append(new_finnish)
            self.finnish[player_color].remove(number)
            return True

        elif is_finnish == False and is_idle == False:
            new_number = number + self.dice
            if new_number > 44 or new_number in self.regular[player_color]:
                return False
            elif new_number > 40:
                final_number = new_number - 40
                if final_number in self.finnish[player_color]:
                    return False
                self.finnish[player_color].append(final_number)
            else:
                self.regular[player_color].append(new_number)

            try:
                self.regular[player_color].remove(number)
            except ValueError:
                pass
            return True

    def roll_the_dice(self):
        self.dice = r.randint(1, 6)

    # def handle_players_other_move(self, player_id, player_move: dict):
    #     other_move = player_move['other_move']
    #     type = other_move['type']
    #     if type == "pick_new_card" and self.is_blocked is False:
    #         self.pick_new_card(player_id)
    #         self.can_skip = True
    #
    #     elif type == "skip" and self.can_skip:
    #         self.is_blocked = False
    #         return True

    # @staticmethod
    # def set_deck(cards_in_game: List[Card]) -> List[Card]:
    #     all_cards = Game.set_full_deck()
    #     all_cards_not_in_game = []
    #     if not any(cards_in_game):
    #         return all_cards
    #     for card in all_cards:
    #         if card not in cards_in_game:
    #             all_cards_not_in_game.append(card)
    #     return all_cards_not_in_game

    # def get_card(self) -> Card:
    #     if len(self.stack) == 0:
    #         self.stack.extend(map(lambda x: Card.from_code(x), self.used_cards))
    #         self.used_cards = []
    #     return self.stack.pop()

    # def get_nonfunctional_card(self) -> Card:
    #     while Card.is_functional(self.stack[-1]):
    #         self.shuffle_deck()
    #     return self.get_card()

    # def remove_players_cards(self, game_id):
    #     self.used_cards.extend(self.players[game_id])
    #     self.players[game_id] = []
    #
    # def get_player(self, _id: str):
    #     return self.players[_id]
    #
    # def is_card_in_players_hand(self, player_id: str, picked_card: str):
    #     if picked_card not in self.get_player(player_id):
    #         return False
    #     return True
    #
    # def can_put_on_pile(self, picked_card: str) -> bool:
    #     can_put = False
    #     players_card = Card.from_code(picked_card)
    #     pile_card = Card.from_code(self.pile[-1])  # todo 0 or -1
    #
    #     # króle
    #     if pile_card.figure == Figure.King and pile_card.color == Color.Spades \
    #             or pile_card.figure == Figure.King and pile_card.color == Color.Hearts:
    #         if players_card.figure == Figure.King and players_card.color == Color.Diamonds \
    #                 or players_card.figure == Figure.King and players_card.color == Color.Clubs \
    #                 or self.pick_count == 1:
    #             can_put = True
    #
    #     elif self.is_blocked is False or self.is_blocked is True and players_card.figure == Figure.Four:
    #         if self.pick_count == 1 or players_card.figure == Figure.Two or players_card.figure == Figure.Three or pile_card.figure == Figure.Joker:
    #             if self.color_call is not None:
    #                 can_put = self.color_call == players_card.color
    #                 self.color_call = None
    #             elif self.figure_call is not None:
    #                 can_put = self.figure_call == players_card.figure
    #                 self.figure_call = None
    #             elif players_card.color == pile_card.color or players_card.figure == pile_card.figure \
    #                     or players_card.figure == Figure.Joker or players_card.figure == Figure.Queen \
    #                     or pile_card.figure == Figure.Queen or pile_card.figure == Figure.Joker:
    #                 can_put = True
    #             else:
    #                 print("can not put this card on pile")
    #     return can_put
    #
    # def remove_cards_from_players_hand(self, player_id: str, card: str):
    #     self.players[player_id].remove(card)
    #
    # def pick_new_card(self, player_id):
    #     try:
    #         for i in range(self.pick_count):
    #             self.players[player_id].append(self.get_card().code)
    #     except IndexError:
    #         print("no cards in stack!!!")
    #     self.pick_count = 1
    #
    # def reset_parameters(self):
    #     self.reverse = False
    #     if self.is_blocked is False:
    #         self.can_skip = False
    #
    def get_current_state(self, player_id):
        return {
            "idle": self.idle,
            "finnish": self.finnish,
            "regular": self.regular
        }

    #
    # def handle_two(self):
    #     if self.pick_count == 1:
    #         self.pick_count = 2
    #     else:
    #         self.pick_count += 2
    #
    # def handle_three(self):
    #     if self.pick_count == 1:
    #         self.pick_count = 3
    #     else:
    #         self.pick_count += 3
    #
    # def handle_four(self):
    #     self.is_blocked = True
    #     self.can_skip = True
    #
    # def handle_king(self, color):
    #     if color == Color.Spades:
    #         self.pick_count = 5
    #         self.reverse = True
    #     elif color == Color.Clubs:
    #         self.pick_count = 1
    #         self.can_skip = True
    #     elif color == Color.Hearts:
    #         self.pick_count = 5
    #     elif color == Color.Diamonds:
    #         self.pick_count = 1
    #         self.can_skip = True
    #
    # def handle_jack(self, call_figure):
    #     self.figure_call = Figure(call_figure)
    #     print("handling jack: ", self.figure_call)
    #
    # def handle_ace(self, call_color):
    #     self.color_call = Color(call_color)
    #     print("handling ace: ", self.color_call)
    #
    # def get_call(self):
    #     if self.color_call:
    #         return self.color_call.__str__()
    #     elif self.figure_call:
    #         return self.figure_call.__str__()
    def new_game_idle(self, taken_ids: List[str]):
        idle = {
            "Red": 0,
            "Green": 0,
            "Blue": 0,
            "Yellow": 0}
        for taken_id in taken_ids:
            idle[taken_id] = 4
        return idle
