# Hospital Quality & Patient Safety Analytics

## Business scenario

Hospital leadership needs an executive view of quality performance to identify facilities with poor outcomes, understand which domains drive risk, and prioritize quality-improvement review.

## Questions answered

- Which hospitals have the highest and lowest CMS overall ratings?
- Where do mortality, safety, and readmission results compare worse than national benchmarks?
- Are low-rated hospitals weak across several domains or driven by one domain?
- How does performance vary by state, ownership, hospital type, and emergency-service status?
- Which hospitals combine a low star rating with multiple worse-than-national measures?
- What share of rated hospitals meet a four- or five-star benchmark?

## Dashboard pages

### 1. Executive Quality Scorecard

KPI cards: rated hospitals, average star rating, four/five-star share, hospitals prioritized for review, and total worse-than-national flags.

Visuals: U.S. state map, rating distribution, quality-domain breakdown, and prioritized-hospital table.

### 2. Hospital Peer Review

Visuals: hospital-versus-peer comparison, domain profile, ownership/type comparison, and detailed measure table.

Filters: state, hospital, hospital type, ownership, rating, birthing-friendly designation, and priority tier.

## Data sources

| Dataset | CMS identifier | Purpose |
|---|---|---|
| Hospital General Information | `xubh-q36u` | Facility characteristics, overall rating, domain counts |
| Complications and Deaths - Hospital | `ynj2-r877` | Mortality and safety measures |
| Unplanned Hospital Visits - Hospital | `632h-zaca` | Readmission and return-visit measures |

All are public CMS Provider Data Catalog resources. The pipeline downloads CSV directly from the CMS API.

## Analytical grain

The Tableau-ready file is one row per hospital. Domain-level measure counts from Hospital General Information are used to create comparable risk flags. Detailed measure files are summarized before joining so hospital totals are not duplicated.

## Priority logic

The project uses transparent operational rules rather than claiming a clinical ranking:

- **High priority:** rating 1–2 and at least two worse-than-national domain flags
- **Review:** rating 1–2 or at least two worse-than-national domain flags
- **Monitor:** one worse-than-national flag
- **Routine:** no worse-than-national flags
- **Not rated:** CMS rating unavailable

The threshold definitions are documented and can be changed in the pipeline or Tableau.

## Reproduce

```bash
python scripts/build_dataset.py
```

Generated files:

- `data/raw/*.csv`: timestamped CMS source extracts
- `data/processed/hospital_quality_tableau.csv`: Tableau source
- `data/processed/qa_summary.json`: validation and metric summary

Then follow [the Tableau build guide](tableau/BUILD_GUIDE.md).

Or open `tableau/hospital-quality-patient-safety.twb` directly in Tableau Desktop. It is connected to the processed CSV with a relative path and includes an editable executive dashboard with four views.

## Responsible interpretation

CMS ratings are intended for comparison but depend on measure availability and reporting rules. A priority flag identifies facilities for further review; it does not prove poor care or establish causality. Missing measures must not be treated as average or favorable performance.
