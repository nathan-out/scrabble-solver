import tkinter as tk
from tkinter import messagebox

class ScrabbleBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("Scrabble Board")
        self.board_size = 15
        self.tile_size = 40
        self.selected_tile = None

        # Cadre principal pour la grille de Scrabble
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.canvas = tk.Canvas(self.board_frame, width=self.board_size * self.tile_size, height=self.board_size * self.tile_size)
        self.canvas.pack()

        self.tiles = []
        self.create_board()

        # Cadre pour les éléments de contrôle à droite
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.entry = tk.Entry(self.control_frame, width=20)
        self.entry.pack(pady=5)

        self.add_word_button = tk.Button(self.control_frame, text="Add Word", command=self.add_word)
        self.add_word_button.pack(pady=5)

        self.player_tiles_entry = tk.Entry(self.control_frame, width=20)
        self.player_tiles_entry.pack(pady=5)
        self.player_tiles_entry.insert(0, "Enter 7 letters")

        self.set_tiles_button = tk.Button(self.control_frame, text="Set Tiles", command=self.set_player_tiles)
        self.set_tiles_button.pack(pady=5)

        self.player_tiles_frame = tk.Frame(self.control_frame)
        self.player_tiles_frame.pack(pady=10)

        self.player_tiles = []
        self.letter_values = {
            'A': 1, 'E': 1, 'I': 1, 'L': 1, 'N': 1, 'O': 1, 'R': 1, 'S': 1, 'T': 1, 'U': 1,
            'D': 2, 'G': 2, 'M': 2,
            'B': 3, 'C': 3, 'P': 3,
            'F': 4, 'H': 4, 'V': 4,
            'J': 8, 'Q': 8,
            'K': 10, 'W': 10, 'X': 10, 'Y': 10, 'Z': 10,
            ' ': 0  # Joker
        }

    def create_board(self):
        for row in range(self.board_size):
            tile_row = []
            for col in range(self.board_size):
                x1 = col * self.tile_size
                y1 = row * self.tile_size
                x2 = x1 + self.tile_size
                y2 = y1 + self.tile_size
                tile = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                tile_row.append((tile, ""))
                self.canvas.tag_bind(tile, "<Button-1>", lambda event, r=row, c=col: self.on_tile_click(r, c))
            self.tiles.append(tile_row)

    def on_tile_click(self, row, col):
        if self.selected_tile:
            self.canvas.itemconfig(self.selected_tile[0], fill="white")
        self.selected_tile = (self.tiles[row][col][0], row, col)
        self.canvas.itemconfig(self.selected_tile[0], fill="lightblue")

    def add_word(self):
        word = self.entry.get().upper()
        if not word:
            messagebox.showwarning("Input Error", "Please enter a word.")
            return

        if self.selected_tile:
            tile, row, col = self.selected_tile
            for i, letter in enumerate(word):
                if col + i >= self.board_size:
                    break
                self.tiles[row][col + i] = (self.tiles[row][col + i][0], letter)
                self.canvas.create_text(col * self.tile_size + self.tile_size // 2, row * self.tile_size + self.tile_size // 2, text=letter)
            self.entry.delete(0, tk.END)
            self.selected_tile = None
        else:
            messagebox.showwarning("Selection Error", "Please select a starting tile.")

    def set_player_tiles(self):
        tiles_input = self.player_tiles_entry.get().upper()
        if len(tiles_input) != 7 or not tiles_input.isalpha():
            messagebox.showwarning("Input Error", "Please enter exactly 7 letters.")
            return

        self.player_tiles = list(tiles_input)
        self.display_player_tiles()

    def display_player_tiles(self):
        for widget in self.player_tiles_frame.winfo_children():
            widget.destroy()

        for letter in self.player_tiles:
            tile_frame = tk.Frame(self.player_tiles_frame, width=self.tile_size, height=self.tile_size, borderwidth=1, relief="solid")
            tile_frame.pack_propagate(False)
            tile_frame.pack(side=tk.LEFT, padx=2, pady=2)

            tile_label = tk.Label(tile_frame, text=letter, font=("Arial", 16))
            tile_label.pack(expand=True)

            value_label = tk.Label(tile_frame, text=str(self.letter_values.get(letter, 0)), font=("Arial", 10))
            value_label.pack(expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScrabbleBoard(root)
    root.mainloop()
