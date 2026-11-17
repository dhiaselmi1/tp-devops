# Rendu — TP guidés DevOps (tp-devops)

Dépôt fil rouge : API Catalogue (FastAPI). Ce document regroupe les livrables des TP 1, 2 et 3.

## TP 1 — Pipeline CI/CD avec GitHub Actions

**Livrable 1 — pipeline en succès (8 tests + flake8 verts)** : voir `preuves-tp1-succes.txt`
(commit `6efbcfe` « Correction du taux de TVA »), 8 passed, couverture 96 %.

**Livrable 2 — pipeline en échec** : voir `preuves-tp1-echec.txt`
(commit `0b42b58` « Mise à jour du taux de TVA »). 3 tests échouent :
`assert 18.0 == 19.0`, `assert 236.0 == 238.0`, `assert 59.0 == 59.5`.

**Livrable 3 — `.github/workflows/ci.yml` final commenté** : voir le fichier dans le dépôt.
Historique Git : vert (`2ff8ae7`) → rouge (`0b42b58`) → vert (`6efbcfe`), exactement la séquence
attendue par le TP (étape 3).

**Livrable 4 — Réponses aux questions de compréhension**

1. Un **job** est un ensemble de *steps* exécutés sur une même machine (runner) ; les steps d'un
   job partagent le système de fichiers, alors que deux jobs tournent sur deux machines distinctes
   et ne partagent rien par défaut. Sans `needs: test`, les jobs `test` et `deploy` démarreraient
   en parallèle : on pourrait déployer du code dont les tests n'ont pas encore (ou pas) réussi.
2. Le déploiement vers `staging` est automatique (dès que les tests passent sur `main`) : c'est du
   **Continuous Delivery**, pas encore du Continuous Deployment, car il n'y a pas de mise en
   production automatique. Pour passer au Continuous Deployment, il faudrait ajouter un job
   `production` qui s'enchaîne automatiquement après `staging` sans intervention humaine
   (aujourd'hui, un job `production` existerait plutôt avec un `environment` à approbation manuelle,
   ce qui resterait du Delivery).
3. En YAML, `3.11` sans guillemets serait interprété comme un nombre flottant et donc lu `3.1` (le
   deuxième zéro est perdu) ; entouré de guillemets, c'est une chaîne de caractères, interprétée
   correctement par `actions/setup-python`. Même piège avec `3.10` ou `3.20`.
4. L'étape 3 (détection immédiate d'une régression avant la mise en production) améliore surtout le
   **Change Failure Rate** (le déploiement défectueux est bloqué avant d'atteindre `staging`) et le
   **Lead Time for Changes** (retour en moins d'une minute au lieu d'un bug découvert plus tard,
   voire en production).
5. Écrire un secret en clair dans `ci.yml` l'expose définitivement : le dépôt (et tout son
   historique Git) reste lisible par quiconque y a accès, même après suppression ultérieure de la
   ligne. La bonne pratique est de déclarer le secret dans *Settings › Secrets and variables ›
   Actions* et de l'utiliser via `${{ secrets.NOM_DU_SECRET }}` : GitHub le masque (`***`) dans les
   journaux et ne l'affiche jamais en clair.

## TP 2 — Conteneurisation avec Docker

**Livrable 1** : `Dockerfile` et `.dockerignore` commentés (dans le dépôt).

**Livrable 2** : `docker-compose.yml` (dans le dépôt).

**Livrable 3 — API + base fonctionnant ensemble** :
```
$ docker compose ps
NAME              IMAGE         STATUS                    PORTS
tp-devops-api-1   tp-api:1.0    Up (healthy dependency)   0.0.0.0:8000->8000/tcp
tp-devops-db-1    postgres:15   Up (healthy)              5432/tcp

$ curl http://localhost:8000/produits
[{"id":1,"nom":"Clavier","prix_ht":50.0,"prix_ttc":59.5,"stock":3}]

$ docker exec tp-devops-db-1 psql -U user -d appdb -c "SELECT * FROM produits;"
 id |   nom   | prix_ht | stock
----+---------+---------+-------
  1 | Clavier |      50 |     3
```
Persistance vérifiée : après `docker compose down` (sans `-v`) puis `docker compose up -d`, le
produit « Clavier » est toujours présent dans `GET /produits`. Après `docker compose down -v`, le
volume `db_data` est supprimé.

**Livrable 4 — Réponses aux questions de compréhension**

1. `docker stop` arrête le conteneur (il existe toujours, visible avec `docker ps -a`) ;
   `docker rm` supprime le conteneur arrêté ; `docker rmi` supprime l'image (impossible tant
   qu'un conteneur l'utilise encore).
2. `COPY requirements.txt .` est placé avant `COPY . .` pour profiter du cache de couches Docker :
   tant que `requirements.txt` ne change pas, la couche contenant `pip install` est réutilisée telle
   quelle, et seule la couche du code applicatif est reconstruite. Dans l'ordre inverse, la moindre
   modification du code invaliderait le cache et relancerait l'installation complète des dépendances.
3. Les deux conteneurs sont isolés mais reliés par le réseau privé `tp-devops_default` créé par
   Compose. L'API trouve la base via le nom du service (`db`) : le DNS interne de Docker résout ce
   nom en l'adresse IP du conteneur de la base (`DATABASE_URL=postgresql://user:pass@db:5432/appdb`).
4. Après `docker compose down`, les conteneurs et le réseau sont supprimés mais le volume nommé
   `db_data` est conservé : les données sont retrouvées au prochain `up`. Après
   `docker compose down -v`, le volume est aussi supprimé : les données sont définitivement perdues.
