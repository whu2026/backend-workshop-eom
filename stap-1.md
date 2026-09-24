# Stap 1 — Je eigen nginx-website

**Doel:** vier YAML-bestanden aanpassen, deployen en je website openen. **Wie:** alle deelnemers. **Tijd:** circa 16 minuten na de uitleg.

## 1. Maak je eigen werkmap

Begin op de workshopserver. De begeleider heeft `~/workshop/nginx` voorbereid. In dit voorbeeld is je naam `wenjie`; vervang die in de commando’s door jouw toegewezen naam. Typ nooit letterlijk `mkdir <naam>`: punthaken hebben in de shell een andere betekenis.

```bash
cd ~
cd workshop/nginx
mkdir wenjie
cp *.yaml wenjie/
cd wenjie
ls
```

**Verwacht:** `configmap.yaml`, `deployment.yaml`, `service.yaml` en `ingress.yaml`. De kopieeropdracht neemt alleen de YAML-bestanden mee, geen deelnemersmappen. Als de map al bestaat, gebruik jouw bestaande map of vraag de begeleider; overschrijf geen werk van een ander.

## 2. Bewerk jouw vier kopieën

Vervang **overal `<naam>`** (inclusief punthaken) door dezelfde naam. De image `nginx:latest` blijft staan. Je hoeft de HTML niet aan te passen; een persoonlijke tekst mag als extra.

| Bestand | Wat controleer je? |
| --- | --- |
| configmap.yaml | `metadata.name: nginx-demo-html-wenjie` |
| deployment.yaml | Naam `nginx-demo-deployment-wenjie`; alle `app`-waarden `nginx-demo-wenjie`; `configMap.name: nginx-demo-html-wenjie` |
| service.yaml | Naam `nginx-demo-service-wenjie`; selector `app: nginx-demo-wenjie` |
| ingress.yaml | Naam `nginx-demo-ingress-wenjie`; host `nginx-web-wenjie.k8s.eom.local`; Serviceverwijzing `nginx-demo-service-wenjie` |

De host is zonder `http://` en zonder pad. Gebruik jouw afgesproken naam binnen het voorbereide domein. Een Ingress maakt zelf geen DNS-record.

### YAML-bestanden aanpassen in MobaXterm

Open in het SFTP-paneel van MobaXterm jouw persoonlijke map workshop/nginx/<naam>.

Dubbelklik op een YAML-bestand om het te openen in de ingebouwde editor van MobaXterm.

Vervang <naam> door je eigen naam en pas de benodigde gegevens aan.

Sla het bestand op met Ctrl + S.

Herhaal dit voor alle vier de YAML-bestanden: configmap.yaml, deployment.yaml, service.yaml en ingress.yaml.

**Vraag:** waarom dezelfde naam in labels en selectors?  
**Antwoord:** de Service vindt jouw Pod via de bijpassende `app`-waarde. Een verkeerde waarde kan naar geen of naar de verkeerde Pods verwijzen.

## 3. Deployen

Blijf in jouw map `workshop/nginx/wenjie`. Als je de map kwijt bent:

```bash
cd ~/workshop/nginx/wenjie
```

Voer daarna uit:

```bash
kubectl -n backend-workshop apply -f .
kubectl -n backend-workshop get pods -o wide
```

**Verwacht:** vier objecten worden aangemaakt of bijgewerkt. Zoek jouw Pod met een naam die begint met `nginx-demo-deployment-wenjie-`. Wacht op **STATUS Running** en **READY 1/1**. Voer `get pods -o wide` opnieuw uit als de container nog start.

**Checkpoint 1:** laat jouw Ready Pod aan de begeleider zien. `created` na apply bewijst alleen dat de configuratie is geaccepteerd.

## 4. Service bekijken

```bash
kubectl -n backend-workshop get svc
```

**Verwacht:** `nginx-demo-service-wenjie`, type `ClusterIP`, poort `80/TCP`. Je ziet ook Services van andere deelnemers.

**Vraag:** wat doet de Service?  
**Antwoord:** hij geeft een stabiel intern toegangspunt en selecteert de juiste Pods. Hij maakt geen Pods aan.

## 5. Website openen

Open op je laptop in de browser:

```text
http://nginx-web-wenjie.k8s.eom.local/
```

Gebruik jouw eigen naam. **Verwacht:** “Backend Workshop” en “Mijn eerste Kubernetes Deployment!”. De pagina komt uit de ConfigMap.

**Checkpoint 2:** laat weten dat jouw pagina zichtbaar is. Hiermee is stap 1 klaar.

**Vraag:** welke route volgt de browser?  
**Antwoord:** DNS leidt naar de Ingress-controller. De Ingress-regel wijst naar jouw Service en die routeert naar de Pod met nginx. De Deployment beheert de Pod, maar is geen tussenstation in het HTTP-verkeer.

## Als het niet werkt

| Situatie | Controle / antwoord |
| --- | --- |
| YAML-fout bij apply | Controleer spaties, inspringing en bestandsnaam. |
| Pod start niet | Controleer de image en ConfigMap-verwijzing; vraag de begeleider de foutmelding te bekijken. |
| Service ontbreekt | Controleer of je in de eigen map stond en alle vier bestanden hebt opgeslagen/geüpload. |
| Website laadt niet | Controleer hostname, VPN en de Serviceverwijzing in ingress.yaml; de begeleider controleert zo nodig DNS/controller. |
| Standaard nginx-welkomstpagina | Controleer of het volume naar jouw ConfigMap verwijst en op `/usr/share/nginx/html` is gekoppeld. |

Een uitgewerkt voorbeeld staat in [oplossingen/nginx](oplossingen/nginx/). Vergelijk de bestanden; deploy niet allemaal met de gedeelde naam `voorbeeld`.
