# Stap 3 — Controleren en verklaren

**Tijd:** circa 2½ minuut. De nginx-opdracht, simulatorbuild en simulator-deployment zijn klaar.

## Opdracht 1 — Zoek jouw resources

```bash
kubectl -n backend-workshop get pods -o wide
kubectl -n backend-workshop get svc
```

Zoek jouw nginx-Pod en simulator-Pod en hun Services. Open zowel de nginx-URL als de simulator-URL met `/sensor` in de browser.

**Verwacht:** beide Pods staan op Running en 1/1 Ready. Beide Services bieden poort 80 aan. De nginx-website toont HTML; de simulator-URL toont JSON.

**Antwoord:** de Podstatus laat zien dat de container draait en Ready is. Het bestaan van de Service bewijst nog niet dat de volledige website werkt. Daarvoor bekijken we de browser.

## Opdracht 2 — Benoem de rollen

| Vraag | Antwoord |
| --- | --- |
| Wat is een image? | Het pakket waaruit een container wordt gestart. |
| Wat is een Pod? | Een Kubernetes-eenheid met één of meer containers; hier één. |
| Wat beheert de gewenste uitvoering? | De Deployment, via een ReplicaSet. |
| Wat vindt de juiste Pods? | De selector van de Service die bij de Podlabels past. |
| Wat koppelt hostname en pad aan een Service? | De Ingress-regel, uitgevoerd door de Ingress-controller. |
| Waar staat de nginx-HTML? | In de ConfigMap, als bestand beschikbaar in de container. |
| Wie bouwde lokaal een simulatorimage? | Iedere deelnemer. |
| Welke image gebruiken de simulator-Pods? | De vooraf beschikbare registry-image van dezelfde code. |
| Wie publiceerde die image? | De begeleider vooraf. Deelnemers pushen niets. |
| Wie deployde de simulator? | Iedere deelnemer in een eigen Deployment. |

## Opdracht 3 — Leg de route uit

Vertel in je eigen woorden hoe een browserverzoek jouw nginx-container bereikt.

**Antwoord:** DNS → Ingress-controller → Service → Pod met nginx. De Ingress configureert de route; de Deployment beheert de Pod.

## Optionele afsluitende demo

De begeleider kan één minuut RabbitMQ tonen als ander voorbeeld van een gedeployde applicatie. De bestaande koppeling is vooraf ingericht. Er zijn geen RabbitMQ-opdrachten of experimenten.

De kernopdracht is afgerond: jullie kunnen bestaande images deployen, de route controleren en zelf een image bouwen.
