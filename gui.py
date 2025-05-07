import tkinter as tk
from tkinter import messagebox
from solver import proposer_meilleurs_mots  # importe ton module

BOARD_SIZE = 15

LETTER_VALUES = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
    'I': 1, 'J': 8, 'K': 10, 'L': 1, 'M': 2, 'N': 1, 'O': 1, 'P': 3,
    'Q': 8, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 10, 'X': 10,
    'Y': 10, 'Z': 10
}

class ScrabbleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Scrabble - Interface Graphique")
        self.board_layout = self.load_board_layout("plateau.txt")
        self.default_colors = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        self.tiles = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected_cell = None  # (row, col)

        self.create_board()
        self.create_controls()
    
    def load_board_layout(self, filepath):
        layout = []
        with open(filepath, "r") as f:
            for line in f:
                tokens = line.strip().split()
                if tokens and not tokens[0].startswith("#"):
                    layout.append(tokens)
        return layout


    def create_board(self):
        board_frame = tk.Frame(self.root)
        board_frame.grid(row=0, column=0, padx=10, pady=10)

        color_map = {
            "MD": "lightpink",
            "MT": "red",
            "LD": "lightblue",
            "LT": "blue",
            "LS": "white"
        }

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                bg = color_map.get(self.board_layout[i][j], "white")
                entry = tk.Entry(board_frame, width=2, font=('Arial', 12), justify='center', bg=bg)
                entry.grid(row=i, column=j)
                entry.bind("<Button-1>", lambda e, r=i, c=j: self.select_cell(r, c))
                self.tiles[i][j] = entry
                self.default_colors[i][j] = bg  # stocke la couleur d'origine


    def select_cell(self, row, col):
        if self.selected_cell:
            prev_row, prev_col = self.selected_cell
            original_color = self.default_colors[prev_row][prev_col]
            self.tiles[prev_row][prev_col].config(bg=original_color)

        self.selected_cell = (row, col)
        self.tiles[row][col].config(bg="lightgreen")  # couleur de sélection



    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.grid(row=0, column=1, sticky='n')

        tk.Label(control_frame, text="Lettres du robot :").pack()
        self.robot_letters_var = tk.StringVar()
        tk.Entry(control_frame, textvariable=self.robot_letters_var, width=10).pack()

        tk.Label(control_frame, text="Mot à ajouter :").pack()
        self.word_var = tk.StringVar()
        tk.Entry(control_frame, textvariable=self.word_var, width=12).pack()

        self.direction_var = tk.StringVar(value='H')
        tk.Radiobutton(control_frame, text="Horizontal", variable=self.direction_var, value='H').pack()
        tk.Radiobutton(control_frame, text="Vertical", variable=self.direction_var, value='V').pack()

        tk.Button(control_frame, text="Ajouter le mot", command=self.add_word).pack(pady=5)
        tk.Button(control_frame, text="Proposer les meilleurs mots", command=self.show_best_words).pack(pady=10)

    def get_plateau(self):
        """Retourne un tableau 15x15 avec les lettres actuelles du plateau."""
        plateau = []
        for row in self.tiles:
            ligne = []
            for cell in row:
                contenu = cell.get().upper().strip()
                ligne.append(contenu if contenu else '')
            plateau.append(ligne)
        return plateau

    def add_word(self):
        word = self.word_var.get().upper()
        direction = self.direction_var.get()
        start = self.selected_cell

        if not start:
            messagebox.showerror("Erreur", "Cliquez sur une case pour commencer le mot.")
            return

        if not word.isalpha():
            messagebox.showerror("Erreur", "Mot invalide.")
            return

        row, col = start

        if direction == 'H' and col + len(word) > BOARD_SIZE:
            messagebox.showerror("Erreur", "Mot trop long pour cette position.")
            return
        if direction == 'V' and row + len(word) > BOARD_SIZE:
            messagebox.showerror("Erreur", "Mot trop long pour cette position.")
            return

        for i, letter in enumerate(word):
            r = row + i if direction == 'V' else row
            c = col + i if direction == 'H' else col
            self.tiles[r][c].delete(0, tk.END)
            self.tiles[r][c].insert(0, letter)
            self.tiles[r][c].config(disabledforeground='black')

    def show_best_words(self):
        plateau = self.get_plateau()
        lettres = self.robot_letters_var.get().upper()

        suggestions = proposer_meilleurs_mots(plateau, lettres, self.board_layout)

        if not suggestions:
            messagebox.showinfo("Suggestions", "Aucun mot trouvé.")
            return

        result = ""
        for mot, datas in suggestions.items():
            result += f"{mot} à ({datas['placement']['ligne']}, {datas['placement']['colonne']}) {datas['placement']['direction']} - Score: {datas['score']}\n"

        messagebox.showinfo("Meilleurs mots proposés", result)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScrabbleGUI(root)
    root.mainloop()
