# Spécification — Site web OCCITEM Electrical Motors

## 1. Contexte & objectif

**Entreprise** : OCCITEM Electrical Motors — 22 Avenue du Louron, 31770 Colomiers, France  
**Type de site** : Vitrine institutionnelle one-page, statique  
**Cible** : Ingénieurs, bureaux d'études, industriels (B2B) — secteurs aéronautique, naval, terrestre  
**Objectif** : Crédibiliser l'entreprise et diriger les visiteurs vers un contact (email / téléphone)

---

## 2. Architecture

Site **one-page** avec navigation fixe en haut et ancres vers chaque section.

| Ordre | Section            | Ancre          |
|-------|--------------------|----------------|
| 1     | Hero               | `#accueil`     |
| 2     | Qui sommes-nous    | `#apropos`     |
| 3     | Technologie U-PIN  | `#technologie` |
| 4     | Nos services       | `#services`    |
| 5     | Nos marchés        | `#marches`     |
| 6     | Vidéo              | `#video`       |
| 7     | Contact            | `#contact`     |

La navigation contient aussi un **switch FR / EN** (bascule de langue).

---

## 3. Contenu par section

### 3.1 Hero (`#accueil`)
- Fond : `assets/hero-bg.jpg` (`bobinage_epingle.jpg`) + overlay bleu marine semi-transparent
- Logo OCCITEM blanc centré (`assets/logo-blanc.png`)
- Tagline bilingue (ex : *"Moteurs électriques haute performance, made in France"*)
- Bouton CTA ancré vers `#contact`

### 3.2 Qui sommes-nous (`#apropos`)
- Phrase clé : *"OCCITEM conçoit, développe et fabrique en petite série des machines électriques de haute fiabilité et haute performance."*
- Quelques lignes sur l'entreprise : PME française basée à Colomiers, technologie U-PIN développée en interne
- **Galerie atelier 2 photos côte à côte** :
  - `assets/atelier-1.png` — machine de bobinage automatisée + opératrice
  - `assets/atelier-2.png` — vue panoramique de l'atelier (zones IMPREGNATION / BOBINAGE / EMBALLAGE)
- `assets/locaux.jpg` en complément (façade)

### 3.3 Technologie U-PIN (`#technologie`)
- Introduction courte sur le bobinage U-PIN et son avantage vs l'état de l'art
- Visuel comparatif : `assets/rotor.png` (U-PIN) vs `assets/bobinage-comparaison.png` (fil rond classique)
- 6 avantages clés en grille (icône + titre + texte court + **compteur animé**) :
  1. Meilleur rendement — coefficient de remplissage **70%** vs 45%
  2. Plus léger — réduction de masse jusqu'à **15%**
  3. Plus robuste — MTBF **+100%**
  4. Meilleure durée de vie — maîtrise du positionnement des fils
  5. Haute performance — refroidissement continu **+200%**
  6. Plus silencieux — bruits magnétiques **-50%**
- Fond sombre, accents orange sanguin

### 3.4 Nos services (`#services`)
- 3 colonnes, chacune avec une illustration :
  - **Conception** — `assets/service-concevoir.png` (écran CAO)
  - **Fabrication** — `assets/service-fabriquer.png` (machine atelier)
  - **Prototypage** — `assets/service-prototyper.png` (technicien sur stator)
- Liste de prestations transversales (sous les colonnes) :
  - Trade-off, Maquettage labo, Dossier de fabrication clé en main, Prototypage, Petite série ≤ 1000/an, Maintenance de produits OCCITEM

### 3.5 Nos marchés (`#marches`)
- 3 cartes avec illustration fond transparent sur fond coloré, titre et courte description :
  - **Aéronautique** — `assets/marche-aero.png` (paramoteur électrique)
  - **Marine & Fluvial** — `assets/marche-marine.png` (voilier) + `assets/marche-pod.png` (POD)
  - **Terrestre** — `assets/marche-terrestre.png` (scooter électrique)

### 3.6 Vidéo (`#video`)
- Player HTML5 natif (`<video controls>`) centré
- Fichier : `OCCITEM_PEPSI_DIFFUSION_MASTER.mp4`
- Titre de section bilingue : *"OCCITEM en action" / "OCCITEM in action"*

### 3.7 Contact (`#contact`)
- Fond bleu marine, deux blocs côte à côte :
  - **Marc Tunzini** — Contact technique — `marc.tunzini@occitem.com` — `+33 (0)6 16 70 67 19`
  - **Géraldine Vieillard** — Contact commercial — `geraldine.vieillard@occitem.com` — `+33 (0)6 12 13 56 51`
