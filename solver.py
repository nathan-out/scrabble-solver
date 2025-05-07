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

def get_score_from_mot(mot):
    score = 0
    for lettre in mot:
        score += letter_values.get(lettre, 0)
    return score

"""
Retourne la valeur de la case coordonnées i, j si lettre est rentrée.
"""
def get_valeur_case_from_lettre(plateau_bonus, lettre, i, j):
    if plateau_bonus[i][j] == 'LS': return letter_values[lettre]
    if plateau_bonus[i][j] == 'LD': return letter_values[lettre]*2
    if plateau_bonus[i][j] == 'LT': return letter_values[lettre]*3

import re
"""
Passer de [ABC][ABC][ABC][ABC][ABC][ABC][ABC]ARBRE[ABC][ABC][ABC]
-> [ABC]{,7}ARBRE[ABC]{,3}
"""
def condenser_regex(regex):
    # Découpe : match soit un bloc [ABC], soit une séquence de lettres hors crochets
    tokens = re.findall(r'\[[^\]]+\]|[A-Z]+', regex)

    result = []
    i = 0

    while i < len(tokens):
        token = tokens[i]
        if re.fullmatch(r'\[[^\]]+\]', token):  # si c'est un bloc entre crochets
            count = 1
            while i + 1 < len(tokens) and tokens[i + 1] == token:
                count += 1
                i += 1
            result.append(f"{token}{{,{count}}}")
        else:
            result.append(token)
        i += 1

    return ''.join(result)

def get_regex_from_plateau2(ligne_or_col, lettres_robot):
    #print('get_regex_from_plateau2, ligne or col', ligne_or_col)    
    raw_regex = ''
    for element in ligne_or_col:
        if element.isalnum():
            raw_regex += element
        else:
            raw_regex += '.'
    
    # à la place de chaque . on injecte toutes les lettres que le robot peut jouer
    long_regex = raw_regex.replace('.', '['+lettres_robot+']')
    print('long_regex', long_regex)
    condensed_regex = condenser_regex(long_regex)
    print('condensed regex', condensed_regex)
    import decouper_regex
    sub_regexes = decouper_regex.decouper_regex(condensed_regex)
    print('sub regexes', sub_regexes)
    if type(sub_regexes) == str: sub_regexes = [sub_regexes] # crade!
    return sub_regexes


"""
OUTDATED
Retourne une liste de string (regex) qui contient les
possibilités sur une ligne ou une colonne.
Prend en compte les lettres du robot pour générer des
regex cohérentes pour la fonction suivante : 
get_mots_conformes_from_regex_lettres
"""
def get_regex_from_plateau(ligne_or_col, lettres_robot):
    raw_regex = ''
    for element in ligne_or_col:
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
        motif = '.{,'+str(len(plus_longue)-1)+'}'
        raw_regex = raw_regex.replace(plus_longue, motif)
        sous_regexes = raw_regex.split(motif)
        for i in range(len(sous_regexes)):
            if i%2 == 0:
                sous_regexes.append(sous_regexes[i]+motif)
            else: sous_regexes.append(motif+sous_regexes[i])

        for s_reg in sous_regexes:
            if len(re.findall(r'[A-Z]', s_reg)) == 1: # la regex a une seule lettre
                if s_reg.count('{') < 2:
                    raw_regexes.append(s_reg)
    # il y aurait encore du boulot sûrement ci-dessus mais on est déjà pas mal
    #print('raw_regexes', raw_regexes)
    regexes = []
    # à la place de chaque . on injecte toutes les lettres que le robot peut jouer
    for raw_regex in raw_regexes:
        raw_regex2 = raw_regex
        if not '.' in raw_regex2:
            raw_regex2 = '.'+raw_regex
        regexes.append(raw_regex2.replace('.', '['+lettres_robot+']'))
    #print('regexes', regexes)
    return regexes

