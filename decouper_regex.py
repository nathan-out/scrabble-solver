import re

def sous_regex(regex):
    #print('regex', regex)
    result = split(regex)
    if result is None:
        #print(f'{regex} is atomic')
        return regex
    
    fils_gauche, fils_droit = result
    #print('fg', fils_gauche, 'fd', fils_droit)
    return (sous_regex(fils_gauche), sous_regex(fils_droit))

def split(regex):
    result = re.search(r'([}\]])[A-Z]{1,}([{\[])', regex)
    if result == None: return None

    span = result.span()
    indice_a_couper = span[0]+1
    fils_gauche = regex[:indice_a_couper+1]
    fils_droit = regex[indice_a_couper:]
    return (fils_gauche, fils_droit)

def aplatir(element):
    resultat = []
    if type(element) == tuple:
        for item in element:
            if isinstance(item, (list, tuple)):
                resultat.extend(aplatir(item))  # appel récursif
            else:
                resultat.append(item)
    else: return element # l'élément est un string
    return resultat

def decouper_regex(regex):
    return aplatir(sous_regex(regex))