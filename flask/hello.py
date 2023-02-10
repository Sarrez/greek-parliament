from pymongo import MongoClient
from flask import Blueprint
from flask_paginate import Pagination, get_page_parameter, request
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from forms import SearchForm
#CONFIGURE FLASK APP
app = Flask(__name__, template_folder='./frontend/templates',static_folder='./frontend/static')
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
#FLASK BOOTSTRAP
Bootstrap(app)
mod = Blueprint('speeches', __name__)

####################CONNECT TO MONGO####################
mongo_client = MongoClient("mongodb://localhost:27017/")
client = mongo_client["GreekParliamentProceedings"]
index = client["InvertedIndex"]
database = client["Database"]
####################CONNECT TO MONGO####################

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    response = ""
    if form.validate_on_submit():
      query = form.query.data
      form.query.data = ""
      return redirect(url_for('show_speeches', query = query))
   
    return render_template('index.html', form=form)
 
@app.route('/speeches/<string:query>)', methods=('GET', 'POST'))
def show_speeches(query):
   search = False
   q = request.args.get('q')
   if q:
      search = True
   results = list(database.find({ })[:int(query)])
   ###########DEFINE PAGINATION###########
   page = request.args.get(get_page_parameter(), type=int, default=1)
   pagination = Pagination(page=page, total=len(results), search=search, record_name='speeches')
   return render_template('speeches.html', speeches=results, page=page, pagination=pagination)

if __name__ == '__main__':
   app.run(debug = True)