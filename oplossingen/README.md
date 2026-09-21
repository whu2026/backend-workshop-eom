# Voorbeeldoplossing

[nginx](nginx/) bevat exact de vier deelnemersbestanden, ingevuld met `voorbeeld`. Vergelijk namen, verwijzingen en labels. Deploy niet allemaal met deze naam.

De oorspronkelijke nginx-template is behouden. Alleen de ontbrekende persoonlijke achtervoegsels bij `configMap.name` en de Ingress-Serviceverwijzing zijn hersteld. De vaste naam in de hostname is vervangen door `<naam>`. De image blijft `nginx:latest`; er zijn geen probes, resources of extra labels toegevoegd.

De simulatorbuild heeft geen verplichte codewijzigingen. De Kubernetes-bestanden onder `workshop/begeleider/simulator` zijn voor de begeleidersdemo.
