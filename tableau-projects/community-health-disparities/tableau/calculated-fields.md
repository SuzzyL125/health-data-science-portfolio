# Tableau calculated fields

## Priority percentile label

```tableau
STR(ROUND([priority_percentile] * 100, 0)) + "th percentile"
```

## Highest-priority county count

```tableau
COUNTD(IF [high_priority_flag] = 1 THEN [locationid] END)
```

## State median prevalence

Use on the long indicator source:

```tableau
{ FIXED [stateabbr], [measureid] : MEDIAN([data_value]) }
```

## Difference from state median

```tableau
AVG([data_value]) - [State median prevalence]
```

## Operational quadrant

```tableau
IF [burden_score] >= 0.5 AND [access_barrier_score] >= 0.5 THEN "High burden / High barrier"
ELSEIF [burden_score] >= 0.5 THEN "High burden / Lower barrier"
ELSEIF [access_barrier_score] >= 0.5 THEN "Lower burden / High barrier"
ELSE "Lower burden / Lower barrier"
END
```
