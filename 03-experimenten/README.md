# Stap 3 - RabbitMQ-experimenten

Gebruik bij alle namen de eigen groepsnaam. De voorbeelden hieronder zijn voor
groep 1. Groep 2 vervangt overal `groep1` door `groep2`.

De basiselementen uit stap 2 blijven bestaan:

```text
Exchange: sim_sensor_exchange_groep1
Queue: sensor_queue_groep1
Routing key: sensor.data
```

Maak voor experimenten aparte queues en exchanges. Zo blijft de basisroute
werken als een experiment verkeerd wordt ingesteld.

## Experiment 2 - Verkeerde routing key

Doel: aantonen dat een direct exchange alleen een exacte match routeert.

### Uitvoeren

Maak een nieuwe queue:

```text
exp-routing-queue-groep1
```

Bind deze queue aan `sim_sensor_exchange_groep1` met de verkeerde key:

```text
sensor.wrong
```

Wacht enkele seconden en bekijk **Ready**. De queue blijft leeg, terwijl
`sensor_queue_groep1` via de correcte binding wel nieuwe berichten ontvangt.

Verwijder daarna alleen de verkeerde binding en maak een nieuwe binding:

```text
sensor.data
```

Nieuwe berichten komen nu in `exp-routing-queue-groep1`.

### Verklaring

Bij een direct exchange moet de binding key exact gelijk zijn aan de routing
key. Berichten die tijdens de verkeerde binding niet naar deze queue zijn
gerouteerd, komen niet achteraf alsnog binnen.

## Experiment 3 - Van één naar twee simulator-Pods

Doel: laten zien dat één Deployment meerdere producer-Pods kan starten.

### Uitvoeren

Controleer eerst de huidige replica:

```bash
kubectl -n workshop-groep1 get deployment,pods
```

Schaal daarna naar twee Pods:

```bash
kubectl -n workshop-groep1 scale deployment/sensor-simulator --replicas=2
kubectl -n workshop-groep1 get pods -l app=sensor-simulator -w
```

Stop de watch met `Ctrl+C` wanneer beide Pods `Running` zijn.

Controleer de logs van beide Pods:

```bash
kubectl -n workshop-groep1 logs \
  -l app=sensor-simulator \
  --prefix \
  --tail=20
```

Bekijk in RabbitMQ de inkomende message rate. Omdat beide Pods ongeveer iedere
seconde publiceren, stijgt de totale rate normaal van ongeveer één naar
ongeveer twee berichten per seconde. De Management UI toont gemiddelden, dus
het getal hoeft niet exact `2.0/s` te zijn.

Schaal na het experiment terug:

```bash
kubectl -n workshop-groep1 scale deployment/sensor-simulator --replicas=1
kubectl -n workshop-groep1 get pods -l app=sensor-simulator
```

### Routing key is geen producer-ID

Beide replicas gebruiken dezelfde routing key `sensor.data`. Die key beschrijft
de route of berichtcategorie, niet automatisch welke Pod de publisher was.

Als de consumer de bron moet herkennen, voeg dan bijvoorbeeld toe:

```json
{
  "publisher_id": "sensor-simulator-abc123",
  "event_id": "een-unieke-uuid"
}
```

De Podnaam kan via de Kubernetes Downward API als environment variable aan de
container worden doorgegeven. Een `event_id` is nuttig omdat `sequence` per Pod
opnieuw bij nul begint en daardoor niet globaal uniek is.

## Queue-policies

Een policy past instellingen toe op queues waarvan de naam bij een patroon
past. Voor deze workshop gebruiken we een exact patroon, zodat de policy niet
per ongeluk queues van andere groepen beïnvloedt.

Voorbeeld:

```text
Queue:   exp-ttl-queue-groep1
Pattern: ^exp-ttl-queue-groep1$
```

In RabbitMQ Management worden policies normaal gemaakt onder:

```text
Admin → Policies → Add / update a policy
```

Het workshopaccount moet hiervoor voldoende rechten hebben. Als dat niet zo is,
maakt de begeleider de policies klassikaal.

## Experiment 4 - Message TTL

Doel: zien dat oude berichten automatisch uit een queue verdwijnen.

### Queue en binding

Maak:

```text
Queue: exp-ttl-queue-groep1
```

Bind deze queue aan:

```text
Exchange: sim_sensor_exchange_groep1
Routing key: sensor.data
```

### Policy

Maak onder **Admin → Policies**:

```text
Name: ttl-policy-groep1
Pattern: ^exp-ttl-queue-groep1$
Apply to: Queues
Priority: 0
Definition: message-ttl = 5000
```

De waarde is in milliseconden. Een bericht mag dus maximaal ongeveer vijf
seconden in deze queue blijven.

### Controleren

Open `exp-ttl-queue-groep1` en bekijk **Ready** gedurende ongeveer vijftien
seconden. Omdat er ongeveer één bericht per seconde binnenkomt en berichten na
vijf seconden verlopen, stabiliseert de voorraad meestal rond enkele
berichten. Het exacte aantal kan door timing en UI-verversing afwijken.

