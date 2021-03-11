# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask import request
#from flask.ext.aiohttp import AioHTTP
from slixmpp import ClientXMPP
import datetime
import json
import couchdb
import pandas as pd

from threading import Lock
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

app = Flask(__name__)
couch = couchdb.Server('http://admin:admin@couchdb:5984/')

#Permet de modifier les templates sans forcement devoir relancer le serveur
app.config['TEMPLATES_AUTO_RELOAD'] = True

socketio = SocketIO(app)
thread = None
thread_lock = Lock()

type_event = ["Embouteillage", "Accident", "Entree de vehicule", "Sortie de vehicule"]
events = pd.DataFrame(columns=['id_e', 'stationId', 'Heading', 'vitesse'])
accidents = []
embouteillages = []

################################################################################
##Exemple pour SocketIO##
@socketio.event
def my_broadcast_event(message):
    emit('my_response',
         {'data': message['data']},
         broadcast=True)

@socketio.event
def connect():
    emit('my_response', {'data': 'Connected'})
    envoi_event()

#################################################################################
def envoi_event(broad=True):
    global events
   
    if(len(events) > 0):
        created_time = datetime.datetime.now() - datetime.timedelta(minutes=5)
        events = events[(events['dt'] > created_time) & (events['dt'] < datetime.datetime.now())]

    #Si tableau contenant les derniers evenement est modifier, on le revoie à tous le monde
    socketio.emit('event', {'data': json.dumps(events.to_json(orient="records"))}, broadcast=broad)
#####################################################
#Page principal
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

#Page d'historique des incidents
@app.route('/history')
def history():
    global type_event
    db = couch["vehicules"]
    data = []
    for docid in db.view('_all_docs', include_docs=True):
        docid["doc"]["type"] = type_event[docid["doc"]["id_e"] -1 ]
        data.append(docid["doc"])

    #On récupère les accidents
    db = couch["accidents"]
    doc = db.get("zone1")
    if(doc is not None):
        doc["type"] = type_event[doc["id_e"] -1 ]
        data.append(doc) 

    #On récupère les embouteillages
    db = couch["embouteillages"]
    doc = db.get("zone1")
    if(doc is not None):
        doc["type"] = type_event[doc["id_e"] -1 ]
        data.append(doc)

        
    return render_template('history.html', data=data)

@app.route('/get_event', methods=['POST'])
def get_event():
    global events

    if(request.method == 'POST'):
        #Renvoie tout les events
        print(request.json)
        new_json = json.loads(request.json)
        new_datetime = datetime.datetime.now()
        new_json["dt"] = new_datetime
        new_json["type"] = type_event[new_json["id_e"] - 1]
        
        #On traite ça différemment si c'est un embouteillage
        if(new_json["id_e"] == 2 or new_json["id_e"] == 1):
            #L'évènement est toujours dans le dataframe, on l'actualise
            if(len(events[events["id_e"] == new_json["id_e"]]) > 0):
                events[events["id_e"] == new_json["id_e"]] = pd.json_normalize(new_json)                
            else:
                #Sinon, on le rajoute
                events = events.append(pd.json_normalize(new_json))

        else:
            events = events.append(pd.json_normalize(new_json))


        envoi_event()


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=3678)