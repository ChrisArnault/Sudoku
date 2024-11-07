#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

__author__ = 'ARNAULT'

Blocs = 3
LargeurBloc = 3
Lignes = 9
Colonnes = 9


class TCase:
    def __init__ (self):
        self.valeur = None
        self.possibles = None
        self.frozen = False

    def to_text (self):
        if not self.valeur:
            result = '.'
        else:
            result = '%d' % self.valeur
        return result

    def init (self, valeur):
        if valeur == '.':
            self.valeur = False
        elif str(valeur) in '123456789':
            self.valeur = int(valeur)
        else:
            print('format error in init case')
            exit()


class TBloc:
    def __init__(self):
        self.possibles = dict()

    # on reçoit les valeurs possibles sur une case
    # on va inverser les données pour enregistrer les cases où sont possibles des valeurs
    def add(self, possibles, ligne, colonne):
        if possibles is None:
            # print 'possibles empty'
            return

        for i in range(len(possibles)):
            c = possibles[i]
            if c in self.possibles:
                ps = self.possibles[c]
            else:
                ps = []

            d = dict()
            d['l'] = ligne
            d['c'] = colonne
            ps.append(d)
            self.possibles[c] = ps

    def analyse(self, context):
        global Grille

        modifications = False

        for c in self.possibles:
            n = self.possibles[c]
            if len(n) == 1:
                ligne = n[0]["l"]
                colonne = n[0]["c"]
                la = ligne + 1
                ca = colonne + 1
                print(f'analyse dans %s [{context} {la} {ca}]={c}')
                case = Grille.une_case (ligne, colonne)
                if not case.valeur:
                    case.init(c)
                    case.possibles = None
                    modifications = True

        return modifications


