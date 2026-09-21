# Voorbereiding en draaiboek voor de begeleider

## Het uur uitvoerbaar maken

Er is 28 minuten voor de twee opdrachten. Dat werkt alleen met vooraf werkende toegang, gecachte basisimages en een geteste registry-/Ingress-route. Reserveer geen installaties of accountaanmaak tijdens het uur. Laat deelnemers de terminal vóór de start openen. De opdrachten bevatten wachttijd en checkpoints; lange foutanalyse wordt individueel opgepakt.

| Tijd | Doel | Beslismoment |
|---|---|---|
| 0–8 | Koppeling met frontend, SAS 9 versus huidig Viya, live Pods | Maximaal 2 minuten live |
| 8–20 | Cluster, Pod, Deployment, Service, Ingress, ConfigMap | Begrippen aan één schema koppelen |
| 20–34 | Nginx zelf deployen en testen | Minuut 27: Ready; minuut 33: browser |
| 34–40 | Dockerfile, image, container, registry | Geen code schrijven |
| 40–54 | Eigen image bouwen en deployen | Minuut 46: lokaal JSON; minuut 49: push klaar |
| 54–57 | Eindcontrole, drie korte begripsvragen | Iedereen benoemt de route |
| 57–59 | RabbitMQ-demonstratie | Als eerste schrappen bij uitloop |
| 59–60 | Afsluiting | Vraag wat men nu zelf kan |

Als stap 1 tot minuut 37 uitloopt: Docker-uitleg inkorten naar 4 minuten, RabbitMQ weglaten, slotcontrole bewaren. Is bouwen/pushen niet op tijd klaar, geef een vooraf gepushte image zodat deelnemers Deployment, Service en Ingress zelf kunnen afronden. Benoem welke Docker-handeling dan nog geoefend moet worden. Extra proeven uit stap 3 zijn geen verplichte inhoud van dit uur. Bij brede toegangsproblemen is eerst herstel nodig; een volledig praktische workshop is dan niet haalbaar binnen dezelfde tijd.

## 1. Omgeving en gegevens invullen

Maak één geteste trainingsnamespace. Laat een bevoegde beheerder vooraf uitvoeren:

```bash
kubectl config current-context
kubectl create namespace backend-workshop
kubectl get ingressclass
```

Als de namespace al bestaat, niet opnieuw aanmaken of verwijderen. Gebruik geen Viya-productienamespace voor oefeningen. Wijs deelnemers unieke namen toe (`a01`, `a02`, enz.). Zorg op een gedeelde server voor eigen OS-gebruikers of afzonderlijke werkmappen en registry-authenticatie; geen gelijktijdige `docker login`/`logout` in één gedeeld Docker-configbestand.

```bash
cp config/workshop.example.json config/workshop.json
nano config/workshop.json
```

Vul bestaande IngressClass, basisdomein en image-repository in. De twee hosts per persoon zijn `nginx-web-a01.<basisdomein>` en `sim-a01.<basisdomein>`. Leg vooraf DNS vast, bijvoorbeeld een wildcard naar het adres van de bestaande controller. Test vanaf de laptops én workshopserver. Een Ingress resource installeert geen controller en maakt geen DNS-record.

De standaardroute gebruikt HTTP. Als jullie controller HTTPS vereist, zet `tls_secret` op een bestaand Secret in `backend-workshop` met een geldig certificaat voor de hosts. De generator maakt dan TLS-hostregels en `SCHEME=https`. Eventuele controller-specifieke annotaties laat je vóór de workshop toevoegen en testen. Gebruik de door jullie platformteam ondersteunde controller; deze workshop installeert geen Ingress-controller. Kubernetes beveelt voor nieuwe netwerkontwerpen Gateway API aan; hier oefenen we bewust Ingress omdat dat de afgesproken omgeving is.

`image_pull_secret` mag leeg blijven bij openbaar pullbare images; anders geef je een bestaand pull-Secret in dezelfde namespace op. De registry moet bereikbaar zijn voor de buildserver én iedere node, inclusief vertrouwde TLS-certificaten. Gebruik een vooraf toegewezen repository met unieke tags. Deel geen credentials via Git. `config/workshop.json` en werkmappen worden daarom niet gecommit.

