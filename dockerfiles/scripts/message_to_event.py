import paho.mqtt.client as mqtt
import json
import pandas as pd
import sys
from slixmpp import ClientXMPP
from envoi_xmpp import Client

'''
Coordonnées des carrés :
- zone : (Sortie : 49.023207, 3.049192, Entrée :49.024037, 3.095388)
evenements :
id :
    1 : embouteillage
    2 : accident
    3 : entree
    4 : sortie
'''

df_cam = pd.DataFrame(columns=['stationId', 'stationType', 'vitesse', 'Heading', 'x', 'y'])
df_denm = pd.DataFrame(columns=['stationId', 'stationType', 'cause', 'subcause', 'x', 'y'])


def xmpp_send(user, json):
    #Arguments : utilisateur et le mdp
    xmpp = Client("pass@iot.com", "test", user, json)
    xmpp.connect(address=("openfire", 5222))
    xmpp.process(forever=False)

def check_events():
    global df_cam,df_denm

    print(df_denm.head(10))
    #Accident si 2 véhicules
    temp = df_denm[df_denm["cause"] == 4]
    if(len(temp["stationId"].unique()) >= 2):
        json_event = {"id_e" : 2}
        xmpp_send("serv@openfire", json.dumps(json_event))
        xmpp_send("bdd@openfire", json.dumps(json_event))

    #Embouteillage si 3 véhicules < 90
    if(len(df_cam[df_cam["vitesse"] < 90]) >= 3):
        json_event = {"id_e" : 1}
        xmpp_send("serv@openfire", json.dumps(json_event))
        xmpp_send("bdd@openfire", json.dumps(json_event))

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("topic/CAM")
    client.subscribe("topic/DENM")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global df_cam,df_denm

    print("Message reçu sur le topic :"+msg.topic+" :\n "+ msg.payload.decode("utf8"))
    json_msg = json.loads(msg.payload.decode("utf8"))

    if(msg.topic == "topic/CAM"):
        #On regarde si le véhicule est déjà dans le dataframe

        #Il l'est
        if(len(df_cam[df_cam["stationId"] == json_msg["stationId"]]) > 0):
            df_cam[df_cam["stationId"] == json_msg["stationId"]] = pd.json_normalize(json_msg)

            #On regarde s'il est sorti
            #On regarde s'il vient de la droite ou de la gauche
            if(json_msg["Heading"] > 200):
                if(json_msg["y"] < 3.049192):
                    print("Sortie de véhicule ! vers l'ouest")
                    #Envoi DENM de sortie
                    json_event = {"id_e" : 4, "stationId" : json_msg["stationId"], "Heading" : json_msg["Heading"], "vitesse" : json_msg["vitesse"]}
                    xmpp_send("serv@openfire", json.dumps(json_event))
                    xmpp_send("bdd@openfire", json.dumps(json_event))

                    #On drop la ligne pandas du véhicule
                    df_cam = df_cam[df_cam["stationId"] != json_msg["stationId"]]
                    df_denm = df_denm[df_denm["stationId"] != json_msg["stationId"]]
                    
            else:
                if(json_msg["y"] > 3.095388):
                    print("Sortie de véhicule ! vers l'est")
                    #Envoi DENM de sortie
                    json_event = {"id_e" : 4, "stationId" : json_msg["stationId"], "Heading" : json_msg["Heading"], "vitesse" : json_msg["vitesse"]}
                    xmpp_send("serv@openfire", json.dumps(json_event))
                    xmpp_send("bdd@openfire", json.dumps(json_event))

                    #On drop la ligne pandas du véhicule
                    df_cam = df_cam[df_cam["stationId"] != json_msg["stationId"]]
                    df_denm = df_denm[df_denm["stationId"] != json_msg["stationId"]]

        #Le véhicule n'est pas dans le dataframe : on l'ajoute
        else:
            df_cam = df_cam.append(pd.json_normalize(json_msg))
            #On envoie un message parce qu'il est entré
            json_event = {"id_e" : 3, "stationId" : json_msg["stationId"], "Heading" : json_msg["Heading"], "vitesse" : json_msg["vitesse"]}
            xmpp_send("serv@openfire", json.dumps(json_event))
            xmpp_send("bdd@openfire", json.dumps(json_event))

    else:
        df_denm = df_denm.append(pd.json_normalize(json_msg))

    check_events()

if __name__ == '__main__':

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("mosquitto")
    client.loop_forever()