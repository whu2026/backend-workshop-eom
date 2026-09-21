# Voorbeeldoplossing

De mappen [stap-1](stap-1) en [stap-2](stap-2) bevatten volledig ingevulde YAML voor deelnemer `voorbeeld`. Hosts onder `workshop.example.com` en de registry onder `registry.example.com` zijn voorbeelden, geen werkende infrastructuur. De IngressClass `voorbeeld-class` is ook fictief. Pas deze bestanden niet rechtstreeks toe in jouw cluster.

Een oplossing met de echte, vooraf ingevulde workshopconfiguratie maak je zo vanaf de repositorymap:

```bash
python3 tools/maak_werkmap.py a01 --oplossing --output werk/oplossing-a01
```

De generator maakt alleen bestanden. Vergelijk ze met jouw eigen YAML; apply niet blind een hele oplossing als je nog met de oefening bezig bent. In de simulator-Deployment moet jouw image eerst naar de registry gepusht zijn.

## Waarop letten bij de vergelijking?

1. Deploymentselector en Podtemplate gebruiken consequent `app: nginx-demo-a01` of `sim-a01`.
2. De Service-selector heeft precies diezelfde waarde.
3. De Service biedt poort 80 aan. De benoemde doelpoort `http` verwijst naar 80 voor nginx of 5000 voor de simulator.
4. Ingress verwijst naar de Servicenaam en Servicepoort 80.
5. Image inclusief tag en host zijn jouw eigen waarden; geen schema of pad in `host`.
6. Namespace is `backend-workshop`; `workshop-owner` maakt jouw objecten terugvindbaar.

**Eindantwoord:** beide applicaties worden door dezelfde Kubernetes-bouwstenen uitgevoerd en bereikbaar gemaakt. Het verschil zit in de image en de applicatie-instellingen, waaronder de doelpoort en healthcheck. Bij een andere image controleer je ook configuratie, opslag en rechten.

## Extra controle voor de nginx-pagina

- ConfigMap `nginx-demo-html-voorbeeld` bevat een echte `index.html`, zonder backslashes voor HTML-tags.
- Deployment `nginx-demo-deployment-voorbeeld` verwijst met `volumes[].configMap.name` naar diezelfde ConfigMap.
- `volumeMounts` maakt het bestand leesbaar onder `/usr/share/nginx/html`.
- Service `nginx-demo-service-voorbeeld` selecteert uitsluitend `app: nginx-demo-voorbeeld`.
- Ingress `nginx-demo-ingress-voorbeeld` verwijst naar die Service.
- Alle vier objecten staan in `backend-workshop`. De bestandsnamen hoeven niet gelijk te zijn aan de objectnamen.

Een gegenereerde werkmap heeft `nginx/` voor stap 1 en `stap-2/` voor de simulator. De voorbeeldoplossingen hier blijven per stap geordend.
