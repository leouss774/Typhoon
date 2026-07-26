# 🗺️ Typhoon — Roadmap & Audit

> **Date :** 26 juillet 2026  
> **Projet :** Plateforme d'évaluation des risques climatiques  
> **Stack :** TypeScript (Front Vite SPA) + Node.js/Express (Backend API)

---

## Table des matières

1. [Routes & Vues par Rôle](#1-routes--vues-par-rôle)
2. [Backend API](#2-backend-api)
3. [Modèle de Données](#3-modèle-de-données)
4. [Workflow Cible vs Réalité](#4-workflow-cible-vs-réalité)
5. [Roadmap — Priorités](#5-roadmap--priorités)
   - [P1 — Workflow de Base](#-priorité-1--faire-fonctionner-le-workflow-de-base-2-3-jours)
   - [P2 — Compléter les Vues](#-priorité-2--compléter-les-vues-existantes-2-3-jours)
   - [P3 — Expert & Admin](#-priorité-3--expert--admin-2-3-jours)
   - [P4 — Polissage](#-priorité-4--polissage--finalisation-1-2-jours)
6. [Ce qui est déjà OK](#6-ce-qui-est-déjà-ok)

---

## 1. Routes & Vues par Rôle

### 👤 ASSUREUR (rôle par défaut)

| Route | Vue | Module TS | Statut | Description |
|---|---|---|---|---|
| `/assureur/dashboard` | Overview | `overview.ts` | ✅ | Stats cartes, graphiques répartition, activité récente |
| `/assureur/portfolio` | Portfolio | `portfolio.ts` | ✅ | Carte interactive, résumé propriétés, tendances |
| `/assureur/clients` | Clients | `clients.ts` | ✅ | Tableau + détail panel (biens, infos, historique) |
| `/assureur/risk-hub` | Risk Hub | `property-risk.ts` | ✅ | 4 étapes : Localiser / Actuariat / Inspecter / Évaluer |
| `/assureur/settings` | Settings | `settings.ts` | ✅ | 5 sous-tabs partagés (Compte/Sécurité/Facturation/Notifications/Connexions) |
| `/assureur/parametres` | Settings (alt) | — | 🔄 | Redirige vers `/assureur/settings` |

#### Sidebar assureur
- Dashboard · Portfolio · Clients · Risk Hub · Paramètres

---

### 👤 ASSURÉ (Espace client)

| Route | Vue | Module TS | Statut | Description |
|---|---|---|---|---|
| `/assure/bien` | Mon Bien | `assure.ts` | ✅ | Formulaire 5 étapes + upload photos/plans + dashboard risques |
| `/assure/travaux` | Mes Travaux | `assure.ts` | ⚠️ | Panel existe, **contenu vide** — à implémenter |
| `/assure/engagement` | Mon Engagement | `assure.ts` | ⚠️ | Panel existe, **contenu vide** — à implémenter |
| `/assure/dossier` | Mon Dossier | `assure.ts` | ⚠️ | Panel existe, **contenu vide** — à implémenter |
| `/assure/parametres` | Settings | — | 🔄 | Redirige vers settings partagé |

#### Sidebar assuré
- Mon Bien · Mes Travaux · Mon Engagement · Mon Dossier · Paramètres

---

### 👤 ADMIN

| Route | Vue | Module TS | Statut | Description |
|---|---|---|---|---|
| `/admin/overview` | Overview | `admin.ts` | ✅ | Stats utilisateurs (total, assureurs, assurés, clients, biens, évaluations) |
| `/admin/clients` | Clients | `clients.ts` | ✅ | Réutilise la vue clients assureur |
| `/admin/experts` | Experts | `admin.ts` | ⚠️ | Tableau experts basique — reprendre le layout clients |
| `/admin/settings` | Settings | `settings.ts` | ✅ | Réutilise settings partagé |

#### Sidebar admin
- Vue d'ensemble · Clients · Experts · Paramètres

---

### 👤 EXPERT

| Route | Vue | Module TS | Statut | Description |
|---|---|---|---|---|
| `/expert/missions` | Missions | `expert.ts` | ⚠️ | Cartes missions mock — **aucune donnée réelle liée** |
| `/expert/biens` | Biens | `portfolio.ts` | ✅ | Réutilise la vue portfolio (carte + résumé) |
| `/expert/settings` | Settings | `settings.ts` | ✅ | Réutilise settings partagé |

#### Sidebar expert
- Missions · Biens · Paramètres

---

### 🔐 Auth

| Route | Description | Statut |
|---|---|---|
| `/auth/sign-in` | Connexion email + mot de passe | ⚠️ | Désactivée pour le développement |
| `/auth/sign-up` | Inscription | ⚠️ | Désactivée pour le développement |
| `/auth/sign-in` | Page blanche (login/magic link/OAuth Google) | ⚠️ | Ne s'affiche pas correctement |

---

## 2. Backend API

### Routes

| Module | Endpoints | Statut |
|---|---|---|
| **Auth** | `POST /register`, `/login`, `/logout`, `/supabase-login` · `GET /me` | ✅ |
| **Clients** | `GET /` · `GET /{id}` · `POST /` · `PUT /{id}` · `DELETE /{id}` | ✅ |
| **Properties** | `GET /` · `GET /{id}` · `POST /input` · `DELETE /{id}` | ✅ |
| **Assessments** | `GET /` · `GET /{id}` · `PATCH /{id}/status` · `DELETE /{id}` | ✅ |
| | `POST /{id}/expert-form` · `GET /{id}/expert-form` | ✅ |
| | `POST /{id}/evaluate` · `GET /{id}/report` | ✅ |
| **Risk** | `POST /assess` (orchestrateur risques) | ✅ |
| **Admin** | `GET /stats` · `GET /users` · `POST /users` · `GET /assessments` | ✅ |
| **Health** | `GET /health` | ✅ |

### Stack Backend
- **Runtime :** Node.js (TypeScript)
- **Framework :** Express
- **ORM :** Drizzle ORM
- **Base :** SQLite (Turso/libSQL)
- **Auth :** JWT + bcrypt (+ Supabase en option)

---

## 3. Modèle de Données

```
┌─────────────┐       ┌──────────────┐
│    User     │       │    Client    │
├─────────────┤       ├──────────────┤
│ id (PK)     │──┐    │ id (PK)      │
│ email       │  │    │ user_id (FK) │──┐
│ password    │  └────│ first_name   │  │
│ role        │       │ last_name    │  │
│ first_name  │       │ email        │  │
│ last_name   │       │ phone        │  │
│ created_at  │       │ address/cp   │  │
└─────────────┘       │ city         │  │
                      │ status       │  │
                      └──────────────┘  │
                      ┌──────────────┐  │
                      │  Property    │  │
                      ├──────────────┤  │
                      │ id (PK)      │  │
                      │ client_id(FK)│◄─┘
                      │ address      │
                      │ city/cp      │
                      │ dpe_class    │
                      │ built_year   │
                      │ lat/lon      │
                      └──────────────┘  │
                      ┌──────────────┐  │
                      │ Assessment   │  │
                      ├──────────────┤  │
                      │ id (PK)      │  │
                      │ property_id  │◄─┘
                      │ user_id (FK) │
                      │ scores (6)   │
                      │ global_score │
                      │ created_at   │
                      └──────────────┘
```

---

## 4. Workflow Cible vs Réalité

```
CE QUI DEVRAIT SE PASSER                    CE QUI SE PASSE RÉELLEMENT
─────────────────────────                   ─────────────────────────────

1. Client remplit formulaire bien    ✅ →   OK, 5 étapes avec upload UI
   + UPLOAD photos/plans/PDFs        ⚠️ →   UI upload OK, fichiers NON envoyés au serveur

2. Notification → Assureur           ❌ →   RIEN ne prévient l'assureur
   "Nouveau bien soumis"

3. Assureur examine la soumission    ❌ →   Pas de file d'attente / badge "en attente"

4. Pré-remplit l'Actuariat (15 ch.)  ⚠️ →   Données client en DB, MAIS PAS LIÉES au Risk Hub

5. Décide : traiter ou assigner      ❌ →   Pas de système d'assignation

6. Si assigné → Expert reçoit        ❌ →   Missions = mock, pas de vraies données
   mission avec données client

7. Expert inspecte terrain           ❌ →   Pas de grille d'inspection / rapport

8. Rapport expert → Assureur         ❌ →   Pas de workflow de retour

9. Score final + prime → Client      ❌ →   Dashboard client = données mock

10. Historique des évaluations       ❌ →   Pas de liste d'évaluations passées
```

---

## 5. Roadmap — Priorités

### 🔴 PRIORITÉ 1 — Faire fonctionner le workflow de base (2-3 jours)

| # | Tâche | Fichiers | Impact | Durée |
|---|---|---|---|---|
| **1.1** | **Lier formulaire assuré → Risk Hub** : Pré-remplir les 15 champs Actuariat avec les données du bien stockées en DB quand on clique "Évaluer ce bien" | `assure.ts`, `property-risk.ts`, `risk-expert-form.ts` | 🔥 Critique — maillon central | 1 jour |
| **1.2** | **Badge notification** : Indicateur "X biens en attente" sur la sidebar assureur + dans l'en-tête | `router.ts`, `data-service.ts`, `index.html` | ✅ Rapide | ½ jour |
| **1.3** | **Upload files → serveur** : Envoyer les photos/plans via FormData multipart vers route backend + stockage | `assure.ts`, backend `upload` route | ⚠️ UI existe déjà | 1 jour |
| **1.4** | **Scores dans le détail client** : Afficher les scores risque et l'historique des assessments dans le panel CDP | `clients.ts`, `assessments` API | 👁️ Visibilité | ½ jour |

### 🟡 PRIORITÉ 2 — Compléter les vues existantes (2-3 jours)

| # | Tâche | Fichiers | Impact | Durée |
|---|---|---|---|---|
| **2.1** | **Remplir les vues assuré** : Travaux, Engagement, Dossier — contenu (liste travaux, statut contrat, uploads) | `assure.ts`, `assure.css`, `index.html` | 👤 Client | 1 jour |
| **2.2** | **Onglet Documents client** : Afficher les fichiers uploadés dans le détail client côté assureur | `clients.ts`, `index.html` | 🔗 Cross-role | ½ jour |
| **2.3** | **Améliorer le Risk Hub** : Carte interactive avec géolocalisation réelle + données BDNB/Géorisques | `property-risk.ts`, services backend | 📊 Data réelle | 1 jour |

### 🟢 PRIORITÉ 3 — Expert & Admin (2-3 jours)

| # | Tâche | Fichiers | Impact | Durée |
|---|---|---|---|---|
| **3.1** | **Assignation expert** : Workflow assureur → assigne une mission avec données du bien | `clients.ts`, `expert.ts`, backend | 🔗 Cross-role | 1 jour |
| **3.2** | **Missions expert réelles** : Remplacer missions mock par vraies données assignées | `expert.ts`, backend assign API | 👤 Expert | ½ jour |
| **3.3** | **Grille d'inspection expert** : Formulaire terrain (photos, notes, constats) | `expert.ts`, backend | 👤 Expert | 1 jour |
| **3.4** | **Dashboard admin stats réelles** : Stats depuis API au lieu de valeurs mock | `admin.ts`, `admin.css` | 👤 Admin | ½ jour |
| **3.5** | **Admin experts table** : Reproduire le layout clients pour la liste des experts | `admin.ts`, `index.html`, `admin.css` | 👤 Admin | ½ jour |

### 🔵 PRIORITÉ 4 — Polissage & Finalisation (1-2 jours)

| # | Tâche | Détail | Durée |
|---|---|---|---|
| **4.1** | **Auth fonctionnelle** : Rétablir l'authentification (login, signup, forgot password, OAuth Google) | 1 jour |
| **4.2** | **Gestion erreurs** : Toasts/notifications quand API échoue + pages 403/404 | ½ jour |
| **4.3** | **Responsive** : Adapter les vues pour tablette et mobile | 1 jour |
| **4.4** | **Dark mode complet** : Vérifier tous les composants dans les deux modes | ½ jour |
| **4.5** | **Landing page** : Finaliser la page d'accueil avec liens fonctionnels | ½ jour |

---

## 6. Ce qui est déjà OK (ne pas retoucher)

### ✅ Frontend
- **Router** : Navigation SPA complète avec 18 routes, sous-tabs, deep-linking, popstate
- **Gestion des rôles** : 4 rôles avec sidebar adaptative et bouton de switch
- **Clients** : CRUD complet avec wizard de création, détail panel, modification, changement de statut
- **Risk Hub** : 4 étapes complètes (Localiser, Actuariat, Inspecter, Évaluer) avec carte, formulaire 15 champs, vue 3D, scores
- **Portfolio** : Carte interactive + résumé + tendances + navigation cross-view
- **Settings** : 5 sous-tabs partagés entre tous les rôles (Compte, Sécurité, Facturation, Notifications, Connexions)
- **Formulaire assuré** : 5 étapes avec 40+ champs, custom dropdowns, zone d'upload UI, résumé récapitulatif
- **Custom dropdowns** : Dropdowns stylés (remplacement des `<select>` natifs)
- **Thème** : Dark/light mode avec persistance localStorage

### ✅ Backend
- **API REST complète** : Auth, Clients, Properties, Assessments, Risk, Admin, Health
- **Auth** : JWT + bcrypt + support Supabase
- **Orchestrateur risques** : Appels aux API externes (Géorisques, BDNB, IGN) + scoring engine
- **Base de données** : Drizzle ORM avec migrations, seed data

---

## 7. Résumé des Tâches

| Priorité | Tâches | Durée estimée |
|---|---|---|
| 🔴 P1 — Workflow de base | 4 tâches | 3 jours |
| 🟡 P2 — Vues existantes | 3 tâches | 2-3 jours |
| 🟢 P3 — Expert & Admin | 5 tâches | 3 jours |
| 🔵 P4 — Polissage | 5 tâches | 2-3 jours |
| **Total** | **17 tâches** | **10-12 jours** |
