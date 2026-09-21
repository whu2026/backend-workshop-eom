# GitHub vernieuwen met new-v1

Deze instructies bewaren de Git-geschiedenis. Maak geen nieuwe lege repository en verwijder de `.git`-map niet. Het pakket bevat de volledige nieuwe deelnemersroute. PowerPoint en spreektekst kun je eventueel apart in `presentatie/` toevoegen.

## 1. Bestaande repository ophalen

Gebruik Git Bash op Windows of Bash op Linux. Werk in een nieuwe map buiten je oude lokale workshopmap:

```bash
git clone https://github.com/whu2026/backend-workshop-eom.git backend-workshop-eom-new-v1
cd backend-workshop-eom-new-v1
git switch -c workshop-new-v1
git status
```

Ontbreekt Git op Windows, installeer eerst Git for Windows en open daarna een nieuwe Git Bash-terminal. Laat Git via de browser authenticeren. Bewaar eigen lokale wijzigingen eerst voordat je een bestaande checkout gebruikt.

## 2. Oude deelnemersinhoud vervangen

Bekijk eerst welke bestanden Git volgt:

```bash
git ls-files
```

Verwijder alleen bestaande, verouderde workshopmappen/bestanden die je wilt vervangen. Onderstaande namen omvatten de eerdere indelingen; ontbrekende namen worden overgeslagen. De andere repositorybestanden blijven behouden:

```bash
git rm -r --ignore-unmatch 01-simulator 02-rabbitmq 03-experimenten stap-1 stap-2 stap-3.md stap-1.md stap-2.md README.md
```

Pak de nieuwe ZIP uit **buiten** deze Git-map. Kopieer de inhoud van de uitgepakte map `backend-workshop-eom` naar deze checkout. Kopieer niet een extra bovenliggende map mee. Neem ook de meegeleverde `.gitignore` over, of voeg de regels toe als je al eigen regels hebt. Kopieer nooit een oude `.git`-map, echte credentials of lokaal `config/workshop.json`.

## 3. Controleren, committen en uploaden

```bash
git add .
git status
git diff --cached --stat
git diff --cached -- README.md stap-1.md stap-2.md stap-3.md
```

Controleer dat de nieuwe route en templates aanwezig zijn en geen secrets, werkmappen of oude RabbitMQ-oefeningen meekomen. Bekijk ook eventuele andere wijzigingen met `git diff --cached`.

```bash
git commit -m "Vernieuw workshop met Kubernetes als hoofdonderwerp"
git push -u origin workshop-new-v1
```

Open op GitHub de voorgestelde pull request van `workshop-new-v1` naar de standaardbranch (meestal `main`). Bekijk de wijzigingen, merge de pull request en controleer de README-links. Dit is gewone versiecontrole; een force-push of het wissen van de repository is niet nodig.

## 4. Eén vaste download voor deelnemers

Maak na je proefrun op GitHub een release met een nieuwe tag `workshop-new-v1` op de bijgewerkte standaardbranch. Deel de release-URL. Deelnemers downloaden daar de broncode-ZIP, zodat iedereen dezelfde versie gebruikt. De lokale, door jou ingevulde workshopconfiguratie verspreid je via de workshopserver.
