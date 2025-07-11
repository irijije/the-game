# The Game (CLI Multiplayer)

This is a command-line interface (CLI), multiplayer implementation of the cooperative card game "The Game".

## Features

- Multiplayer support
- In-game chat.
- ASCII art game board.

## How to Play

### 1. Start the Server

First, run the server in a terminal. The server will wait for players to connect.

```bash
python3 -m server
```

By default, the server listens on `0.0.0.0` (all available network interfaces) and port `12345`. You can specify a different host and port using the `--host` and `--port` options:

```bash
python3 -m server --host 127.0.0.1 --port 55555
```

The server will display: `Server listening on 127.0.0.1:55555` (or your custom host and port).

### 2. Start the Client(s)

Each player needs to run the client script in their own terminal.

```bash
python3 -m client
```

-   You will be prompted to enter the server IP. If you are running the server on the same machine, you can just press Enter to use the default (`127.0.0.1`).
-   You will then be prompted to enter the server port.
-   Next, you will be prompted to enter your name.

### 3. Start the Game

Once all players have connected, go to the **server's terminal** and type `start`, then press Enter. The game will begin, and each player's screen will update with their hand of cards.

### 4. Game Commands

On your turn, enter commands in your client terminal:

- **Play a card**: `play <card_number> <pile_number>`
  - Example: `play 25 1` (Plays the card '25' on ascending pile 1)
- **End your turn**: `end`
  - You must play at least two cards per turn (or one if the deck is empty).
- **Chat with players**: Just type your message and press Enter.
  - Example: `I can make a big jump on a descending pile.`
  - If your message starts with `play`, `end`, or `help`, it will be treated as a command.
- **View rules**: `help`
  - Displays the game rules and commands.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
