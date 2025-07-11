import random
import threading
import json

GAME_RULES = """
*** The Game: Rules ***
- Goal: Cooperatively play all cards from 2 to 99 into four piles.
- Piles:
  - 2 Ascending Piles (labeled 1, 2): Start at 1. Cards must be played in increasing order.
  - 2 Descending Piles (labeled 3, 4): Start at 100. Cards must be played in decreasing order.
- Turn:
  - On your turn, you MUST play at least 2 cards.
  - If the deck is empty, you only need to play 1 card.
- Backwards Trick (The "10 Rule"):
  - You can play a card that is exactly 10 lower on an ASCENDING pile.
  - You can play a card that is exactly 10 higher on a DESCENDING pile.

*** Commands ***
- play <card> <pile>: Play a card on a pile (e.g., play 25 1).
- end: End your turn.
- help: Show this help message.
- To chat, just type your message and press Enter.
"""

class Game:
    def __init__(self):
        self.deck = list(range(2, 100))
        random.shuffle(self.deck)
        self.piles = {'asc1': 1, 'asc2': 1, 'desc1': 100, 'desc2': 100}
        self.players = {}
        self.player_turn_order = []
        self.current_turn_index = 0
        self.cards_played_this_turn = 0
        self.game_started = False
        self.game_over = False
        self.chat_history = []
        self.last_move = None
        self.lock = threading.Lock()


    def add_player(self, player_id, conn):
        with self.lock:
            if not self.game_started:
                self.players[player_id] = {'hand': [], 'conn': conn, 'message': '', 'name': 'Anonymous'}
                self.player_turn_order.append(player_id)
                print(f"Player {player_id} connected.")
                return True
            return False

    def start_game(self):
        with self.lock:
            if not self.game_started and len(self.players) > 0:
                self.game_started = True
                hand_size = 6 if len(self.players) > 2 else 7
                for player_id in self.players:
                    self.players[player_id]['hand'] = [self.deck.pop() for _ in range(hand_size)]
                    self.players[player_id]['hand'].sort()
                self.chat_history.append("System: The game has started!")
                print("Game has started!")
                self.broadcast_state()

    def get_game_state(self, player_id):
        current_turn_name = "N/A"
        if self.game_started and self.player_turn_order:
            current_turn_player_id = self.player_turn_order[self.current_turn_index]
            current_turn_name = self.players[current_turn_player_id]['name']
        
        state = {
            'piles': self.piles,
            'my_hand': self.players[player_id]['hand'],
            'players_info': {
                pid: {'name': p_info['name'], 'hand_size': len(p_info['hand'])}
                for pid, p_info in self.players.items()
            },
            'deck_size': len(self.deck),
            'current_turn': current_turn_name,
            'my_player_id': player_id,
            'my_name': self.players[player_id]['name'],
            'message': self.players[player_id]['message'],
            'game_over': self.game_over,
            'chat_history': self.chat_history,
            'last_move': self.last_move
        }
        self.players[player_id]['message'] = '' # Clear message after sending
        return state

    def broadcast_state(self):
        # This method should be called within a lock
        for player_id, player_info in self.players.items():
            try:
                state = self.get_game_state(player_id)
                player_info['conn'].sendall((json.dumps(state) + '\n').encode('utf-8'))
            except (BrokenPipeError, ConnectionResetError):
                print(f"Player {player_id} seems to have disconnected.")

    def play_card(self, player_id, card, pile_num):
        pile_map = {1: 'asc1', 2: 'asc2', 3: 'desc1', 4: 'desc2'}
        pile_name = pile_map.get(pile_num)
        
        if not pile_name:
            self.players[player_id]['message'] = "Invalid pile number."
            return

        current_pile_value = self.piles[pile_name]
        is_valid_move = False
        if 'asc' in pile_name:
            if card > current_pile_value or card == current_pile_value - 10:
                is_valid_move = True
        else: # desc
            if card < current_pile_value or card == current_pile_value + 10:
                is_valid_move = True

        if is_valid_move:
            self.piles[pile_name] = card
            self.players[player_id]['hand'].remove(card)
            self.cards_played_this_turn += 1
            self.players[player_id]['message'] = f"Played {card} on pile {pile_num} ({current_pile_value} -> {card})."
            self.last_move = {
                'player_name': self.players[player_id]['name'],
                'card': card,
                'pile_num': pile_num,
                'old_pile_value': current_pile_value
            }
        else:
            self.players[player_id]['message'] = "Invalid move."

    def end_turn(self, player_id):
        min_cards_to_play = 1 if not self.deck else 2
        if self.cards_played_this_turn < min_cards_to_play:
            self.players[player_id]['message'] = f"You must play at least {min_cards_to_play} cards."
            return

        # Refill hand
        for _ in range(self.cards_played_this_turn):
            if self.deck:
                self.players[player_id]['hand'].append(self.deck.pop())
        self.players[player_id]['hand'].sort()
        
        self.cards_played_this_turn = 0
        self.current_turn_index = (self.current_turn_index + 1) % len(self.player_turn_order)
        self.players[player_id]['message'] = "Turn ended."
        
        if self.check_win_lose():
            self.game_over = True

    def check_win_lose(self):
        if not self.deck and all(not p['hand'] for p in self.players.values()):
            print("Game Won!")
            self.chat_history.append("System: Congratulations, you won!")
            return True

        can_play = False
        for player_id in self.player_turn_order:
             for card in self.players[player_id]['hand']:
                for pile_name, pile_value in self.piles.items():
                    if 'asc' in pile_name and (card > pile_value or card == pile_value - 10): can_play = True
                    if 'desc' in pile_name and (card < pile_value or card == pile_value + 10): can_play = True
                    if can_play: break
                if can_play: break
             if can_play: break
        
        if not can_play:
            print("Game Lost!")
            self.chat_history.append("System: Game Over. No more possible moves.")
            return True
        return False

    def handle_player_action(self, player_id, data):
        with self.lock:
            action = data.get('action')

            if action == 'set_name':
                name = data.get('name', 'Anonymous')
                self.players[player_id]['name'] = name
                print(f"Player {player_id} set name to {name}")
                self.chat_history.append(f"System: {name} has joined the game.")
                self.broadcast_state()
                return
            
            if action == 'chat':
                sender_name = self.players[player_id]['name']
                chat_text = data.get('text', '')
                if chat_text:
                    self.chat_history.append(f"{sender_name}: {chat_text}")
                self.broadcast_state()
                return
            
            if action == 'help':
                self.players[player_id]['message'] = GAME_RULES
                self.broadcast_state()
                return

            if not self.game_started:
                self.players[player_id]['message'] = "The game has not started yet."
                self.broadcast_state()
                return

            if self.game_over:
                self.players[player_id]['message'] = "The game is over."
                self.broadcast_state()
                return

            if player_id != self.player_turn_order[self.current_turn_index]:
                self.players[player_id]['message'] = "It's not your turn."
                self.broadcast_state()
                return

            if action == 'play':
                card = data.get('card')
                pile = data.get('pile')
                if card in self.players[player_id]['hand']:
                    self.play_card(player_id, card, pile)
                else:
                    self.players[player_id]['message'] = "Card not in your hand."
            elif action == 'end_turn':
                self.end_turn(player_id)
            
            self.broadcast_state()
