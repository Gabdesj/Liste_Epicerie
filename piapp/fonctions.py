#Fichier avec les fonctions utilitaires et exemples de code





#@app.route("/login", methods=["POST", "GET"])
# def login():
    # if request.method == "POST":
        # user = request.form["nm"]
        # session["user"] = user
        
        # found_user = users.query.filter_by(name=user).first()
        
        # if found_user:
            # session["email"] = found_user.email
            # flash("utilisateur existe déjà dans la db")
        # else:
            # usr = users(user, "")
            # db.session.add(usr)
            # db.session.commit()
            # flash("utilisateur ajouté dans db")
        
        
       
        # return redirect(url_for("user"))
    # else: 
        # if "user" in session:
            # flash("Vous êtes déjà connecté")
            # return redirect(url_for("user"))
        # return render_template("login.html")
        
# @app.route("/logout")    
# def logout():
    # session.pop("user", None)
    # session.pop("email", None)
    # flash("Vous êtes déconnecté","info")
    # return redirect(url_for("login"))


    
# @app.route("/user", methods=["POST", "GET"])
# def user():
    # if "user" in session:
        # user = session["user"]
        # if request.method == "POST":
            # email = request.form["email"]
            # session["email"] = email
            # found_user = users.query.filter_by(name=user).first() 
            # found_user.email = email
            # db.session.commit()
            # flash("email sauvegardé dans la db")
            # #exemple d'update du email dans la db
        # else:
            # if "email" in session:
                # email = session["email"]
        # return render_template("user.html")
    # else:
        # flash("vous n'êtes pas connecté")
        # return redirect(url_for("login"))
        
    

    
    
    
#@app.route("/<name>") Il est possible de passer un argument d'une page à une autre avec l'URL
#def allo(name):
#    return "Allo {}".format(name) 

#@app.route("/admin")
#def admin():
#    return redirect(url_for("allo", name="Karmaconda!")) 