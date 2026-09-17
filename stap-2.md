# Stap 2 — RabbitMQ en de sensorsimulator koppelen

## Doel en werkwijze

We deployen één gedeelde RabbitMQ-broker. Deelnemers maken ieder een eigen queue en binding en controleren eerst een handmatig bericht. Pas wanneer die route werkt, bouwt de begeleider simulatorversie `2.0` en verbindt deze met RabbitMQ.

De volgorde is belangrijk: de tweede simulatorversie maakt zelf geen exchange aan. `sim_sensor_exchange` moet dus bestaan voordat we versie `2.0` starten.

## 1. Uitgangspunten

Stap 1 is afgerond. De simulator draait nog met image `1.0`. De namespace `backend-workshop` bestaat al en de bestanden uit de pakketmap `stap-2` zijn vooraf in `~/workshop/stap-2` klaargezet.

```bash
cd ~/workshop/stap-2
pwd
ls -l
kubectl config current-context
kubectl -n backend-workshop get deployment
```

| Onderdeel | Waarde in deze workshop |
| --- | --- |
| Namespace | `backend-workshop` |
| RabbitMQ Deployment | `rabbitmq-deployment` |
| RabbitMQ Service | `rabbitmq-service` |
| RabbitMQ-image | `rabbitmq:4.2-management` |
| Management UI | `http://rabbitmq.workshop.example` |
| AMQP-host binnen het cluster | `rabbitmq-service.backend-workshop.svc.cluster.local` |
| AMQP-poort | `5672` |
| Virtual host | `/` |
| Gedeelde exchange | `sim_sensor_exchange` |
| Exchange-type | `direct` |
| Routing key | `sensor.data` |
| Persoonlijke queue | `sensor_queue_<naam>` |
| Simulator Deployment | `sensor-simulator` |
| Simulator-image na de upgrade | `whu1/sensor-simulator:2.0` |

Gebruik een unieke korte naam voor `<naam>`, bijvoorbeeld `sensor_queue_wenjie`. Er zijn geen groepen en geen aparte Kubernetes-namespaces per deelnemer.

## 2. Eenmalige voorbereiding: credentials buiten GitHub

Beide Deployments lezen de credentials uit Secret `rabbitmq-credentials`. De losse Python- en YAML-bestanden in dit pakket gebruiken dezelfde configuratie.

De begeleider doet dit vóór de workshop. Controleer eerst alleen of het Secret bestaat, zonder de inhoud te tonen:

```bash
kubectl -n backend-workshop get secret rabbitmq-credentials
```

Bestaat het juiste Secret al, sla het aanmaken over. Bestaat het nog niet, maak het in een niet-opgenomen Bash-terminal interactief aan:

```bash
read -r -p 'RabbitMQ-gebruikersnaam: ' RMQ_WORKSHOP_USER
read -r -s -p 'RabbitMQ-wachtwoord: ' RMQ_WORKSHOP_PASS
printf '\n'
kubectl -n backend-workshop create secret generic rabbitmq-credentials \
  --from-literal=username="$RMQ_WORKSHOP_USER" \
  --from-literal=password="$RMQ_WORKSHOP_PASS"
unset RMQ_WORKSHOP_USER RMQ_WORKSHOP_PASS
```

