# Tableau calculated fields

## Rating band

```tableau
IF ISNULL([hospital_overall_rating]) THEN "Not rated"
ELSE STR(INT([hospital_overall_rating])) + " star"
END
```

## Rated facility

```tableau
IF NOT ISNULL([hospital_overall_rating]) THEN [facility_id] END
```

## Four/Five Star Share

```tableau
AVG([four_five_star_flag])
```

Filter to non-null ratings before using this measure.

## High Priority Facility

```tableau
COUNTD(IF [priority_tier] = "High priority" THEN [facility_id] END)
```

## Rating versus state average

```tableau
AVG([hospital_overall_rating])
- { FIXED [state] : AVG([hospital_overall_rating]) }
```

## Any domain risk

```tableau
IF [domain_worse_flags] > 0 THEN "At least one risk flag"
ELSE "No risk flag"
END
```
