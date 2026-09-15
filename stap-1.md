# Stap 1 — Sensorsimulator bouwen en testen

## Doel en werkwijze

We beginnen met een Python-applicatie die iedere seconde sensordata genereert. De begeleider bouwt hiervan een Docker-image, laat de container lokaal draaien en deployt dezelfde image vervolgens in Kubernetes. RabbitMQ komt pas in stap 2.

De bestanden zijn vooraf klaargezet; de commando's worden tijdens de workshop live uitgevoerd. Deelnemers kijken in deze stap mee. Het hands-on gedeelte met eigen queues en bindings volgt in stap 2.

## 1. Voorbereiding

Gebruik een Bash-terminal op de workshopmachine. De begeleider zet de map `stap-1` uit dit pakket vooraf in `~/workshop/stap-1`. Docker moet daar beschikbaar zijn en `kubectl` moet toegang hebben tot het bedoelde cluster. De namespace `backend-workshop` is al aangemaakt.

```bash
cd ~/workshop/stap-1
pwd
ls -l
kubectl config current-context
kubectl get namespace backend-workshop
```

Controleer het cluster voordat je resources toepast. De map bevat:

| Bestand | Functie |
| --- | --- |
| `app.py` | Sensordata genereren en via HTTP aanbieden |
| `requirements.txt` | Python-dependencies |
| `Dockerfile` | Docker-image bouwen |
| `sensor-simulator-deployment.yaml` | Simulator in Kubernetes draaien |
| `sensor-simulator-service.yaml` | Simulator intern bereikbaar maken |

## 2. Wat doet de applicatie?

De simulator genereert iedere seconde een temperatuur en luchtvochtigheid. Hij bewaart alleen de laatste meting in het geheugen en biedt deze aan via `GET /sensor`.

- `sensor_id`: de naam van de gesimuleerde sensor.
- `timestamp`: het tijdstip in UTC.
- `temperature` en `humidity`: willekeurige meetwaarden.
- `sequence`: een teller binnen dit proces; die begint opnieuw bij een herstart.

### `app.py`

```python
from flask import Flask, jsonify
from datetime import datetime, timezone
import random
import threading
import time

app = Flask(__name__)

latest_data = {
    "sensor_id": "sensor-001",
    "timestamp": None,
    "temperature": None,
    "humidity": None,
    "sequence": 0
}


def generate_sensor_data():
    while True:
        latest_data["sequence"] += 1
        latest_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        latest_data["temperature"] = round(random.uniform(18.0, 28.0), 2)
        latest_data["humidity"] = round(random.uniform(35.0, 65.0), 2)
        print(latest_data, flush=True)
        time.sleep(1)


@app.route("/sensor")
def get_sensor_data():
    return jsonify(latest_data)


if __name__ == "__main__":
    sensor_thread = threading.Thread(target=generate_sensor_data, daemon=True)
    sensor_thread.start()
    app.run(host="0.0.0.0", port=5000)
```

`0.0.0.0` zorgt dat Flask ook op de netwerkinterface van de container luistert. De ontwikkelserver is hier voldoende voor een workshopdemo; dit is geen productieopstelling.

De terminal toont iedere seconde een Python-dictionary. De HTTP-route geeft dezelfde soort gegevens als geldige JSON terug.

### `requirements.txt`

```text
flask
pika
```

Dit is de dependencylijst uit de geteste opstelling. `pika` is alvast geïnstalleerd voor stap 2, maar wordt in deze eerste applicatieversie nog niet geïmporteerd of gebruikt. Er wordt dus nog niets naar RabbitMQ verstuurd. De versies zijn hier, net als in het testdocument, niet vastgezet; leg ze na de laatste repetitie eventueel vast voor reproduceerbare builds.

### `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

De image bevat Python, de dependencies en de applicatie. `EXPOSE 5000` beschrijft de containerpoort; het publiceren van die poort gebeurt bij `docker run`.

## 3. Image bouwen

Voer uit vanuit `~/workshop/stap-1`:

```bash
docker build -t sensor-simulator:1.0 .
docker images sensor-simulator
```

Verwacht: een image met repository `sensor-simulator` en tag `1.0`. De punt bij `docker build` gebruikt de huidige map als buildcontext.

## 4. Container lokaal testen

```bash
docker run --rm -p 5000:5000 sensor-simulator:1.0
```

De terminal blijft bezet en laat de metingen zien. `-p 5000:5000` koppelt poort 5000 van de Docker-host aan poort 5000 in de container. Gebruik deze demo alleen op de bedoelde workshopmachine; de poort kan via de host bereikbaar zijn.

Open een tweede terminal op dezelfde machine en voer enkele keren uit, met ongeveer een seconde ertussen:

```bash
curl -sS http://localhost:5000/sensor
```

Voorbeeld van de HTTP-output:

```json
{
  "sensor_id": "sensor-001",
  "timestamp": "2026-09-08T09:15:23.123456+00:00",
  "temperature": 23.4,
  "humidity": 51.2,
  "sequence": 12
}
```

