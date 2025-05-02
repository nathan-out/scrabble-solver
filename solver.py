letter_values = {
            'A': 1, 'E': 1, 'I': 1, 'L': 1, 'N': 1, 'O': 1, 'R': 1, 'S': 1, 'T': 1, 'U': 1,
            'D': 2, 'G': 2, 'M': 2,
            'B': 3, 'C': 3, 'P': 3,
            'F': 4, 'H': 4, 'V': 4,
            'J': 8, 'Q': 8,
            'K': 10, 'W': 10, 'X': 10, 'Y': 10, 'Z': 10,
            ' ': 0  # Joker
}

def load_dictionary():
    dic = {}
    mots = open('data/French ODS dictionary.txt', 'r').readlines()
    print('Calcul des valeurs des mots...')
    for mot in mots:
        mot = mot.replace('\n', '')
        valeur_mot = 0
        for lettre in mot:
            valeur_mot += letter_values[lettre]
        dic[mot] = valeur_mot
    return dic

print('Chargement du dictionnaire...')
dictionary = load_dictionary()

def proposer_meilleurs_mots(plateau_lettres, lettres_robot, plateau_bonus):
    """
    Reçoit l’état du plateau (15x15, chaque case contient '' ou une lettre),
    et les lettres disponibles du robot (str).
    Retourne une liste de suggestions, chaque suggestion est un dictionnaire :
    {
        'mot': 'EXEMPLE',
        'score': 23,
        'ligne': 7,
        'colonne': 5,
        'direction': 'H'  # ou 'V'
    }
    """
    print("PROPOSER LES MEILLEURS MOTS")
    print("plateau lettres",plateau_lettres, "plateau bonus",plateau_bonus)
    # Ce qui suit est un exemple fictif pour tester l'interface
    return [
        {'mot': 'RIRE', 'score': 12, 'ligne': 7, 'colonne': 5, 'direction': 'H'},
        {'mot': 'LOUP', 'score': 15, 'ligne': 10, 'colonne': 3, 'direction': 'V'}
    ]
