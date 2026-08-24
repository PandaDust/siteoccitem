# CLAUDE.md — Site OCCITEM Electrical Motors

## Contexte projet
Site vitrine one-page B2B pour OCCITEM, fabricant de moteurs électriques haute performance (Colomiers, 31).  
Spec complète : voir `SPEC.md`.

## Stack
- HTML5 + CSS3 + JS vanilla — aucun framework, aucune librairie externe
- Contenu textuel centralisé dans `content.json` (FR + EN)
- Icônes : Lucide Icons via CDN
- Polices : Exo 2 + Inter via Google Fonts + PillGothic-Light (auto-hébergée dans `assets/fonts/`)

## Structure des fichiers
```
index.html            ← page principale, data-key sur chaque texte
carriere.html         ← page des offres d'emploi (liste rendue par main.js)
style.css             ← tout le CSS (variables, layout, animations)
main.js               ← switch langue, scroll reveal, compteurs, nav active, offres
content.json          ← tous les textes FR/EN (seul fichier à éditer pour les textes)
careers.json          ← offres d'emploi + intro RH (édité via career-admin.html)
editor.html           ← éditeur visuel de content.json + gestion des comptes
career-admin.html     ← mini-éditeur RH des offres (careers.json)
editor_server.py      ← serveur des deux éditeurs (python editor_server.py → port 8081)
assets/
  logo-blanc.png
  hero-bg.jpg
  locaux.jpg
  video.mp4
  rotor.png
  atelier-1.png, atelier-2.png
  bobinage-comparaison.png, tech-upin.jpg
  marche-aero.png, marche-marine.png, marche-pod.png, marche-terrestre.png
  service-concevoir.png, service-fabriquer.png, service-prototyper.png
  careers-intro.png                                ← visuel d'intro page carrières
  fonts/
    PillGothic-Light.ttf, PillGothic-Light.woff2   ← police auto-hébergée
  logos/
    (logos partenaires PNG pour le carrousel #confiance)
```

Non versionnés (voir `.gitignore`) : `_ressources/`, les `*.bak` créés à chaque
enregistrement, `git-sync.log`, et `users.json` — ce dernier contient des
empreintes de mots de passe et ne doit jamais entrer dans le dépôt. `stats.json`
(compteur de visites, voir « Compteur de visites ») est exclu pour une raison
différente : il change à chaque visite et spammerait l'historique git.

## Règles de code

