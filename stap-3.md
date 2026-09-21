# Stap 3 — Controleren en verklaren

**Tijd:** circa 2½ minuut. De nginx-opdracht en simulatorbuild zijn klaar.

## Opdracht 1 — Zoek jouw resources

```bash
kubectl -n backend-workshop get pods -o wide
kubectl -n backend-workshop get svc
```

Zoek jouw nginx-Pod en Service. Open ook je nginx-URL in de browser.

**Verwacht:** jouw Pod staat op Running en 1/1 Ready; de Service biedt poort 80 aan; de browser toont HTML uit de ConfigMap.

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
| Wie bouwde de simulatorimage? | De deelnemers; de begeleider gebruikte zijn eigen demo-build. |
| Wie pushte en deployde de simulator? | De begeleider, met zijn eigen Docker Hub-account. |

## Opdracht 3 — Leg de route uit

Vertel in je eigen woorden hoe een browserverzoek jouw nginx-container bereikt.

**Antwoord:** DNS → Ingress-controller → Service → Pod met nginx. De Ingress configureert de route; de Deployment beheert de Pod.

## Optionele afsluitende demo

De begeleider kan één minuut RabbitMQ tonen als ander voorbeeld van een gedeployde applicatie. De bestaande koppeling is vooraf ingericht. Er zijn geen RabbitMQ-opdrachten of experimenten.

De kernopdracht is afgerond: jullie kunnen bestaande images deployen, de route controleren en zelf een image bouwen.
