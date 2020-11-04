#Application pour générer la liste d'épicerie à partir d'un menu repas V2.0
#Possibilité d'ajouter du code python intégré aux pages HTML
#Garder toutes les entrées dans la db en minuscule (.lower())

#pour modifier une entrée:
#entry = users.query.filter_by(name=user).first()
#entry.colonne = "string"

#pour inclure une image:
#<image src="{{url_for('static', filename='images/image.png')}}">

#pour du custom css:
#dans <head> --> <link rel="stylesheet" type="text/css" href="{{url_for('static', filename='styles/style.css')}}" >

#exemple LED pour GPIO
#------------------------
#import RPi.GPIO as GPIO
#import time
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#GPIO.setup(18,GPIO.OUT)
#print "LED on"
#GPIO.output(18,GPIO.HIGH)
#time.sleep(1)
#print "LED off"
#GPIO.output(18,GPIO.LOW)


#Librairies pour DB, affichage de pages HTML, etc
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import random

#Librairies pour OCR
from PIL import Image
import pytesseract
from wand.image import Image as Img
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

#librairies pour les GPIOs
import RPi.GPIO as GPIO
import time


app = Flask(__name__)
app.secret_key = "!&%@sdsdsahywybfkb15446456565566svdfjhsfgjjdjeugfbcotsc#!(@%$@(!?(!diihbc*@?$!@(&" #utilisé par flask pour se connecter à la DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/pi/db/flaskDB' # Si la DB n'existe pas, la créer manuellement avec sqlite3 dans la console linux à l'endroit désiré
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #Désactive un warning gossant

# SECTION BASE DE DONNÉES
db = SQLAlchemy(app)

 
# class users(db.Model): #modèle de table dans la db
    # _id = db.Column("id", db.Integer, primary_key=True)
    # name = db.Column(db.String(100))
    # email = db.Column(db.String(100))
    
    # def __init__(self, name, email):
        # self.name = name
        # self.email = email
        
class t_repas(db.Model): #table incluant les repas disponibles
     _id = db.Column("id", db.Integer, primary_key=True)
     nomRepas = db.Column(db.String(100))
     ingredient = db.Column(db.String(100))
     
     def __init__(self, nomRepas, ingredient):
         self.nomRepas = nomRepas
         self.ingredient = ingredient

db.create_all() #Placer cette méthode juste après les classes
db.session.commit() #Sauvegarder les changements

    
# SECTION NAVIGATION ET QUERIES

@app.route("/") #racine de l'application, menu principal
def index():
    session["nbr_ing"] = None # Variable de session permettant de savoir quel formulaire à afficher pour l'ajout de repas
    #flash("test flash") --> peut flasher n'importequoi sur la page template (string, int, bool, liste, dictionnaire)
    #flash() permet d'envoyer une variable sur la prochaine page html en passant par render_template
    return render_template("index.html")
    
@app.route("/ajoutRepas", methods=["POST", "GET"]) # formulaire + fonction pour ajouter des nouvelles entrées dans la DB
def ajoutRepas():
    if request.method == "POST": #refresh du nombre d'ingrédients à mettre avec la variable de session
        if request.form["f_nbrIngredient"] == "": # on s'assure qu'elle n'est pas vide
            flash("Veuillez entrer une valeur dans la case")
            return render_template("ajoutRepas.html")
        f_nombreIngredient = int(request.form["f_nbrIngredient"]) #va chercher la valeur dans le formulaire
        session["nbr_ing"] = f_nombreIngredient
    return render_template("ajoutRepas.html")
    
    
    

