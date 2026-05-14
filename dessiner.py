# Ce script crée un éditeur graphique sur codeboot qui permet
# de tracer des ellipses de différentes couleurs. Il gère la
# détection des clics, l'affichage de l'ellipse flottante et
# le dessin final. L'ensemble repose sur la manipulation directe
# des pixels dans une fenêtre et des concepts de géométrie.

def dans_rectangle(x_c1, x_c2, y_c1, y_c2, x, y):
    return x_c1 <= x <= x_c2 and y_c1 <= y <= y_c2


def dans_ellipse(cx, cy, rx, ry, x, y):
    return ((x - cx)**2 / rx**2) + ((y - cy)**2 / ry**2) <= 1

# Cette fonction sert à découper un une string en tableau
# selon un caractère choisi et enlève les "\n" ou non
def decouper_string(tableau, caractere, retour):
    index1 = 0
    tableau_final = []
    for index2 in range(1,len(tableau)):
        if tableau[index2] == caractere:
            if tableau[index1:index2][-1:] == "\n" and retour:
                tableau_final.append(tableau[index1:index2-1])
            else:
                tableau_final.append(tableau[index1:index2])
            index1 = index2
            
        elif index2 == len(tableau)-1:
            tableau_final.append(tableau[index1:])
        
    return tableau_final


# Obtenir un tableau des couleurs de pixels selon
# l'image d'entrée. image_in est une string
# contenant les couleurs de chaque pixel,
# on retourne un tableau dont chaque élément est une couleur
def obtenir_tableau_image_pixel(image_in):
    image = []
    
    ecran = decouper_string(image_in, "#", True)
    
    for y in range(hauteur):          # boucle sur les lignes
        ligne = []
        for x in range(largeur):      # boucle sur les colonnes
            index = y*largeur + x
            ligne.append(ecran[index])
        image.append(ligne)
    return image


def obtenir_image_actuelle():
    return obtenir_tableau_image_pixel(export_screen())


def creer_boutons(couleurs, taille, espace, couleur_effacer):
    # Retourner un tableau vide si la taille est 0 ou moins
    # (le carré n'existerait pas)
    if taille <= 0:
        return []

    # Tableau contenant les enregistrements des boutons disponibles
    boutons_dispos = []
    y_h_g = espace           # y du coin haut gauche
    y_b_d = taille + espace  # y du coin bas droit
    
    # Les x ne changent pas car les boutons sont en colonne
    x_h_g = espace + x_m_c1
    x_b_d = taille + espace + x_m_c1
    
    # Création des paramètres du boutton effacer
    if couleur_effacer:
        boutons_dispos.append(
            struct(
                coin1=struct(x=x_h_g, y=y_h_g),
                coin2=struct(x=x_b_d, y=y_b_d),
                couleur=couleur_effacer,
                effacer=True
        ))
    
    # Création des paramètres des autres boutons
    for bouton_couleur in couleurs:
        # Actualiser les y pour le prochain bouton
        y_h_g = y_b_d + espace
        y_b_d = y_h_g + taille
        
        boutons_dispos.append(
            struct(
                coin1=struct(x=x_h_g, y=y_h_g),
                coin2=struct(x=x_b_d, y=y_b_d),
                couleur=bouton_couleur,
                effacer=False
            )
        )
            
    return boutons_dispos


def trouver_bouton(boutons, position):
    for bouton in boutons:
        x_c1 = bouton.coin1.x
        y_c1 = bouton.coin1.y
        
        x_c2 = bouton.coin2.x
        y_c2 = bouton.coin2.y
        
        # Verifie si le point position est dans le carré formé par le bouton
        if dans_rectangle(x_c1, x_c2, y_c1, y_c2, position.x, position.y):
            return bouton # Retourne l'enregistrement du bouton choisi
    
    # Vérifie si le point position est dans la barre menu
    # mais pas dans un des boutons (vérification bouton déjà effectuée)
    if dans_rectangle(x_m_c1, x_m_c2, y_m_c1, y_m_c2, position.x, position.y):
        return False
    
    # Retourne None si le point position n'est pas dans la barre menu
    return None


def restaurer_image(image_originale, rectangle):
    x1, y1, x2, y2 = rectangle
    for y in range(y1, y2):
        for x in range(x1, x2):
            if 0 <= x < largeur and 0 <= y < hauteur:
                set_pixel(x, y, image_originale[y][x])     