## 2. Compatibiliteit en capaciteit vooraf controleren

- Test de nginx-image, Pod Security-regels, quota, NetworkPolicies en poorten. De officiële nginx-image start standaard als root. Als jullie beleid dat blokkeert, gebruik een door het platformteam goedgekeurde nginx-variant met bijbehorende poort/probe/configuratie. Verlaag het clusterbeleid niet voor deze oefening.
- Zorg dat elke deelnemer zijn eigen ConfigMap, Deployment, Service en Ingress kan beheren en Pods/logs kan lezen en `pods/exec` kan gebruiken. Een namespace met standaard RBAC beperkt meestal niet op deelnemerlabels; spreek daarom duidelijk af alleen eigen resources te wijzigen.
- Test desgewenst `kubectl -n backend-workshop auth can-i create deployments`, `... create services`, `... create ingresses.networking.k8s.io`, `... get pods`, `... get pods/log` en `... create pods/exec`; controleer ook get/list/watch/patch/delete voor de gebruikte resources.
- Reserveer capaciteit voor twee Pods per persoon plus tijdelijk extra Pods tijdens rollout. Requests per gewone Pod in deze templates: 50m CPU en 32Mi geheugen; daadwerkelijke ruimte en limieten met jullie cluster valideren.
- Controleer node-architectuur versus buildmachine. Bij verschillende architecturen bouw je vooraf een passende image of gebruik je een ingerichte multi-platform build; introduceer Buildx niet tijdens deze beginnersworkshop.

Haal vooraf op de buildserver `python:3.12-slim` en de gekozen nginx-image op. Doe een complete proefbuild. Het standaardvoorbeeld `nginx:stable-alpine` kan later naar een andere versie wijzen; zet `web_image` voor de echte sessie liefst vast op een geteste digest. Leg ook de gebruikte Python-basisimage/digest vast. Pre-pull of mirror images op de nodes via de bestaande beheerprocedure, niet met deelnemersrechten.

## 3. Volledige proefrun en fallback

Loop stap 1 en 2 exact door met één eigen testnaam en deelnemersrechten. Controleer output én browser via de echte host. Maak vervolgens een vooraf gepushte simulatorimage met bekende tag/digest als fallback. Bewaar de naam buiten de slide in je draaiboek. Verifieer vooraf dat nodes hem zonder extra handelingen kunnen ophalen.

Test de geïsoleerde deelnemersnamen ook met twee accounts tegelijkertijd. Controleer dat Docker-poorten automatisch verschillen en dat tags, resource-namen en hosts uniek zijn. De generator overschrijft geen bestaande werkmap. Maak na een mislukte oefenrun een nieuwe werkmap of bewaar eerst het eerdere werk.

De server van de simulator gebruikt alleen de Python-standaardbibliotheek om afhankelijkheden en buildtijd te beperken. Hij is een leerapp met vluchtig geheugen. Kubernetes geeft zo'n app niet automatisch persistente opslag of productiegeschiktheid.

## 4. Live SAS Viya bekijken — alleen lezen

Vul vooraf de echte Viya-namespace in je terminal in; deel geen configuratie met geheimen:

```bash
VIYA_NS='sasviya4'
kubectl -n "$VIYA_NS" get deployments
kubectl -n "$VIYA_NS" get pods -o wide
kubectl -n "$VIYA_NS" get services
```

Kies vooraf twee of drie herkenbare workloads uit deze installatie. Leg uit welke rol ze hier hebben. De precieze namen en Podaantallen variëren per versie, licentie en configuratie; neem geen fictieve namen over als echte output. Begin met de door jou aangeleverde Deployments sas-studio en sas-visual-analytics. Bij get deployments is READY het aantal Ready Pods / gewenste Pods; UP-TO-DATE telt Pods met de huidige template en AVAILABLE telt beschikbare Pods. AGE is de leeftijd van het object, niet uptime of laatste update. Ga daarna naar get pods: daar telt READY containers en kun je STATUS en NODE aanwijzen. Verklaar tijdelijke compute-Pods alleen als ze daadwerkelijk aanwezig zijn. Bewaar een geschoonde screenshot als de liveverbinding faalt.

