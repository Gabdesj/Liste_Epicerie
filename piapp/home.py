
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import random


from PIL import Image
import pytesseract
from wand.image import Image as Img
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag


import RPi.GPIO as GPIO
import time


app = Flask(__name__)
app.secret_key = "!&%@sdsdsahywybfkb15446456565566svdfjhsfgjjdjeugfbcotsc#!(@%$@(!?(!diihbc*@?$!@(&"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/pi/db/flaskDB'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)



class t_repas(db.Model):
     _id = db.Column("id", db.Integer, primary_key=True)
     nomRepas = db.Column(db.String(100))
     ingredient = db.Column(db.String(100))

     def __init__(self, nomRepas, ingredient):
         self.nomRepas = nomRepas
         self.ingredient = ingredient

db.create_all()
db.session.commit()



@app.route("/")
def index():
    session["nbr_ing"] = None
    return render_template("index.html")

@app.route("/ajoutRepas", methods=["POST", "GET"])
def ajoutRepas():
    if request.method == "POST":
        if request.form["f_nbrIngredient"] == "":
            flash("Veuillez entrer une valeur dans la case")
            return render_template("ajoutRepas.html")
        f_nombreIngredient = int(request.form["f_nbrIngredient"])
        session["nbr_ing"] = f_nombreIngredient
    return render_template("ajoutRepas.html")




@app.route("/ajoutRepas_query", methods=["POST","GET"])
def ajoutRepas_query():
    if request.method == "POST":
        if request.form["f_repas"] == "":
            flash("Ne pas laisser de case vide svp")
            return render_template("ajoutRepas.html")

        for i in range(session["nbr_ing"]):
            texte = "f_ingredient{}".format(i+1)
            if request.form[texte] == "":
                flash("Ne pas laisser de case vide svp")
                return render_template("ajoutRepas.html")

        repas = request.form["f_repas"].lower()
        for i in range(session["nbr_ing"]):
            texte = "f_ingredient{}".format(i+1)
            ingredient = request.form[texte].lower()
            entry = t_repas(repas,ingredient)
            db.session.add(entry)
            db.session.commit()
        flash("le repas a été ajouté à la liste!")
        session["nbr_ing"] = None
    return render_template("index.html")



@app.route("/enleverRepas", methods=["POST", "GET"])
def enleverRepas():
    if request.method == "POST":
        flash("methode post utilisée")
    values=t_repas.query.all()
    repas = []
    for i in values:
        repas.append(i.nomRepas)
        repas = sorted(list(dict.fromkeys(repas)))
    return render_template("enleverRepas.html", listeRepas=repas)


@app.route("/enleverRepas_query", methods=["POST","GET"])
def enleverRepas_query():
    if request.method == "POST":
        repas_a_enlever = request.form["f_dropdown"]
        delete_entries = t_repas.query.filter_by(nomRepas=repas_a_enlever).all()
        for i in delete_entries:
            db.session.delete(i)
            db.session.commit()

        flash("le repas a été supprimé de la liste")
    return render_template("index.html")


@app.route("/modifRepas", methods=["POST", "GET"])
def modifRepas():
    if request.method == "POST":
        flash("méthode post activée")
    values=t_repas.query.all()
    repas = []
    for i in values:
        repas.append(i.nomRepas)
        repas = list(dict.fromkeys(repas))
    return render_template("modifRepas.html", listeRepas=repas)



@app.route("/printListe", methods=["POST", "GET"])
def printListe():
    if request.method == "POST":
        flash("méthode post activée")
    values=t_repas.query.all()
    repas = []
    for i in values:
        repas.append(i.nomRepas)
        repas = sorted(list(dict.fromkeys(repas)))

    return render_template("printListe.html", listeRepas=repas)



@app.route("/confirmation", methods=["POST","GET"])
def confirmation():
    if request.method == "POST":
        if request.form.get("checkbox") == "on":
            Repas = repasAleatoire()
            d_repas = ingrédientsRequisAleatoire(Repas)

            joursSemaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

            for i in range(7):
                Repas[i] = Repas[i] + " pour {}".format(joursSemaine[i])


            return render_template("confirmation.html", dico_ingredient=d_repas, listeRepas=Repas)


        repasLundi = request.form["f_dropdown1"]+" pour Lundi"
        repasMardi = request.form["f_dropdown2"]+" pour Mardi"
        repasMercredi = request.form["f_dropdown3"]+" pour Mercredi"
        repasJeudi = request.form["f_dropdown4"]+" pour Jeudi"
        repasVendredi = request.form["f_dropdown5"]+" pour Vendredi"
        repasSamedi = request.form["f_dropdown6"]+" pour Samedi"
        repasDimanche = request.form["f_dropdown7"]+" pour Dimanche"

        Repas = [repasLundi,repasMardi,repasMercredi,repasJeudi,repasVendredi,repasSamedi,repasDimanche]
        d_repas = ingrédientsRequis()

        return render_template("confirmation.html", dico_ingredient=d_repas, listeRepas=Repas)
    else:
        return render_template("index.html")


