import copy
import curses
import random

from baseUI import TextUI

P1_MARKER = 'X'
P2_MARKER = 'O'
X_STEP = 4
Y_STEP = 2
X_OFFSET = 1
Y_OFFSET = 4

TIE = "_                       _\n| |                     | |\n| |                     | |\n| |                     | " \
      "|\n| |                     | |\n| |        .---.        | |\n| |     _.'\   /'._     | |\n| b__--- | .'''. | " \
      "---__d |\n| p__---_| '._.' |_---''q |\n| |       ./   \.       | |\n| |        '---'        | |\n| |           " \
      "          | |\n| |                     | |\n|_|                     |_| "


class Game(TextUI):

    def __init__(self):
        super().__init__()
        self.game_is_on = True
        self.is_player1_turn = bool(random.getrandbits(1))
        self.total_moves = 0
        self.board_state = [list('   ') for _ in range(3)]
        self.position_x = 1
        self.position_y = 1
        self.window_lines = 0
        self.window_cols = 0
        self.plays = []
        self.title = "### TIC-TAC-TOE ###"
        self.instructions = "Use 'arrow keys' to move,  'Space' to place marker,  'Q' to Quit"

    def input(self, key):
        # Quit the game anytime
        if key in ["q", "Q"] or key and not self.game_is_on:
            self.stop()

        # Get coordinates to place elements based on window size
        middle_y = int(self.window_lines / 2)
        middle_x = int(self.window_cols / 2)

        # Move cursor or place marker accordingly to input
        if key == "KEY_UP":
            self.position_y = max(0, self.position_y - 1)
        elif key == "KEY_DOWN":
            self.position_y = min(2, self.position_y + 1)
        elif key == "KEY_LEFT":
            self.position_x = max(0, self.position_x - 1)
        elif key == "KEY_RIGHT":
            self.position_x = min(2, self.position_x + 1)
        elif key == " ":
            # Get cursor position
            y, x = self.screen.getyx()

            # Don't place marker if position already has a marker. Play a warning sound instead.
            if self.screen.inch(y, x) == ord(' '):
                # Place a marker, change player turn, update game total moves and save board state.
                self.place_marker()
                self.is_player1_turn = not self.is_player1_turn
                self.total_moves += 1
                self.plays.append(copy.deepcopy(self.board_state))


                # Check if someone has won or if it's a tie
                if self.someone_has_won():

                    winning_message = f"### Player {P2_MARKER if self.is_player1_turn else P1_MARKER} wins ###"

                    self.screen.clear()
                    self.screen.addstr(middle_y, middle_x - int(len(winning_message) / 2),
                                       winning_message,
                                       curses.A_BLINK)
                    self.end_game()

                elif self.total_moves > 8:
                    self.screen.clear()
                    self.screen.addstr(middle_y, middle_x, f"### It's a tie. ###\n {TIE}", curses.A_BLINK)

                    self.end_game()

            else:
                curses.beep()

    def end_game(self):
        self.game_is_on = False
        self.draw()
        curses.curs_set(0)

        self.pause()

    def draw(self):
        # self.screen.addstr(20, 20, str(self.board_state))
        # self.screen.addstr(22, 20, str(self.total_moves))
        # self.screen.addstr(24, 20, str(self.game_is_on))
        # self.screen.addstr(26, 20, str(self.plays))

        self.screen.border()

        self.window_lines = curses.LINES
        self.window_cols = curses.COLS

        top_y = int(self.window_lines / 4)
        middle_x = int(self.window_cols / 2)

        self.screen.addstr(1, middle_x - int(len(self.title) / 2), self.title)
        self.screen.addstr(3, middle_x - int(len(self.instructions) / 2), self.instructions)

        self.screen.addstr(top_y, middle_x,
                           f'{self.board_state[0][0]} │ {self.board_state[0][1]} │ {self.board_state[0][2]} ')
        self.screen.addstr(top_y + 1, middle_x, '──┼───┼──')
        self.screen.addstr(top_y + 2, middle_x,
                           f'{self.board_state[1][0]} │ {self.board_state[1][1]} │ {self.board_state[1][2]} ')
        self.screen.addstr(top_y + 3, middle_x, '──┼───┼──')
        self.screen.addstr(top_y + 4, middle_x,
                           f'{self.board_state[2][0]} │ {self.board_state[2][1]} │ {self.board_state[2][2]} ')

        self.show_players_info()

        self.screen.move(top_y + self.position_y * Y_STEP, middle_x + self.position_x * X_STEP)

    def show_players_info(self):
        if self.game_is_on:
            self.screen.addstr(Y_OFFSET + 6, 1, f'Player {P1_MARKER}',
                               curses.A_BLINK if self.is_player1_turn else 0)
            self.screen.addstr(Y_OFFSET + 7, 1, f'Player {P2_MARKER}',
                               curses.A_BLINK if not self.is_player1_turn else 0)

    def place_marker(self):

        # Mark on the board depends on current player
        self.board_state[self.position_y][self.position_x] = P1_MARKER if self.is_player1_turn else P2_MARKER

    def someone_has_won(self):
        # Check last move for horizontal victory
        if self.board_state[0][self.position_x] \
                == self.board_state[1][self.position_x] \
                == self.board_state[2][self.position_x]:
            return True
        # Check last move for vertical victory
        if self.board_state[self.position_y][0] \
                == self.board_state[self.position_y][1] \
                == self.board_state[self.position_y][2]:
            return True

        # Check last move for main diagonal victory i.e. where position_y == position_x
        if self.position_y == self.position_x and self.board_state[0][0] \
                == self.board_state[1][1] \
                == self.board_state[2][2]:
            return True
        # Check last move for secondary diagonal victory i.e. where position_x + position_y == 2
        if self.position_y + self.position_x == 2 and self.board_state[0][2] \
                == self.board_state[1][1] \
                == self.board_state[2][0]:
            return True

        return False


new_game = Game()

new_game.start()
