# Tableau Healthcare Analytics Portfolio

Two decision-oriented Tableau projects built around first-party U.S. government public data. Together they demonstrate hospital quality analytics, operational prioritization, population health, geographic analysis, metric design, and executive communication.

## Projects

| Project | Decision supported | Public source |
|---|---|---|
| [Hospital Quality & Patient Safety](hospital-quality-patient-safety/) | Which hospitals and quality domains should leadership prioritize for review? | CMS Care Compare |
| [Community Health Disparities & Access](community-health-disparities/) | Which counties combine high disease burden with low access and adverse social needs? | CDC PLACES |

## Why these two

The hospital project demonstrates medical-center quality improvement and KPI reporting. The community-health project demonstrates epidemiology, health equity, geographic analysis, and intervention prioritization. They complement the predictive modeling and statistical-computing projects elsewhere in this repository.

## Reproducible workflow

Each project follows the same pattern:

```text
Official API -> immutable raw files -> validation and cleaning -> Tableau-ready CSV -> Tableau workbook
```

Run the data pipelines from this directory:

```bash
python hospital-quality-patient-safety/scripts/build_dataset.py
python community-health-disparities/scripts/build_dataset.py
```

The scripts retrieve current public data, preserve raw downloads, validate key fields, create analysis-ready outputs, and write a small QA summary. Network access is required.

## Tableau files

The `tableau/` folder in each project contains an editable `.twb` workbook, dashboard specification, and calculated-field definitions. Run the data pipeline first, then open the workbook in Tableau Desktop. The CSV connection is relative, so the repository can be moved without editing an absolute local path.

Regenerate both workbook templates with:

```bash
python scripts/build_workbooks.py
```

## Data publishing policy

Raw files are excluded from Git because government datasets may be large and are refreshed over time. The repository records the source URL, retrieval timestamp, transformations, schema, and row-count checks. Small Tableau-ready outputs may be committed after generation if GitHub file-size limits permit.