5. Deux différences avec une machine virtuelle (séance 6) : (a) le conteneur partage le noyau Linux
   de l'hôte alors qu'une VM embarque un système d'exploitation complet avec son propre noyau ;
   (b) le conteneur démarre en une seconde et pèse quelques centaines de Mo, contre une à deux
   minutes et plusieurs Go pour une VM.

## TP 3 — Déploiement sur Kubernetes avec Minikube

**Livrable 1** : `k8s/deployment.yaml` commenté (dans le dépôt).

**Livrable 2 — auto-réparation (preuve réelle, cluster Minikube local)** :
```
$ kubectl get pods
NAME                      READY   STATUS    RESTARTS   AGE
tp-api-55bf9cc56d-brmwk   1/1     Running   0          35s
tp-api-55bf9cc56d-r64lh   1/1     Running   0          35s
tp-api-55bf9cc56d-tggbm   1/1     Running   0          35s

$ kubectl delete pod tp-api-55bf9cc56d-brmwk
pod "tp-api-55bf9cc56d-brmwk" deleted

$ kubectl get pods       # quelques secondes plus tard
NAME                      READY   STATUS    RESTARTS   AGE
tp-api-55bf9cc56d-4lmjx   1/1     Running   0          10s   <- nouveau pod recréé automatiquement
tp-api-55bf9cc56d-r64lh   1/1     Running   0          41s
tp-api-55bf9cc56d-tggbm   1/1     Running   0          41s

$ kubectl describe deployment tp-api | grep -A3 Events:
Events:
  Type    Reason             Age   From                   Message
  Normal  ScalingReplicaSet  41s   deployment-controller  Scaled up replica set tp-api-55bf9cc56d from 0 to 3
```

**Livrable 3 — mise à l'échelle à 5 réplicas** :
```
$ kubectl scale deployment tp-api --replicas=5
deployment.apps/tp-api scaled

$ kubectl get pods
NAME                      READY   STATUS    RESTARTS   AGE
tp-api-55bf9cc56d-4lmjx   1/1     Running   0          20s
tp-api-55bf9cc56d-9v8xz   1/1     Running   0          6s
tp-api-55bf9cc56d-bpv7r   1/1     Running   0          6s
tp-api-55bf9cc56d-r64lh   1/1     Running   0          51s
tp-api-55bf9cc56d-tggbm   1/1     Running   0          51s
```

**Bonus réalisés** : rolling update (`APP_VERSION=2.0.0`) suivi d'un `kubectl rollout undo`
(retour à la révision 1, succès confirmé par `deployment "tp-api" successfully rolled out`), et
Horizontal Pod Autoscaler (`kubectl autoscale --cpu-percent=70 --min=2 --max=10`, addon
`metrics-server` activé).

Répartition de charge observée via `minikube service tp-api-service --url` : six requêtes
successives sur `/` renvoient des champs `hote` différents (`brmwk`, `r64lh`, `tggbm`), confirmant
que le Service répartit le trafic entre les pods.

**Livrable 4 — Réponses aux questions de compréhension**

1. Le contrôleur du Deployment, via son ReplicaSet, a recréé le pod supprimé : il observe en
   permanence l'état réel (2 pods) par rapport à l'état désiré (3 pods déclarés dans
   `spec.replicas`) et corrige l'écart. Kubernetes est dit « déclaratif » parce qu'on décrit le
   résultat voulu (« il doit toujours y avoir 3 pods de cette image »), pas la suite d'actions à
   exécuter ; la boucle de réconciliation se charge d'atteindre et de maintenir cet état.
2. Le `selector` du Deployment indique quels pods lui appartiennent (ceux dont les labels
   correspondent). S'il ne correspond pas aux labels du `template`, `kubectl apply` est refusé
   (« selector does not match template labels »). Un Service dont le selector est erroné, en
   revanche, est accepté mais n'a aucun endpoint et ne répond à aucune requête.
3. `EXTERNAL-IP` reste `<pending>` sur Minikube car le type `LoadBalancer` demande normalement à un
   fournisseur cloud (GCP, AWS, Azure) de provisionner un répartiteur de charge public. Minikube
   tourne en local sans fournisseur cloud : personne n'attribue d'IP externe. Sur GKE/EKS/AKS, le
   cloud provider répond automatiquement à cette demande et affecte une IP publique réelle.
4. `readinessProbe` répond à « ce pod peut-il recevoir du trafic maintenant ? » : s'il échoue, le
   pod est simplement retiré de la liste des endpoints du Service, sans redémarrage.
   `livenessProbe` répond à « le conteneur est-il encore vivant ? » : s'il échoue, Kubernetes
   redémarre le conteneur.
5. `kubectl set env` déclenche un **rolling update** : les pods sont remplacés progressivement,
   sans interruption de service. Son principal inconvénient est que, pendant la transition, les
   versions 1 et 2 cohabitent (ce qui peut poser problème si elles ne sont pas compatibles côté
   client ou base de données), et qu'un retour arrière n'est pas instantané : il refait lui-même un
   rolling update vers l'ancienne révision.
6. Pour relier ce TP au job `deploy` du TP 1 et obtenir un vrai pipeline CI/CD : le job `deploy`
   construirait l'image avec le tag du commit (`${{ github.sha }}`), la pousserait vers un registre
   (ghcr.io ou Docker Hub), puis exécuterait
   `kubectl set image deployment/tp-api tp-api=ghcr.io/<compte>/tp-api:<sha>` en utilisant un
   kubeconfig stocké dans les secrets GitHub — remplaçant ainsi le simple `echo` de simulation par
   un déploiement réel, déclenché automatiquement si les tests du job `test` réussissent.
