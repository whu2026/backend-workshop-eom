# Voorbeeldoplossing

[nginx](nginx/) bevat exact de vier deelnemersbestanden, ingevuld met `voorbeeld`. Vergelijk namen, verwijzingen en labels. Deploy niet allemaal met deze naam.

De oorspronkelijke nginx-template is behouden. Alleen de ontbrekende persoonlijke achtervoegsels bij `configMap.name` en de Ingress-Serviceverwijzing zijn hersteld. De vaste naam in de hostname is vervangen door `<naam>`. De image blijft `nginx:latest`; er zijn geen probes, resources of extra labels toegevoegd.

[simulator](simulator/) bevat de drie deelnemerstemplates ingevuld met naam `voorbeeld` en voorbeeldimage `whu1/sensor-simulator:workshop-v5`. De begeleider moet die tag vooraf beschikbaar maken of vervangen door de definitieve image. Gebruik je eigen naam bij het deployen.

De simulatorbuild vereist geen codewijzigingen. Deelnemers bouwen lokaal, vullen vervolgens de beschikbare registry-image in hun Deployment in en deployen zelf. Niemand hoeft tijdens de workshop een image te pushen.