`timestamp` en `sequence` veranderen bij nieuwe metingen. Willekeurige meetwaarden kunnen soms toevallig gelijk zijn. Gebruik je SSH, dan betekent `localhost` hier de workshopmachine, niet je eigen laptop.

Stop de container in de eerste terminal met `Ctrl+C`. Door `--rm` wordt de gestopte container verwijderd; de image blijft bestaan.

## 5. Image taggen en pushen

De begeleider gebruikt de registry-repository `whu1/sensor-simulator`:

```bash
docker login -u whu1
docker tag sensor-simulator:1.0 whu1/sensor-simulator:1.0
docker push whu1/sensor-simulator:1.0
```

Voer de login interactief uit. Zet geen wachtwoord of access token in scripts, screenshots of GitHub. Gebruik je een eigen registry-account, pas dan zowel de tag/push-commando's als `image` in de Deployment aan. Bij een private image moet het cluster vooraf de juiste pull-toegang hebben.

## 6. Deployment en Service bekijken

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
          image: whu1/sensor-simulator:1.0
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 5000
```

### `sensor-simulator-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: sensor-simulator-service
  namespace: backend-workshop
spec:
  type: ClusterIP
  selector:
    app: sensor-simulator
  ports:
    - name: http
      port: 80
      targetPort: 5000
```

De Deployment draait één simulator-Pod. De Service selecteert Pods met label `app: sensor-simulator` en stuurt verkeer op poort `80` door naar poort `5000` in de Pod. Meer uitleg over deze koppeling staat in de [Kubernetes-documentatie over Services](https://kubernetes.io/docs/concepts/services-networking/service/).

## 7. Deployen in Kubernetes

Pas alleen de twee bedoelde bestanden toe:

```bash
kubectl -n backend-workshop apply -f sensor-simulator-deployment.yaml
kubectl -n backend-workshop apply -f sensor-simulator-service.yaml
kubectl -n backend-workshop rollout status deployment/sensor-simulator --timeout=120s
kubectl -n backend-workshop get deployment,pods,service
kubectl -n backend-workshop get endpoints sensor-simulator-service
```

Het geteste commando `kubectl -n backend-workshop apply -f .` kan ook wanneer deze map uitsluitend de bedoelde Kubernetes-manifesten bevat. Expliciete bestandsnamen voorkomen dat andere YAML-bestanden onbedoeld worden toegepast.

Verwacht: de Deployment is beschikbaar, de simulator-Pod is `Running` en de Service heeft een endpoint met poort `5000`. De namen en IP-adressen van Pods verschillen per uitvoering.

Bij nieuwere clusters kan `get endpoints` een deprecation-waarschuwing geven. Gebruik dan de EndpointSlice-weergave:

```bash
kubectl -n backend-workshop get endpointslices \
  -l kubernetes.io/service-name=sensor-simulator-service
```

## 8. Service vanuit het cluster testen

```bash
kubectl -n backend-workshop run curl-test \
  --image=curlimages/curl \
  --restart=Never \
  -it --rm \
  -- curl http://sensor-simulator-service/sensor
```

Dit start een tijdelijke curl-Pod in dezelfde namespace. De Pod vraagt `/sensor` op via de Service en wordt na afloop verwijderd. Verwacht dezelfde JSON-velden als bij de lokale test.

## Checkpoint

Stap 1 is klaar wanneer:

- de container lokaal sensordata toont;
- de HTTP-route geldige JSON teruggeeft;
- image `whu1/sensor-simulator:1.0` is gepusht;
- de Kubernetes Deployment beschikbaar is;
- de interne curl-test via `sensor-simulator-service` slaagt.

Er is nog geen RabbitMQ-verbinding. De volgende stap is één gedeelde broker, een persoonlijke queue per deelnemer en daarna simulatorversie `2.0`.

## Snelle foutcontrole

| Probleem | Controle |
| --- | --- |
| Lokale poort 5000 is bezet | Bekijk `docker ps`; stop niet zomaar een onbekende container. |
| YAML-bestand niet gevonden | Controleer `pwd`, `ls -l` en de bestandsnaam, inclusief spelling en extensie. |
| `ImagePullBackOff` | Controleer image-naam, tag, succesvolle push en registry-toegang van het cluster. |
| Geen Service-endpoint | Controleer Podstatus en de overeenkomst tussen selector en Podlabel. |
| Curl geeft geen verbinding | Controleer endpoint, poorten en applicatielogs. |
| `curl-test` bestaat al | Controleer `kubectl -n backend-workshop get pod curl-test`; gebruik voor een nieuwe test bijvoorbeeld de naam `curl-test-2`. |

Applicatielogs bekijken:

```bash
kubectl -n backend-workshop logs deployment/sensor-simulator --tail=30
```

[Verder naar stap 2](stap-2.md) · [Terug naar de workshop](README.md)
