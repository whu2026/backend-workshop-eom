# Stap 2 — Zelf bouwen en daarna zelf deployen

**Doel:** zelf een image bouwen en de bekende Kubernetes-stappen herhalen. Je pusht niets naar Docker Hub. Voor de deployment gebruik je een vooraf beschikbare image die de begeleider doorgeeft.

## 1. Maak een eigen kopie en bouw

Vervang `wenjie` door jouw naam. De begeleider heeft `~/workshop/simulator` klaargezet.

```bash
cd ~/workshop/simulator
mkdir wenjie
cp app.py Dockerfile *.yaml wenjie/
cd wenjie
docker build -t sensor-simulator:wenjie .
docker images sensor-simulator
```

Je eigen map bevat app.py, Dockerfile, deployment.yaml, service.yaml en ingress.yaml. Gebruik bij herhaling je bestaande map; overschrijf geen werk van een ander.

**Verwacht:** de build eindigt zonder fout en de imagelijst bevat jouw lokale tag. De image-ID kan gelijk zijn aan die van anderen als de code en basis gelijk zijn.

**Checkpoint 3:** wijs jouw gebouwde image aan.

**Vraag:** wat betekent de punt achter docker build?  
**Antwoord:** de huidige map is de buildcontext. De Dockerfile kopieert app.py. De YAML-bestanden worden door deze Dockerfile niet in de image gekopieerd.

De app maakt iedere seconde JSON-metingen. `/sensor` geeft de laatste meting via HTTP op poort 5000. De Dockerfile gebruikt alleen Python-standaardmodules; er is geen pip-installatie nodig.

## 2. Optioneel: kort lokaal testen

```bash
docker run --rm sensor-simulator:wenjie
```

**Verwacht:** JSON met `sensor_id`, `timestamp`, `temperature`, `humidity` en `sequence`. Stop na enkele regels met **Ctrl+C**. De testcontainer wordt opgeruimd, de image blijft staan. Er wordt geen hostpoort gepubliceerd.

## 3. Vul de beschikbare image en jouw naam in

De begeleider geeft de **volledige registry-image inclusief tag**. Het voorbeeld in dit pakket is:

```text
whu1/sensor-simulator:1.0
```

Dit is een **voorbeeldtag die de begeleider vooraf moet publiceren of vervangen**. Gebruik tijdens de workshop de bevestigde naam. Je eigen lokale tag `sensor-simulator:wenjie` is voor deze opdracht niet de image die Kubernetes ophaalt. We deployen een vooraf gepubliceerde image van dezelfde code.

YAML-bestanden aanpassen in MobaXterm

Open in het SFTP-paneel van MobaXterm jouw persoonlijke map workshop/simulator/<naam>.
Dubbelklik op deployment.yaml om het bestand te openen in de editor van MobaXterm.
Vul de juiste imagenaam in en vervang <naam> door je eigen naam.
Sla het bestand op met Ctrl + S.
Herhaal dit voor service.yaml en ingress.yaml.

| Bestand | Aanpassen / controleren |
| --- | --- |
| deployment.yaml | Vervang `VUL_BESCHIKBARE_IMAGE_IN` door de verstrekte image; vervang overal `<naam>` door jouw naam. |
| service.yaml | Vervang overal `<naam>`; de selector moet bij het Podlabel passen. |
| ingress.yaml | Vervang overal `<naam>`, inclusief de host en de Serviceverwijzing. |

Voorbeeld: `sensor-simulator-deployment-wenjie`, `sensor-simulator-service-wenjie` en `simulator-wenjie.k8s.eom.local`. Gebruik de afgesproken host binnen het voorbereide domein. De host in YAML bevat geen `http://` of `/sensor`.

**Wat herken je van nginx?** Deployment, Service en Ingress. De simulator heeft eigen namen en labels, zodat jouw nginx-applicatie blijft bestaan. Er is geen ConfigMap nodig: deze app geeft JSON uit de Python-code terug. De app luistert op **5000**, dus de Service gebruikt **targetPort 5000**. De Servicepoort blijft **80**.

**Vraag:** waarom gebruiken we de beschikbare image?  
**Antwoord:** een lokale Docker-build is niet automatisch beschikbaar op Kubernetes-nodes. De nodes halen de verstrekte image uit de registry. Zo kunnen we het deployen oefenen zonder zelf te pushen.

## 4. Deploy zelf en controleer

Blijf in `~/workshop/simulator/wenjie`. Sla alle wijzigingen op of upload ze terug. Voer daarna uit:

```bash
kubectl -n backend-workshop apply -f .
kubectl -n backend-workshop get pods -o wide
kubectl -n backend-workshop get svc
```

`apply -f .` gebruikt hier de drie YAML-bestanden. App.py en Dockerfile worden niet als Kubernetes-manifests behandeld.

**Verwacht:** jouw Deployment, Service en Ingress worden aangemaakt. Zoek `sensor-simulator-deployment-wenjie-...`. Wacht op **Running** en **1/1 Ready**. Zoek ook `sensor-simulator-service-wenjie` met poort **80/TCP**. De nginx-resources blijven daarnaast bestaan.

**Checkpoint 4:** wijs jouw simulator-Pod en Service aan. Dit zijn dezelfde controles als in stap 1.

## 5. Open je eigen simulator-URL

Open op je laptop, met jouw naam:

```text
http://simulator-wenjie.k8s.eom.local/sensor
```

**Verwacht:** JSON-metingen. Vernieuw de pagina; het volgnummer en de waarden veranderen. Vraag hulp als de Pod niet Ready wordt of de URL niet werkt.

**Vraag:** draait deze app in jouw lokale testcontainer?  
**Antwoord:** nee, deze URL bereikt jouw simulator-Pod in Kubernetes. Die is gestart uit de vooraf beschikbare registry-image.

**Stap 2 is klaar:** je hebt zelf gebouwd en zelf gedeployed. Vergelijk zo nodig met [de voorbeeldoplossing](oplossingen/simulator/), met de voorbeeldtag die vóór gebruik moet worden bevestigd. Ga samen verder naar [stap 3](stap-3.md).
