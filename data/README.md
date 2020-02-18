# BEIS Indicators Data

## Indicator Data

Indicators are stored in `processed`.

Each individual indicator is stored as a single csv with a consistent format and column order:

```
year, nuts_id, nuts_year_spec, <indicator value>
```

## Schemas and Metadata

Each indicator requires an individual schema to describe the dataset fields as well as the provenance of the data. An indicator schema template can be found in `.schema/schema_template.yaml`.

