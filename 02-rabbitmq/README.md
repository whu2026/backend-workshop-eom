# Stap 2 - Sensordata naar RabbitMQ sturen

Alle groepen gebruiken dezelfde RabbitMQ-broker. RabbitMQ is vooraf door de
workshopbegeleider gedeployed. Deelnemers maken in de Management UI alleen een
eigen exchange, queue en binding.

## 1. De route

```text
Producer → Exchange → Queue → Consumer
```

- **Producer**: de Python-sensorsimulator;
- **Exchange**: ontvangt berichten en bepaalt de route;
- **Routing key**: label dat de producer met het bericht meestuurt;
- **Binding**: routeringsregel tussen een exchange en queue;
- **Queue**: bewaart gerouteerde berichten totdat een consumer ze verwerkt;
- **Consumer**: bijvoorbeeld Python, SAS ESP of een andere service.

## 2. RabbitMQ draait al in Kubernetes

De begeleider laat de YAML kort zien. Deelnemers voeren deze deployment niet
zelf uit.

Belangrijke regel uit de Deployment:

```yaml
containers:
  - name: rabbitmq
    image: rabbitmq:4.2-management
    ports:
      - name: amqp
        containerPort: 5672
      - name: management
        containerPort: 15672
```

Belangrijke regels uit de interne Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq-service
  namespace: luke
spec:
  type: ClusterIP
  selector:
    app: rabbitmq
  ports:
    - name: amqp
      port: 5672
      targetPort: 5672
    - name: management
      port: 15672
      targetPort: 15672
```

- poort `5672` is voor AMQP-verkeer van de sensorsimulator;
- poort `15672` hoort bij de RabbitMQ Management UI;
- de simulator gebruikt intern
  `rabbitmq-service.luke.svc.cluster.local:5672`;
- voor de browser gebruiken deelnemers de vooraf verstrekte workshop-URL.

De exacte manier waarop de browser de Management UI bereikt, is al door de
beheerder ingericht en is geen onderdeel van deze workshop.

De begeleider heeft vooraf uitgevoerd:

```bash
kubectl -n luke apply -f rabbitmq-deployment.yaml
kubectl -n luke apply -f rabbitmq-service.yaml
kubectl -n luke rollout status deployment/rabbitmq
kubectl -n luke get deployment,pods,service
```

## 3. Experiment 1 - Kubernetes vervangt de RabbitMQ-Pod

Dit is een korte demonstratie door de workshopbegeleider. Deelnemers hoeven de
RabbitMQ-Pod niet zelf te verwijderen.

Voer dit experiment uit voordat deelnemers exchanges en queues maken. De
voorbeelddeployment gebruikt geen permanente opslag. RabbitMQ-configuratie en
berichten in de container kunnen daarom bij vervanging van de Pod verloren
gaan.

Volg de RabbitMQ-Pod in een terminal:

```bash
kubectl -n luke get pods -l app=rabbitmq -w
```

Zoek in een tweede terminal de Podnaam:

```bash
kubectl -n luke get pods -l app=rabbitmq
```

Verwijder alleen die Pod:

```bash
kubectl -n luke delete pod <podnaam>
```

De Deployment wil nog steeds één replica. Kubernetes maakt daarom automatisch
een nieuwe RabbitMQ-Pod:

```bash
kubectl -n luke rollout status deployment/rabbitmq
kubectl -n luke get pods -l app=rabbitmq
kubectl -n luke get endpoints rabbitmq-service
```

De Podnaam verandert, maar de Servicenaam
`rabbitmq-service.luke.svc.cluster.local` blijft gelijk. De Management UI kan
tijdens de herstart kort niet bereikbaar zijn.

## 4. Inloggen bij RabbitMQ Management

Open de vooraf verstrekte workshop-URL en log in met het workshopaccount.

Controleer vóór de workshop dat dit account:

- exchanges, queues en bindings mag maken;
- voor stap 3 policies mag maken;
- toegang heeft tot de gebruikte virtual host.

## 5. Eigen direct exchange aanmaken

Ga naar **Exchanges** en kies **Add a new exchange**.

Voor groep 1:

```text
Name: sim_sensor_exchange_groep1
Type: direct
Durability: Durable
Auto delete: No
```

Voor groep 2:

```text
Name: sim_sensor_exchange_groep2
```

De naam moet exact overeenkomen met `EXCHANGE_NAME` in de eigen `app.py`.

## 6. Eigen queue aanmaken

Ga naar **Queues and Streams** en kies **Add a new queue**.

Voor groep 1:

```text
Name: sensor_queue_groep1
Type: Classic
Durability: Durable
Auto delete: No
```

Voor groep 2:

```text
Name: sensor_queue_groep2
```

## 7. Exchange en queue binden

Open de eigen queue of exchange en voeg een binding toe.

Voor groep 1:

```text
Exchange: sim_sensor_exchange_groep1
Queue: sensor_queue_groep1
Routing key: sensor.data
```

Bij een direct exchange moet de binding key exact overeenkomen met de routing
key van de publisher:

```python
ROUTING_KEY = os.getenv("ROUTING_KEY", "sensor.data")
```

Berichten die vóór het maken van de binding zijn gepubliceerd, worden niet
achteraf alsnog in de queue geplaatst. Alleen nieuwe berichten volgen de
nieuwe route.

## 8. Verbinding en berichten controleren

Controleer de simulator-Pod en logs:

```bash
kubectl -n workshop-groep1 get pods
kubectl -n workshop-groep1 logs deployment/sensor-simulator --tail=30
```

Als de publisher na het aanmaken van de exchange nog niet is hersteld:

```bash
kubectl -n workshop-groep1 rollout restart deployment/sensor-simulator
kubectl -n workshop-groep1 rollout status deployment/sensor-simulator
```

Open daarna de eigen queue in RabbitMQ Management:

- **Ready** laat zien hoeveel berichten klaarstaan;
- de message rate laat zien hoe snel nieuwe berichten aankomen;
- met **Get messages** kun je de JSON-inhoud bekijken.

Bij **Get messages** werkt de Management UI tijdelijk als consumer. Gebruik
`requeue=true` wanneer het bekeken bericht in de queue moet blijven.

## 9. Checkpoint

De basisroute werkt wanneer:

1. de simulatorlog een RabbitMQ-verbinding laat zien;
2. de eigen queue nieuwe berichten ontvangt;
3. een opgehaald bericht de verwachte sensor-JSON bevat.

De experimenten met routing keys, replicas, policies en exchange-types staan
in [stap 3](../03-experimenten/README.md).

Referenties:

- [RabbitMQ AMQP-concepten](https://www.rabbitmq.com/tutorials/amqp-concepts)
- [RabbitMQ Management](https://www.rabbitmq.com/docs/management)
- [RabbitMQ policies](https://www.rabbitmq.com/docs/parameters)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
