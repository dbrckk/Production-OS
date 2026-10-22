# Validation Production-OS — 2026-10-21

## Périmètre

- Serveur : `cd85b78ff9a4050366c061bde509d1b20e282d67` (code applicatif issu de PR285 ; PR286/287 mettent à jour le suivi).
- Worker : `623b1b142b61b7b8d111640cdfad8151f1616e45`, suivi de `1831aab1bb38762741ce3a85d8ab6bb7c52e9a2b` qui ne modifie que `.ai/`.
- Vérification demandée par le propriétaire après les correctifs de livraison et de délais.

## Vérifications exécutées à nouveau

| Contrôle | Résultat observé |
| --- | --- |
| Suite serveur, PostgreSQL16 isolé | 1 325 réussis, aucun ignoré, 125,78 s |
| Suite worker | 1 845 réussis +199 sous-tests, 28,23 s |
| Serveur/worker HTTP authentifiés | 6 réussis, 4,062 s |
| HTTP lent, budget2 s | Disponibilité et suivi interrompus à2,01 s ; un GET, aucun POST |
| HTTP transitoire | Trois503 puis succès, quatre GET, aucun POST |
| HTTP403 | Arrêt après un GET, aucun POST |
| Compilation serveur | compileall avec SyntaxWarning traité en erreur : succès |
| Distribution | sdist et wheel construits ; wheel installé dans un venv distinct, import depuis site-packages et CLI fonctionnels |
| CI serveur au commit exact | Quatre jobs réussis, [run39683727822](https://github.com/dbrckk/Production-OS/actions/runs/39683727822) |
| CI worker au commit exact | Huit workflows après fusion réussis, [preuves PR374](https://github.com/dbrckk/ai-dev-server/pull/374) |
| Render | `dep-dbcjdlss728c73al7810` live au commit serveur attendu |
| HTTP public | healthz200, readyz200/base accessible, dashboard200 ; API protégée sans jeton401 |

Le premier GET healthz a pris22,52 s ; les lectures suivantes ont pris moins d'une seconde. Cette observation ne constitue pas une garantie de disponibilité permanente. La base Docker de validation a été supprimée avec ses volumes. Aucun nouveau test unitaire n'a été créé.

## État actuel des livraisons cibles

- **Correction du suivi précédent :** [Jumpy37](https://github.com/dbrckk/Jumpy/pull/37) a été fusionnée par `dbrckk` le2026-10-21 à18:37:29UTC, commit `7ba62fce709f852aa1a43f4246f1ca8a142c7ad2`. La mention antérieure « reste en brouillon » était périmée.
- Ses trois workflows au commit de fusion sont réussis : [Godot](https://github.com/dbrckk/Jumpy/actions/runs/39654404595), [APK Android](https://github.com/dbrckk/Jumpy/actions/runs/39654404846) et [standards](https://github.com/dbrckk/Jumpy/actions/runs/39654406518). Un APK construit ne prouve pas le fonctionnement sur appareil physique.
- [star-list154](https://github.com/dbrckk/star-list/pull/154) est toujours un brouillon non fusionné, tête `c415a3235fe701c93e19cf656722bc03b70c735b`. Sa récupération antérieure a été assistée par l'opérateur.
- Aucune fusion de dépôt cible n'a été effectuée pendant cette validation.

## Qualification encore ouverte

Le diagnostic hébergé existant, [run39697046716](https://github.com/dbrckk/ai-dev-server/actions/runs/39697046716), a échoué le2026-10-22 : génération de codeHTTP503 ; autres sondes404/JSON invalide, avec une disponibilité JSON valide. Accès opérateur GET réussi ; réveil immédiat déclaré prêt par le serveur, sans tâche/dispatch réel. Secours Cloudflare gratuit non configuré. Les sept workflows logiciels et trois contrôles CircleCI après fusion du worker sont tous réussis. Résultats exacts : [worker PR376](https://github.com/dbrckk/ai-dev-server/pull/376). Aucune tâche source ni nouvelle sonde modèle ; les anciens objectifs sont obsolètes et le canary42 n'est pas activé.

Un diagnostic synthétique réussi peut établir une disponibilité ponctuelle. Il ne prouve ni une livraison autonome complète sur une nouvelle tâche source, ni une capacité d'inférence gratuite durable. Aucun changement de fournisseur, de plafond de projet ou de licence n'est demandé.

## Correction de l'inférence — 2026-10-22

[Worker377](https://github.com/dbrckk/ai-dev-server/pull/377) corrige un défaut du chemin réel après503 : l'enveloppe de6000 conservait la charge4242 du premier appel, mais le repli conservait une réservation de sortie4096 devenue trop grande. Le nouveau calcul utilise le registre courant : deuxième appel plafonné à1612, succès, charge totale conservatrice4292/6000. Avec4500, la capacité restante est insuffisante et aucun second appel n'est envoyé.

Le diagnostic corrige aussi ses petites sondes Nemotron et exerce le repli dans un budget de sortie total384 tokens/40 secondes, avec les échecs visibles. Suite locale finale1845+199 sous-tests et six intégrations authentifiées réussies. Deux tests existants étendus ; aucune nouvelle fonction de test unitaire.

Un appel Kilo distinct, limité à un exercice public synthétique, a produit du code vérifié avec75 tokens de sortie et un coût déclaré nul. Aucun fournisseur n'a été activé pour des données de projet. La qualification NVIDIA réelle sera consignée dans PR377 après ses CI et sa fusion ; la dernière observation hébergée reste l'échec503 documenté ci-dessus jusqu'à ce résultat. Aucun plafond augmenté, travail source mis en file ou dépôt cible fusionné.
