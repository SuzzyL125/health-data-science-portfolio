# Tableau build guide: Hospital Quality & Patient Safety

## Connect

Connect Tableau Desktop to `../data/processed/hospital_quality_tableau.csv`. Confirm `facility_id` and `zip_code` are strings so leading zeroes are preserved. Assign geographic roles to `state`, `citytown`, and `zip_code`.

## Create calculated fields

Use the definitions in [calculated-fields.md](calculated-fields.md).

## Worksheet 1: KPI cards

Create five text worksheets:

1. `COUNTD([facility_id])` — Rated Hospitals, filtered to non-null rating
2. `AVG([hospital_overall_rating])` — Average Rating
3. `AVG([four_five_star_flag])` — 4–5 Star Share, formatted as percentage
4. count of `priority_tier = "High priority"` — High Priority
5. `SUM([domain_worse_flags])` — Domain Risk Flags

## Worksheet 2: State performance map

- Marks: filled map
- Detail: State
- Color: average hospital overall rating
- Tooltip: rated facilities, average rating, 4–5 star share, high-priority count
- Use a color-blind-safe diverging palette with low ratings in orange and high ratings in blue.

## Worksheet 3: Rating distribution

- Columns: hospital overall rating
- Rows: distinct facility count
- Color: rating band
- Sort 1 through 5; exclude nulls by default and disclose the exclusion.

## Worksheet 4: Domain risk profile

Use Measure Names/Measure Values for mortality, safety, and readmission worse flags. Display percent of hospitals flagged in each domain. Keep the same orange risk color across the dashboard.

## Worksheet 5: Priority hospital table

Rows: facility name. Columns: state, rating, domain flags, detailed outcome worse count, detailed readmission worse count, ownership, priority tier. Sort High priority first, then by rating ascending and flags descending.

## Dashboard 1: Executive Quality Scorecard

- Fixed desktop size: 1300 × 850
- Top: title, subtitle, data-as-of note, and filters
- Row 2: five KPI cards
- Middle: state map (60%) and rating distribution (40%)
- Bottom: domain risk profile (35%) and priority hospital table (65%)
- Add dashboard actions so selecting a state filters the table and all visuals.

## Dashboard 2: Hospital Peer Review

- Hospital selector at top
- Left: selected hospital profile
- Middle: rating and flags versus state/ownership peer group
- Right: detailed outcome and readmission counts
- Bottom: explanatory note that flags support review and are not causal rankings

## QA checklist

- KPI counts reconcile to `qa_summary.json`.
- Null ratings are not silently converted to zero.
- Facility IDs retain six digits.
- Map filters the priority table correctly.
- Percentages use the rated-hospital denominator where appropriate.
- Every tooltip states the unit and denominator.
- No red/green-only encoding.
