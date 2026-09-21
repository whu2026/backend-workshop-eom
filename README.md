# Backendworkshop Kubernetes — new-v4

Van SAS Studio en Visual Analytics naar de backend: wat doet Kubernetes en hoe laat je zelf een applicatie draaien?

## Route van het uur

| Onderdeel | Wie doet het? | Resultaat |
| --- | --- | --- |
| SAS 9, SAS Viya en Kubernetes | Uitleg en live demo | Begrijpen wat achter de schermen draait |
| [Stap 1](stap-1.md): nginx | Deelnemers | Eigen YAML, Pod, Service en website |
| [Stap 2](stap-2.md): simulatorimage | Deelnemers | Zelf gebouwde lokale image |
| Simulator pushen en deployen | Begeleider | Dezelfde code draait in Kubernetes |
| [Stap 3](stap-3.md): controleren en verklaren | Samen | De route kunnen uitleggen |
| RabbitMQ | Optionele demo van één minuut | Een ander voorbeeld van een workload |

De workshop duurt 60 minuten. [Tijdschema en voorbereiding](BEGELEIDER.md).

## Beginnen

Open de handleiding bij de huidige stap. De begeleider zet de map **workshop** vooraf in je thuismap op de workshopserver. Je voert de commando’s daar in Bash uit via MobaXterm/SSH. Op je laptop heb je een browser en eventueel Notepad of VS Code nodig. Gebruik VPN als dat nodig is voor het interne workshopnetwerk.

Iedereen gebruikt namespace **backend-workshop**, maar krijgt een unieke korte naam: kleine letters, cijfers en eventueel een koppelteken. Begin en eindig met een letter of cijfer. Gebruik steeds dezelfde naam; bijvoorbeeld `wenjie`. De punthaken in `<naam>` zijn alleen een invulmarkering en worden niet overgenomen.

Je bewerkt eerst vier YAML-bestanden in jouw eigen map. Je kunt vim gebruiken of de bestanden via SFTP downloaden, lokaal aanpassen en terug uploaden. De oorspronkelijke templates blijven beschikbaar.

## Bestanden

- [NGINX-templates](workshop/nginx/): de vier oorspronkelijke templates met `<naam>`.
- [Voorbeeldoplossing](oplossingen/nginx/): dezelfde templates met naam `voorbeeld`.
- [Simulatorcode](workshop/simulator/): app.py en Dockerfile voor de build.
- [Simulator-deploybestanden](workshop/begeleider/simulator/): alleen voor de begeleidersdemo.
- [GitHub vernieuwen](GITHUB-VERNIEUWEN.md): zelf lokaal uitvoeren.
- [SAS 9 en Viya](SAS-9-EN-VIYA.md) en [bronnen](BRONNEN.md).

Deelnemers hebben geen Docker Hub-account nodig en voeren geen push of simulator-deployment uit. De begeleider gebruikt zijn eigen account. DNS en toegang voor de aangeleverde workshophostnamen worden vooraf geregeld.
