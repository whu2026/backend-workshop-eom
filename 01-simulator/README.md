# Stap 1 - Sensorsimulator containeriseren en in Kubernetes testen

In deze stap bouwen en testen we de sensorsimulator. De Pika-code staat al in
`app.py`. Als RabbitMQ nog niet bereikbaar is, blijft de simulator sensordata
genereren en blijft `/sensor` beschikbaar.

## 1. Eigen exchange instellen in app.py

Iedere groep gebruikt later een eigen RabbitMQ-exchange. Pas vóór het bouwen
van de image deze regel in `app.py` aan.

Voor groep 1:

```python
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "sim_sensor_exchange_groep1")
```

Voor groep 2:

```python
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "sim_sensor_exchange_groep2")
```

De routing key blijft voor alle groepen:

```python
ROUTING_KEY = os.getenv("ROUTING_KEY", "sensor.data")
```

De exchanges zelf worden in stap 2 in RabbitMQ aangemaakt.

## 2. Docker-image bouwen en lokaal testen

Onderstaand voorbeeld is voor groep 1:

```bash
sudo docker build -t sensor-simulator:1.0 .
sudo docker run --rm -p 5000:5000 sensor-simulator:1.0
```

Test vanuit een tweede terminal:

```bash
curl http://localhost:5000/sensor
```

Stop de container daarna met `Ctrl+C`.

## 3. Image taggen en pushen

```bash
sudo docker login -u whu1
sudo docker tag \
  sensor-simulator:1.0 \
  whu1/sensor-simulator:groep1-1.0
sudo docker push whu1/sensor-simulator:groep1-1.0
```

Groep 2 gebruikt bijvoorbeeld de tag `groep2-1.0`. `whu1` blijft de
Docker Hub-gebruiker of organisatie; `groep1` is onderdeel van de tag.

## 4. Namespaces vooraf aanmaken

Dit wordt door de workshopbegeleider of Kubernetesbeheerder uitgevoerd:

```bash
kubectl create namespace workshop-groep1
kubectl create namespace workshop-groep2
```

Een Kubernetes-namespace mag geen underscore bevatten. Gebruik daarom
`workshop-groep1` en niet `workshop_groep1`.

## 5. Deployment en Service toepassen

Controleer eerst of in `deployment.yaml` de juiste groepstag staat:

```yaml
image: whu1/sensor-simulator:groep1-1.0
```

De Deployment leest de RabbitMQ-gebruikersnaam en het wachtwoord uit het
Kubernetes Secret `rabbitmq-credentials`. De begeleider maakt dit Secret vooraf
in iedere groepsnamespace. Als het Secret ontbreekt, krijgt de Pod bijvoorbeeld
de status `CreateContainerConfigError`.

Pas daarna de bestanden toe:

```bash
kubectl -n workshop-groep1 apply -f deployment.yaml
kubectl -n workshop-groep1 apply -f service.yaml
```

## 6. Kubernetes-resources controleren

```bash
kubectl -n workshop-groep1 rollout status deployment/sensor-simulator
kubectl -n workshop-groep1 get deployment,pods,service
kubectl -n workshop-groep1 get endpoints sensor-simulator-service
```

## 7. JSON via de interne Service testen

```bash
kubectl -n workshop-groep1 run curl-test --image=curlimages/curl --restart=Never -it --rm -- curl http://sensor-simulator-service/sensor
```

De URL bestaat uit:

- `sensor-simulator-service`: de naam uit `service.yaml`;
- poort 80: de `port` van de Service, daarom hoeft `:80` niet in de URL;
- `/sensor`: de route uit de Flask-applicatie.

De Service stuurt het verzoek vanaf poort 80 door naar poort 5000 van de
container. Het korte adres werkt omdat `curl-test` in dezelfde namespace wordt
gestart. Vanuit een andere namespace is het volledige adres nodig:

```text
http://sensor-simulator-service.workshop-groep1.svc.cluster.local/sensor
```

Gebruik hier niet `localhost`. Vanuit de `curl-test`-Pod verwijst `localhost`
naar de curl-Pod zelf, niet naar de sensor-Pod.

Ga na deze controle verder met
[stap 2: RabbitMQ](../02-rabbitmq/README.md).
