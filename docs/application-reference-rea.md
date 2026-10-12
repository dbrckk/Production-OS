# Étape « applications de référence / REA » dans Production-OS

## Finalité

Tout projet de **nouvelle application Android** ou de refonte majeure doit démarrer par une phase de comparaison de solutions existantes, pour comprendre les besoins déjà traités avant de choisir une implémentation originale. Cette procédure **n'est pas** une règle 89 et n'autorise aucune copie de code propriétaire.

## Protocole de préparation

1. **Recherche réelle** : identifier idéalement 3 à 5 alternatives adaptées au brief. Produire une matrice de fonctionnalités, onboarding, navigation, performances, ergonomie, options hors ligne et avis, avec URLs officielles et dates/versions lorsque vérifiables.
2. **Preuve d'identité** : pour chaque candidat, relever éditeur, identifiant du package Android et page éditeur/Google Play/F-Droid/GitHub. Vérifier si l'éditeur propose *réellement* le téléchargement direct d'un APK, sans confondre fiche du store et fichier téléchargeable.
3. **Référence binaire uniquement autorisée** : utiliser le répertoire local privé `reference-apks/` de `dbrckk/zombie-apk` pour tout APK obtenu légalement ; cataloguer nom, version, URL d'obtention, SHA-256 des octets et certificat de signature indépendamment vérifié lorsque possible. Le dépôt GitHub `zombie-apk` est **public**, ne jamais y publier de nouveau fichier propriétaire dans le code ou en release sans droits de redistribution explicites.
4. **REA** : utiliser le [skill central REA](https://github.com/dbrckk/repo-standards/blob/50662421a37d91cda086261d9b20b42288f66cc0/skills/app-reference-rea/SKILL.md) et son moteur Android basé sur JADX/JDK si le binaire est disponible. Consigner outils réellement exécutés, SHA exact, portée et limites. Ne pas contourner anti-triche/DRM/authentification ; ne pas traiter des données d'utilisateur tiers.
5. **Adaptation** : rédiger `docs/app-reference-research.md` dans le projet applicatif : références officielles, statut d'acquisition/inspection, observations et preuves, fonctionnalités communes, améliorations originales, licences/risques et validation prévue. Réutiliser **des principes** et du code ouvert compatible ; pas de dump de code/ressources de tiers.
6. **Blocage** : quand l'APK officiel n'est pas redistribuable/obtenable ou que les outils REA manquent, écrire clairement `apk_status=store_only|unavailable|unverified` et `rea_status=blocked_missing_apk|blocked_missing_tool|not_run`. La recherche fonctionnelle publique continue sans prétendre avoir fait du REA.

## Connexion aux dépôts

- [Catalogue et import local d'APK : zombie-apk](https://github.com/dbrckk/zombie-apk/blob/ad335eab2d65def1e63fbde0374fe2cba785b400/references/catalog.json) — outil `scripts/reference_intake.py`.
- [Skill opérationnel : repo-standards/REA](https://github.com/dbrckk/repo-standards/blob/50662421a37d91cda086261d9b20b42288f66cc0/skills/app-reference-rea/SKILL.md) — compléter le standard **88 règles**, sans le modifier.
- [REA amont](https://github.com/morluto/rea), [guide Android](https://github.com/morluto/rea/blob/main/docs/android-analysis.md).
- [AI Dev Server : Studio mobile](https://github.com/dbrckk/ai-dev-server/pull/289) — intègre le contrat documentaire et le prompt produit sourcé.

## Preuve de réalisation, sans inventer

La phase est **réalisée** seulement si des recherches réelles, URLs, dates, matrices et les preuves correspondantes sont disponibles. L'analyse REA est marquée `completed` uniquement après exécution locale d'un binaire acquis légitimement ; un commentaire, une recherche web ou l'absence de crash ne suffit pas.

**État actuel :** ce guide et les instructions d'agent sont proposés par PR DRAFT. Ils ne sont **pas** un composant exécutable du moteur d'orchestration de Production-OS ; une phase automatisée exigerait l'accès aux sources autorisées, l'installation de REA/JDK/JADX et une intégration contrôlée de la file de tâches. Aucun de ces effets n'est présumé.

Aucun nouveau test unitaire, aucun déploiement ou merge n'est créé par cette documentation.