def meilleur_placement(mot, placements, plateau_bonus, lettre_valeurs, plateau_lettres, dictionnaire):
    mot = mot.upper()
    meilleur_score = -1
    meilleur = None

    for placement in placements:
        ligne, colonne = placement['ligne'], placement['colonne']
        direction = placement['direction']
        lettres_placees = placement['a_placer']
        total_score = 0
        multiplicateur_mot = 1
        mot_valide = True

        for i, lettre in enumerate(mot):
            r = ligne if direction == 'H' else ligne + i
            c = colonne + i if direction == 'H' else colonne

            lettre_score = lettre_valeurs.get(lettre.upper(), 0)
            case_est_vide = (r, c) in lettres_placees
            bonus = plateau_bonus[r][c] if case_est_vide else 'LS'

            # Score principal
            if case_est_vide:
                if bonus == 'LS':
                    total_score += lettre_score
                elif bonus == 'LD':
                    total_score += lettre_score * 2
                elif bonus == 'LT':
                    total_score += lettre_score * 3
                elif bonus == 'MD':
                    total_score += lettre_score
                    multiplicateur_mot *= 2
                elif bonus == 'MT':
                    total_score += lettre_score
                    multiplicateur_mot *= 3
                else:
                    total_score += lettre_score
            else:
                total_score += lettre_score  # déjà sur le plateau

            # Vérifie mot croisé
            if case_est_vide:
                cross_word = lettre
                cross_score = lettre_score
                cross_multiplier = 1
                before, after = '', ''

                if direction == 'H':
                    # Parcours haut
                    i_up = r - 1
                    while i_up >= 0 and plateau_lettres[i_up][c] != '':
                        before = plateau_lettres[i_up][c] + before
                        i_up -= 1
                    # Parcours bas
                    i_down = r + 1
                    while i_down < len(plateau_lettres) and plateau_lettres[i_down][c] != '':
                        after += plateau_lettres[i_down][c]
                        i_down += 1
                else:
                    # Parcours gauche
                    i_left = c - 1
                    while i_left >= 0 and plateau_lettres[r][i_left] != '':
                        before = plateau_lettres[r][i_left] + before
                        i_left -= 1
                    # Parcours droite
                    i_right = c + 1
                    while i_right < len(plateau_lettres[0]) and plateau_lettres[r][i_right] != '':
                        after += plateau_lettres[r][i_right]
                        i_right += 1

                cross_word = before + lettre + after

                # Si un vrai mot croisé a été formé, le tester
                if len(cross_word) > 1:
                    if cross_word not in dictionnaire:
                        mot_valide = False
                        break  # mot croisé invalide
                    # Calcule le score croisé
                    for j, ch in enumerate(cross_word):
                        cross_r = r - len(before) + j if direction == 'H' else r
                        cross_c = c if direction == 'H' else c - len(before) + j
                        ch_score = lettre_valeurs.get(ch.upper(), 0)
                        if (cross_r, cross_c) == (r, c):
                            # lettre posée sur une case bonus
                            if bonus == 'LD':
                                ch_score *= 2
                            elif bonus == 'LT':
                                ch_score *= 3
                            elif bonus == 'MD':
                                cross_multiplier *= 2
                            elif bonus == 'MT':
                                cross_multiplier *= 3
                        cross_score += ch_score
                    total_score += cross_score * cross_multiplier

        if mot_valide:
            total_score *= multiplicateur_mot
            if total_score > meilleur_score:
                meilleur_score = total_score
                meilleur = {
                    'score': total_score,
                    'ligne': ligne,
                    'colonne': colonne,
                    'direction': direction,
                    #'a_placer': lettres_placees
                }

    return meilleur