- Adresse : 22 Avenue du Louron, 31770 Colomiers, France
- Logo + mention légale en footer
- **Pas de formulaire**

---

## 4. Design system

| Élément              | Valeur                                      |
|----------------------|---------------------------------------------|
| Fond principal       | `#0d1b2a` (bleu marine profond)             |
| Couleur accent       | `#cc3517` (orange sanguin)                  |
| Couleur secondaire   | `#104766` (bleu plein)                      |
| Texte principal      | `#ffffff`                                   |
| Texte secondaire     | `#a0aec0` (gris clair)                      |
| Police titres        | `Exo 2` (Google Fonts — proche Pill Gothic) |
| Police corps         | `Inter` (Google Fonts)                      |
| Style global         | Dark tech industrial — fidèle à la plaquette |
| Border-radius        | 4–8px (sobre, pas arrondi excessif)         |

---

## 5. Stack technique

| Élément          | Choix                                                     |
|------------------|-----------------------------------------------------------|
| Structure        | HTML5 sémantique (un seul `index.html`)                   |
| Style            | CSS3 custom (`style.css`), pas de framework               |
| Interactivité    | JS vanilla (`main.js`) — switch langue, scroll smooth     |
| Contenu texte    | `content.json` — tous les textes FR + EN centralisés      |
| Vidéo            | `<video>` HTML5 natif, fichier local                      |
| Icônes           | SVG inline ou bibliothèque légère (Lucide Icons CDN)      |
| Hébergement      | Fichiers statiques — compatible GitHub Pages / Netlify    |
| Pas de backend   | Pas de formulaire, pas de CMS, pas de base de données     |

---

## 6. Assets — inventaire complet

### Logos
| Fichier source (`_ressources/02-VISUELS ET CHARTE GRAPHIQUE/`) | Usage |
|----------------------------------------------------------------|-------|
| `LOGO/[OCCITEM] Logo+Isotype_Blanc.png` | Header + footer — transparent, blanc pur, parfait sur fond sombre |
| `LOGO/[OCCITEM] Logo+Isotype_Noir.png` | Réserve (non utilisé si site 100% sombre) |

### Images de fond / ambiance
| Fichier source | Usage |
|----------------|-------|
| `images/bobinage_epingle.jpg` | **Hero background** — même visuel bleu marine + moteur cuivre rouge |
| `Photo Locaux Louron.jpg` | Section "Qui sommes-nous" — façade des locaux |
| `[OCCITEM] Rotor.png` | Section Technologie — rotor réel fond transparent |
| `images/bobinage_fil_rond.png` | Section Technologie — comparaison visuelle bobinage classique vs U-PIN |

### Photos atelier (nouvelles)
| Fichier source | Usage |
|----------------|-------|
| `images/photo_atelier_1.png` | Section "Qui sommes-nous" — machine de bobinage automatisée, opératrice en action |
| `images/photo_atelier_2.png` | Section "Qui sommes-nous" — vue panoramique de l'atelier (zones IMPREGNATION / BOBINAGE / EMBALLAGE) — montre l'échelle industrielle |

### Illustrations services
| Fichier source | Service | Contenu |
|----------------|---------|---------|
| `images/illustration_concevoir.png` | **Conception** | Écran CAO/simulation moteur |
| `images/illustration_fabriquer.png` | **Fabrication** | Machine industrielle en atelier |
| `images/illustration_prototyper.png` | **Prototypage** | Technicien assemblant un stator |

### Illustrations marchés
| Fichier source | Marché | Contenu |
|----------------|--------|---------|
| `images/illustration_air.png` | **Aéronautique** | Paramoteur électrique (fond transparent) |
| `images/illustration_mer.png` | **Marine & Fluvial** | Voilier/catamaran (fond transparent) |
| `images/illustration_terre.png` | **Terrestre** | Scooter électrique (fond transparent) — lacune comblée |
| `images/image_pod.png` | **Marine** | POD électrique avec hélice — produit OCCITEM |

### Vidéo
| Fichier source | Usage |
|----------------|-------|
| `OCCITEM_PEPSI_DIFFUSION_MASTER.mp4` | Section `#video` |

### ~~Lacune identifiée~~
Toutes les illustrations marchés sont maintenant disponibles. Lacune comblée.

### Charte graphique appliquée
Source : `[TEM] Charte-graphique-simplifiee-2019.pdf`

| Couleur | Hex | Usage |
|---------|-----|-------|
| Bleu marine profond | `#0d1b2a` | Fond global |
| Bleu plein | `#104766` | Sections alternées, boutons secondaires |
| Orange sanguin | `#cc3517` | Accents, hover, highlights |
| Gris anthracite | `#292728` | Footer, séparateurs |
| Blanc | `#ffffff` | Texte principal |
| Police titres | `Exo 2` (Google Fonts) | Proche de Pill Gothic Light (charte) |
| Police corps | `Inter` (Google Fonts) | Lisibilité body text |

