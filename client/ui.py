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
    last_move = state.get('last_move')

    # Header
    print("╔══════════════════════════════════════════════════════╗")
    print("║                     THE GAME                         ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"My Name: {my_name} | Current Turn: {current_turn}")
    print("────────────────────────────────────────────────────────")

    # Piles (Game Board)
    pile_map = {1: 'asc1', 2: 'asc2', 3: 'desc1', 4: 'desc2'}
    pile_vals = {}
    for i in range(1, 5):
        pile_name = pile_map[i]
        val = piles.get(pile_name, 'X')
        is_last_move = last_move and last_move.get('pile_num') == i
        pile_vals[pile_name] = f"{val}{'*' if is_last_move else ''}"

    print("                --- GAME BOARD ---")
    print("   Ascending :  [1] {:<4}     [2] {:<4}".format(pile_vals['asc1'], pile_vals['asc2']))
    print("   Descending:  [3] {:<4}     [4] {:<4}".format(pile_vals['desc1'], pile_vals['desc2']))
    print("────────────────────────────────────────────────────────")
    
    # System Message
    if message:
        print(f"Message: {message}")
        print("--------------------------------------------------------")
    
    # Player Info
    player_list = []
    for pid, info in players_info.items():
        player_str = f"{info.get('name', '?')} ({info.get('hand_size', '?')} cards)"
        if pid == my_player_id:
            player_str = f"▶ {player_str}"
        
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

