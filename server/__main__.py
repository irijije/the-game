import socket
import threading
import json
import time
import argparse
from .game import Game, GAME_RULES



def client_thread(conn, addr, game):
    player_id = f"{addr[0]}:{addr[1]}"
    if not game.add_player(player_id, conn):
        conn.sendall((json.dumps({'error': 'Game already started.'}) + '\n').encode('utf-8'))
        conn.close()
        return

    buffer = ""
    try:
        # First message must be the name
        raw_data = conn.recv(1024)
        if not raw_data:
            raise ConnectionResetError
        
        buffer += raw_data.decode('utf-8')
        message, buffer = buffer.split('\n', 1)
        action_data = json.loads(message)
        if action_data.get('action') == 'set_name':
            game.handle_player_action(player_id, action_data)
        else:
            print(f"Player {player_id} sent invalid initial message.")
            conn.close()
            return

    except (ConnectionResetError, json.JSONDecodeError, IndexError):
        print(f"Player {player_id} disconnected during setup.")
        with game.lock:
            if player_id in game.players:
                del game.players[player_id]
                game.player_turn_order.remove(player_id)
        conn.close()
        return

    while True:
        try:
            raw_data = conn.recv(1024)
            if not raw_data:
                break
            
            buffer += raw_data.decode('utf-8')
            while '\n' in buffer:
                message, buffer = buffer.split('\n', 1)
                action_data = json.loads(message)
                game.handle_player_action(player_id, action_data)
                if game.game_over: # Check if the game ended after the action
                    break
            if game.game_over:
                break

        except (ConnectionResetError, json.JSONDecodeError):
            break
    
    print(f"Player {player_id} connection closed.")
    with game.lock:
        if player_id in game.players:
            # Find the player's name before removing them
            player_name = game.players[player_id].get('name', player_id)
            
            # Remove the player
            game.player_turn_order.remove(player_id)
            del game.players[player_id]

            # Announce the departure
            if game.game_started and not game.game_over:
                game.chat_history.append(f"System: {player_name} has left the game.")
                print(f"Player {player_name} left. Broadcasting new state.")
                if game.player_turn_order:
                    game.current_turn_index %= len(game.player_turn_order)
                game.broadcast_state()

    conn.close()



def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Server listening on {host}:{port}")
    
    game = Game()

    # A simple thread to start the game after a delay or specific command
    def game_starter():
        print("Waiting for players... Type 'start' to begin the game.")
        while True:
            cmd = input()
            if cmd.lower() == 'start':
                game.start_game()
                break
    
    threading.Thread(target=game_starter, daemon=True).start()

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=client_thread, args=(conn, addr, game))
        thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Game Server")
    parser.add_argument('--host', type=str, default='0.0.0.0', help='The host to listen on.')
    parser.add_argument('--port', type=int, default=12345, help='The port to listen on.')
    args = parser.parse_args()
    start_server(args.host, args.port)
