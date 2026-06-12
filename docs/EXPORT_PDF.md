# Export des documents en PDF (mise en forme professionnelle)

## Prérequis

- [Pandoc](https://pandoc.org/) 3.x
- Moteur PDF : MiKTeX ou wkhtmltopdf

## Commandes (PowerShell, à la racine du projet)

```powershell
# Cahier des charges
pandoc docs/cahier_des_charges/Cahier_des_charges.md -o docs/cahier_des_charges/Cahier_des_charges.pdf --toc -V geometry:margin=2.5cm -V lang=fr

# Documentation technique
pandoc docs/documentation_technique/Documentation_technique.md -o docs/documentation_technique/Documentation_technique.pdf --toc -V geometry:margin=2.5cm

# Rapport technique (inclure captures d'écran avant export)
pandoc docs/rapport_technique/Rapport_technique.md -o docs/rapport_technique/Rapport_technique.pdf --toc -V geometry:margin=2.5cm

# Rapport de faisabilité
pandoc docs/rapport_faisabilite/Rapport_de_faisabilite.md -o docs/rapport_faisabilite/Rapport_de_faisabilite.pdf --toc
```

## Mise en forme Word (alternative)

1. Ouvrir chaque fichier `.md` dans Microsoft Word (ou copier le contenu).
2. Appliquer la styles **Titre 1 / Titre 2**, numérotation automatique, page de garde ENSP.
3. Insérer en-têtes/pieds de page, table des matières Word.
4. Exporter PDF.

## Diagrammes UML

Rendre les diagrammes Mermaid en PNG via https://mermaid.live/ ou extension VS Code, puis insérer dans le rapport technique avant export.

## Volume de pages visé

| Document | Pages indicatives (PDF) |
|----------|----------------------|
| Cahier des charges | 25–35 (avec annexes référencées) |
| Documentation technique | 30–40 |
| Rapport technique | 18–25 (ENSP) + annexes |
| Rapport faisabilité | 10–15 |

Ajoutez captures d'écran, page de garde et glossaire pour atteindre le niveau « travail d'ingénieur ».