def ajouter_ellipse(image, ellipse, couleur, mise_a_jour):
    x1, y1, x2, y2, cx, cy, rx, ry = ellipse
    x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2) 
    
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            dans_menu = dans_rectangle(x_m_c1,
                                             x_m_c2,
                                             y_m_c1,
                                             y_m_c2,
                                             x,
                                             y)
            if dans_ellipse(cx, cy, rx, ry, x, y)  and not dans_menu:
                set_pixel(x, y, couleur)
                if mise_a_jour:
                    # Mettre à jour le pixel dans l'image originale
                    image[y][x] = couleur

    
def dessiner_ellipse_flottante(image_originale, debut, couleur):
    last_x1 = last_y1 = last_x2 = last_y2 = None

    while get_mouse().button == 1:
        attrib = get_mouse()

        # Calcul du centre et des rayons
        cx, cy = (attrib.x + debut.x)//2, (attrib.y + debut.y)//2
        rx, ry = abs(attrib.x - debut.x)//2, abs(attrib.y - debut.y)//2
        if rx == 0: rx = 0.0001
        if ry == 0: ry = 0.0001

        # Rectangle actuel
        # On prend les x et y des point haut gauche et bas droit
        # selon la direction dans laquelle le rectangle est tracé 
        x1, y1 = min(debut.x, attrib.x), min(debut.y, attrib.y)
        x2, y2 = max(debut.x, attrib.x), max(debut.y, attrib.y)

        # Déterminer le rectangle combiné (ancien + nouveau)
        if last_x1 is not None:
            gx1 = min(x1, last_x1)
            gy1 = min(y1, last_y1)
            gx2 = max(x2, last_x2)
            gy2 = max(y2, last_y2)
        else:
            gx1, gy1, gx2, gy2 = x1, y1, x2, y2

        # Parcours du rectangle combiné
        for y in range(gy1, gy2 + 1):
            for x in range(gx1, gx2 + 1):
                if 0 <= x < largeur and 0 <= y < hauteur:
                    # Verifier si les pixels sont dans la barre menu ou pas
                    # pour ne pas recouvrir la barre
                    dans_menu = dans_rectangle(x_m_c1,
                                                     x_m_c2,
                                                     y_m_c1,
                                                     y_m_c2,
                                                     x, y)                  
                    # À l'intérieur de la nouvelle ellipse ?
                    if dans_ellipse(cx, cy, rx, ry, x, y) and not dans_menu:
                        set_pixel(x, y, couleur)
                    else:
                        # Sinon on restaure depuis l'image originale
                        set_pixel(x, y, image_originale[y][x])

        # Mémoriser le rectangle actuel
        last_x1, last_y1, last_x2, last_y2 = x1, y1, x2, y2

        sleep(0.01)
    
    # Effacer l'ellipse flottante avant d'ajouter la définitive
    restaurer_image(image_originale, [last_x1, last_y1, last_x2, last_y2])
    
    # Ajouter l'ellipse finale
    ajouter_ellipse(image_originale,
                    [debut.x, debut.y, attrib.x, attrib.y, cx, cy, rx, ry,],
                    couleur,
                    True)

    
def traiter_prochain_clic(etat, boutons):
    global couleur_dessin
    global image_originale
    
    while True:
        attrib = get_mouse()
        if attrib.button == 1:
            btn = trouver_bouton(boutons, attrib)
            
            if btn:
                if btn.effacer:
                    # Si le bouton effacer est cliqué, effacer l'écran
                    fill_rectangle(0, 0, largeur-24, hauteur, blanc)
                    image_originale = obtenir_image_actuelle()
                else:
                    couleur_dessin = btn.couleur
                break # Sortir de la boucle pour actualiser l'état
            
            elif btn == None:
                # Si le clic est dans la zone de dessin,
                # déssiner une ellipse flottante
                dessiner_ellipse_flottante(etat.image,
                                           attrib,
                                           etat.couleur_dessin)
                break # Pareil que l'autre break
        sleep(0.01)
    
    # Retourner le nouvel état
    return struct(couleur_dessin=couleur_dessin, image=image_originale)

    
# Définitions des couleurs
blanc = "#fff"
noir =  "#000"
rouge = "#f00"
jaune = "#ff0"
lime =  "#0f0"
bleu =  "#00f"
fuchsia = "#f0f"

couleurs = [blanc, noir, rouge, jaune, lime, bleu, fuchsia]
couleur_dessin = "#fff" # Couleur actuelle des ellipses

# Dimension de la fenêtre en pixels
largeur = 240
hauteur = 180

# Position coin 1 (haut gauche) et coin 2 (bas droit) de la barre menu
x_m_c1 = largeur-24
y_m_c1 = 0

