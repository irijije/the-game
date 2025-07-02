import socket
import threading
import json
import os
import time

def display_board(state):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    piles = state.get('piles', {})
    my_hand = state.get('my_hand', [])
    players_info = state.get('players_info', {})
    deck_size = state.get('deck_size', '?')
    current_turn = state.get('current_turn', 'N/A')
    my_name = state.get('my_name', 'N/A')
    my_player_id = state.get('my_player_id', '')
    message = state.get('message', '')
    chat_history = state.get('chat_history', [])

    print("======================== The Game ========================")
    print(f"My Name: {my_name} | Current Turn: {current_turn}")
    print("--------------------------------------------------------")
    print(" Ascending:  [1] {:<3}   [2] {:<3}".format(piles.get('asc1', 'X'), piles.get('asc2', 'X')))
    print(" Descending: [3] {:<3}   [4] {:<3}".format(piles.get('desc1', 'X'), piles.get('desc2', 'X')))
    print("--------------------------------------------------------")
    
    player_list = []
    for pid, info in players_info.items():
        player_str = f"{info.get('name', '?')} ({info.get('hand_size', '?')} cards)"
        if pid == my_player_id:
            player_str = f"-> {player_str} <-"
        player_list.append(player_str)
    
    print("Players: " + " | ".join(player_list))
    print(f"Deck: {deck_size} cards remaining")
    print("========================================================")
    print("Your Hand: ", " ".join(map(str, sorted(my_hand))))
    print("========================================================")
    
    if chat_history:
        print("Chat:")
        for chat_msg in chat_history[-5:]: # Display last 5 messages
            print(f"  {chat_msg}")
        print("--------------------------------------------------------")

    if message:
        print(f"Message: {message}")
        print("--------------------------------------------------------")

def listen_to_server(client_socket):
    buffer = ""
    while True:
        try:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                print("Connection to server lost.")
                break
            
            buffer += data
            while '\n' in buffer:
                message, buffer = buffer.split('\n', 1)
                state = json.loads(message)
                if 'error' in state:
                    print(f"Error from server: {state['error']}")
                    return
                
                state['my_player_id'] = f"{client_socket.getsockname()[0]}:{client_socket.getsockname()[1]}"
                display_board(state)

        except (json.JSONDecodeError, ConnectionResetError, BrokenPipeError) as e:
            print(f"An error occurred: {e}")
            break
    client_socket.close()
    os._exit(1)

def start_client():
    host = input("Enter server IP (default: 127.0.0.1): ") or '127.0.0.1'
    port = 12345
    
    name = input("Enter your name: ")
    while not name:
        name = input("Name cannot be empty. Enter your name: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        print("Connected to the server.")
        
        message = {'action': 'set_name', 'name': name}
        client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))

    except ConnectionRefusedError:
        print("Connection failed. Is the server running?")
        return
    except (BrokenPipeError, ConnectionResetError):
        print("Failed to send name to the server.")
        return

    thread = threading.Thread(target=listen_to_server, args=(client_socket,), daemon=True)
    thread.start()

    print("Waiting for the game to start...")
    while thread.is_alive():
        try:
            command = input("Enter command ('play', 'end', 'say', 'help'): ")
            parts = command.strip().split()
            
            if not parts:
                continue

            action = parts[0].lower()

            if action == 'play' and len(parts) == 3:
                try:
                    card = int(parts[1])
                    pile = int(parts[2])
                    message = {'action': 'play', 'card': card, 'pile': pile}
                    client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
                except ValueError:
                    print("Invalid card or pile number.")
            elif action == 'end':
                message = {'action': 'end_turn'}
                client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
            elif action == 'say':
                chat_text = " ".join(parts[1:])
                if chat_text:
                    message = {'action': 'chat', 'text': chat_text}
                    client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
                else:
                    print("You must provide a message to say.")
            elif action == 'help':
                message = {'action': 'help'}
                client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
            else:
                print("Unknown command. Use 'play <c> <p>', 'end', 'say <msg>', or 'help'.")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        except (BrokenPipeError, ConnectionResetError):
            print("Connection to server was lost.")
            break
    
    client_socket.close()



if __name__ == "__main__":
    start_client()
