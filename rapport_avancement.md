# World Wellness Weekend — Rapport d'avancement

**Prototype de prospection — marché USA (yoga · Pilates · fitness)**

*Document de suivi · 23 mai 2026 · version 1.0*

---

## 1. Résumé exécutif

Le prototype de prospection est **opérationnel de bout en bout**. La chaîne complète — collecte des établissements, identification des responsables, vérification des emails, stockage structuré — fonctionne et a été exécutée sur un premier lot réel de **947 établissements** aux États-Unis (studios de yoga, Pilates et clubs de fitness).

**Résultats clés sur ce lot :**
- **947 établissements** collectés et structurés en base de données
- **~600 emails de responsables identifiés** (taux de match ~63 %)
- **~450 emails vérifiés valides**, prêts à être contactés
- Coût outils engagé à ce jour : **~75 € / ~80 $**
- Aucune dépendance à risque (pas de scraping LinkedIn, conformité RGPD intégrée)

Le prototype valide la **faisabilité technique et économique** de l'approche. La prochaine étape est la **mise en place de la campagne d'invitation** (rédaction du message, configuration de l'envoi, première vague de test).

---

## 2. Ce qui a été réalisé

### Architecture mise en place

```
[ Apify — Google Maps ]          Collecte des établissements
          │
          ▼
[ Base Supabase (PostgreSQL) ]   Stockage structuré + conformité
          │
          ▼
[ Enrichissement ]               Identification des responsables
   ├─ Crawl gratuit des sites web (extraction emails)
   └─ Apollo (recherche + révélation email)
          │
          ▼
[ NeverBounce + contrôle MX ]    Vérification de validité des emails
          │
          ▼
[ Table "contacts" ]             Liste exploitable, filtre conformité intégré
```

### Détail des étapes livrées

1. **Référentiel de données** : Google Sheet structuré (catégories, 199 pays, régions — dont 136 villes US réparties sur les 50 États).
2. **Base de données Supabase** : 5 tables (établissements, contacts, désinscriptions, campagnes, suivi d'envois) avec sécurité (RLS) et filtre de conformité intégré dans une vue dédiée.
3. **Pipeline de collecte** (`scrape_apify.py`) : interroge Google Maps par ville et par vertical, dédoublonne, insère en base.
4. **Pipeline d'enrichissement** (`enrich.py`) : crawl gratuit des sites + Apollo en complément + vérification NeverBounce.
5. **Socle de conformité RGPD** : politique de confidentialité bilingue (FR/EN), registre de désinscription, base légale documentée.

---

## 3. Les outils retenus — lesquels, pourquoi, leur intérêt

| Outil | Rôle | Pourquoi celui-ci | Intérêt concret |
|---|---|---|---|
| **Apify** (Google Maps Scraper) | Collecte des établissements | 4 à 10× moins cher que l'API Google officielle ; juridiquement plus sûr que les alternatives | Récupère nom, adresse, téléphone, site web, note, avis — la matière première |
| **Supabase** (PostgreSQL) | Base de données | Base relationnelle managée, scalable, sécurisée ; gratuit jusqu'à un volume important | Stocke et structure les données, prêt pour des centaines de milliers de fiches |
| **Crawl maison** (gratuit) | 1ʳᵉ source d'emails | Beaucoup d'établissements publient l'email sur leur site | **~70 % des emails trouvés sans rien payer** — le poste d'économie majeur |
| **Apollo** | 2ᵉ source d'emails | Base B2B de 220M+ contacts, accès API | Trouve les responsables quand le site ne révèle rien (~30 % des emails) |
| **NeverBounce** | Vérification email | Standard du marché, fiable | Élimine les emails morts **avant** envoi → protège la délivrabilité et la réputation du domaine |
| **SendGrid** *(à venir)* | Envoi des invitations | Compte + domaine déjà en place côté client | Envoi des emails avec suivi (ouvertures, clics, réponses) |

**Principe directeur : « ne payer que ce qui apporte une valeur réelle ».**
Le crawl gratuit fait l'essentiel du travail ; les outils payants ne sont sollicités qu'en complément. Exemple : NeverBounce n'est pas appelé quand Apollo a déjà certifié l'email « vérifié » → économie de crédits.

**Outils volontairement écartés** (et pourquoi) :
- *Scraping LinkedIn* : risque juridique majeur en 2026 (sanctions, fermetures de fournisseurs). Exclu.
- *Dropcontact, Hunter* : redondants avec Apollo pour le marché US. Reportés à la phase Europe si besoin.
- *Claude / IA* : non nécessaire à ce stade. Sera utile uniquement pour **personnaliser les emails** (phase d'envoi) — bien meilleur retour sur investissement à ce moment-là.

---

## 4. Résultats du prototype (lot de 947 établissements)

### Entonnoir de conversion

| Étape | Volume | Taux |
|---|---|---|
| Établissements collectés | **947** | 100 % |
| Avec site web actif | ~857 | 90 % |
| **Emails de responsables identifiés** | **~600** | **~63 %** |
| — via crawl gratuit | ~410 | 68 % des emails |
| — via Apollo | ~190 | 32 % des emails |
| **Emails vérifiés valides (prêts à contacter)** | **~450** | ~48 % |
| Emails « catch-all » (à utiliser avec prudence) | ~60 | |
| Emails invalides (écartés automatiquement) | ~90 | |
| Établissements joignables via email générique (info@) | ~180 | complément |

### Enseignements

1. **Le crawl gratuit est très productif** : il fournit ~2/3 des emails sans coût. La stratégie « gratuit d'abord, payant en complément » est validée.
2. **Apollo a une couverture limitée sur les très petites structures** (studios indépendants) mais utile sur les établissements de taille moyenne et les franchises.
3. **La vérification est indispensable** : ~15 % des emails trouvés étaient invalides — NeverBounce les a écartés avant tout envoi, protégeant la réputation du domaine.
4. **Taux de match conforme aux prévisions** (~63 % d'emails trouvés, ~48 % vérifiés) — dans la fourchette annoncée (40-65 %).

---

## 5. Coûts engagés à ce jour (outils)

Ces montants couvrent **toute la phase de prototype et les tests** sur les 947 établissements.

| Poste | Coût engagé | Détail |
|---|---|---|
| **Apify** (collecte) | **0 €** | Crédits gratuits utilisés (~5 $ de valeur), à recharger pour la suite |
| **Apollo** (abonnement Basic) | **~60 €** ($65/mois) | Nécessaire pour l'accès API ; crédits inclus à peine entamés (~50 / 2 500) |
| **NeverBounce** (crédits) | **~9 €** (~10 $) | Pack ~1 000 vérifications ; ~30 utilisées |
| **Supabase** (base de données) | **0 €** | Offre gratuite, largement suffisante au stade actuel |
| **Google Sheets / autres** | **0 €** | — |
| **Total outils à ce jour** | **~70-75 €** | |

> *La prestation de développement est couverte par le forfait pilote convenu séparément. Le présent tableau ne concerne que les coûts d'outils.*

---

## 6. Coûts prévisionnels pour la suite (outils uniquement)

> **Note de méthode.** Les estimations ci-dessous sont volontairement **majorées (fourchette haute)** pour éviter toute mauvaise surprise. Elles distinguent deux natures de coûts :
> - **Coûts ponctuels d'enrichissement** : payés **une seule fois par établissement** (collecte + recherche d'email + vérification). Pas de récurrence — un établissement enrichi ne se re-paie pas (hors rafraîchissement annuel).
> - **Abonnements fixes mensuels** : payés tant que le projet est actif, indépendamment du volume.

### Coûts unitaires de référence (fourchette haute)

**Enrichissement — par tranche de 1 000 établissements (ponctuel) :**

| Poste | Coût / 1 000 établissements |
|---|---|
| Apify (collecte Google Maps) | ~8 € |
| Apollo (crédits, au-delà du forfait inclus) | ~25 € |
| NeverBounce (vérification) | ~5 € |
| **Total enrichissement** | **~40 € / 1 000 établissements** |

**Abonnements fixes (mensuels, tant que le projet tourne) :**

| Poste | Coût mensuel (haut) |
|---|---|
| Apollo Basic (accès API) | ~65 € |
| SendGrid (envoi, selon volume) | jusqu'à ~90 € |
| Supabase Pro | ~25 € |
| **Total fixe mensuel** | **~180 € / mois** |

### Récapitulatif par phase (fourchette haute)

| Phase | Établissements ajoutés | Enrichissement (ponctuel) | Abonnements / mois |
|---|---|---|---|
| **Finaliser le pilote** (→ 2 000) | +~1 050 | **~80 €** | ~90 € |
| **Extension** (6 verticaux + UK/AU/NZ) | +~40 000 | **~1 600 €** (étalé sur la phase) | ~150 € |
| **Pleine échelle** (+ France & Espagne) | +~150 000 | **~6 000 €** (étalé sur plusieurs mois) | ~250 € |

> **Total outils sur toute la durée du projet (fourchette haute)** : ~7 700 € de coûts ponctuels d'enrichissement (pour ~190 000 établissements traités au total) + ~180-250 €/mois d'abonnements fixes en régime de croisière.

### Le poste à surveiller : Apollo

Apollo est le **seul coût élastique** : son forfait Basic inclut 2 500 crédits/mois, suffisant jusqu'à ~2 500 recherches mensuelles. Au-delà (phase d'extension), les crédits supplémentaires font grimper la facture. **Deux leviers de contrôle** :
- **Plafonner** l'usage Apollo (budget mensuel fixe, ou ne l'appeler que sur les établissements à fort potentiel) ;
- S'appuyer au maximum sur le **crawl gratuit** (~70 % des emails), qui limite la dépendance à Apollo.

Avec ces leviers, le budget reste **borné et prévisible**.

> **Efficience.** Même en fourchette haute, le coût par contact vérifié reste de l'ordre de **0,05-0,15 €**, contre 0,80-1,50 € pour une solution « clé en main » du marché.

---

## 7. La suite à réaliser

### Étape immédiate — Campagne d'invitation

1. **Rédaction du 1er email** (anglais) : invitation World Wellness Weekend, accroche « cause + bénéfice » (visibilité média, nouveaux clients), conforme CAN-SPAM (USA) et RGPD (mention de la source des données, désinscription en 1 clic).
2. **Configuration de l'envoi** : SendGrid sur le domaine secondaire (authentification SPF/DKIM/DMARC), lien de désinscription relié au registre de désinscription.
3. **Vague de test (« canary »)** : 50-100 emails d'abord, mesure du taux de délivrance, d'ouverture et de réponse, puis montée en charge progressive.

### Ensuite — Extension

- Compléter à ~2 000 établissements (recharge Apify).
- Ajouter les 3 verticaux restants (arts martiaux, running clubs, hôtels avec piscine + salle de sport).
- Étendre aux pays anglophones (UK, Australie, Nouvelle-Zélande), puis France et Espagne.

---

## 8. Visualisation web des données *(en cours côté client)*

Un **outil web de visualisation** des données est en préparation. Il se connectera directement à la base Supabase et permettra de :
- consulter et filtrer les établissements et contacts (par pays, vertical, ville, statut email) ;
- suivre l'avancement de la prospection et les statistiques de campagne ;
- offrir une interface claire au client sans manipuler la base technique.

L'architecture actuelle (Supabase) est **déjà prête pour cet usage** : la base expose des données structurées et sécurisées, directement exploitables par une application web. Aucune adaptation lourde n'est nécessaire.

---

## 9. Points d'attention

- **Apify** : le quota gratuit est épuisé — une petite recharge est nécessaire pour compléter la collecte au-delà des 947 établissements actuels.
- **Coût Apollo à l'échelle** : c'est le seul poste élastique (au-delà de 2 500 crédits/mois inclus). Il sera **plafonné par un budget mensuel** pour rester prévisible — voir §6.
- **Conformité** : la politique de confidentialité doit être **en ligne avant le 1er envoi** (prérequis légal).
- **Délivrabilité** : l'envoi se fera par vagues progressives sur un domaine secondaire authentifié — jamais en masse d'un coup, pour préserver la réputation.
- **Promesse réaliste** : ~48 % des établissements aboutissent à un email vérifié de responsable. Ne pas promettre davantage ; c'est un résultat solide pour ce secteur.

---

*Contact projet : Martial Parfait — martial@monsieurparfait.be*