@app.route("/table")
@app.route("/viewtable")
def viewtable():
    query = list(t_repas.query.all())
    return render_template("view.html", values=query)


@app.route("/circulaire", methods=["POST", "GET"])
def listeRabais():
    if request.method == "POST":
        flash("methode post utilisée")
    values=t_repas.query.all()
    repas = []
    for i in values:
        repas.append(i.ingredient)
        repas = sorted(list(dict.fromkeys(repas)))
    return render_template("listeRabais.html", listeRepas=repas)

@app.route("/listeCirculaire", methods=["POST", "GET"])
def printCirculaire():
    if request.method == "POST":

        input_dropdown = []
        listeRepas=[]
        iterations = int(request.form["nbrIngredients"])
        for i in range(iterations):
            ingredient = request.form["f_dropdown{}".format(i+1)]
            input_dropdown.append(ingredient)


        selection_repas = {}
        repas_confirmation = {}

        for i in range(iterations):

            Query = t_repas.query.filter_by(ingredient=input_dropdown[i]).all()
            for item in Query:
                if item.nomRepas not in selection_repas:
                    selection_repas[item.nomRepas] = 1
                else:
                    selection_repas[item.nomRepas] += 1

        if len(selection_repas) >= 7:
            for i in range(7):
                repasRabais = max(selection_repas,key=selection_repas.get)
                listeRepas.append(repasRabais)
                selection_repas.pop(repasRabais)

            random.shuffle(listeRepas)
            d_repas = ingrédientsRequisAleatoire(listeRepas)
            return render_template("confirmation.html", dico_ingredient=d_repas, listeRepas=listeRepas)

        else:
            listeRepas = []
            nombreRepasManquants = 7 - len(selection_repas)

            for i in range(len(selection_repas)):
                repasRabais = max(selection_repas, key=selection_repas.get)
                listeRepas.append(repasRabais)
                selection_repas.pop(repasRabais)

            values=t_repas.query.all()
            repasDispos = []
            listeRepasChoisis = []

            for i in values:
                repasDispos.append(i.nomRepas)
                repasDispos = list(dict.fromkeys(repasDispos))

            for i in range(nombreRepasManquants):
                randomIndex = random.randint(0, len(repasDispos) - 1)
                listeRepasChoisis.append(repasDispos[randomIndex])
                repasDispos.pop(randomIndex)

            listefinale = listeRepas + listeRepasChoisis
            d_repas = ingrédientsRequisAleatoire(listefinale)

            repasLundi = listefinale[0]+" pour Lundi"
            repasMardi = listefinale[1]+" pour Mardi"
            repasMercredi = listefinale[2]+" pour Mercredi"
            repasJeudi = listefinale[3]+" pour Jeudi"
            repasVendredi = listefinale[4]+" pour Vendredi"
            repasSamedi = listefinale[5]+" pour Samedi"
            repasDimanche = listefinale[6]+" pour Dimanche"

            listefinale = [repasLundi, repasMardi, repasMercredi, repasJeudi, repasVendredi, repasSamedi, repasDimanche]

            return render_template("confirmation.html", dico_ingredient=d_repas, listeRepas=listefinale)

    else:
        return render_template("index.html")



def repasAleatoire():
    values=t_repas.query.all()
    repasDispos = []
    listeRepasChoisis = []

    for i in values:
        repasDispos.append(i.nomRepas)
        repasDispos = list(dict.fromkeys(repasDispos))

    for i in range(7):
        randomIndex = random.randint(0, len(repasDispos) - 1)
        listeRepasChoisis.append(repasDispos[randomIndex])
        repasDispos.pop(randomIndex)


    return listeRepasChoisis

def ingrédientsRequis():
    d_repas = {}
    liste_ing = []
    for i in range(7):
            Query = t_repas.query.filter_by(nomRepas=request.form["f_dropdown{}".format(i+1)]).all()
            for item in Query:
                liste_ing.append(item.ingredient)


    for ingredient in liste_ing:
        if ingredient not in d_repas:
            d_repas[ingredient] = 1
        else:
            d_repas[ingredient] += 1

    return d_repas

def ingrédientsRequisAleatoire(listeRepas):
    d_repas = {}
    liste_ing = []
    for repas in listeRepas:
            Query = t_repas.query.filter_by(nomRepas=repas).all()
            for item in Query:
                liste_ing.append(item.ingredient)


    for ingredient in liste_ing:
        if ingredient not in d_repas:
            d_repas[ingredient] = 1
        else:
            d_repas[ingredient] += 1

    return d_repas


if __name__ == "__main__":
    app.run()
    session["nbr_ing"] = None