x_m_c2 = largeur
y_m_c2 = hauteur

# Liste qui contiendra les boutons créés
boutons = []

# Image originale (sujette à changer)
image_originale = []

def dessiner():    
    global boutons
    global image_originale
    
    # Créer une fenêtre de largeur px sur hauteur px
    set_screen_mode(largeur, hauteur)
    
    fill_rectangle(0, 0, largeur, hauteur, blanc)       # écran blanc de départ
    
    fill_rectangle(x_m_c1, y_m_c1, 24, hauteur, "#999") # barre de menu grise
    
    boutons = creer_boutons(couleurs, 12, 6, "#fff")    # Créer les boutons
    
    # Afficher les boutons avec la bordure dans la barre de menu
    for bouton in boutons:
        # Hauteur et longueur des boutons sont les même car ce sont des carrés
        taille = bouton.coin2.x - bouton.coin1.x
        fill_rectangle(bouton.coin1.x,
                       bouton.coin1.y,
                       taille,
                       taille,
                       bouton.couleur)
        
        # Dessiner la bordure noire pour chaque bouton
        x1, y1 = bouton.coin1.x, bouton.coin1.y
        x2, y2 = bouton.coin2.x, bouton.coin2.y
        
        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                # On dessine que si on est sur un bord d'un bouton
                if y in (y1, y2) or x in (x1, x2):
                    set_pixel(x, y, noir)
            
        # Dessiner la croix rouge sur le bouton si c'est le bouton effacer
        if bouton.effacer:
            i = 0
            while i != (x2 - x1-1):
                i += 1
                set_pixel(x1 + i, y1 + i, rouge)
                set_pixel(x1 + taille - i, y1 + i, rouge)
    
    # Boucle principale (qui fait tourner tout le programme)
    image_originale = obtenir_image_actuelle()
    etat = struct(couleur_dessin=couleur_dessin, image=image_originale)
    while True:
        etat = traiter_prochain_clic(etat, boutons)


