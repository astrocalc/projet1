from flask import Flask, render_template
from forms import CoordsForm
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from functions import generateData
import os

csrf = CSRFProtect()

app = Flask(__name__)
csrf.init_app(app)
bootstrap = Bootstrap(app)

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

@app.route('/', methods = ['GET','POST'])
def index():

    mypath = "static/temp" #Enter your path here
    for root, dirs, files in os.walk(mypath):
        for file in files:
            os.remove(os.path.join(root, file))

    jour_naissance = None
    mois_naissance = None
    annee_naissance = None
    heure_naissance = None
    min_naissance = None
    latitude = None
    longitude = None
    form = CoordsForm()

    if form.validate_on_submit():
        jour_naissance = form.jour_naissance.data
        mois_naissance = form.mois_naissance.data
        annee_naissance = form.annee_naissance.data
        heure_naissance = form.heure_naissance.data
        min_naissance = form.min_naissance.data
        latitude = form.latitude.data
        longitude = form.longitude.data

        processedData = generateData(jour_naissance,mois_naissance,annee_naissance,heure_naissance,min_naissance,latitude,longitude)

        return render_template('dashboard.html', data = processedData)

    
    return render_template('index.html', form=form)




if __name__ == "__main__":
    app.run(debug=True)