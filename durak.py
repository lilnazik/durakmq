import random
import itertools

SPADES = '♠'
HEARTS = '♥'
DIAMS = '♦'
CLUBS = '♣'

NOMINALS = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
NAME_TO_VALUE = {n: i for i, n in enumerate(NOMINALS)}

CARDS_IN_HAND_MAX = 6

N_PLAYERS = 2

DECK = [(nom, suit) for nom in NOMINALS for suit in [SPADES, HEARTS, DIAMS, CLUBS]]


class Player:
    def __init__(self, index, deck):
        self.index = index
        self.cards = []
        self.take_cards_from_deck(deck)

    def take_cards_from_deck(self, deck: list):
        lack = max(0, CARDS_IN_HAND_MAX - len(self.cards))
        n = min(len(deck), lack)
        self.cards += deck[:n]
        del deck[:n]
        self.cards.sort(key=lambda c: (NAME_TO_VALUE[c[0]], c[1]))

    def __repr__(self):
        return f"Player{self.cards!r}"

    def take_card(self, card):
        self.cards.remove(card)


def rotate(l, n):
    return l[n:] + l[:n]


class Game:
    NORMAL = 'normal'
    TOOK_CARDS = 'took_cards'
    GAME_OVER = 'game_over'

    def __init__(self):
        self.attacker_index = 0

        self.deck = list(DECK)
        random.shuffle(self.deck)

        self.players = [Player(i, self.deck) for i in range(N_PLAYERS)]

        self.trump = self.deck[0][1]

        self.field = {}  # atack card: defend card
        self.winner = None

    def card_match(self, card1, card2):
        if card1 is None or card2 is None:
            return False
        n1, _ = card1
        n2, _ = card2
        return n1 == n2

    def can_beat(self, card1, card2):
        nom1, suit1 = card1
        nom2, suit2 = card2
        if suit2 == self.trump:
            return suit1 != self.trump or nom2 > nom1
        elif suit1 == suit2:
            return nom2 > nom1
        else:
            return False

    def can_add_to_field(self, card):
        if not self.field:
            return True

        for attack_card, defend_card in self.field.items():
            if self.card_match(attack_card, card) or self.card_match(defend_card, card):
                return True

        return False

    def attacking_cards(self):
        return list(filter(bool, self.field.keys()))

    def defending_cards(self):
        return list(filter(bool, self.field.values()))

    def current_player(self):
        return self.players[self.attacker_index]

    def opponent_player(self):
        return self.players[(self.attacker_index + 1) % N_PLAYERS]

    def attack(self, card):
        assert not self.winner

        if not self.can_add_to_field(card):
            return False
        cur, opp = self.current_player(), self.opponent_player()
        cur.take_card(card)
        self.field[card] = None
        return True

    def defend(self, attacking_card, defending_card):
        assert not self.winner

        if self.field[attacking_card] is not None:
            return False
        if self.can_beat(attacking_card, defending_card):
            self.field[attacking_card] = defending_card
            self.opponent_player().take_card(defending_card)
            return True
        return False

    def attack_succeed(self):
        return any(def_card is None for _, def_card in self.field.items())

    def finish_turn(self):
        assert not self.winner

        took_cards = False
        if self.attack_succeed():
            self._take_all_field()
            took_cards = True
        else:
            self.field = {}

        for p in rotate(self.players, self.attacker_index):
            p.take_cards_from_deck(self.deck)
            if not self.deck:
                self.winner = p.index
                return self.GAME_OVER

        if took_cards:
            return self.TOOK_CARDS
        else:
            self.attacker_index = self.opponent_player().index
            return self.NORMAL

    def _take_all_field(self):
        cards = self.attacking_cards() + self.defending_cards()
        self.opponent_player().cards += cards
        self.field = {}