Het wachtwoord wordt niet op het scherm of als letterlijke waarde in de shellgeschiedenis gezet, maar wordt tijdens dit commando wel als procesargument doorgegeven. Gebruik daarom een vertrouwde beheeromgeving en geen shell-debugging (`set -x`). Commit geen Secret-export: base64 is geen versleuteling. Kubernetes kan Secret-waarden als omgevingsvariabelen aan containers doorgeven. Zie [Kubernetes: credentials via Secrets](https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/) en [beveiliging van Secrets](https://kubernetes.io/docs/concepts/configuration/secret/).

Gebruik bij een bestaande broker de werkelijke geldige accountgegevens. Een Secret aanpassen is op zichzelf geen wachtwoordwijziging van een bestaand RabbitMQ-account. De default-user-instellingen zijn voor het initialiseren van een nieuwe broker; zie de [RabbitMQ-configuratiedocumentatie](https://www.rabbitmq.com/docs/configure).

## 3. RabbitMQ centraal deployen — begeleider

### `rabbitmq-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbitmq-deployment
  namespace: backend-workshop
  labels:
    app: rabbitmq
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rabbitmq
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      containers:
        - name: rabbitmq
          image: rabbitmq:4.2-management
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5672
              name: amqp
            - containerPort: 15672
              name: http
          env:
            - name: RABBITMQ_DEFAULT_USER
              value: "sas_user"
            - name: RABBITMQ_DEFAULT_PASS
              value: "sas_password123"
```

Dit is een eenvoudige workshopbroker zonder persistent volume en zonder readiness-probe. `Running` is daarom nog geen bewijs dat RabbitMQ klaar is voor clients: controleer ook de Management UI. Bij vervanging van de Pod kunnen queues, bindings en berichten verloren gaan. Ook `Durable` queues en persistente berichten lossen ontbrekende blijvende opslag niet op. Deploy de broker dus vóór de deelnemers hun queues maken; herdeploy hem niet tussendoor.

### `rabbitmq-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq-service
  namespace: backend-workshop
spec:
  type: NodePort
  selector:
    app: rabbitmq
  ports:
    - name: amqp
      port: 5672
      targetPort: 5672
      nodePort: 30673
    - name: http
      port: 15672
      targetPort: 15672
      nodePort: 31673
```

Deze Service neemt de geteste configuratie over, inclusief de bestaande nodepoorten. Die zijn geen workshoponderwerp en worden in de opdrachten niet gebruikt. De simulator gebruikt intern Servicepoort `5672`; de browser gebruikt de Ingress naar `15672`. Beperk toegang tot de bedoelde workshopomgeving: deze configuratie heeft ook poorten op de nodes beschikbaar. Het Service-type en de interne routering worden beschreven in de [Kubernetes-documentatie](https://kubernetes.io/docs/concepts/services-networking/service/).

### `rabbitmq-ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rabbitmq-backend-workshop-ingress
  namespace: backend-workshop
spec:
  ingressClassName: nginx
  rules:
    - host: rabbitmq.workshop.example
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: rabbitmq-service
                port:
                  number: 15672
```

`rabbitmq.workshop.example` is een voorbeeldadres. De begeleider vervangt de host in `rabbitmq-ingress.yaml` vóór het deployen door het afgesproken adres. De Ingress-controller en DNS moeten daarvoor al geregeld zijn. Deze Ingress is voor de HTTP-Management UI, niet voor AMQP. De geteste URL gebruikt HTTP, dus geen versleutelde browserverbinding. Gebruik alleen tijdelijke workshopcredentials in de afgesproken omgeving; regel HTTPS voordat je dit breder inzet.

### Commando's

```bash
kubectl -n backend-workshop apply -f rabbitmq-deployment.yaml
kubectl -n backend-workshop apply -f rabbitmq-service.yaml
kubectl -n backend-workshop apply -f rabbitmq-ingress.yaml
kubectl -n backend-workshop rollout status deployment/rabbitmq-deployment --timeout=120s
kubectl -n backend-workshop get deployment,pods,service,ingress
```

Let op: de Deployment heet `rabbitmq-deployment`, niet `rabbitmq`. Anders geeft `rollout status` een `NotFound`-melding.

In het testdocument staat `kubectl -n backend-workshop apply -f .`. Hier passen we de bestanden afzonderlijk toe, zodat `sensor-simulator-deployment.yaml` met image `2.0` nog niet wordt uitgerold vóór de handmatige RabbitMQ-test.

Open daarna de Management UI via het echte adres dat de begeleider heeft geregeld; `http://rabbitmq.workshop.example` is alleen een voorbeeld. Deelnemers ontvangen de inloggegevens apart. Dit interne adres werkt alleen met de vereiste netwerk- en DNS-toegang.

## 4. RabbitMQ kort introduceren

De producer maakt een bericht en publiceert het naar een exchange. De exchange gebruikt bindings om te bepalen naar welke queues een kopie gaat. De queue bewaart berichten zodat een consumer ze kan ophalen en verwerken.

| Begrip | Rol in deze workshop |
| --- | --- |
| Producer | Eerst de handmatige publicatie in de UI, daarna de sensorsimulator |
| Exchange | `sim_sensor_exchange`: verdeelt de berichten |
| Routing key | `sensor.data`: bepaalt samen met bindings de route |
| Binding | Regel die de exchange met een queue verbindt |
| Queue | Persoonlijke buffer `sensor_queue_<naam>` |
| Consumer | Nu handmatig ophalen via de UI; later bijvoorbeeld een database- of meldingsapp |

We gebruiken een `direct` exchange: de binding key moet exact overeenkomen met de routing key. Meerdere verschillende queues met dezelfde binding ontvangen elk een kopie. Meerdere consumers van één gedeelde queue krijgen niet automatisch allemaal elk bericht. Zie de [RabbitMQ-routingtutorial](https://www.rabbitmq.com/tutorials/tutorial-four-python).

## 5. Eén gedeelde exchange maken — begeleider

Selecteer in de UI virtual host `/`. Ga naar **Exchanges → Add a new exchange** en gebruik:

| Veld | Waarde |
| --- | --- |
| Name | `sim_sensor_exchange` |
| Type | `direct` |
| Durability | `Durable` |
| Auto delete | `No` |
| Internal | `No` |
| Arguments | Leeg |

Klik op **Add exchange**. Bestaat de exchange al, controleer dan de instellingen; verwijder geen gedeelde exchange tijdens de workshop. Deelnemers hoeven geen eigen exchange te maken voor deze basisroute.

## 6. Een persoonlijke queue maken — deelnemers

Ga naar **Queues and Streams → Add a new queue**:

| Veld | Waarde |
| --- | --- |
| Virtual host | `/` |
| Name | `sensor_queue_<naam>` |
| Type | `Classic` |
| Durability | `Durable` |
| Auto delete | `No` |
| Arguments | Leeg |

Maak de queue aan en open de detailpagina. Gebruik een naam die niemand anders gebruikt. Stel voor de basistest nog geen TTL of maximumlengte in; policies komen bij de experimenten.

## 7. Queue binden — deelnemers

Open op de queuepagina **Bindings → Add binding to this queue** en vul in:

| Veld | Waarde |
| --- | --- |
| From exchange | `sim_sensor_exchange` |
| Routing key | `sensor.data` |
| Arguments | Leeg |

Klik op **Bind**. Controleer of de binding zichtbaar is. Let op hoofdletters, punten en spaties.

## 8. Eerst één bericht handmatig testen

Laat één persoon op **Exchanges → sim_sensor_exchange → Publish message** publiceren:

| Veld | Waarde |
| --- | --- |
| Routing key | `sensor.data` |
| Payload | `{"test":"workshop-route"}` |

Klik één keer op **Publish message**. Bij een lege, correct gebonden queue zonder actieve consumer wordt `Ready` daarna `1`; bij een niet-lege queue neemt het aantal met één toe. De UI kan een korte verversingsvertraging hebben.

Iedere deelnemer opent de eigen queue en gebruikt **Get messages** met één bericht. Kies de requeue-optie als je het bericht na het bekijken wilt terugplaatsen. Kies de optie zonder requeue als je het definitief uit de queue wilt halen.

Controleer gezamenlijk:

- iedereen met een correcte binding ziet de testpayload;
- iedere persoonlijke queue heeft haar eigen kopie;
- als één deelnemer zijn bericht verwijdert, blijven de kopieën in andere queues bestaan.

Wie de binding pas ná publicatie maakt, ontvangt dat eerdere bericht niet alsnog. Publiceer dan een nieuw testbericht. Als iedereen zelf een bericht publiceert, ontvangt iedere gebonden queue ook die berichten; spreek daarom af wie de eerste test uitvoert.

**Checkpoint vóór de upgrade:** alle deelnemers hebben een werkende queue en binding. Ga pas daarna verder met simulator `2.0`.

## 9. Simulatorversie 2.0 voorbereiden — begeleider

Gebruik `app.py` in `~/workshop/stap-2`. Laat de versie in `stap-1` ongewijzigd, zodat de eerste demo apart herhaalbaar blijft. `Dockerfile` en `requirements.txt` blijven hetzelfde als in stap 1, inclusief `pika`.

Deze versie behoudt `/sensor` en voegt een achtergrondthread toe die ongeveer iedere seconde de nieuwste meting publiceert. De exchange wordt niet door Python aangemaakt.

### `app.py`

```python
from flask import Flask, jsonify
from datetime import datetime, timezone
import random
import threading
import time
import os
import json
import pika

app = Flask(__name__)

latest_data = {
    "sensor_id": "sensor-001",
    "timestamp": None,
    "temperature": None,
    "humidity": None,
    "sequence": 0,
}

RABBITMQ_HOST = os.getenv(
    "RABBITMQ_HOST",
    "rabbitmq-service.backend-workshop.svc.cluster.local",
)
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ["RABBITMQ_USER"]
RABBITMQ_PASS = os.environ["RABBITMQ_PASS"]
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "sim_sensor_exchange")
ROUTING_KEY = os.getenv("ROUTING_KEY", "sensor.data")


def generate_sensor_data():
    """Generate a new sensor measurement every second."""
    while True:
        latest_data["sequence"] += 1
        latest_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        latest_data["temperature"] = round(random.uniform(18.0, 28.0), 2)
        latest_data["humidity"] = round(random.uniform(35.0, 70.0), 2)
        time.sleep(1)


def publish_to_rabbitmq():
    """Publish the latest measurement and retry when RabbitMQ is unavailable."""
    connection = None
    channel = None
    while True:
        try:
            if connection is None or connection.is_closed:
                credentials = pika.PlainCredentials(
                    RABBITMQ_USER,
                    RABBITMQ_PASS,
                )
                parameters = pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    virtual_host=RABBITMQ_VHOST,
                    credentials=credentials,
                    heartbeat=30,
                    blocked_connection_timeout=5,
                    connection_attempts=3,
                    retry_delay=2,
                )
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                print(
                    f"Connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}",
                    flush=True,
                )

            message = latest_data.copy()
            if message["timestamp"] is not None:
                channel.basic_publish(
                    exchange=EXCHANGE_NAME,
                    routing_key=ROUTING_KEY,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=2,
                    ),
                )
            time.sleep(1)
        except (pika.exceptions.AMQPError, OSError) as error:
            print(
                f"RabbitMQ is unavailable: {error}. Retrying in 5 seconds.",
                flush=True,
            )
            connection = None
            channel = None
            time.sleep(5)


@app.get("/sensor")
def get_sensor_data():
    return jsonify(latest_data.copy())


if __name__ == "__main__":
    threading.Thread(target=generate_sensor_data, daemon=True).start()
    threading.Thread(target=publish_to_rabbitmq, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
```

Twee functionele aanpassingen ten opzichte van het aangeleverde script:

1. Gebruikersnaam en wachtwoord zijn verplichte omgevingsvariabelen, zonder hardcoded defaults. De Deployment hieronder levert ze vanuit het Secret.
2. `virtual_host=RABBITMQ_VHOST` wordt nu ook aan de verbinding doorgegeven. In het testscript was die variabele wel gedefinieerd, maar niet gebruikt. Met de standaardwaarde `/` blijft de route hetzelfde. Zie ook de [Pika-verbindingsparameters](https://pika.readthedocs.io/en/stable/modules/parameters.html).

De bovengrens voor luchtvochtigheid is in versie `2.0` net als in het testdocument `70.0`; in versie `1.0` was dat `65.0`.

Dit is een eenvoudige demo van de nieuwste meting, geen gegarandeerd aflevermechanisme voor iedere afzonderlijke meting. Tijdens verbindingsproblemen blijft de simulator meten, maar worden gemiste metingen niet opgeslagen en later ingehaald. De twee threads lopen onafhankelijk; `sequence` is geen wereldwijde unieke bericht-ID. Een geslaagde verbinding bewijst nog niet dat er een passende binding is: de controle in de queue blijft noodzakelijk.

### `sensor-simulator-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sensor-simulator
  namespace: backend-workshop
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sensor-simulator
  template:
    metadata:
      labels:
        app: sensor-simulator
    spec:
      containers:
        - name: sensor-simulator
          image: whu1/sensor-simulator:2.0
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 5000
          env:
            - name: RABBITMQ_HOST
              value: rabbitmq-service.backend-workshop.svc.cluster.local
            - name: RABBITMQ_PORT
              value: "5672"
            - name: RABBITMQ_VHOST
              value: "/"
            - name: EXCHANGE_NAME
              value: sim_sensor_exchange
            - name: ROUTING_KEY
              value: sensor.data
            - name: RABBITMQ_USER
              valueFrom:
                secretKeyRef:
                  name: rabbitmq-credentials
                  key: username
            - name: RABBITMQ_PASS
              valueFrom:
                secretKeyRef:
                  name: rabbitmq-credentials
                  key: password
```

Deze YAML werkt dezelfde Deployment `sensor-simulator` bij. Er komt geen tweede Deployment bij. De Service uit stap 1 blijft bestaan en hoeft niet opnieuw aangemaakt te worden.

## 10. Image 2.0 bouwen, pushen en uitrollen

Controleer vóór het bouwen dat `app.py` de tweede versie is en de twee andere Docker-bestanden in deze map staan:

```bash
cd ~/workshop/stap-2
ls -l app.py Dockerfile requirements.txt sensor-simulator-deployment.yaml
docker build -t sensor-simulator:2.0 .
docker tag sensor-simulator:2.0 whu1/sensor-simulator:2.0
docker push whu1/sensor-simulator:2.0
```

De Docker-login uit stap 1 kan nog actief zijn. Zo niet, gebruik opnieuw `docker login -u whu1`. Zorg dat de push slaagt voordat je de Deployment bijwerkt.

```bash
kubectl -n backend-workshop apply -f sensor-simulator-deployment.yaml
kubectl -n backend-workshop rollout status deployment/sensor-simulator --timeout=120s
kubectl -n backend-workshop get pods
kubectl -n backend-workshop logs deployment/sensor-simulator --tail=40
```

Verwacht in de applicatielogs:

```text
Connected to RabbitMQ at rabbitmq-service.backend-workshop.svc.cluster.local:5672
```

Anders dan in versie `1.0` print deze code niet iedere meting. Controleer de gepubliceerde gegevens daarom in de RabbitMQ-queue.

Bij opnieuw bouwen en pushen onder dezelfde tag `2.0` verandert het Podtemplate niet automatisch. Gebruik bij voorkeur een nieuwe tag en pas de Deployment aan. Moet je tijdens een repetitie dezelfde tag hergebruiken, herstart dan alleen de simulator nadat de push geslaagd is:

```bash
kubectl -n backend-workshop rollout restart deployment/sensor-simulator
kubectl -n backend-workshop rollout status deployment/sensor-simulator --timeout=120s
```

Dit is een optionele herhaalstap; niet nodig bij de eerste wijziging van image `1.0` naar `2.0`. Start RabbitMQ hiervoor niet opnieuw op.

## 11. Deelnemers controleren de sensordata

Open je persoonlijke queue. Zonder consumers of beperkende policies neemt `Ready` normaal ongeveer iedere seconde toe. Bekijk één of enkele berichten met **Get messages**.

Verwacht JSON met `sensor_id`, `timestamp`, `temperature`, `humidity` en `sequence`. Door eerdere testberichten of requeue kun je eerst nog een oude payload zien. Bekijk zo nodig enkele volgende berichten zonder requeue; dat verwijdert alleen die opgehaalde berichten uit je eigen queue.

Controleer samen:

- iedereen ontvangt nieuwe sensorberichten;
- de berichten gebruiken dezelfde veldstructuur;
- één simulator publiceert en meerdere persoonlijke queues ontvangen elk een kopie.

De HTTP-route bestaat ook nog. De begeleider kan hem optioneel opnieuw testen:

```bash
kubectl -n backend-workshop run curl-test \
  --image=curlimages/curl \
  --restart=Never \
  -it --rm \
  -- curl http://sensor-simulator-service/sensor
```

## Checkpoint

Stap 2 is klaar wanneer:

1. de RabbitMQ Management UI bereikbaar is;
2. de gedeelde direct exchange bestaat;
3. iedereen een eigen queue met binding `sensor.data` heeft;
4. het handmatige testbericht in de persoonlijke queues is aangekomen;
5. simulatorimage `2.0` draait en een RabbitMQ-verbinding heeft;
6. nieuwe sensorberichten in de queues zichtbaar zijn.

Nu werkt de keten van simulator naar RabbitMQ. Het Jetson/ESP-project uit de opening gebruikt dezelfde principes. Ga nu, afhankelijk van de tijd, verder met [stap 3: experimenten](stap-3.md).

## Snelle foutcontrole

| Probleem | Controle |
| --- | --- |
| `deployments.apps "rabbitmq" not found` | Gebruik `deployment/rabbitmq-deployment` en namespace `backend-workshop`. |
| `CreateContainerConfigError` | Controleer of `rabbitmq-credentials` bestaat met keys `username` en `password`. Toon of deel geen Secret-inhoud. |
| Management UI niet bereikbaar | Controleer netwerk/DNS, Ingress, Service en RabbitMQ-logs. |
| `ACCESS_REFUSED` of login mislukt | Controleer account, wachtwoord en rechten op vhost `/`; een bestaand account wordt niet vanzelf gewijzigd door een Secret. |
| `NOT_FOUND - no exchange` | Maak `sim_sensor_exchange` eerst in vhost `/` aan. |
| Verbinding werkt, queue blijft leeg | Controleer exchange, vhost, exacte binding key `sensor.data` en eventuele consumers of policies. |
| `ImagePullBackOff` | Controleer succesvolle push, tag en registry-toegang. |
| Nieuwe code verschijnt niet | Controleer image-tag; bij hergebruik van dezelfde tag is een nieuwe Pod nodig. |
| Nodepoort is al in gebruik | Laat de beheerder de Serviceconfiguratie controleren; verwijder geen onbekende Service om een poort vrij te maken. |

Nuttige controles zonder credentials te tonen:

```bash
kubectl -n backend-workshop get deployment,pods,service,ingress
kubectl -n backend-workshop get endpoints rabbitmq-service
kubectl -n backend-workshop logs deployment/rabbitmq-deployment --tail=50
kubectl -n backend-workshop logs deployment/sensor-simulator --tail=50
```

Bij een deprecation-waarschuwing voor Endpoints:

```bash
kubectl -n backend-workshop get endpointslices \
  -l kubernetes.io/service-name=rabbitmq-service
```

[Verder naar stap 3](stap-3.md) · [Terug naar de workshop](README.md)