SAS 9.4 gebruikt doorgaans een klassieke meerlagenarchitectuur met clients, middentier en server-/metadataservices. Het is niet letterlijk één proces. Met Viya bedoelen we hier het huidige Kubernetes-platform (vaak Viya 4 genoemd), niet alle historische Viya-versies. Apps zoals Studio en VA gebruiken meerdere backenddiensten; CAS en compute hebben eigen uitvoeringsrollen. ESP-inzet hangt van product en architectuur af; claim niet dat elke ESP-instantie in dit cluster staat. Geen algemene belofte van 15-minuten-upgrades, lagere kosten of storingsvrij onafhankelijk schalen.

## 5. RabbitMQ — maximaal twee minuten

Gebruik uitsluitend jouw reeds werkende, vooraf gekoppelde simulator/broker-demo. De deelnemer-simulator in dit pakket heeft geen AMQP-code. Controleer vóór de sessie het juiste scherm en binnenkomende berichten. Bij storing toon je een vooraf gemaakte screenshot en ga je door; geen live RabbitMQ-configuratie.

Spreektekst: “RabbitMQ is een message broker: software die berichten tussen toepassingen doorgeeft en tijdelijk kan bewaren. Ook dit is backendsoftware die je met een passende image en Kubernetes-configuratie kunt uitvoeren. Ik heb deze aparte simulator vooraf gekoppeld; in de beheerinterface zien we nu berichten binnenkomen.”

Wijs eventueel image en Servicepoorten aan, zonder routingsbegrippen te behandelen. Voor productie zijn ook opslag, secrets, herstel en beheer belangrijk; een eenvoudige Deployment alleen is daarvoor niet het hele ontwerp. RabbitMQ is hier alleen een tweede softwarevoorbeeld, geen nieuw leerdoel.

## Aanvulling: nginx met ConfigMap

Reserveer voor de twee SAS-dia’s samen drie minuten. De totale opening plus live demo duurt acht minuten; Kubernetes plus ConfigMap twaalf minuten. Stap 1 blijft minuut 20–34.

Controleer dat deelnemers ConfigMaps mogen maken en lezen. Alle vier nginx-objecten moeten in backend-workshop staan. Geef iedere deelnemer een unieke naam en hostname; bij een gedeeld Linux-account maakt iedere deelnemer een eigen map `~/workshop/<naam>/nginx`. De werkmapgenerator blijft optioneel als jij vooraf ingevulde bestanden uitdeelt. Hij maakt geen Kubernetes-objecten.

De nginx-host wordt `nginx-web-<naam>.<base_domain>`. Gebruik de bestaande ingressClassName alleen als die in deze cluster bestaat; de naam nginx is een klasse, geen opdracht om een controller te installeren. Zet eigen interne domeinen in de lokale config, niet in de te publiceren voorbeeldconfig.

De deelnemers vullen alle vier YAML-bestanden in voordat ze vanuit hun eigen nginx-map `kubectl -n backend-workshop apply -f .` uitvoeren. De map bevat geen oude of andermans YAML. Een kortstondig ontbrekende ConfigMap tijdens het aanmaken kan herstellen zodra het object bestaat; blijvende FailedMount-events vragen controle van naam en namespace.

Jouw oorspronkelijke voorbeeld gebruikt nginx:latest. Het pakket houdt nginx:stable-alpine aan voor de bestaande wget-controle. Kies vooraf één geteste image/tag of digest en controleer of de HTTP-client beschikbaar is. Ga bij een andere variant niet uit van dezelfde ingebouwde tools.

Test dat de browser Backend Workshop en de eigen deelnemersnaam laat zien. De ConfigMap-mount bedekt de standaard nginx-HTML-map. Plan een extra HTML-wijziging alleen bij tijd over; volumeverversing kan vertragen en veroorzaakt op zichzelf geen rollout.