@app.route("/ajoutRepas_query", methods=["POST","GET"]) # traitement backend pour l'ajout d'un nouveau repas dans la liste
def ajoutRepas_query():
    if request.method == "POST":
        if request.form["f_repas"] == "": #vérification cases vides
            flash("Ne pas laisser de case vide svp")
            return render_template("ajoutRepas.html")
            
        for i in range(session["nbr_ing"]):
            texte = "f_ingredient{}".format(i+1)
            if request.form[texte] == "":
                flash("Ne pas laisser de case vide svp")
                return render_template("ajoutRepas.html")
            
        repas = request.form["f_repas"].lower() #section d'ajout dans la DB , tous les str en minuscule
        for i in range(session["nbr_ing"]):
            texte = "f_ingredient{}".format(i+1)
            ingredient = request.form[texte].lower()
            entry = t_repas(repas,ingredient) #Création d'une ligne pour la table t_repas
            db.session.add(entry) #insertion de la ligne dans la table
            db.session.commit()
        flash("le repas a été ajouté à la liste!")
        session["nbr_ing"] = None
    return render_template("index.html")
    
    
    
@app.route("/enleverRepas", methods=["POST", "GET"]) # passe par HTML avant d'aller dans enleverRepas_query
def enleverRepas():
    if request.method == "POST":
        flash("methode post utilisée")
    values=t_repas.query.all()
    repas = []
    for i in values:
        repas.append(i.nomRepas)
        repas = sorted(list(dict.fromkeys(repas))) #enlève les duplicates dans la liste
    return render_template("enleverRepas.html", listeRepas=repas)
    
    
@app.route("/enleverRepas_query", methods=["POST","GET"])
def enleverRepas_query():
    if request.method == "POST":
        repas_a_enlever = request.form["f_dropdown"]
        #flash(repas_a_enlever)
        delete_entries = t_repas.query.filter_by(nomRepas=repas_a_enlever).all() #on va chercher toutes les lignes en lien avec le repas à supprimer
        for i in delete_entries:#on les supprime une par une
            db.session.delete(i)
            db.session.commit()
            
        flash("le repas a été supprimé de la liste")
    return render_template("index.html")    

    
@app.route("/modifRepas", methods=["POST", "GET"]) # À faire éventuellement, ou pas selon les besoins
def modifRepas():
    if request.method == "POST":
        flash("méthode post activée")
    values=t_repas.query.all() # on va chercher les repas disponibles
    repas = []
    for i in values:
        repas.append(i.nomRepas)
        repas = list(dict.fromkeys(repas)) #enlève les duplicates dans la liste
    return render_template("modifRepas.html", listeRepas=repas)
    
    
    
@app.route("/printListe", methods=["POST", "GET"]) # Page pour la sélection des repas de la semaine. Va vers /confirmation
def printListe():
    if request.method == "POST":
        flash("méthode post activée")
    values=t_repas.query.all() # on va chercher les repas disponibles
    repas = []
    for i in values:
        repas.append(i.nomRepas)
        repas = sorted(list(dict.fromkeys(repas))) #enlève les duplicates dans la liste
   
    return render_template("printListe.html", listeRepas=repas)
    
    
    
@app.route("/confirmation", methods=["POST","GET"])
def confirmation():
    if request.method == "POST":
        if request.form.get("checkbox") == "on": # la checkbox retourne on quand on appuie dessus
            Repas = repasAleatoire() # Query aléatoire dans les repas disponibles
            d_repas = ingrédientsRequisAleatoire(Repas) # remplissage du dictionnaire avec repas aléatoires
            
            joursSemaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            
            for i in range(7):
                Repas[i] = Repas[i] + " pour {}".format(joursSemaine[i])
            
            
            return render_template("confirmation.html", dico_ingredient=d_repas, listeRepas=Repas) # Envoi vers la page de résumé, liste aléatoire
            
        
        repasLundi = request.form["f_dropdown1"]+" pour Lundi" #trop lâche pour faire une for loop
        repasMardi = request.form["f_dropdown2"]+" pour Mardi"
        repasMercredi = request.form["f_dropdown3"]+" pour Mercredi"
        repasJeudi = request.form["f_dropdown4"]+" pour Jeudi"
        repasVendredi = request.form["f_dropdown5"]+" pour Vendredi"
        repasSamedi = request.form["f_dropdown6"]+" pour Samedi"
        repasDimanche = request.form["f_dropdown7"]+" pour Dimanche"
        
        Repas = [repasLundi,repasMardi,repasMercredi,repasJeudi,repasVendredi,repasSamedi,repasDimanche] # Liste avec les choix de l'utilisateur
        d_repas = ingrédientsRequis() #remplissage du dictionnaire d'ingrédients selon les repas sélectionnés
        
        return render_template("confirmation.html", dico_ingredient=d_repas, listeRepas=Repas) # Envoi vers la page de résumé
    else:
        return render_template("index.html") # Si on tente d'y accéder par l'URL, retourne à l'index


