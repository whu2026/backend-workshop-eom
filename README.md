# Backendworkshop Kubernetes — new-v5

Van SAS Studio en Visual Analytics naar de backend: wat doet Kubernetes en hoe laat je zelf een applicatie draaien?

## Route van het uur

| Onderdeel | Wie doet het? | Resultaat |
| --- | --- | --- |
| SAS 9, SAS Viya en Kubernetes | Uitleg en live demo | Begrijpen wat achter de schermen draait |
| [Stap 1](stap-1.md): nginx | Deelnemers | Eigen YAML, Pod, Service en website |
| [Stap 2](stap-2.md): simulator | Deelnemers | Zelf bouwen en daarna zelf deployen met de beschikbare image |
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
- [Simulatorbestanden](workshop/simulator/): app.py, Dockerfile en drie YAML-templates.
- [Simulatoroplossing](oplossingen/simulator/): ingevulde YAML met voorbeeldnaam en voorbeeldimage.
- [GitHub vernieuwen](GITHUB-VERNIEUWEN.md): zelf lokaal uitvoeren.
- [SAS 9 en Viya](SAS-9-EN-VIYA.md) en [bronnen](BRONNEN.md).

Deelnemers bouwen en deployen zelf, maar hoeven niets naar Docker Hub te pushen en hebben geen Docker Hub-account nodig. De begeleider zorgt vooraf voor een beschikbare image van dezelfde code en geeft de volledige image-naam inclusief tag door. De voorbeeldtag in dit pakket is `whu1/sensor-simulator:workshop-v5`; beschikbaarheid moet vooraf worden geregeld. DNS en toegang voor de nginx- en simulatorhostnamen worden vooraf voorbereid.