---

## 7. Structure des fichiers

```
site_occitem/
├── index.html
├── style.css
├── main.js
├── content.json               ← tous les textes FR/EN
├── assets/
│   ├── logo-blanc.png              ← LOGO/[OCCITEM] Logo+Isotype_Blanc.png
│   ├── hero-bg.jpg                 ← images/bobinage_epingle.jpg
│   ├── locaux.jpg                  ← Photo Locaux Louron.jpg
│   ├── atelier-1.png               ← images/photo_atelier_1.png
│   ├── atelier-2.png               ← images/photo_atelier_2.png
│   ├── rotor.png                   ← [OCCITEM] Rotor.png
│   ├── bobinage-comparaison.png    ← images/bobinage_fil_rond.png
│   ├── service-concevoir.png       ← images/illustration_concevoir.png
│   ├── service-fabriquer.png       ← images/illustration_fabriquer.png
│   ├── service-prototyper.png      ← images/illustration_prototyper.png
│   ├── marche-aero.png             ← images/illustration_air.png
│   ├── marche-marine.png           ← images/illustration_mer.png
│   ├── marche-terrestre.png        ← images/illustration_terre.png
│   ├── marche-pod.png              ← images/image_pod.png
│   └── video.mp4                   ← OCCITEM_PEPSI_DIFFUSION_MASTER.mp4
└── _ressources/               ← dossier source (non servi)
```

---

## 7. Fonctionnement de `content.json`

Tous les textes visibles du site sont dans ce fichier JSON, organisés par section et par langue. Le JS charge ce fichier au démarrage et injecte le contenu dans les éléments HTML marqués avec `data-key="section.cle"`.

**Exemple de structure :**
```json
{
  "nav": {
    "fr": { "about": "À propos", "tech": "Technologie", "services": "Services", "markets": "Marchés", "contact": "Contact" },
    "en": { "about": "About", "tech": "Technology", "services": "Services", "markets": "Markets", "contact": "Contact" }
  },
  "hero": {
    "fr": { "tagline": "Moteurs électriques haute performance, made in France", "cta": "Nous contacter" },
    "en": { "tagline": "High-performance electrical motors, made in France", "cta": "Contact us" }
  }
}
```

**Pour modifier un texte** : ouvrir `content.json` dans n'importe quel éditeur de texte, changer la valeur entre guillemets, sauvegarder.

---

## 8. Contrainte locale

En développement, le fichier `content.json` est chargé via `fetch()`. Il faut donc servir le site via un petit serveur HTTP local :

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

En production (Netlify, GitHub Pages, hébergement classique), aucune contrainte.

---

## 9. Animations & transitions

### Style général : Scroll reveal
Chaque bloc de contenu est **invisible au chargement** (opacity 0, légèrement décalé vers le bas). Quand il entre dans le viewport au scroll, il glisse vers sa position finale en fondu.

```
opacity: 0  translateY(30px)
      ↓ IntersectionObserver
opacity: 1  translateY(0)
transition: 0.6s ease-out
```

Implémentation : **CSS transitions** + **IntersectionObserver** natif (pas de bibliothèque).  
Les éléments d'une même section apparaissent en **cascade décalée** (`delay: 0ms, 100ms, 200ms…`).

---

### Effets interactifs

| Élément | Comportement |
|---------|-------------|
| **Cartes services / marchés** | `transform: translateY(-6px)` + bordure orange en bas au hover — transition 0.25s |
| **Compteurs animés** | Les valeurs clés (`70%`, `-15%`, `+100%`…) s'incrémentent de 0 à leur valeur cible quand la section Technologie entre dans le viewport |
| **Navigation active** | Le lien de la section visible est mis en évidence (couleur orange + underline) via IntersectionObserver — se met à jour en temps réel au scroll |
| **Bouton CTA** | Pas de pulse — hover simple avec fond orange plein et légère élévation |

---

### Ce qui ne change PAS
- Pas de parallax (cohérence avec choix scroll reveal)
- Pas d'animations au chargement initial (page s'affiche immédiatement)
- Pas de librairie externe (AOS, GSAP, etc.) — tout en CSS + JS vanilla

---

## 10. Ce qui est hors périmètre

- Formulaire de contact (remplacé par coordonnées directes)
- CMS ou interface d'administration
- Blog ou actualités
- Espace client / login
- Animations complexes / 3D
