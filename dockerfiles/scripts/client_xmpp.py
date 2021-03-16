import logging
import sys
from slixmpp import ClientXMPP
import requests
import json
import couchdb
import datetime
import pytz
from pytz import timezone

couch = None

class Client(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            obj = msg['body']
            print("###############################################################")
            json_obj = json.loads(obj)
            print(json_obj["id_e"])


            if(json_obj["id_e"] <= 2):
                if(json_obj["id_e"] == 1):
                    db = couch["embouteillages"]
                else:
                    db = couch["accidents"]

                doc = db.get("zone1")
                if(doc == None):
                    doc = json_obj
                    doc["_id"] = "zone1" 
                else:
                    doc["id_e"] = json_obj["id_e"]

            else:
                db = couch["vehicules"]
                doc = json_obj

            zone = timezone("Europe/Paris")

            dt = datetime.datetime.now(zone)
            dt = dt.strftime("%d-%m-%Y à %H:%M:%S")
            doc["dt"] = dt
            try:
                db.save(doc)
            except:
                print("Erreur de co à la BDD")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    while couch == None:
        try:
            couch = couchdb.Server('http://admin:admin@couchdb:5984/')
        except:
            print("Echec de la connexion à la BDD, reessai")

    if 'vehicules' not in couch:
        couch.create('vehicules')
    if 'embouteillages' not in couch:
        couch.create('embouteillages')
    if 'accidents' not in couch:
        couch.create('accidents')

    xmpp = Client("bdd@iot.com", "test")
    xmpp.connect(address=("openfire", 5222))
    xmpp.process()