# Stap 2 — Zelf een Docker-image bouwen

**Uitleg: 34–40 minuten · Zelf doen: 40–54 minuten.**

Een image bevat de applicatie en de gebruikersruimte die deze nodig heeft. Een container is een draaiende instantie van die image. Docker bouwt en test onze image. Kubernetes laat containers op nodes draaien via een container runtime; Docker Engine is daarvoor niet verplicht.

Onze kleine Python-simulator maakt iedere seconde een voorbeeldmeting. `GET /sensor` geeft de nieuwste meting als JSON; `/healthz` is de controle-URL. Hij publiceert geen berichten. De code gebruikt alleen de Python-standaardbibliotheek; daarom is hier geen `requirements.txt` of pip-installatie nodig. De eenvoudige HTTP-server is voor deze oefening, niet een uitgewerkte productieserver.

## 1. Bouwbestanden bekijken en bouwen — 4 minuten

Keer terug naar de repositorymap met `cd "$REPO"`, met de variabelen uit stap 1. In een nieuwe terminal laad je eerst `source "$HOME/workshop/a01/workshop.env"` (gebruik je eigen naam) en ga je handmatig naar de repositorymap:

```bash
cat stap-2/simulator/Dockerfile
printf '%s\n' "$IMAGE"
docker build -t "$IMAGE" stap-2/simulator
docker image inspect "$IMAGE" --format '{{.Id}}'
```

| Regel | Betekenis |
|---|---|
| `FROM python:3.12-slim` | Basisimage met Python |
| `WORKDIR /app` | Werkmap in de image |
| `COPY app.py .` | Voeg onze code toe |
| `USER 10001:10001` | Voer de app zonder root uit |
| `EXPOSE 5000` | Documenteert de applicatiepoort |
| `CMD ["python", "app.py"]` | Startcommando van de container |

**Verwacht:** een succesvolle build met jouw eigen tag. Het laatste argument van `docker build` is de buildcontext, niet de naam van de Dockerfile. Deze bestanden zijn vooraf klaar; je hoeft geen Python te schrijven.

## 2. Als container testen — 2 minuten

```bash
docker run -d --name "$SIM" -p 127.0.0.1::5000 "$IMAGE"
docker port "$SIM" 5000/tcp
LOCAL_PORT=$(docker port "$SIM" 5000/tcp | awk -F: '{print $NF}')
curl --fail --retry 5 --retry-connrefused --retry-delay 1 "http://127.0.0.1:$LOCAL_PORT/sensor"
docker logs "$SIM" --tail=3
```

Docker kiest een vrije lokale poort. Zo botsen deelnemers op dezelfde server niet op poort 8080. `127.0.0.1` verwijst hier naar de workshopserver waarop je terminal draait. De mapping is hostpoort → containerpoort 5000; `EXPOSE` op zichzelf publiceert geen poort.

**Verwacht:** JSON met `sensor_id`, `timestamp`, `temperature`, `humidity` en `sequence`. Herhaal `curl` na enkele seconden: de sequence neemt toe. De waarden zijn willekeurig, dus exacte temperaturen verschillen. Je container heeft jouw eigen naam.

## 3. Image beschikbaar maken voor Kubernetes — 2 minuten

```bash
docker push "$IMAGE"
```

**Verwacht:** push voltooid en een digest in de uitvoer. Registry-login is vooraf geregeld in je eigen gebruikersomgeving. Een lokaal gebouwde image staat niet automatisch op alle clusternodes. Docker-login geeft Kubernetes geen pullrechten: bij een private registry regelt de begeleider ook een pull-Secret in de namespace. Zet geen tokens of wachtwoorden in Git of in commando's op de slide.

## 4. Eigen image deployen — 4 minuten

```bash
printf '%s\n' "$IMAGE"
nano "$WORK/stap-2/deployment.yaml"
```

Vervang `VUL_IMAGE_IN` door exact de gepushte image inclusief tag. De template heeft al de juiste containerpoort 5000 en readiness-probe.

```bash
kubectl -n "$NS" apply -f "$WORK/stap-2/deployment.yaml"
kubectl -n "$NS" apply -f "$WORK/stap-2/service.yaml"
kubectl -n "$NS" rollout status deployment/"$SIM" --timeout=90s
kubectl -n "$NS" get pods -l app="$SIM" -o wide
kubectl -n "$NS" logs deployment/"$SIM" --tail=3
kubectl -n "$NS" exec deployment/"$WEB" -- wget -qO- "http://$SIM/sensor"
```

**Verwacht:** eigen simulator-Pod `1/1 Running`, JSON in logs en via de Service. We gebruiken de nginx-Pod uit stap 1 als interne testclient. De simulatorimage zelf bevat geen `curl` of `wget`.

**Checkpoint:** vertel hoe de image vanuit de registry bij jouw Pod komt. **Antwoord:** de node haalt de image op via zijn container runtime; de Deployment beschrijft welke image gebruikt wordt.

## 5. Via eigen hostname testen — 2 minuten

```bash
printf '%s\n' "$SIM_HOST"
nano "$WORK/stap-2/ingress.yaml"
```

Vervang iedere `VUL_HOST_IN` door je simulator-hostname. Daarna:

```bash
kubectl -n "$NS" apply -f "$WORK/stap-2/ingress.yaml"
curl --fail --show-error --max-time 10 "$SCHEME://$SIM_HOST/sensor"
printf 'Open: %s://%s/sensor\n' "$SCHEME" "$SIM_HOST"
docker stop "$SIM"
docker rm "$SIM"
```

**Verwacht:** dezelfde soort JSON via de externe route. De lokale container en de Kubernetes-Pod zijn aparte processen: hun sequence en metingen hoeven niet gelijk te zijn. Na stoppen van de lokale container blijft de Kubernetes-Pod werken.

**Stap 2 afgerond:** je hebt gebouwd, lokaal getest, gepusht, gedeployed en via een Service plus Ingress getest. Ga naar [stap 3](stap-3.md).

**Bij vertraging:** meld het aan de begeleider. Gebruik desnoods de vooraf gebouwde simulatorimage om de Kubernetes-stappen af te ronden; oefen het bouwen later opnieuw. Hergebruik bij een nieuwe build liever een nieuwe tag, bijvoorbeeld `a01-new-v1-2`, en pas de Deployment aan. Dezelfde tag met `IfNotPresent` kan een oude image op de node blijven gebruiken.
