from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
app = Flask(__name__, template_folder='./frontend/templates',static_folder='./frontend/static')
mongo_client = MongoClient("mongodb://localhost:27017/")
#mongo_client.drop_database("GreekParliamentProceedings")
client = mongo_client["GreekParliamentProceedings"]
index = client["InvertedIndex"]
database = client["Database"]
import json
import requests

@app.route('/', methods=['POST', 'GET'])
def home():
   if request.method=='POST':
      print("Got request")
      id = request.form.get('query')
      print(id)
      speeches = list(database.find({"_id":str(id)}, { "_id": 0, "speech": 1 }))
      return render_template('speeches.html', speeches = speeches)

   return render_template('index.html')

@app.route('/hello', methods=('GET', 'POST'))
def show_speeches():
   return render_template('speeches.html')

if __name__ == '__main__':
   app.run(debug = True)