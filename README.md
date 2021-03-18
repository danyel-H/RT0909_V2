# Mode d'emploi du projet de RT0909

## Auteurs

Ce projet à été développé par :
- DE SOUSA Luciano / luciano.de-sousa@etudiant.univ-reims.fr
- HOQUIGNY Danyel / danyel.hocquigny@etudiant.univ-reims.fr

## Description du projet

Ceci est une application de tracking sportif, chaque utilisateur dispose d'un terminal qui lui permet, lorsque il commence une activité, de sélectionner ce qu'il veut faire et envoyer au serveur son parcours. 
L'utilsateur pourra ensuite allez voir ses performances sur le site web.
Un système d'administration est aussi présent, attention aux petits malins.

## Prérequis

Vous devez avoir installé Docker ainsi que Docker-Compose

Et devez disposer de :
- Un ordinateur
- Un navigateur graphique
- Un terminal pour lancer les dockers
- Le port 3678 disponible et accessible depuis le navigateur
- Une connexion à Internet depuis la machine où le projet est éxécuté

Si jamais il n'était pas possible de libérer le port 3678, rendez vous dans le docker-compose.yml et cherchez les lignes "- port" dans le service nommé "web", remplacez la ligne "3678:80" par "portvoulu:80"

## Lancement de l'application

Après avoir installé docker et docker-compose, rendez vous dans le fichier "dockerfiles" et lancez le script "build-dockerfiles.sh", celui-ci va build toutes les images docker nécessaires à l'exécution du projet. Une fois vous être assuré que tout s'est bien executé, revenez dans le dossier "docker" et lancez un simple

> docker-compose up

L'application devrait alors se préparer puis se lancer, rendez vous ensuite sur le port 3678 de la machine qui a lancé le docker-compose, un site Web devrait apparaitre, vous pourrez y observer les véhicules rentrer, sortir, et se rentrer dedans, provoquant ainsi de lourds dégâts et quelques embouteillages

