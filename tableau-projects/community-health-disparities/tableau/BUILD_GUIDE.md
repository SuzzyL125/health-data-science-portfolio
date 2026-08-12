# Tableau build guide: Community Health Disparities & Access

## Connect

Connect `community_health_tableau.csv` as the county-level source and `indicator_long_tableau.csv` as the indicator-detail source. Relate them on `locationid`; do not physically join at row level, because the long table contains multiple indicators per county.

Assign geographic roles:

- `stateabbr`: State/Province
- `locationname`: County
- `locationid`: County FIPS (string)

## Dashboard 1: National Equity Overview

### KPI cards

- `COUNTD([locationid])` — Counties Included
- `SUM([totalpopulation])` — Population Represented
- `MEDIAN([burden_score])` — Median Burden Percentile
- `MEDIAN([access_barrier_score])` — Median Access Barrier Percentile
- `SUM([high_priority_flag])` — Highest-Priority Counties

### Map

Use a filled county map colored by `priority_percentile`. Keep the scale fixed from 0 to 1 and use a sequential light-to-dark purple palette. Tooltip: county/state, population, burden, access, social-needs, and priority percentiles.

### Burden-versus-access scatterplot

- Columns: access barrier score
- Rows: burden score
- Detail: county FIPS
- Size: total population
- Color: priority quintile
- Add median reference lines to create four operational quadrants.

### Priority table

Display county, state, priority percentile, burden, access, social needs, diabetes, obesity, lack of insurance, and transportation barriers. Sort descending by priority percentile.

## Dashboard 2: State & County Profile

- State and county selectors at top
- Indicator dot plot comparing selected county with state median
- Confidence-interval bars from the long indicator table
- County rank within state
- Population and data-year context

## Dashboard actions

- Selecting a state filters the map, scatterplot, and county table.
- Selecting a county opens the profile dashboard.
- Selecting an indicator updates the confidence-interval comparison.

## QA checklist

- `locationid` retains five-digit FIPS formatting.
- Scores are shown as percentiles, not prevalence percentages.
- Prevalence values use percentage formatting and identify age adjustment.
- Protective indicators such as routine checkup are reversed only for the gap score.
- Missing indicators remain null and are not converted to zero.
- Priority score is labeled as an operational screening index, not a validated risk model.
- Include the CDC warning that PLACES estimates should not be used for causal program evaluation.
