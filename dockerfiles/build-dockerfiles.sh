docker build -f Dockerfile.openfire -t xmpp/iot .
docker build -f Dockerfile.serveurweb -t flask/iot .
docker build -f Dockerfile.simulation -t vehicules/iot .
docker build -f Dockerfile.xmppbdd -t xmppbdd/iot .
docker build -f Dockerfile.xmppweb -t xmppweb/iot .
docker build -f Dockerfile.convertisseur -t convertisseur/iot .