# Stap 3 — Controleren en terugkijken

**Tijd: 54–57 minuten.** Dit is de gezamenlijke controle. De extra proeven hieronder zijn voor als je eerder klaar bent of na de workshop.

## Gezamenlijk eindresultaat

```bash
kubectl -n "$NS" get deployments,pods,services,ingresses,configmaps -l workshop-owner="$NAAM"
curl --fail --show-error --max-time 10 "$SCHEME://$SIM_HOST/sensor"
```

**Verwacht:** jouw twee Deployments, twee Services en twee Ingresses en één nginx-ConfigMap; normaal één Ready Pod per Deployment. Andere deelnemers hebben andere namen. De simulator geeft JSON.

| Vraag | Antwoord |
|---|---|
| Wat is het verschil tussen image en container? | De image is het pakket; de container is een draaiende instantie. |
| Waarvoor is een Pod? | Het is de kleinste inzetbare Kubernetes-eenheid met één of meer containers die o.a. netwerk delen. |
| Wat doet de Deployment? | Beschrijft de gewenste Pods en beheert ze via ReplicaSets. |
| Waarom een Service? | Stabiele interne naam en routering naar passende Ready endpoints, ook als Podadressen wijzigen. |
| Wat doet de Ingress? | Beschrijft de HTTP(S)-routering; een Ingress-controller voert de regels uit. |
| Wat doet onze ConfigMap? | Levert index.html als bestand aan nginx, zonder een nieuwe image te bouwen. |
| Waarom pushen? | Zodat clusternodes de image uit een bereikbare registry kunnen ophalen. |
| Is een SAS-app precies één Pod? | Niet in het algemeen. Een toepassing gebruikt meerdere samenwerkende diensten; aantallen en namen hangen van de installatie af. |

## Foutzoeken in een vaste volgorde

Voor de webserver verschillen Deploymentnaam, app-label, Service en Ingress. Gebruik `$WEB`, `$WEB_APP`, `$WEB_SERVICE` en `$WEB_INGRESS` op de bijbehorende plek; vervang niet overal blind `$SIM` door dezelfde waarde.

```bash
kubectl -n "$NS" get pods -l app="$SIM"
kubectl -n "$NS" describe deployment "$SIM"
kubectl -n "$NS" describe pods -l app="$SIM"
kubectl -n "$NS" logs deployment/"$SIM" --tail=30
kubectl -n "$NS" get endpointslices -l kubernetes.io/service-name="$SIM"
kubectl -n "$NS" describe ingress "$SIM"
```

| Wat zie je? | Controle / verwachte oplossing |
|---|---|
| `ImagePullBackOff` | Image/tag, registry, netwerk of imagePullSecret corrigeren. Events geven de concrete fout. |
| ConfigMap ontbreekt / `FailedMount` | Vergelijk de ConfigMap-naam met `volumes[].configMap.name` en controleer dat beide in backend-workshop staan. |
| Verkeerde HTML | Controleer ConfigMap, mountPath en of de Service uitsluitend jouw Pod selecteert. |
| `Pending` | Kijk naar capaciteit, quota en scheduling-events. |
| `CrashLoopBackOff` | Bekijk logs en eventueel `kubectl logs PODNAAM --previous`; corrigeer start/configuratie. |
| Running maar `0/1` | Controleer readiness-probe en of app op de juiste poort luistert. |
| Service geeft geen antwoord | Controleer selector, Podlabels, Ready endpoints, poorten en NetworkPolicy. |
| DNS-fout | Controleer hostname en vooraf ingestelde DNS; YAML maakt geen DNS-record. |
| HTTP 404 via host | Controleer host/path en IngressClass; de 404 kan van app of controller komen. |
| HTTP 502/503 | Controleer endpoints, readiness en de backendpoort. De exacte code is controllerafhankelijk. |

## Extra proef A — Een eigen Pod laten vervangen

**Alleen bij extra tijd, circa 3 minuten.** Voorspel eerst: wat blijft staan als je één eigen nginx-Pod verwijdert?

Terminal 1 (eerst opnieuw je `workshop.env` sourcen):

```bash
kubectl -n "$NS" get pods -l app="$WEB_APP" -w
```

Terminal 2:

```bash
POD=$(kubectl -n "$NS" get pods -l app="$WEB_APP" -o jsonpath='{.items[0].metadata.name}')
printf '%s\n' "$POD"
kubectl -n "$NS" delete pod "$POD"
kubectl -n "$NS" rollout status deployment/"$WEB" --timeout=90s
curl --fail --max-time 10 "$SCHEME://$WEB_HOST/"
```

**Verwacht:** een nieuwe Podnaam, dezelfde Deployment, Service en Ingress. Met één replica kan er tijdelijk onderbreking zijn. Sluit `-w` af met Ctrl+C.

**Antwoord:** de ReplicaSet onder de Deployment zorgt weer voor het gewenste aantal. De Service maakt geen Pods. Verwijder nooit Pods uit de Viya-namespace tijdens deze oefening.

## Extra proef B — Labels en selector vergelijken

**Circa 2 minuten, alleen lezen.**

```bash
kubectl -n "$NS" get service "$WEB_SERVICE" -o jsonpath='{.spec.selector}'
kubectl -n "$NS" get pods -l app="$WEB_APP" --show-labels
```

**Verwacht:** dezelfde `app`-waarde in de Service-selector en de Podlabels. **Antwoord:** zo vindt de Service de juiste Pods; niet op basis van een toevallig gelijkende Podnaam. Een verkeerde selector kan een Service zonder geschikte endpoints opleveren.

## Opruimen — na toestemming van de begeleider aan het einde

Bekijk eerst je eigen resources met het eerste commando van deze pagina. Verwijder daarna alleen jouw objecten:

```bash
kubectl -n "$NS" delete ingress,service,deployment,configmap -l workshop-owner="$NAAM"
```

Verwijder de gedeelde namespace niet. De korte RabbitMQ-demo wordt door de begeleider beheerd.
