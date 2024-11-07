#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

from tkinter import *
import tkinter.font as font
import time

Lignes = 9
Colonnes = 9

white = (255, 255, 255)
blue = (255, 0, 0)
green = (0, 255, 0)
red = (0, 0, 255)
yellow = (0, 255, 255)
magenta = (255, 0, 255)
cyan = (255, 255, 0)


Refresh_Sec = 0.01


def scale(x):
    s = 1.8
    return int(x * s)

Changed = False

def set_changed(info = ''):
    global Changed
    print(f"set changed {info}")
    Changed = True

def reset_changed():
    global Changed
    print("reset changed")
    Changed = False

class SudoCase:
    def __init__ (self, colonne, ligne):
        self.colonne = colonne
        self.ligne = ligne
        self.valeur = None
        self.allowed = None
        self.forbidden = list()
        self.frozen = False

    def __repr__(self):
        if not self.valeur:
            result = '.'
        else:
            result = '%d' % self.valeur
        return result

    def init (self, valeur):
        self.valeur = valeur

    def in_square(self, sq_colonne, sq_ligne):
        same_colonne = int((self.colonne - 1)/3) == (sq_colonne - 1)
        same_ligne = int((self.ligne - 1)/3) == (sq_ligne - 1)
        return same_colonne and same_ligne

    def add_forbidden(self, valeur, info=""):
        if self.forbidden is None:
            self.forbidden = list()

        if self.allowed is not None and valeur in self.allowed:
            self.allowed.remove(valeur)

        if valeur not in self.forbidden:
            self.forbidden.append(valeur)
            set_changed(f"add forbidden {valeur} {info}")
            return True
        return False

    def allow(self):
        if self.allowed is None:
            self.allowed = list()
            for i in range(1, 10):
                if self.forbidden is not None and i not in self.forbidden:
                    self.allowed.append(i)

    def draw(self, frame):
        square = int((self.ligne - 1)/3)*3 + int((self.colonne - 1)/3)
        background = 'yellow'
        if square % 2 == 0:
            background = 'lightgray'
        canvas = Canvas(frame, width=scale(50), height=scale(50), background=background)
        canvas.grid(row=self.ligne, column=self.colonne)
        if self.valeur != 0:
            txt = canvas.create_text(scale(24), scale(24), text=f'{self.valeur}', font=("Arial 16 italic", scale(28)), fill="blue")
            pass
        else:
            y0 = scale(8)
            dy = scale(18)
            x0 = scale(8)
            dx = scale(18)
            y = y0
            n = 1
            for ly in range(3):
                x = x0
                for cx in range(3):
                    if n not in self.forbidden:
                        canvas.create_text(x, y, text=f'{n}', font=("Arial 16 italic", scale(10)), fill="red")
                    x += dx
                    n += 1
                y += dy


class SudoLine:
    def __init__(self, ligne):
        self.ligne = ligne

    def __repr__(self):
        t = ""
        for colonne in range(1, Colonnes+1):
            case = Grille.cases[(colonne, self.ligne)]
            t += f"{case}"
        return (f"SudoLine[{self.ligne}]=[{t}]")

    def check(self, selected_case, info=""):
        if self.ligne != selected_case.ligne:
            return

        for colonne in range(1, Colonnes+1):
            if colonne == selected_case.colonne:
                continue
            case = Grille.cases[(colonne, self.ligne)]
            if case.valeur != 0:
                if selected_case.add_forbidden(case.valeur, info):
                    # print(f"Line> [{colonne}, {self.ligne}] v={case.valeur} c=[{selected_case.colonne}, {selected_case.ligne}] f=[{selected_case.forbidden}]")
                    pass

class SudoColonne:
    def __init__(self, colonne):
        self.colonne = colonne

    def __repr__(self):
        t = ""
        for ligne in range(1, Lignes+1):
            case = Grille.cases[(colonne, ligne)]
            t += f"{case}"
        print(f"SudoColonne[{colonne}]=[{t}]")

    def check(self, selected_case, info=""):
        if self.colonne != selected_case.colonne:
            return

        for ligne in range(1, Lignes+1):
            if ligne == selected_case.ligne:
                continue
            case = Grille.cases[(self.colonne, ligne)]
            if case.valeur != 0:
                if selected_case.add_forbidden(case.valeur, info):
                    # print(f"Colonne>  [{self.colonne}, {ligne}] v={case.valeur} c=[{selected_case.colonne}, {selected_case.ligne}] f=[{selected_case.forbidden}]")
                    pass


