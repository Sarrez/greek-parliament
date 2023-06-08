from pymongo import MongoClient
from flask import Blueprint
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from forms import SearchForm
from speech_queries import main_
#CONFIGURE FLASK APP
app = Flask(__name__, template_folder='./frontend/templates',static_folder='./frontend/static')
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
app.config['TEMPLATES_AUTO_RELOAD'] = True
#FLASK BOOTSTRAP
Bootstrap(app)
mod = Blueprint('speeches', __name__)

####################CONNECT TO MONGO####################
mongo_client = MongoClient(""mongodb+srv://sarrez:sarrez@cluster0.dqcywqp.mongodb.net/?retryWrites=true&w=majority"")
client = mongo_client["GreekParliamentProceedings"]
index = client["InvertedIndex"]
database = client["Database"]
####################CONNECT TO MONGO####################

#@app.route('/', methods=['GET', 'POST'])
#def index():
#    form = SearchForm()
#    response = ""
#    if form.validate_on_submit():
#      query = form.query.data
#      form.query.data = ""
#      return redirect(url_for('show_speeches', query = query))
   
#    return render_template('index.html', form=form)
  
@app.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    response = ""
    if form.validate_on_submit():
      query = form.query.data
      form.query.data = ""
      return redirect(url_for('show_speeches', query = query))
   
    return render_template('search.html', form=form)
  
@app.route('/speeches/<string:query>)', methods=('GET', 'POST'))
def show_speeches(query):
   topk = main_(query)
   results = [list(database.find({'_id':id_})) for id_ in topk]

   return render_template('speeches.html', speeches=results)

@app.route('/render_speech/<string:id>)', methods=('GET', 'POST'))
def render_speech(id):
  results = list(database.find({"_id":id}))
  return render_template('render_speech.html', data=results)
 
if __name__ == '__main__':
   app.run(host="0.0.0.0", debug = True)