Verwijder tijdelijk de binding of stop de publisher. De queue loopt daarna
vanzelf leeg zodra de resterende berichten verlopen.

## Experiment 5 - Maximum queue length

Doel: zien dat een queue maximaal een vastgesteld aantal ready messages
bewaart.

### Queue en binding

Maak:

```text
Queue: exp-maxlen-queue-groep1
```

Bind deze queue aan:

```text
Exchange: sim_sensor_exchange_groep1
Routing key: sensor.data
```

### Policy

Maak:

```text
Name: maxlen-policy-groep1
Pattern: ^exp-maxlen-queue-groep1$
Apply to: Queues
Priority: 0
Definition: max-length = 5
```

### Controleren

Open de queue en wacht totdat meer dan vijf berichten zouden zijn
gepubliceerd. **Ready** hoort niet boven vijf uit te komen.

Bij de standaard overflow-instelling verwijdert RabbitMQ de oudste ready
messages wanneer de limiet wordt bereikt. Gebruik **Get messages** om te zien
dat vooral recente sequence-waarden overblijven.

TTL en max length lossen verschillende problemen op:

| Policy | Limiet | Voorbeeld |
|---|---|---|
| `message-ttl` | tijd | metingen ouder dan vijf seconden zijn niet meer relevant |
| `max-length` | aantal | de queue mag maximaal vijf wachtende berichten bevatten |

## Experiment 6 - Direct exchange

Doel: exacte routing keys nogmaals handmatig testen.

Maak:

```text
Exchange: exp-direct-groep1
Type: direct
Queue: exp-direct-q-groep1
Binding key: sensor.data
```

Publiceer via de exchangepagina twee losse berichten:

```text
Routing key: sensor.data
Payload: {"test":"direct-match"}
```

```text
Routing key: sensor.alert
Payload: {"test":"direct-no-match"}
```

Alleen het eerste bericht komt in de queue.

## Experiment 7 - Topic exchange

Doel: patronen in routing keys testen.

Maak:

```text
Exchange: exp-topic-groep1
Type: topic
Queue: exp-topic-q-groep1
Binding key: sensor.*
```

Publiceer:

| Routing key | Verwacht |
|---|---|
| `sensor.data` | komt binnen |
| `sensor.alert` | komt binnen |
| `system.data` | komt niet binnen |
| `sensor.room1.data` | komt niet binnen |

Bij een topic exchange staat `*` voor precies één woord. `#` staat voor nul of
meer woorden.

## Experiment 8 - Fanout exchange

Doel: broadcast naar meerdere queues testen.

Maak:

```text
Exchange: exp-fanout-groep1
Type: fanout
Queue 1: exp-fanout-q1-groep1
Queue 2: exp-fanout-q2-groep1
```

Bind beide queues aan de fanout exchange. De routing key wordt bij fanout
genegeerd.

Publiceer één bericht:

```json
{"test":"fanout-broadcast"}
```

Beide queues ontvangen ieder één kopie.

## Experiment 9 - Exchange naar exchange

Doel: laten zien dat een exchange ook aan een andere exchange kan worden
gebonden.

### Onderdelen maken

Maak:

```text
Exchange E1: exp-e1-groep1
Type: direct

Exchange E2: exp-e2-groep1
Type: direct

Queue Q1: exp-e2e-q1-groep1
```

### Drie bindings maken

Gebruik voor alle bindings:

```text
Routing key: demo.key
```

Maak deze routes:

```text
E1 → Q1
E1 → E2
E2 → Q1
```

De precieze naam van de knop kan per RabbitMQ-versie verschillen. Open de
exchange of queue en gebruik het onderdeel **Bindings** om de bron, bestemming
en routing key in te stellen.

### Publiceren en controleren

Publiceer precies één bericht naar E1:

```text
Routing key: demo.key
Payload: {"test":"exchange-to-exchange"}
```

Er bestaan nu twee routes naar Q1:

```text
E1 → Q1
E1 → E2 → Q1
```

Toch krijgt Q1 voor deze ene publicatie precies één kopie. RabbitMQ voorkomt
dat dezelfde gepubliceerde message via meerdere paden dubbel in dezelfde queue
terechtkomt.

Let op: twee afzonderlijke publicaties leveren natuurlijk wel twee berichten
op. De eenmalige kopie geldt per gepubliceerde message en per doelqueue.

## Opruimen

Verwijder na de experimenten de tijdelijke policies, queues en exchanges met
prefix `exp-`. Laat de basisroute uit stap 2 staan als deze later nog nodig is.

Controleer ook dat de simulator weer één replica heeft:

```bash
kubectl -n workshop-groep1 scale deployment/sensor-simulator --replicas=1
```

## Officiële referenties

- [RabbitMQ AMQP-concepten en exchange-types](https://www.rabbitmq.com/tutorials/amqp-concepts)
- [RabbitMQ message TTL](https://www.rabbitmq.com/docs/ttl)
- [RabbitMQ maximum queue length](https://www.rabbitmq.com/docs/maxlength)
- [RabbitMQ exchange-to-exchange bindings](https://www.rabbitmq.com/docs/e2e)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
