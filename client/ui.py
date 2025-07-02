import os

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

    # Header
    print("╔══════════════════════════════════════════════════════╗")
    print("║                     THE GAME                         ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"My Name: {my_name} | Current Turn: {current_turn}")
    print("────────────────────────────────────────────────────────")

    # Piles (Game Board)
    print("                --- GAME BOARD ---")
    print("   Ascending :  [1] {:<3}      [2] {:<3}".format(piles.get('asc1', 'X'), piles.get('asc2', 'X')))
    print("   Descending:  [3] {:<3}      [4] {:<3}".format(piles.get('desc1', 'X'), piles.get('desc2', 'X')))
    print("────────────────────────────────────────────────────────")
    
    # Player Info
    player_list = []
    for pid, info in players_info.items():
        player_str = f"{info.get('name', '?')} ({info.get('hand_size', '?')} cards)"
        if pid == my_player_id:
            player_str = f"▶ {player_str} ◀"
        player_list.append(player_str)
    
    print("Players: " + " | ".join(player_list))
    print(f"Deck: {deck_size} cards remaining")
    print("========================================================")

    # Player's Hand
    print("            --- YOUR HAND ---")
    hand_str = " ".join(map(str, sorted(my_hand)))
    print(f"           {hand_str}")
    print("========================================================")
    
    # Chat History
    if chat_history:
        print("Chat:")
        for chat_msg in chat_history[-5:]: # Display last 5 messages
            print(f"  {chat_msg}")
        print("--------------------------------------------------------")

    # System Message
    if message:
        print(f"Message: {message}")
        print("--------------------------------------------------------")
