# Community Health Disparities & Access

## Decision scenario

A population-health team needs to prioritize counties for outreach by identifying places where chronic-disease burden, limited healthcare access, and adverse social needs overlap.

## Questions answered

- Which counties have the highest age-adjusted diabetes, obesity, and cardiovascular burden?
- Where are lack of insurance, delayed care, and routine-checkup gaps greatest?
- Which counties combine disease burden with social-needs barriers?
- How do counties compare with their state benchmark?
- Which counties should be prioritized for further needs assessment?

## Source

CDC PLACES: Local Data for Better Health, County Data, 2025 release (`swc5-untb`). PLACES includes model-based county estimates derived from BRFSS and Census/ACS inputs. CDC cautions that the small-area model cannot detect effects caused by local interventions; the dashboard must not be used as a causal program evaluation.

## Selected indicators

| Domain | PLACES measure ID |
|---|---|
| Burden | `DIABETES`, `OBESITY`, `CHD`, `STROKE`, `GHLTH` |
| Access/prevention | `ACCESS2`, `CHECKUP`, `DELAYMED` |
| Social needs | `LACKTRPT`, `FOODSTAMP`, `HOUSINSECU`, `ISOLATION` |

The pipeline uses age-adjusted prevalence when available and creates domain percentiles. A composite priority score is the average of available adverse-direction percentile ranks; it is an operational screening index, not a validated clinical or causal score.

In the retrieved 2025 county release, `DELAYMED` and `ISOLATION` were not present. The pipeline records the indicators actually available in `qa_summary.json` and computes scores only from observed measures; it does not impute or invent these fields.

## Dashboard pages

### 1. National Equity Overview

KPI cards: counties included, population represented, median burden score, median access-barrier score, and high-priority counties.

Visuals: county/state map, priority distribution, burden-versus-access scatterplot, and top-priority county table.

### 2. State & County Profile

Visuals: selected county indicator profile, county versus state median, confidence intervals, and peer-county ranking.

Filters: state, indicator, priority quintile, population band, and rural/urban field if later joined from another public source.

## Reproduce

```bash
python scripts/build_dataset.py
```

Generated files:

- `data/raw/places_county_*.csv`
- `data/processed/community_health_tableau.csv`
- `data/processed/indicator_long_tableau.csv`
- `data/processed/qa_summary.json`

Then follow [the Tableau build guide](tableau/BUILD_GUIDE.md).

Or open `tableau/community-health-disparities.twb` directly in Tableau Desktop. It is connected to the processed CSV with a relative path and includes an editable executive dashboard with four views.