"""
TODO
"""
def trouver_placements_valides_sur_ligne_ou_colonne(mot, index, direction, plateau_lettres):
    n = len(plateau_lettres)
    taille_mot = len(mot)
    placements = []

    if mot not in dictionary:
        return []

    for start in range(n - taille_mot + 1):
        coords_a_placer = []
        mot_valide = True
        touche_lettre_existante = False  # Nouvelle condition

        for i, lettre in enumerate(mot):
            r = index if direction == 'H' else start + i
            c = start + i if direction == 'H' else index

            case = plateau_lettres[r][c]

            if case != '' and case != lettre:
                mot_valide = False
                break

            if case == '':
                coords_a_placer.append((r, c))
            else:
                touche_lettre_existante = True

            # Vérification des mots croisés
            mot_croisé = lettre
            r1, c1 = r, c
            while direction == 'H' and r1 > 0 and plateau_lettres[r1 - 1][c] != '':
                r1 -= 1
                mot_croisé = plateau_lettres[r1][c] + mot_croisé
            while direction == 'V' and c1 > 0 and plateau_lettres[r][c1 - 1] != '':
                c1 -= 1
                mot_croisé = plateau_lettres[r][c1] + mot_croisé
            r2, c2 = r, c
            while direction == 'H' and r2 < n - 1 and plateau_lettres[r2 + 1][c] != '':
                r2 += 1
                mot_croisé = mot_croisé + plateau_lettres[r2][c]
            while direction == 'V' and c2 < n - 1 and plateau_lettres[r][c2 + 1] != '':
                c2 += 1
                mot_croisé = mot_croisé + plateau_lettres[r][c2]

            if len(mot_croisé) > 1 and mot_croisé.upper() not in dictionary:
                mot_valide = False
                break

        # Vérification finale : le mot doit toucher au moins une lettre posée
        if mot_valide and touche_lettre_existante:
            placements.append({
                #'mot': mot,
                'ligne': index if direction == 'H' else start,
                'colonne': start if direction == 'H' else index,
                'direction': direction,
                'a_placer': coords_a_placer
            })
        #else: print(mot, 'ne touche pas. mot valide', mot_valide, 'touche lettre', touche_lettre_existante)

    return placements


"""
Retourne les mots qui matche la disposition des lettres sur le
plateau (symbolisé par regex).
Prend en compte les lettres du robots (string de forme A,B,C...)
Retourne une liste de string
"""
def get_mots_conformes_from_regex_lettres(regex, lettres_robot, ligne_and_col):
    import re # calcul des mots qui matchent la regex
    # i.e les mots qui matchent l'ordre des lettres
    # mais pas les mots qui matche le bon nombre de lettres
    # on vérifie cela plus bas dans l'algorithme
    pattern = re.compile(regex, re.IGNORECASE)
    mots = [mot for mot in dictionary if pattern.fullmatch(mot)]
    #print('pré mots', mots)
    lettres_robot = list(lettres_robot) # liste des lettres du robot
    mots_retenus = mots.copy() # on doit faire une copie indépendante sinon on se marche dessus pendant la boucle

    # on filtre les éléments vides dans la ligne ou colonne
    ligne_and_col_filtree = [s for s in ligne_and_col if s != '']
    # il faut ajouter les lettres présentes sur la grille (i.e dans base_regex) dans les lettres consomables
    # on s'en fiche de l'ordre car ça a déjà été check juste au-dessus
    # on considère toutes les lettres (celles du robot + celles sur le plateau) comme des consommables
    # ici on ajoute les lettres du robot aux lettres sur le plateau dans une seule liste
    for c in ligne_and_col_filtree: lettres_robot.append(c) # parfois des mots impossibles ici BUG.
    print('get mots conformes from regex, lettres conso :', lettres_robot)

    for mot in mots:
        mot_valide = True
        lettres_consomables = lettres_robot.copy() # on doit faire une copie indépendante sinon on se marche dessus pendant la boucle
        #print(f'testing {mot}, reste {lettres_consomables}')
        for lettre in mot:
            if lettre in lettres_consomables:
                lettres_consomables.remove(lettre)
                #print(lettres_consomables, end='')
            else: # quand les consomables sont épuisés -> mot incorrect
                if mot in dictionary and len(lettres_consomables) == 0:# cas limite on a épuisé toutes les lettres et le mot est valide
                    print('CAS LIMITE', mot)
                    break
                mot_valide = False
                print(f'{mot} impossible : {lettres_consomables}')
                break
        if not mot_valide: mots_retenus.remove(mot)

    return mots_retenus