# Tests unitaires
def test_dessiner():
    global largeur, hauteur
    temp_largeur = largeur; temp_hauteur = hauteur


    # ----------Fonction creer_boutons----------
    # aucun boutons
    assert creer_boutons([], 12, 6, "") == []
    
    # Variable result juste par rapport au nombre maximal
    # de caractères pour chaque ligne
    result = [struct(coin1=struct(x=222, y=6),
                    coin2=struct(x=234, y=18),
                    couleur='#fff',
                    effacer=True)]

    # seulement le bouton effacer
    assert creer_boutons([], 12, 6, "#fff") == result

    # seulement un bouton blanc, pas de bouton effacer
    result = [struct(coin1=struct(x=222, y=24),
                     coin2=struct(x=234, y=36),
                     couleur='#fff',
                     effacer=False)]
    assert creer_boutons([blanc], 12, 6, "") == result

    # trois boutons, dimensions différentes
    # et espace entre eux différent
    result = [struct(coin1=struct(x=220, y=4),
                    coin2=struct(x=228, y=12),
                    couleur='#fff',
                    effacer=True),
                struct(coin1=struct(x=220, y=16),
                    coin2=struct(x=228, y=24),
                    couleur='#fff',
                    effacer=False),
                struct(coin1=struct(x=220, y=28),
                    coin2=struct(x=228, y=36),
                    couleur='#00f',
                    effacer=False)]
    assert creer_boutons([blanc, bleu], 8, 4, "#fff") == result

    # deux boutons, espace de 0 entre les boutons
    result = [struct(coin1=struct(x=216, y=0),
                    coin2=struct(x=228, y=12),
                    couleur='#fff', effacer=True),
                struct(coin1=struct(x=216, y=12),
                    coin2=struct(x=228, y=24), 
                    couleur='#fff',
                    effacer=False)]
    assert creer_boutons([blanc], 12, 0, "#fff") == result

    # deux boutons, espace et taille à 0
    assert creer_boutons([blanc], 0, 0, "#fff") == []

    # deux boutons, taille à 0 et espace à 6
    assert creer_boutons([blanc], 0, 6, "#fff") == []

    
    # ----------Fonction trouver_boutons----------
    # Variables qu'on va utiliser pour les tests de cette fonction:
    boutons = creer_boutons(couleurs, 12, 6, "#fff")
    # Simule la fonction get_mouse() :
    attrib = struct(x=228, y=6, button=1, shift=False, ctrl=False, alt=False)

    result = struct(coin1=struct(x=222, y=6),
                    coin2=struct(x=234, y=18),
                    couleur='#fff',
                    effacer=True)
    assert trouver_bouton(boutons, attrib) == result

    attrib.y = 28 # On "actualise" la position factice de la souris
    result = struct(coin1=struct(x=222, y=24),
                    coin2=struct(x=234, y=36),
                    couleur='#fff',
                    effacer=False)
    assert trouver_bouton(boutons, attrib) == result

    # On actualise et on vérifie le résultat quand le bouton
    # n'est pas enfoncé (car ce n'est pas cette fonction
    # qui fait cette vérification)
    attrib.y = 134; attrib.button = 0
    result = struct(coin1=struct(x=222, y=132),
                    coin2=struct(x=234, y=144),
                    couleur='#f0f',
                    effacer=False)
    assert trouver_bouton(boutons, attrib) == result
    
    # Cas où la souris est dans la barre de menu
    # mais pas dans un bouton
    attrib.x = 220; attrib.y = 156
    assert trouver_bouton(boutons, attrib) == False
    
    # Cas où la souris est dans la zone de dessin
    attrib.x = 86; attrib.y = 65
    assert trouver_bouton(boutons, attrib) == None
    
    
    # ----------Fonction restaurer_image----------
    # Tester avec un écran de 5x5 pixels pour simplifier
    # L'écran est noir par défaut
    largeur = 5; hauteur = 5
    set_screen_mode(largeur, hauteur)

    # Image originale blanche
    image_originale = "#fff#fff#fff#fff#fff\n"*4 + "#fff#fff#fff#fff#fff"
    restaurer_image(obtenir_tableau_image_pixel(image_originale), [0,0,5,5])
    assert export_screen() == image_originale
    
    # Image originale blanche avec ligne horizontale
    set_screen_mode(largeur, hauteur) # Remettre l'ecran par défaut
    image_originale = "#fff#fff#fff#fff#fff\n"*4 + "#f00#f00#f00#f00#f00"
    restaurer_image(obtenir_tableau_image_pixel(image_originale), [0,0,5,5])
    assert export_screen() == image_originale

    # Image originale blanche avec ligne verticale
    set_screen_mode(largeur, hauteur)
    image_originale = "#fff#fff#f00#fff#fff\n"*4 + "#fff#fff#f00#fff#fff"
    restaurer_image(obtenir_tableau_image_pixel(image_originale), [0,0,5,5])
    assert export_screen() == image_originale

    # Image originale blanche mais rectangle inexistant
    set_screen_mode(largeur, hauteur)
    ecran_depart = export_screen()
    image_originale = "#fff#fff#fff#fff#fff\n"*4 + "#fff#fff#fff#fff#fff"
    restaurer_image(obtenir_tableau_image_pixel(image_originale), [0,0,0,0])
    assert export_screen() == ecran_depart
    
    # Image originale blanche mais rectangle inexistant
    set_screen_mode(largeur, hauteur)
    ecran_depart = export_screen()
    image_originale = "#fff#fff#fff#fff#fff\n"*4 + "#fff#fff#fff#fff#fff"
    restaurer_image(obtenir_tableau_image_pixel(image_originale), [0,0,0,0])
    assert export_screen() == ecran_depart
    
    # Rectangle au centre
    set_screen_mode(largeur, hauteur)
    image_originale = "#000#000#000#000#000\n" + \
        "#000#fff#fff#fff#000\n"*3 + "#000#000#000#000#000"
    restaurer_image(obtenir_tableau_image_pixel(image_originale), [0, 0, 5, 5])
    assert export_screen() == image_originale
    

    # ----------Fonction ajouter_ellipse----------
    largeur = 30; hauteur = 30
    set_screen_mode(largeur, hauteur)

    # petite ellipse centrée
    image = obtenir_tableau_image_pixel("#000"*900)
    ellipse = [12, 12, 18, 18, 15, 15, 3, 3]
    ajouter_ellipse(image, ellipse, "#f00", False)
    screen = export_screen()
    # Le centre doit contenir du rouge
    assert "#f00" in screen

    # ellipse très large (presque plein écran)
    set_screen_mode(largeur, hauteur)
    image = obtenir_tableau_image_pixel("#000"*900)
    ellipse = [0, 0, 29, 29, 15, 15, 15, 15]
    ajouter_ellipse(image, ellipse, "#0f0", False)
    screen = export_screen()
    # beaucoup de vert attendu
    assert screen.count("#0f0") > 200

    # ellipse aplatie horizontalement
    set_screen_mode(largeur, hauteur)
    image = obtenir_tableau_image_pixel("#000"*900)
    ellipse = [5, 10, 25, 20, 15, 15, 10, 3]
    ajouter_ellipse(image, ellipse, "#00f", False)
    screen = export_screen()
    assert "#00f" in screen
    assert screen.count("#00f") > 10    

    # ellipse aplatie verticalement
    set_screen_mode(largeur, hauteur)
    image = obtenir_tableau_image_pixel("#000"*900)
    ellipse = [10, 5, 20, 25, 15, 15, 3, 10]
    ajouter_ellipse(image, ellipse, "#ff0", False)
    screen = export_screen()
    assert "#ff0" in screen
    assert screen.count("#ff0") > 10


    # ----------Fonction dans_rectangle----------
    # rectangle non carré, point à l'intérieur
    assert dans_rectangle(2, 10, 3, 7, 5, 5) == True

    # point sur le bord gauche
    assert dans_rectangle(2, 10, 3, 7, 2, 5) == True

    # point sur le coin inférieur droit
    assert dans_rectangle(2, 10, 3, 7, 10, 7) == True

    # point à l'extérieur (au-dessus)
    assert dans_rectangle(2, 10, 3, 7, 5, 8) == False

    # point à l'extérieur (à droite)
    assert dans_rectangle(2, 10, 3, 7, 11, 5) == False

    # rectangle carré, point à l'intérieur
    assert dans_rectangle(0, 5, 0, 5, 3, 3) == True

    # rectangle carré, point sur le bord supérieur
    assert dans_rectangle(0, 5, 0, 5, 2, 0) == True

    # rectangle dégénéré (un seul point)
    assert dans_rectangle(4, 4, 4, 4, 4, 4) == True
    assert dans_rectangle(4, 4, 4, 4, 4, 5) == False


    # ----------Fonction dans_ellipse----------
    # point au centre
    assert dans_ellipse(0, 0, 5, 3, 0, 0) == True

    # point sur le bord horizontal (à droite)
    assert abs(((5 - 0)**2 / 5**2) + ((0 - 0)**2 / 3**2) - 1) < 1e-9
    assert dans_ellipse(0, 0, 5, 3, 5, 0) == True

    # point strictement à l'intérieur
    assert dans_ellipse(0, 0, 5, 3, 2, 1) == True

    # point à l'extérieur (trop à droite)
    assert dans_ellipse(0, 0, 5, 3, 6, 0) == False

    # point à l'extérieur (trop haut)
    assert dans_ellipse(0, 0, 5, 3, 0, 4) == False

    # ellipse très petit (rx, ry très petit)
    assert dans_ellipse(0, 0, 0.5, 0.5, 0, 0) == True
    assert dans_ellipse(0, 0, 0.5, 0.5, 1, 1) == False


    # ----------Fonction decouper_string----------
    # string d'entrée comme la fonction export_screen()
    ecran = "#fff#fff#fff#fff#fff\n" + \
            "#fff#fff#fff#fff#fff\n" + \
            "#fff#fff#fff#fff#fff\n" + \
            "#fff#fff#fff#fff#fff"
    result = ['#fff', '#fff', '#fff', '#fff',
            '#fff', '#fff', '#fff', '#fff',
            '#fff', '#fff', '#fff', '#fff',
            '#fff', '#fff', '#fff', '#fff',
            '#fff', '#fff', '#fff', '#fff']
    assert decouper_string(ecran, "#", True) == result

    # sans enlever les retours à la ligne
    result = ['#fff', '#fff', '#fff', '#fff',
            '#fff\n', '#fff', '#fff', '#fff',
            '#fff', '#fff\n', '#fff', '#fff',
            '#fff', '#fff', '#fff\n', '#fff',
            '#fff', '#fff', '#fff', '#fff']
    assert decouper_string(ecran, "#", False) == result

    # string d'entrée vide
    ecran = ""
    result = []
    assert decouper_string(ecran, "#", True) == result    

    # changement du caractère de auquel on fait le decoupement
    ecran = "#fff#fff#fff#fff#fff"
    result = ['#', 'f', 'f', 'f#', 'f',
            'f', 'f#', 'f', 'f', 'f#',
            'f', 'f', 'f#', 'f', 'f']
    assert decouper_string(ecran, "f", True) == result    


    # Remettre variables largeur et hauteur à
    # leur valeurs après les tests
    largeur = temp_largeur
    hauteur = temp_hauteur
    
    # Mettre l'écran aux dimensions pour
    # cacher dernier test unitaire
    set_screen_mode(largeur, hauteur)


test_dessiner()