@app.route("/table")
@app.route("/viewtable")
def viewtable():    # page pour faire afficher la table actuelle t_repas
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
        repas = sorted(list(dict.fromkeys(repas))) #enlève les duplicates dans la liste
    return render_template("listeRabais.html", listeRepas=repas)

@app.route("/listeCirculaire", methods=["POST", "GET"]) 
def printCirculaire():
    if request.method == "POST":

        input_dropdown = []
        listeRepas=[]
        iterations = int(request.form["nbrIngredients"])
        for i in range(iterations): # on va chercher les ingrédients du formulaire dynamique
            ingredient = request.form["f_dropdown{}".format(i+1)]
            input_dropdown.append(ingredient)

        # Les ingrédients en rabais arrivent dans la liste input_dropdown
        selection_repas = {}
        repas_confirmation = {}
        
        for i in range(iterations):
             # Pour chaque ingrédient, on va chercher les repas concernés
            Query = t_repas.query.filter_by(ingredient=input_dropdown[i]).all()
            for item in Query:
                if item.nomRepas not in selection_repas:
                    selection_repas[item.nomRepas] = 1
                else:
                    selection_repas[item.nomRepas] += 1

        if len(selection_repas) >= 7: #Si le dictionnaire a 7 repas ou plus, on a assez de repas pour la semaine
            for i in range(7):
                repasRabais = max(selection_repas,key=selection_repas.get) #on va chercher le repas avec le plus d'ingrédients en rabais
                listeRepas.append(repasRabais) # on l'ajoute à la liste de repas de la semaine
                selection_repas.pop(repasRabais) # on enlève le repas des choix et on recommence 6 fois

            random.shuffle(listeRepas) # on mélange le vecteur
            d_repas = ingrédientsRequisAleatoire(listeRepas) # remplit le dictionnaire d'ingrédients
            return render_template("confirmation.html", dico_ingredient=d_repas, listeRepas=listeRepas)

        else:
            listeRepas = []
            nombreRepasManquants = 7 - len(selection_repas)  #Sinon on doit aller chercher d'autres repas dans la DB

            for i in range(len(selection_repas)):
                repasRabais = max(selection_repas, key=selection_repas.get)
                listeRepas.append(repasRabais)
                selection_repas.pop(repasRabais)

            values=t_repas.query.all()
            repasDispos = []
            listeRepasChoisis = []
    
            for i in values:
                repasDispos.append(i.nomRepas)
                repasDispos = list(dict.fromkeys(repasDispos)) #enlève les duplicates dans la liste et on a les repas disponibles
    
            for i in range(nombreRepasManquants): 
                randomIndex = random.randint(0, len(repasDispos) - 1)
                listeRepasChoisis.append(repasDispos[randomIndex])
                repasDispos.pop(randomIndex)

            listefinale = listeRepas + listeRepasChoisis
            d_repas = ingrédientsRequisAleatoire(listefinale)

            repasLundi = listefinale[0]+" pour Lundi" #trop lâche pour faire une for loop
            repasMardi = listefinale[1]+" pour Mardi"
            repasMercredi = listefinale[2]+" pour Mercredi"
            repasJeudi = listefinale[3]+" pour Jeudi"
            repasVendredi = listefinale[4]+" pour Vendredi"
            repasSamedi = listefinale[5]+" pour Samedi"
            repasDimanche = listefinale[6]+" pour Dimanche"

            listefinale = [repasLundi, repasMardi, repasMercredi, repasJeudi, repasVendredi, repasSamedi, repasDimanche]

            return render_template("confirmation.html", dico_ingredient=d_repas, listeRepas=listefinale)

   

    #---------------------------------------------------------------
    # Algo de tri pour la liste à partir d'ingrédients du circulaire
    #---------------------------------------------------------------

    # si le dictionnaire a 7 éléments ou plus, 
    # repasRabais = max(dico,key=dico.get) va chercher le repas avec le plus de repas en rabais
    # liste.append(repasRabais) on l'ajoute à la liste de sélection
    # dico.pop("repasRabais") on enlève le repas du dictionnaire
    # refaire les étapes 7 fois pour avoir une liste de 7 éléments
    # shuffle la liste avant de la retourner
    # call la fonction pour les ingrédients requis
    # render_template --> affichage liste en html


    # si le dictionnaire a moins de 7 éléments 
    # compter le nombre de repas aléatoire à aller chercher dans la db x = 7 - len(dico)
    # repasRabais = max(dico, key=dico.get)
    # liste.append(repasRabais)
    # dico.pop(repasRabais)
    # on va chercher le nombre de repas qu'il faut pour remplir notre liste à 7 repas
    # shuffle la liste
    # call fonction pour les ingrédients requis
    # render_template --> affichage liste en html


        
    else:
        return render_template("index.html")

