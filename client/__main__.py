import socket
import threading
import json
import os
import time
import sys
import io
from .ui import display_board



def listen_to_server(client_socket):
    buffer = ""
    while True:
        try:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                print("\nConnection to server lost.")
                break
            
            buffer += data
            while '\n' in buffer:
                message, buffer = buffer.split('\n', 1)
                state = json.loads(message)
                if 'error' in state:
                    print(f"\nError from server: {state['error']}")
                    return
                
                state['my_player_id'] = f"{client_socket.getsockname()[0]}:{client_socket.getsockname()[1]}"
                display_board(state)
                sys.stdout.write("> ")
                sys.stdout.flush()

        except (json.JSONDecodeError, ConnectionResetError, BrokenPipeError) as e:
            print(f"\nAn error occurred: {e}")
            break
    client_socket.close()
    os._exit(1)

def start_client():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    host = input("Enter server IP (default: 127.0.0.1): ") or '127.0.0.1'
    port_str = input("Enter server port (default: 12345): ") or '12345'
    try:
        port = int(port_str)
    except ValueError:
        print("Invalid port number. Using default 12345.")
        port = 12345
    
    name = input("Enter your name: ")
    while not name:
        name = input("Name cannot be empty. Enter your name: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        print(f"Connected to the server at {host}:{port}.")
        
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
            command = input("> ")
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
            elif action == 'help':
                message = {'action': 'help'}
                client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
            else:
                chat_text = command.strip()
                if chat_text:
                    message = {'action': 'chat', 'text': chat_text}
                    client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        except (BrokenPipeError, ConnectionResetError):
            print("Connection to server was lost.")
            break
    
    client_socket.close()



if __name__ == "__main__":
    start_client()

