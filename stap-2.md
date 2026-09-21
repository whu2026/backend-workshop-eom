# Stap 2 — Een simulatorimage bouwen

**Doel:** begrijpen hoe code een image wordt. **Deelnemers bouwen zelf. De begeleider pusht en deployt.**

## 1. Bekijk de code en het bouwrecept

De simulator maakt iedere seconde een JSON-meting en schrijft die naar de logs. Hij biedt HTTP op poort 5000: `/sensor` geeft de laatste meting en `/healthz` de status. Er zit geen RabbitMQ-koppeling in deze oefencode.

De Dockerfile kiest Python als basis, kopieert app.py en start Python. Er zijn geen extra packages nodig; de code gebruikt de standaardbibliotheek.

## 2. Maak een eigen kopie en bouw

De begeleider heeft `~/workshop/simulator` klaargezet. Vervang `wenjie` door jouw naam.

```bash
cd ~/workshop/simulator
mkdir wenjie
cp app.py Dockerfile wenjie/
cd wenjie
docker build -t sensor-simulator:wenjie .
docker images sensor-simulator
```

De centrale code blijft intact. Als je de opdracht herhaalt, ga je naar je bestaande eigen map.

**Verwacht:** de build eindigt zonder fout en de lijst bevat repository `sensor-simulator` met jouw tag. De image-ID kan bij deelnemers gelijk zijn: dezelfde code en basis kunnen dezelfde image opleveren.

**Vraag:** wat is de punt bij docker build?  
**Antwoord:** de huidige map is de buildcontext. Docker vindt daar de Dockerfile en app.py.

**Checkpoint 3:** wijs je eigen image en tag aan. Hiermee is je bouwopdracht afgerond. Je hoeft niet in te loggen op Docker Hub, te pushen of de simulator te deployen.

## 3. Optioneel: kort als container starten

```bash
docker run --rm sensor-simulator:wenjie
```

**Verwacht:** JSON-metingen met `sensor_id`, `timestamp`, `temperature`, `humidity` en `sequence`. Stop na enkele regels met **Ctrl+C**. Door `--rm` wordt de container opgeruimd; de image blijft staan. Er wordt geen serverpoort gepubliceerd, dus deelnemers krijgen geen poortconflict.

**Vraag:** wat is het verschil tussen image en container?  
**Antwoord:** de image is het pakket; de container is een draaiende uitvoering ervan.

## 4. Kijk mee met de begeleidersdemo

De begeleider gebruikt een demo-image van dezelfde code en zijn eigen Docker Hub-account:

1. De lokale demo-image krijgt een repositorynaam en tag.
2. De begeleider pusht de image.
3. De Deployment verwijst naar die gepubliceerde image.
4. De Service biedt poort 80 aan en stuurt naar applicatiepoort 5000.
5. Na apply bekijkt de begeleider Pods en Services.
6. In de browser toont `/sensor` de JSON uit de Kubernetes-Pod.

Je voert deze stappen niet zelf uit tijdens de workshop. Demo-instructies staan apart in [BEGELEIDER.md](BEGELEIDER.md).

**Vraag:** waarom publiceren in een registry?  
**Antwoord:** een lokaal gebouwde image is niet automatisch aanwezig op de Kubernetes-nodes. Die moeten hem kunnen ophalen.

**Vraag:** welke onderdelen herken je van nginx?  
**Antwoord:** Deployment, Pod, Service en Ingress. De image en doelpoort zijn anders.

Stap 2 is klaar. Ga samen door naar [stap 3](stap-3.md).