### HTML
- Deux pages seulement : `index.html` (one-page) et `carriere.html` (offres d'emploi). Pas de fichiers partiels.
- Chaque texte visible porte `data-key="section.cle"` — le contenu est injecté par JS depuis `content.json`
- Sections d'`index.html` : `#accueil`, `#apropos`, `#histoire`, `#technologie`, `#services`, `#marches`, `#confiance`, `#soutiens`, `#video`, `#contact`
- `#confiance` = carrousel logos partenaires (assets/logos/)
- Le lien « Carrières » de la nav est le seul lien sortant de la one-page ; son affichage dépend de `careers.nav_enabled`, et la page elle-même (accès direct par URL compris) peut être coupée via `careers.page_enabled` (voir « Langue »)

### CSS
- Variables CSS dans `:root` pour toutes les couleurs et espacements
- Couleurs principales :
  - `--color-bg: #0d1b2a`
  - `--color-accent: #cc3517`
  - `--color-blue: #104766`
  - `--color-text: #ffffff`
  - `--color-muted: #a0aec0`
- Mobile-first — breakpoints : 768px (tablette), 1024px (desktop)
- Pas de `!important`

### JS
- Pas de framework, pas de jQuery
- `content.json` chargé via `fetch()` au démarrage — remplit tous les `[data-key]`
- `IntersectionObserver` pour : scroll reveal + nav active + déclenchement des compteurs
- Scroll reveal : `opacity: 0; transform: translateY(30px)` → `opacity: 1; transform: none` en `0.6s ease-out`
- Cascade décalée dans une section : `transitionDelay` de 0 à N×100ms selon l'index de l'élément

## Design
- Style : dark tech industrial, fidèle à la plaquette commerciale
- Hover cartes : `translateY(-6px)` + bordure basse `--color-accent` en `0.25s`
- Compteurs animés : sections Technologie uniquement, valeurs issues de `content.json`
- Navigation : lien actif coloré en `--color-accent` via IntersectionObserver sur chaque section

## Éditeur de contenu
- `editor.html` + `editor_server.py` forment un éditeur visuel local (WYSIWYG) pour `content.json` et les images du site — voir `python editor_server.py` (port 8081)
- `career-admin.html`, servi par le même serveur, édite `careers.json` (offres d'emploi). Destiné au client, avec des identifiants distincts de ceux de l'éditeur principal.
- L'éditeur permet d'éditer les textes FR/EN et de visualiser/remplacer les images (fond hero, logo, photos atelier, cadres technologie, cartes services/marchés, logos partenaires confiance) via upload
- **Important** : à chaque modification du site (nouvelle section, nouveau champ texte dans `content.json`, nouvelle image, renommage/déplacement d'un asset, changement de structure d'une liste), vérifier si `editor.html` doit être mis à jour en conséquence (nouveau champ à éditer, chemin d'image à corriger, etc.) pour qu'il reste synchronisé avec le site réel
- Si un asset est utilisé à plusieurs endroits (ex : une image reprise dans deux sections), préférer des fichiers distincts pour que chaque usage soit modifiable indépendamment depuis l'éditeur
- Les chemins d'API des éditeurs sont **relatifs** (`api/save`, pas `/api/save`) : en production ils sont servis sous `/admin/`, et un chemin absolu partirait à la racine du domaine, hors du bloc proxy.

### Comptes et permissions
- **Compte maître** : `AUTH_USER` / `AUTH_PASS` (variables d'environnement). Toujours administrateur, accès complet, non supprimable. Il ne figure pas dans `users.json`, pour qu'un fichier corrompu ou vidé ne puisse jamais verrouiller l'accès à l'éditeur.
- **Comptes créés** depuis la section « Comptes d'accès » d'`editor.html` : deux accès indépendants (`content`, `careers`) et un indicateur `admin` qui autorise la gestion des comptes. Stockés dans le fichier désigné par `USERS_FILE`, en PBKDF2-HMAC-SHA256.
- `RH_AUTH_USER` / `RH_AUTH_PASS` : compte RH hérité, conservé pour compatibilité. Supprimable une fois un vrai compte RH créé.
- Basic Auth réémettant les identifiants à chaque requête, `editor_server.py` met en cache le résultat de l'authentification (TTL 5 min) : sans ce cache, chaque requête relancerait une dérivation de ~300 ms. Un changement de mot de passe exige donc un redémarrage du service pour prendre effet immédiatement.
- Sans `AUTH_USER`/`AUTH_PASS`, l'éditeur reste **ouvert sans authentification** (usage local). Ne jamais exposer le serveur sans ces variables.

### Compteur de visites
- `main.js` appelle `POST /admin/api/hit` (sans identifiants, sans cookie) à chaque chargement d'`index.html` — pas `carriere.html`, repéré via l'absence de `#careersGrid`. Échec ignoré silencieusement : un compteur en panne ne doit jamais gêner l'affichage du site.
- Comptage agrégé pur (total + par jour), aucun identifiant de visiteur stocké : ne nécessite pas de bandeau de consentement RGPD, mais ne distingue pas non plus les visiteurs uniques des rechargements de page.
- Chemin backend canonique : `/api/hit` (comme les autres routes d'API, sans préfixe `/admin/`, celui-ci étant retiré par le proxy nginx en production). `/admin/api/hit` est accepté en alias uniquement pour qu'`editor_server.py` réponde aussi en test local, où il sert tout le site à la racine sans passer par nginx.
- Stocké dans le fichier désigné par `STATS_FILE` (par défaut `stats.json` à la racine du dépôt — voir « Non versionnés »).
- Visible dans `editor.html` (section « Statistiques de visites », réservée aux comptes `admin`) via `GET /api/stats`, qui renvoie le total et les 30 derniers jours.

## Déploiement (VPS)
Le site est servi par nginx **directement depuis un clone git**, ce qui rend la
synchronisation bidirectionnelle : les éditeurs écrivent dans le clone, et leurs
modifications remontent sur GitHub.

```
GitHub (PandaDust/siteoccitem, branche master)
   ↓ cron */2 : auto-deploy.sh (pull --rebase)      ↑ commit + push à chaque enregistrement
/opt/occitem/site        ← clone git = racine web servie par nginx
```

Hôte : VPS Oracle Cloud x86 (Ubuntu 24.04 Minimal, shape `VM.Standard.E2.1.Micro`,
Always Free), accès SSH `occitem-vps`, IP réservée `82.70.250.62` — une IP
réservée reste attachée à l'instance même après un arrêt/redémarrage côté
Oracle, contrairement à une IP éphémère qui peut changer. Domaine `occitem.com`
/ `www.occitem.com`, HTTPS via certbot (Let's Encrypt, renouvellement
automatique, plugin nginx). VPS dédié uniquement au site occitem.

Avant migration (jusqu'à fin août 2026), le site tournait sur le VPS ARM
`qualityhub-vps` (129.151.226.11, partagé avec QualityHub) — entièrement
décommissionné depuis : compte `occitem`, vhost nginx et clone git supprimés.
Ne pas y chercher de trace du site.

Éditeurs en production : `/admin/editor.html` et `/admin/career-admin.html`.
Les identifiants vivent uniquement dans `/etc/occitem/editor.env` sur le VPS —
ne jamais les écrire dans le dépôt.

- **nginx** : vhost `occitem`. Sert le site en public et proxifie `/admin/` vers `127.0.0.1:8081`.
  Le bloc `/admin/` doit rester en `location ^~` : sans le `^~`, les `location` regex
  (`\.json$`, images) l'emportent sur le préfixe et nginx cherche les fichiers dans
  `<racine>/admin/`, qui n'existe pas — les éditeurs s'ouvrent alors sans aucune donnée.
- **Blocages** : `/.git`, `*.py`, `*.bak`, `_ressources` renvoient 404, sur le vhost public
  **et** dans le bloc `/admin/`. Le second n'est pas redondant : `_check_auth` laisse passer
  sans authentification tout chemin absent de ses listes, donc `/admin/.git/config` fuiterait
  le dépôt entier sans lui.
- **Service** : `occitem-editor.service` (utilisateur `occitem`), variables dans
  `/etc/occitem/editor.env`, comptes dans `/var/lib/occitem/users.json`, compteur de
  visites dans `/var/lib/occitem/stats.json` (variable `STATS_FILE`).
  `GIT_AUTO_SYNC=1` n'y est posé qu'en production — en local les commits restent manuels.
- **auto-deploy.sh** (cron `*/2`) : commite les résidus, `pull --rebase`, puis pousse les
  commits en attente. Il annule le rebase en cas de conflit plutôt que de laisser le dépôt
  à moitié rebasé, et redémarre le service si `editor_server.py` a changé.
- Toute modification poussée sur `master` part en production dans les 2 minutes.
  Il n'y a pas d'environnement de préproduction.

## Langue
- Switch FR/EN dans la nav — bascule via attribut `lang` sur `<html>` et re-render de tous les `[data-key]`
- Langue par défaut : français
- Tout le contenu texte est dans `content.json`, jamais hardcodé dans le HTML
- Structure : `section.<lang>.<clé>`. Les **réglages non linguistiques** se placent à côté
  de `fr`/`en`, jamais dedans — par exemple `careers.nav_enabled` (affichage du lien
  « Carrières » dans le menu) et `careers.page_enabled` (la page elle-même). Dupliqués par
  langue, de tels réglages autoriseraient des états contradictoires entre FR et EN sans que
  rien ne le signale dans l'éditeur. `getVal`/`setVal` d'`editor.html` insèrent toujours la
  langue courante : ces réglages s'écrivent donc directement sur `data.<section>.<clé>`.
- Un réglage absent de `content.json` doit valoir « activé » : un déploiement antérieur à
  son introduction ne doit pas faire disparaître d'élément du site.
- `careers.page_enabled` à `false` : `carriere.html` redirige tout visiteur vers l'accueil
  (vérifié côté client, dans `main.js`, avant tout rendu). `carriere.html?apercu=1` contourne
  la redirection pour prévisualiser la page pendant qu'elle est coupée au public (bandeau
  d'avertissement affiché) — utile pendant la construction d'une nouvelle campagne avec le
  service RH. `editor.html` affiche un lien direct vers cet aperçu quand la case est décochée.

## Ne pas faire
- Ne pas lancer de build ni de serveur — laisser l'utilisateur le faire
- Ne pas introduire de dépendances npm ou bundler (webpack, vite, etc.)
- Ne pas créer de fichiers CSS ou JS supplémentaires — tout dans `style.css` et `main.js`
- Ne pas modifier `_ressources/` — c'est le dossier source original, en lecture seule
- Ne pas versionner `users.json` ni le placer dans la racine web : il contient des
  empreintes de mots de passe, partirait sur GitHub au premier enregistrement et serait
  écrasé à chaque déploiement
- Ne pas tester les routes d'écriture (`/api/save`, `/api/save-careers`) avec un corps
  partiel : elles remplacent le fichier entier, et un `{}` vide le contenu du site — puis
  le commit automatique le pousse sur GitHub. Toujours renvoyer le JSON complet, modifié.
- Ne pas utiliser de chemins d'API absolus dans les éditeurs (voir « Éditeur de contenu »)
