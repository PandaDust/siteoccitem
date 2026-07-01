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
index.html            ← structure HTML, data-key sur chaque texte
style.css             ← tout le CSS (variables, layout, animations)
main.js               ← switch langue, scroll reveal, compteurs, nav active
content.json          ← tous les textes FR/EN (seul fichier à éditer pour les textes)
editor.html           ← éditeur visuel de content.json (UI WYSIWYG)
editor_server.py      ← serveur local pour l'éditeur (python editor_server.py → port 8081)
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
  fonts/
    PillGothic-Light.ttf, PillGothic-Light.woff2   ← police auto-hébergée
  logos/
    (14 logos partenaires PNG pour le carrousel #confiance)
```

## Règles de code

### HTML
- Un seul `index.html`, pas de fichiers partiels
- Chaque texte visible porte `data-key="section.cle"` — le contenu est injecté par JS depuis `content.json`
- Sections : `#accueil`, `#apropos`, `#technologie`, `#services`, `#marches`, `#confiance`, `#video`, `#contact`
- `#confiance` = carrousel logos partenaires (assets/logos/)

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
- L'éditeur permet d'éditer les textes FR/EN et de visualiser/remplacer les images (fond hero, logo, photos atelier, cadres technologie, cartes services/marchés, logos partenaires confiance) via upload
- **Important** : à chaque modification du site (nouvelle section, nouveau champ texte dans `content.json`, nouvelle image, renommage/déplacement d'un asset, changement de structure d'une liste), vérifier si `editor.html` doit être mis à jour en conséquence (nouveau champ à éditer, chemin d'image à corriger, etc.) pour qu'il reste synchronisé avec le site réel
- Si un asset est utilisé à plusieurs endroits (ex : une image reprise dans deux sections), préférer des fichiers distincts pour que chaque usage soit modifiable indépendamment depuis l'éditeur

## Langue
- Switch FR/EN dans la nav — bascule via attribut `lang` sur `<html>` et re-render de tous les `[data-key]`
- Langue par défaut : français
- Tout le contenu texte est dans `content.json`, jamais hardcodé dans le HTML

## Ne pas faire
- Ne pas lancer de build ni de serveur — laisser l'utilisateur le faire
- Ne pas introduire de dépendances npm ou bundler (webpack, vite, etc.)
- Ne pas créer de fichiers CSS ou JS supplémentaires — tout dans `style.css` et `main.js`
- Ne pas modifier `_ressources/` — c'est le dossier source original, en lecture seule
