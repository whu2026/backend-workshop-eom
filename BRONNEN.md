# Achtergrond en bronnen

De inhoud vergelijkt SAS 9.4 met het huidige Kubernetes-gebaseerde SAS Viya-platform. De aangeleverde begeleidersslides zijn gebruikt als inhoudelijke inspiratie. De vergelijking is bewust beperkt tot architectuur en beheer; geen vaste upgrade-, kosten- of beschikbaarheidsgaranties.

- [SAS officiële Viya-deploymentcode](https://github.com/sassoftware/viya4-deployment) — deployment in een bestaande Kubernetes-omgeving; niet nodig om deze workshop uit te voeren.
- [SAS Viya-documentatie](https://support.sas.com/en/software/viya-support.html) — kies de documentatie voor jullie eigen release.
- [Kubernetes-componenten](https://kubernetes.io/docs/concepts/overview/components/).
- [Pods](https://kubernetes.io/docs/concepts/workloads/pods/).
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).
- [Services](https://kubernetes.io/docs/concepts/services-networking/service/).
- [Ingress en controllervereiste](https://kubernetes.io/docs/concepts/services-networking/ingress/).
- [Docker-images](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/).
- [Bouwen, taggen en publiceren](https://docs.docker.com/get-started/docker-concepts/building-images/build-tag-and-publish-an-image/).
- [Officiële nginx-image](https://hub.docker.com/_/nginx).

Een YAML-template is een oefenvoorbeeld. De begeleider controleert imageversies, toegangsrechten, controller, DNS, certificaten, registry en beleid in de echte omgeving vóór de sessie.

- [Kubernetes ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/) — niet-geheime tekst en volumegebruik.