class SudoSquare:
    def __init__(self, colonne, ligne):
        self.colonne = colonne
        self.ligne = ligne

    def range_colonne(self):
        c0 = (self.colonne - 1) * 3
        return range(c0 + 1, c0 + 4)

    def range_ligne(self):
        l0 = (self.ligne - 1) * 3
        return range(l0 + 1, l0 + 4)

    def __repr__(self):
        for ligne in self.range_ligne():
            tl = ""
            for colonne in self.range_colonne():
                case = Grille.cases[(colonne, ligne)]
                tl += f"{case}"
            print(f"SudoSquare[{self.colonne}, {self.ligne}]=[{tl}]")

    def check(self, selected_case, info=""):
        if not selected_case.in_square(self.colonne, self.ligne):
            return

        for colonne in self.range_colonne():
            for ligne in self.range_ligne():
                if ligne == selected_case.ligne and colonne == selected_case.colonne:
                    continue
                case = Grille.cases[(colonne, ligne)]
                if case.valeur != 0:
                    if selected_case.add_forbidden(case.valeur, info):
                        # print(f"Square>  [{colonne}, {ligne}] v={case.valeur} c=[{selected_case.colonne}, {selected_case.ligne}]  f=[{selected_case.forbidden}]")
                        pass

class SudoGrille:
    def __init__(self, filename):
        self.cases = dict()
        for colonne in range(1, Colonnes+1):
            for ligne in range(1, Lignes+1):
                self.cases[(colonne, ligne)] = SudoCase(colonne, ligne)

        f = open(filename, 'rb')
        lines = f.readlines()
        for linenumber, fileline in enumerate(lines):
            fileline = fileline.strip()
            if len(fileline) != 9:
                print('format error lecture sur une ligne SU')
                exit()
            for position in range(9):
                car = fileline[position]
                if car == 46:
                    valeur = 0
                elif car >= 48 or car <= 56:
                    valeur = car - 48
                else:
                    print(f'format error in init case {car}')
                    exit()

                ligne = linenumber+1
                colonne = position+1
                case = self.cases[(colonne, ligne)]
                case.init(valeur)
                # print(f'line={fileline} car={car} set valeur[{colonne}, {ligne}]={case.valeur}')

        set_changed("init Grille")