def proposer_meilleurs_mots(plateau_lettres, lettres_robot, plateau_bonus):
    """
    Reçoit l’état du plateau (15x15, chaque case contient '' ou une lettre),
    et les lettres disponibles du robot (str).
    Retourne une liste de suggestions, chaque suggestion est un dictionnaire :
    {
        'EXEMPLE':
        {
            'score': 23,
            'ligne': 7,
            'colonne': 5,
            'direction': 'H'  # ou 'V'
        }
    }
    """
    #lettres_robot = "V,O,L,E,F,C,E,X" # debug
    # get_regex_from_plateau va trouver des regex à partir d'une liste d'éléments
    # pour lui faire chercher sur les lignes et les colonnes,
    # il faut donc un peu ruser.
    # On créé une liste de listes qui contient les lignes et les col du plateau
    print('Calcul des regex sur les lignes et les colonnes...')
    lignes_and_cols = []
    for i in range(len(plateau_lettres)):
        # ajout d'une ligne
        lignes_and_cols.append(plateau_lettres[i])
        col = []
        for j in range(len(plateau_lettres[i])):
            # ajout d'une col
            col.append(plateau_lettres[j][i])
        lignes_and_cols.append(col)
    #print(lignes_and_cols) # debug

    mots_proposes = {}
    for i, ligne_and_col in enumerate(lignes_and_cols):
        # petit gain de perf ici : si ligne ou col vide on passe à la suite
        if all(e == '' for e in ligne_and_col):
            #print(f'{i+1}/45 VIDE -> non calculé') 
            continue
        
        print(f'{i+1}/45')
        regexes = get_regex_from_plateau2(ligne_and_col, lettres_robot)
        print('regexes', regexes)
        # Ici il reste potentiellement des mots impossibles (qui utilisent plusieurs fois une lettre par ex)
        # Mais on a déjà fait un GROS pré-tri. Il faut vérifier pour chaque mot s'il respecte les règles
        # On fait ça dans get_mots_conformes_from_regex_lettres
        for regex in regexes:
            mots_conformes = get_mots_conformes_from_regex_lettres(regex, lettres_robot, ligne_and_col)
            print('mots conformes', mots_conformes)
            for mot in mots_conformes:
                ligne = (i//2) if i % 2 == 0 else '?'
                colonne = (i//2) if i % 2 != 0 else '?'
                direction = 'H' if i % 2 == 0 else 'V'
                # un mot conforme ne veut pas dire un mot valide au sens où
                # il peut colisionner avec une col adjacente s'il est placé verticalement
                # idem pour horizontalement.
                # il faut donc simuler le placement du mot sur la grille pour en être sûr
                # et calculer son score avec les cases spéciales
                index = (i//2)
                coords_mot = trouver_placements_valides_sur_ligne_ou_colonne(mot, index, direction, plateau_lettres)
                print('coords mot pour',mot, coords_mot)
                if coords_mot != []:
                    meilleur = meilleur_placement(mot, coords_mot, plateau_bonus, letter_values, plateau_lettres, dictionary)
                    mots_proposes[mot] = {
                        'score': meilleur['score'],
                        'placement': meilleur,
                    }
                    #print('meilleur', meilleur)
            print(f'Nb de mots conformes et valides : {len(mots_proposes)}')
        mots_ordonnes = dict(sorted(mots_proposes.items(), key=lambda item: item[1]['score'], reverse=True))
    print('mots placables', mots_proposes)
    # Retourne les 3 mots qui ont le plus de score
    return dict(list(mots_ordonnes.items()))


if __name__ == "__main__":
    proposer_meilleurs_mots([], [], [])