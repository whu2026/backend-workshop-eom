# Backend workshop EOM

In deze workshop bouwen we een Python-sensorsimulator als Docker-image, draaien
we de container in Kubernetes en sturen we de sensordata naar RabbitMQ.

## Leerdoelen

Na de workshop kun je:

- uitleggen wat een Docker-image en container zijn;
- een image bouwen, lokaal testen, taggen en pushen;
- een Kubernetes Deployment, Pod en ClusterIP Service herkennen;
- een applicatie via een interne Kubernetes Service testen;
- uitleggen hoe producer, exchange, routing key, binding en queue samenwerken;
- eenvoudige RabbitMQ-experimenten uitvoeren.

## Workshoproute

1. [Sensorsimulator en Kubernetes](01-simulator/README.md)
2. [RabbitMQ](02-rabbitmq/README.md)
3. [RabbitMQ-experimenten](03-experimenten/README.md)

## Benodigdheden

- toegang tot de workshopserver of beheerterminal;
- `docker`, `kubectl` en `curl`;
- toegang tot de juiste Kubernetes-namespace;
- toegang tot de RabbitMQ Management UI;
- een Docker Hub-account of het vooraf verstrekte workshopaccount.

## Groepsnamen

Gebruik overal dezelfde groepsnaam:

| Onderdeel | Groep 1 | Groep 2 |
|---|---|---|
| Namespace | `workshop-groep1` | `workshop-groep2` |
| Image-tag | `groep1-1.0` | `groep2-1.0` |
| Exchange | `sim_sensor_exchange_groep1` | `sim_sensor_exchange_groep2` |
| Queue | `sensor_queue_groep1` | `sensor_queue_groep2` |

## Start

Download de repository of clone deze:

```bash
git clone https://github.com/whu2026/backend-workshop-eom.git
cd backend-workshop-eom/01-simulator
```

Volg daarna de README van iedere stap.

## Belangrijk

- Zet nooit echte wachtwoorden, tokens of Kubernetes Secrets in GitHub.
- Log bij Docker interactief in; zet geen wachtwoord achter `-p`.
- De begeleider maakt vooraf de namespaces en het Secret
  `rabbitmq-credentials` aan.
- De RabbitMQ-broker wordt één keer centraal gedeployed. Deelnemers maken
  alleen hun eigen exchange, queue en bindings.
