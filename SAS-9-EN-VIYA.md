# SAS 9 en SAS Viya — de kern

Deze vergelijking gaat over SAS 9.4 en het huidige, op Kubernetes gebaseerde SAS Viya-platform.

| Kernwoord | SAS 9 | Huidig SAS Viya |
|---|---|---|
| Omgeving | Traditionele servers | Containers op Kubernetes |
| Levering | Software installeren op servers | Containerimages uitvoeren |
| Beheer | SAS-componenten en serverprocessen | Samenwerkende diensten en Kubernetes-workloads |

## Wat biedt deze aanpak?

- **Gericht beheer:** onderdelen als afzonderlijke workloads beheren; afhankelijkheden blijven bestaan.
- **Schalen:** geschikte workloads extra capaciteit geven.
- **Herstel:** verdwenen beheerde Pods kunnen worden vervangen.
- **Updates:** regelmatig nieuwe Viya-versies; testen en plannen blijven nodig.

## Waarom Kubernetes?

**Starten · herstellen · schalen.** SAS Studio, Visual Analytics, Compute en andere diensten werken samen. Hun containers draaien in Pods. Eén applicatie is niet altijd precies één Pod.

## Live demo — alleen de begeleider

```bash
kubectl -n sasviya4 get deployments
kubectl -n sasviya4 get pods -o wide
```

In de aangeleverde demo stonden onder andere sas-studio en sas-visual-analytics. Controleer de namen en aantallen live; dit is geen actuele clusterinventaris.

| Uitvoer | Betekenis |
|---|---|
| Deployment READY 1/1 | Eén Ready Pod van één gewenste Pod |
| Deployment UP-TO-DATE | Pods met de huidige Podtemplate |
| Deployment AVAILABLE | Beschikbare Pods volgens de beschikbaarheidsinstellingen |
| Deployment AGE | Leeftijd van het object; niet de uptime van de app |
| Pod READY 1/1 | Eén Ready container van één container |
| Pod STATUS / NODE | Toestand en node waarop de Pod draait |

Bronnen: [SAS Viya deploymentproject](https://github.com/sassoftware/viya4-deployment), [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) en de aangeleverde begeleidersslides.
