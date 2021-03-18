'''
Coordonnées des carrés :
- zone : (Sortie : 49.023207, 3.049192, Entrée :49.024037, 3.095388)
Entrée : DENM cause 8
Sortie : DENM cause 9
'''
import random
import time
import paho.mqtt.client as mqtt
import asyncio
import json

class Vehicle:
    def __init__(self):
        self.id = random.randint(1, 999999)

        #Choisi un type de voiture aléatoire
        rand_type = random.randint(0, 100)
        if(rand_type < 5):
            self.Type = 10
        elif(rand_type < 15):
            self.Type = 15
        else:
            self.Type = 5

        self.Vitesse = random.randint(90, 110)
        
        #On choisi si la voiture arrive de l'entrée où de la sortie
        #True : Entrée
        #False : Sortie
        if(random.randint(0, 100) < 50):
            self.depart = True
            self.Heading = 270
        else:
            self.depart = False
            self.Heading = 90

        if(self.depart):
            self.Pos_gps = [49.024037, 3.095388]
        else:
            self.Pos_gps = [49.023207, 3.049192]

    def update_pos_sec(self, mov=10):
        #Le vehicule avancera plus ou moins vite en fonction de ça vitesse
        for i in range(0, mov):
            if(self.Vitesse < 90):
                varia = 0
            elif(self.Vitesse < 100):
                varia = 0.000001
            elif(self.Vitesse < 110):
                varia = 0.000002
            elif(self.Vitesse < 120):
                varia = 0.000004
            else:
                varia = 0.000005
            
            if(self.depart):
                #self.Pos_gps[0] -= 0.000001
                self.Pos_gps[1] -= 0.00004+varia
            else:
                #self.Pos_gps[0] += 0.000001
                self.Pos_gps[1] += 0.00004+varia

    #Fonction faisant évoluer la voiture
    def update(self):
        #Update vehicule (position + vitesse + Heading)
        if(self.Vitesse <= 90):
           self.update_pos_sec(10)
        else:
           self.update_pos_sec()

        #Vitesse de la voiture, on considère qu'ils ne peuvent pas être plus lent que 70 et plus rapide que 130
        if(random.randint(0,100) < 40):
            if(self.Vitesse >= 70 and self.Vitesse <= 130):
                self.Vitesse = self.Vitesse + random.randint(-5, 5)
            elif(self.Vitesse <= 70):
                self.Vitesse = self.Vitesse + random.randint(1, 5)
            elif(self.Vitesse >= 130):
                self.Vitesse = self.Vitesse + random.randint(-5, -1)


        #DENM
        #Proba que la voiture voit un accident, sinon envois un autre DENM si elle est lente
        rand = random.randint(0, 500)
        if(rand <= 1):
            self.send_DENM(4)
        elif(rand <= 10):
            self.send_DENM(random.choice([3, 5, 6, 7]))

        #CAM
        self.send_CAM()

        #Retourne le temps qu'il y aura avant la prochaine update
        if(self.Vitesse < 90):
            return 1.00
        else:
            return 0.10

    def json(self):
        return {"stationId": self.id, "stationType": self.Type, "vitesse": self.Vitesse, "Heading": self.Heading, "x": self.Pos_gps[0], "y": self.Pos_gps[1]}

    def send_CAM(self):
        client = mqtt.Client()
        client.connect("mosquitto")
        client.publish("topic/CAM", json.dumps(self.json()))
        client.disconnect()
    
    def send_DENM(self, cause, subcause=0):
        json_denm = {"stationId": self.id, "stationType": self.Type, "cause": cause, "subcause": subcause, "x": self.Pos_gps[0], "y": self.Pos_gps[1]}
       
        client = mqtt.Client()
        client.connect("mosquitto")
        client.publish("topic/DENM", json.dumps(json_denm))
        client.disconnect()

    def sortie(self):
        if(self.depart):
            if(self.Pos_gps[1] < 3.049192):
                return True
            else:
                return False
        else:
            if(self.Pos_gps[1] > 3.095388):
                return True
            else:
                return False

async def actionVehicle(v):
    while(True):
        rate = v.update()
        if(not v.sortie()):
            await asyncio.sleep(rate)
        else:
            print("Un vehicule sort")
            break
    
async def runVehicles(number=0):
    #Si aucun nombre n'est indiqué, on tourne à l'infini
    print("Attente avant lancement des vehicules")
    await asyncio.sleep(60)
    print("Début lancement véhicule")
    if(number > 0):
        for i in range(0, number):
            print("Ajout d'un Vehicule")
            v = Vehicle()
            asyncio.ensure_future(actionVehicle(v))
            await asyncio.sleep(random.randint(1, 10))
    else:
        while True:
            print("Ajout d'un Vehicule")
            v = Vehicle()
            asyncio.ensure_future(actionVehicle(v))
            await asyncio.sleep(random.randint(1, 50))
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(runVehicles())
    loop.run_forever()