def algo1():
    # premier algo:
    # on vérifie pour une case donnée:
    #   toutes les valeurs exactes
    #     sur la ligne de la case
    #     sur la colonne de la case
    #     sur le carré de la case
    #   deviennent interdites pour cette case

    print("Algo1 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    for ligne in range(1, Lignes+1):
        for colonne in range(1, Colonnes+1):
            selected_case = Grille.cases[(colonne, ligne)]

            sq_colonne = int((colonne - 1)/3) + 1
            sq_ligne = int((ligne - 1)/3) + 1

            # print(f"-----------------[{colonne},{ligne},[{sq_colonne},{sq_ligne}]]")

            SudoLine(ligne).check(selected_case, f"from [{colonne},{ligne}]")
            SudoColonne(colonne).check(selected_case, f"from [{colonne},{ligne}]")
            SudoSquare(sq_colonne, sq_ligne).check(selected_case, f"from [{colonne},{ligne}]")

    print("Algo1 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

def algo2():
    # mettre en place les valeurs autorisées (inverses des interdits)
    # lorsqu'il y a une seule autorisée, cette valeur devient exacte

    print("Algo2 -----------------------------------------------------------------------")

    for ligne in range(1, Lignes+1):
        for colonne in range(1, Colonnes+1):
            selected_case = Grille.cases[(colonne, ligne)]
            selected_case.allow()
            if selected_case.valeur == 0 and len(selected_case.allowed) == 1:
                selected_case.valeur = selected_case.allowed[0]
                selected_case.allowed = None
                selected_case.forbidden = None
                set_changed(f"validate value {selected_case.valeur} at [{colonne},{ligne}]")

def algo3():
    # on va détecter dans un carré les valeurs autorisées uniques
    # c'est à dire lorsque une valeur autorisée n'existe que dans une seule case

    print("Algo3 -----------------------------------------------------------------------")


    for colonne in range(1, 4):
        for ligne in range(1, 4):
            # carré [colonne, ligne]
            unique = dict()
            for ccolonne in range(1, 4):
                for cligne in range(1, 4):
                    col = (colonne-1)*3 + ccolonne
                    lig = (ligne-1)*3 + cligne
                    selected_case = Grille.cases[(col, lig)]
                    if selected_case.valeur != 0:
                        continue
                    # print(f"[{colonne},{ligne}] [{col},{lig}]  {selected_case.allowed}")
                    if len(selected_case.allowed) > 0:
                        for v in selected_case.allowed:
                            if v not in unique:
                                unique[v] = list()
                            unique[v].append((col, lig))
            for v in unique:
                if len(unique[v]) == 1:
                    # print(f"{v}={unique[v]} {len(unique[v])}")
                    adresse = unique[v][0]
                    c = Grille.cases[adresse]
                    c.valeur = v
                    c.allowed = None
                    c.forbidden = None
                    set_changed(f"algo3> validate {v} at [{colonne},{ligne}]")

def algo4():
    # on détecte la situation suivante dans un carré:
    #   sur une ligne ou une colonne, des valeurs autorisées n'existent que dans cette ligne ou dans cette colonne
    # cela signifie que ces valeurs ne peuvent exister qu'à l'intérieur de ce carré sur cette ligne ou cette colonne
    # et donc elles doivent être supprimées des valeurs autorisées dans cette ligne ou dans cette colonne
    # dans les autres carrés.

    print("Algo4 -----------------------------------------------------------------------")


    for colonne in range(1, 4):
        for ligne in range(1, 4):
            # carré [colonne, ligne]
            # toutes les addresses pour ce carré ordonnées par valeur autorisées
            print(f"algo4> [{colonne},{ligne}]")
            aligned = dict()
            for ccolonne in range(1, 4):
                for cligne in range(1, 4):
                    col = (colonne-1)*3 + ccolonne
                    lig = (ligne-1)*3 + cligne
                    selected_case = Grille.cases[(col, lig)]

                    if selected_case.valeur != 0:
                        continue

                    print(f"     algo4> case: [{col},{lig}] {selected_case.allowed} {selected_case.forbidden}")

                    # print(f"[{colonne},{ligne}] [{col},{lig}]  {selected_case.allowed}")
                    if len(selected_case.allowed) > 0:
                        for v in selected_case.allowed:
                            if v not in aligned:
                                aligned[v] = list()
                            aligned[v].append((col, lig))

            # je cherche les valeurs alignées (ligne ou colonne)
            for v in aligned:
                # print(f"algo4> [{colonne},{ligne}] {v}={aligned[v]}")
                addresses = aligned[v]
                c = None
                l = None
                c_aligned = True
                l_aligned = True
                for a in addresses:
                    if c is None:
                        c = a[0]
                        l = a[1]
                        continue
                    if a[0] != c:
                        c_aligned = False
                    if a[1] != l:
                        l_aligned = False

                if c_aligned:
                    a = aligned[v]
                    print(f"c_aligned [{colonne},{ligne}] {v}={aligned[v]} colonne={a[0][0]}")
                    # il faut chercher les occurrences des valeurs autorisées v dans les autres carrés
                    # et sur la colonne a[0][0] et les supprimer
                    for allowline in range(1, Lignes):
                        sq_line = int((allowline-1)/3 + 1)
                        if sq_line == ligne:
                            # on évite le carré courant
                            continue
                        allowcolonne = a[0][0]
                        allowcase = Grille.cases[(allowcolonne, allowline)]
                        if allowcase.forbidden is not None and v not in allowcase.forbidden:
                            allowcase.add_forbidden(v)
                            set_changed(f"algo4> add forbidden {v} from colonne {allowcolonne}")
                        pass
                    pass
                if l_aligned:
                    a = aligned[v]
                    print(f"l_aligned [{colonne},{ligne}] {v}={aligned[v]} ligne={a[0][1]}")
                    # il faut chercher les occurrences des valeurs autorisées v dans les autres carrés
                    # et sur la ligne a[0][1] et les supprimer
                    for allowcolonne in range(1, Colonnes):
                        sq_colonne = int((allowcolonne-1)/3 + 1)
                        if sq_colonne == colonne:
                            # on évite le carré courant
                            continue
                        allowline = a[0][1]
                        allowcase = Grille.cases[(allowcolonne, allowline)]
                        if allowcase.forbidden is not None and v not in allowcase.forbidden:
                            allowcase.add_forbidden(v)
                            set_changed(f"algo4> add forbidden {v} from ligne {allowline}")
                        pass
                    pass

    pass

def algo5():
    # situation:
    # on a nettoyé les valeurs autorisées dans toutes les cases.
    # dans un carré, si une case contient une valeur autorisée unique pour le carré
    # alors cette valeur devient la valeur exacte

    print("Algo5 -----------------------------------------------------------------------")

    for colonne in range(1, 4):
        for ligne in range(1, 4):
            # on est dans un carré
            print(f"algo5> [{colonne},{ligne}]")
            # on scan toutes les cases avec des valeurs autorisées
            for ccolonne in range(1, 4):
                for cligne in range(1, 4):
                    col = (colonne-1)*3 + ccolonne
                    lig = (ligne-1)*3 + cligne
                    selected_case = Grille.cases[(col, lig)]

                    print(f"     algo5> case: [{col},{lig}] {selected_case.allowed} {selected_case.forbidden}")

                    if selected_case.valeur != 0:
                        continue
                    if len(selected_case.allowed) == 1:
                        selected_case.valeur = selected_case.allowed[0]
                        selected_case.allowed = None
                        selected_case.forbidden = None
                        set_changed(f"algo5> validate {selected_case.valeur} at [{ccolonne},{cligne}]")

            pass


def algo6():
    # Ici, on n'a plus d'approche strictement algorithmique
    # On va donc trouver une situation où
    # - dans une ligne ou une colonne, il ne reste plus à résoudre que deux cases
    #   situées à l'intérieur d'un carré (donc 2 chiffres [a, b] ou [b, a])
    # Pour résoudre cette situation, on commance par sauvegarder la Grille en l'état
    # Puis on choisi la combinaison [a, b] ce qui valide deux cases arbitrairement
    # Puis on relance la suite des algos comme précédemment.
    # Si on aboutit à une contradiction, alors on sait que c'était l'autre combinaison qui
    # était la bonne. On la valide et on on reprend la suite des algos
    # On peut aboutir à une non décision lorsque la Grille n'a pas été résolue mais sans contradiction
    # Alors on doit reprendre l'algo6 récursivement là où on est arrivé

    # sauvegarde de la grille

    # recherche du pattern [ab, ab] sur une ligne ou un colonne d'un carré

    # Choix arbitraire de la combinaison [a, b]

    # Relance de la suite des algos



    print("Algo6 -----------------------------------------------------------------------")



match = dict()

def redraw(frame):
    for ligne in range(1, Lignes+1):
        for colonne in range(1, Colonnes+1):
            # print(f"C={colonne} L={ligne}")
            c = Grille.cases[(colonne, ligne)]
            c.draw(frame)

class Animation:
    def __init__(self, fenetre, text, frame):
        self.fenetre = fenetre
        self.text = text
        self.frame = frame
        self.step = 1
        self.loop = 1
        self.match = {
            1:(f"Boucle {self.loop}", None),
            2:("Algo1", algo1),
            3:("Algo2", algo2),
            4:("Algo3", algo3),
            5:("Algo4", algo4),
            6:("Algo5", algo5),
        }

    def next_step(self):
        action = self.match[self.step]
        if self.step == 1:
            reset_changed()
            start = action[1]
            action = (f"Boucle {self.loop}", start)
            print(f"============= Changed {Changed}==================")
        else:
            print(f"============= {self.loop} Step {self.step} action {action[0]} ==================")
            action[1]()
            print(f"============= Changed {Changed} ==================")

        if not Changed:
            print(f"============= Next step ==================")
            self.step += 1
            if self.step > 6:
                self.step = 1
                self.loop += 1

                reset_changed()
        else:
            print(f"============= Restart steps ==================")
            self.step = 1
            reset_changed()

        action = self.match[self.step]
        if self.step == 1:
            start = action[1]
            self.text.set(f"Start boucle {self.loop}")
        else:
            self.text.set(f"(boucle {self.loop}) Run {action[0]}")
        redraw(self.frame)
        self.fenetre.update()


if __name__ == '__main__':
    Grille = SudoGrille('A.su')

    fenetre = Tk()
    fenetre.title("Sudoku")
    fenetre.config(bg = "#87CEEB")
    fenetre.geometry(f"{scale(640)}x{scale(640)}")

    myfont = font.Font(family='Helvetica', size=14)

    # frame
    out_frame = Frame(fenetre, borderwidth=2, relief=GROOVE)
    out_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    text = StringVar()
    text.set("Continue")

    animation = Animation(fenetre, text, out_frame)

    button = Button(fenetre, textvariable=text, command=animation.next_step)
    button.pack()
    button['font'] = myfont


    stop = Button(fenetre, text='Stop', command=fenetre.destroy)
    stop.pack()
    stop['font'] = myfont

    animation.next_step()

    # redraw(out_frame)
    # text.set("Fin.......................")

    fenetre.mainloop()