class TGrille:
    def __init__(self, filename):
        self.cases = dict()
        for i in range(Lignes):
            for j in range(Colonnes):
                self.cases[(i, j)] = TCase ()

        f = open(filename, 'rb')
        lines = f.readlines()
        for linenumber, fileline in enumerate(lines):
            fileline = fileline.strip()
            if len(fileline) != 9:
                print('format error lecture sur une ligne SU')
                exit()
            for position, car in range(9):
                valeur = fileline[car]
                ligne = linenumber + 1
                colonne = position + 1
                print(f'set valeur[{colonne}, {ligne}]={valeur}')
                case = self.cases[(colonne, ligne)]
                case.init(valeur)

    def une_case(self, ligne, colonne):
        if (ligne, colonne) in self.cases:
            c = self.cases[(ligne, colonne)]
            return c
        return None

    def reset(self):
        for i in range(Lignes):
            for j in range(Colonnes):
                c = self.une_case(i, j)
                if c:
                    c.valeur = None
                    c.frozen = False
                    c.possibles = None

    def complet(self):
        for i in range(Lignes):
            for j in range(Colonnes):
                c = self.une_case(i, j)
                if not c.valeur:
                    return False
        return True

    def to_text (self):
        result = ""

        for i in range(Lignes):
            if i % 3 == 0:
                result += '+---+---+---+\n'

            ligne = ''
            for j in range(Colonnes):
                c = self.une_case(i, j)
                t = c.to_text()
                if j % 3 == 0:
                    ligne += '|'
                ligne += t
            ligne += '|\n'
            result += ligne

        result += '+---+---+---+\n'

        return result

    def step1(self, ligne, colonne, exclus):
        # On exclut les valeurs définies dans le bloc courant.

        lbloc = int(ligne / 3)
        premligne = lbloc * 3
        cbloc = int(colonne / 3)
        premcolonne = cbloc * 3

        for l in range(premligne, premligne + LargeurBloc):
            for c in range(premcolonne, premcolonne + LargeurBloc):
                if (l == ligne) and (c == colonne):
                    continue
                case = self.une_case(l, c)
                if case.valeur:
                    exclus[case.valeur] = True

        return exclus

    def step2(self, ligne, colonne, exclus):
        # On exclut les autres valeurs définies dans la ligne.

        cbloc = int(colonne / 3)
        premcolonne = cbloc * 3

        for c in range(Colonnes):
            if c == colonne:
                continue
            # on a déjà traité les colonnes du bloc courant
            if (c >= premcolonne) and (c < (premcolonne + LargeurBloc)):
                continue

            case = self.une_case (ligne, c)
            if case.valeur:
                exclus[case.valeur] = True

        return exclus

    def step3(self, ligne, colonne, exclus):
        # On exclut les autres valeurs définies dans la colonne.

        lbloc = int(ligne / 3)
        premligne = lbloc * 3

        for l in range(Lignes):
            if l == ligne:
                continue
            if (l >= premligne) and (l < (premligne + LargeurBloc)):
                continue

            case = self.une_case(l, colonne)
            if case.valeur:
                exclus[case.valeur] = True

        return exclus

    def algo1(self):
        for ligne in range(Lignes):
            for colonne in range(Colonnes):
                case = self.une_case(ligne, colonne)

                # on ne considère que les cases vides
                if case.valeur:
                    continue

                exclus = dict()
                exclus = self.step1(ligne, colonne, exclus)
                exclus = self.step2(ligne, colonne, exclus)
                exclus = self.step3(ligne, colonne, exclus)

                # On en déduit la liste des valeurs possibles pour cette case
                p = ""
                for i in range(1, 10):
                    if i not in exclus:
                        p += "%d" % i

                # On doit vérifier si cette liste a évolué
                if case.possibles != p:
                    la = ligne + 1
                    ca = colonne + 1
                    print(f"nouveaux possibles pour [{la},{ca}] {p}")
                    case.possibles = p

        modifications = False

        # on vérifie si des cases sont devenues définies

        for ligne in range(Lignes):
            for colonne in range(Colonnes):
                case = self.une_case(ligne, colonne)
                if case.valeur:
                    continue

                p = case.possibles
                if len(p) == 1:
                    la = ligne + 1
                    ca = colonne + 1
                    print(f'algo1 [{la} {ca}]={p}')
                    case.init (p)
                    case.possibles = ""
                    modifications = True

        return modifications


    def algo2(self):
        print("------- Analyse par blocs (algo2)")

        """
            On va maintenant chercher région par région les
            valeurs qui n'apparaissent qu'une fois dans les possibles
        """

        modifications = False
        m = False

        for il in range(Blocs):
            premligne = il * 3
            for ic in range(Blocs):
                premcolonne = ic * 3

                x = TBloc()

                # On regarde dans la région.
                for ligne in range(premligne, premligne + LargeurBloc):
                    for colonne in range(premcolonne, premcolonne + LargeurBloc):
                        c = self.une_case(ligne, colonne)
                        if not c.valeur and c.possibles:
                            print('Test dans la région [', (il + 1), (ic + 1), '] [', (ligne + 1), (colonne + 1), ']:', c.possibles)
                            x.add(c.possibles, ligne, colonne)

                if x.analyse('algo2'):
                    m = True
                if m:
                    break
            if m:
                break
        if m:
            modifications = True

        return modifications

    def algo3(self):
        print("------- Analyse par lignes")

        """
            On va maintenant chercher ligne par ligne les
            valeurs qui n'apparaissent qu'une fois dans les possibles
        """

        modifications = False
        m = False

        for ligne in range(Lignes):
            x = TBloc()

            # On regarde dans la ligne.
            for colonne in range(Colonnes):
                c = self.une_case(ligne, colonne)
                print('Test dans la ligne [', (ligne + 1), (colonne + 1), ']:', c.possibles)
                x.add(c.possibles, ligne, colonne)
                if not c.valeur and c.possibles:
                    pass

            if x.analyse ('algo3'):
                m = True
            if m:
                break
        if m:
            modifications = True

        return modifications

    def algo4(self):
        print("------- Analyse par colonne")

        """
            On va maintenant chercher colonne par colonne les
            valeurs qui n'apparaissent qu'une fois dans les possibles
        """

        modifications = False
        m = False

        for colonne in range(Colonnes):
            x = TBloc()

            # On regarde dans la colonne.
            for ligne in range(Lignes):
                c = self.une_case(ligne, colonne)
                if not c.valeur and c.possibles:
                    print('Test dans la colonne [', (ligne + 1), (colonne + 1), ']:', c.possibles)
                    x.add(c.possibles, ligne, colonne)
            if x.analyse ('algo4'):
                m = True
            if m:
                break
        if m:
            modifications = True

        return modifications

    def candidats (self):
        tour = 0
        modifications = True

        for ligne in range(Lignes):
            for colonne in range(Colonnes):
                c = self.une_case(ligne, colonne)
                c.possibles = None

        while modifications:
            tour += 1

            print('tour=', tour)

            modifications = self.algo1()
            if modifications:
                continue

            if self.complet():
                break

            g = Grille.to_text()
            print(g)

            modifications = self.algo2()
            if modifications:
                continue

            if self.complet():
                break

            g = Grille.to_text()
            print(g)

            modifications = self.algo3()
            if modifications:
                continue

            if self.complet():
                break

            g = Grille.to_text()
            print(g)

            modifications = self.algo4()
            if modifications:
                continue



if __name__ == '__main__':
    Grille = TGrille ('A.su')

    Grille.candidats()

    g = Grille.to_text()
    print(g)
