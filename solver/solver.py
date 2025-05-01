class ScrabbleSolver:
    def __init__(self):
        self.letter_values = {
            'A': 1, 'E': 1, 'I': 1, 'L': 1, 'N': 1, 'O': 1, 'R': 1, 'S': 1, 'T': 1, 'U': 1,
            'D': 2, 'G': 2, 'M': 2,
            'B': 3, 'C': 3, 'P': 3,
            'F': 4, 'H': 4, 'V': 4,
            'J': 8, 'Q': 8,
            'K': 10, 'W': 10, 'X': 10, 'Y': 10, 'Z': 10,
            ' ': 0  # Joker
        }
        print('Chargement du dictionnaire...')
        self.dictionary = self.load_dictionary()

    def load_dictionary(self):
        dic = {}
        mots = open('data/French ODS dictionary.txt', 'r').readlines()
        print('Calcul des valeurs des mots...')
        for mot in mots:
            mot = mot.replace('\n', '')
            valeur_mot = 0
            for lettre in mot:
                valeur_mot += self.letter_values[lettre]
            dic[mot] = valeur_mot
        return dic


    def find_best_words(self, player_tiles):
        # Trouve les meilleurs mots possibles à partir des lettres du joueur (à implémenter)
        # Pour l'instant, retourne simplement une liste de mots d'exemple
        return ["EXAMPLE", "WORDS"]

if __name__ == "__main__":
    solver = ScrabbleSolver()
