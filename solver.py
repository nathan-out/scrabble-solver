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

"""
Retourne la valeur de la case coordonnées i, j si lettre est rentrée.
"""
def get_valeur_case_from_lettre(plateau_bonus, lettre, i, j):
    if plateau_bonus[i][j] == 'LS': return letter_values[lettre]
    if plateau_bonus[i][j] == 'LD': return letter_values[lettre]*2
    if plateau_bonus[i][j] == 'LT': return letter_values[lettre]*3

"""
Retourne une liste de string (regex) qui contient les
possibilités sur le plateau de jeu.
Prend en compte les lettres du robot pour générer des
regex cohérentes pour la fonction suivante : 
get_mots_conformes_from_regex_lettres
"""
def get_regex_from_plateau(plateau_lettres, lettres_robot):
    raw_regex = ''

    for element in plateau_lettres[0]:
        if element.isalnum():
            raw_regex += element
        else:
            raw_regex += '.'
    
    # ici on a le regex du plus grand mot possible
    # il faut découper ce regex en sous-regex
    # ex : A.....B.C -> A.{,4}, A.....B, .{4,}B, B.C
    # pour ça on trouve la plus longue sous chaine
    # de points > len(1)
    raw_regexes = [raw_regex]
    import re
    points = re.findall(r'\.+', raw_regex)
    # Prendre la plus longue
    plus_longue = max(points, key=len) if points else ''
    while len(plus_longue) > 1:
        points = re.findall(r'\.+', raw_regex)
        # Prendre la plus longue
        plus_longue = max(points, key=len) if points else ''
        # TODO bug par ici : on peut se retrouver avec {,6}B...
        # alors qu'on veut .{,6}B...
        motif = '.{,'+str(len(plus_longue)-1)+'}'
        raw_regex = raw_regex.replace(plus_longue, motif)
        sous_regexes = raw_regex.split(motif)
        for i in range(len(sous_regexes)):
            if i%2 == 0:
                sous_regexes.append(sous_regexes[i]+motif)
            else: sous_regexes.append(motif+sous_regexes[i])
        print('sous regexes', sous_regexes)

        for s_reg in sous_regexes:
            if len(re.findall(r'[A-Z]', s_reg)) == 1: # la regex a une seule lettre
                if s_reg.count('{') < 2:
                    raw_regexes.append(s_reg)
    # il y aurait encore du boulot sûrement ci-dessus mais on est déjà pas mal

    regexes = []
    # à la place de chaque . on injecte toutes les lettres que le robot peut jouer
    for raw_regex in raw_regexes:
        regexes.append(raw_regex.replace('.', '['+lettres_robot+']'))
    print('regexes', regexes)

"""
Retourne les mots qui matche la disposition des lettres sur le
plateau (symbolisé par regex).
Prend en compte les lettres du robots (string de forme A,B,C...)
Retourne une liste de string
"""
def get_mots_conformes_from_regex_lettres(regex, lettres_robot):
    import re # calcul des mots qui matchent la regex
    pattern = re.compile(regex, re.IGNORECASE)
    mots = [mot for mot in dictionary if pattern.match(mot)]

    lettres_robot = lettres_robot.split(',') # liste des lettres du robot
    mots_retenus = mots.copy() # on doit faire une copie indépendante sinon on se marche dessus pendant la boucle

    # il faut ajouter les lettres présentes sur la grille (i.e dans base_regex) dans les lettres consomables
    # on s'en fiche de l'ordre car ça a déjà été check juste au-dessus
    # on considère toutes les lettres (celles du robot + celles sur le plateau) comme des consommables
    # ici on ajoute les lettres du robot aux lettres sur le plateau dans une seule liste
    for c in re.findall(r'[A-Z]', regex): lettres_robot.append(c)
    
    for mot in mots:
        mot_valide = True
        lettres_consomables = lettres_robot.copy() # on doit faire une copie indépendante sinon on se marche dessus pendant la boucle
        #print('mot : ',mot, lettres_consomables)
        for lettre in mot:
            if lettre in lettres_consomables:
                lettres_consomables.remove(lettre)
            else: # quand les consomables sont épuisés -> mot incorrect
                #print(f'mot {mot} invalide pour lettre {lettre} (lettres à conso {lettres_consomables})')
                mot_valide = False
                break
        if not mot_valide: mots_retenus.remove(mot)
    return mots_retenus

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
    lettres_robot = "V,O,L,E,F,C,E,X"

    regexes = get_regex_from_plateau(plateau_lettres, lettres_robot)
   
    #mots = ['TEFAL', 'TEFALS'] # debug
    # Ici il reste potentiellement des mots impossibles (qui utilisent plusieurs fois une lettre par ex)
    # Mais on a déjà fait un GROS pré-tri. Il faut vérifier pour chaque mot s'il respecte les règles
    mots = [] # TODO revoir cette struct de données y'a sûrement mieux à faire
    for regex in regexes:
        mots.append(get_mots_conformes_from_regex_lettres(regex, lettres_robot))
    
    # TODO calculer la valeur du mot
    
    # Ce qui suit est un exemple fictif pour tester l'interface
    return [
        {'mot': 'RIRE', 'score': 12, 'ligne': 7, 'colonne': 5, 'direction': 'H'},
        {'mot': 'LOUP', 'score': 15, 'ligne': 10, 'colonne': 3, 'direction': 'V'}
    ]


if __name__ == "__main__":
    proposer_meilleurs_mots([], [], [])