@app.route("/LED") # Controle des entrées sorties par interface web
def allumeLED():

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False) #fuk les warnings
    GPIO.setup(18,GPIO.OUT) # Set pin 18 as output 
    GPIO.output(18,GPIO.HIGH)
    time.sleep(5) #allume 5 secondes puis éteint
    GPIO.output(18,GPIO.LOW)

    return render_template("index.html") 



@app.route("/OCR") # Reconaissance de caractères dans des pdf 
def ocr():
    # À venir
    return render_template("index.html")


@app.route("/discord") # Reconaissance de caractères dans des pdf 
def discord():
    # Test widjet discord server
    return render_template("discord.html")



def repasAleatoire(): # retourne une liste avec 7 repas aléatoires provenant de la base de donnée
    values=t_repas.query.all()
    repasDispos = []
    listeRepasChoisis = []
    
    for i in values:
        repasDispos.append(i.nomRepas)
        repasDispos = list(dict.fromkeys(repasDispos)) #enlève les duplicates dans la liste et on a les repas disponibles
    
    for i in range(7): #on remplit la liste de 7 repas
        randomIndex = random.randint(0, len(repasDispos) - 1)
        listeRepasChoisis.append(repasDispos[randomIndex])
        repasDispos.pop(randomIndex) #on enlève le repas pour éviter d'avoir 2 fois le même repas dans la semaine
    
        
    return listeRepasChoisis
    
def ingrédientsRequis(): # retourne un dictionnaire avec les ingrédients requis pour chaque plat (repas sélectionnés manuellement)
    d_repas = {}
    liste_ing = []
    for i in range(7): #Génération de la liste des ingrédients (avec répétitions)
            Query = t_repas.query.filter_by(nomRepas=request.form["f_dropdown{}".format(i+1)]).all()
            for item in Query:
                liste_ing.append(item.ingredient)
            
        
    for ingredient in liste_ing: # on compte le nombre d'occurence pour chaque ingrédient
        if ingredient not in d_repas:
            d_repas[ingredient] = 1
        else:
            d_repas[ingredient] += 1 
    
    return d_repas
    
def ingrédientsRequisAleatoire(listeRepas): # retourne un dictionnaire avec les ingrédients requis pour chaque plat (repas aléatoire)
    d_repas = {}
    liste_ing = []
    for repas in listeRepas: #Génération de la liste des ingrédients selon les repas aléatoires
            Query = t_repas.query.filter_by(nomRepas=repas).all()
            for item in Query:
                liste_ing.append(item.ingredient)
            
        
    for ingredient in liste_ing: # on compte le nombre d'occurence pour chaque ingrédient
        if ingredient not in d_repas:
            d_repas[ingredient] = 1
        else:
            d_repas[ingredient] += 1 
    
    return d_repas

    
if __name__ == "__main__":
    app.run()
    session["nbr_ing"] = None
    
