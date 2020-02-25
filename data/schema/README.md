# How to provide schemas

## Simple indicators

For simple indicators obtained from a single source, please refer to [`data/schema_template.yaml`](./schema_template.yaml): for each field, substitute type and comment with an actual value, with the exception of:

```yaml
order: [year, <region_type>_id, <region_type>_year_spec, value.id]
```

Keep this as is, eventually just remove the doc comment.

Please remove any unneeded comments.

## Derived indicators

When an indicator is obtained from 2 or more other indicators:
- please document the base indicators using the schema template above;
- in the derived indicator schema, where applicable please list the base indicators under `derived_from`. For example, if an indicator is derived from the indicators `ashe_nuts_2_sci_tech` and `nuts_house_prices`, you can document provenance like this:

   ```yaml
   derived_from:
      - ashe_nuts_2_sci_tech
      - nuts_house_prices
   ```

## Stripping the tracking token from URLs

If present, we should always strip any tracking token from URLs: these usually start with `utm_`.

For example this URL:

```yaml
www.a-data-site.com/companies?utm_medium=GOV.UK&utm_source=datadownload&utm_campaign=full_fil&utm_term=9.30_16_10_19
```

should become:

```yaml
www.a-data-site.com/companies
```

Please take care of not removing query parameters used by the endpoint to serve the dataset.

```yaml
www.a-data-site.com/companies?year=2003&city=London&utm_medium=GOV.UK&utm_source=datadownload&utm_campaign=full_fil&utm_term=9.30_16_10_19
```

we should only strip the token, not the query, so that it becomes:

```yaml
www.a-data-site.com/companies?year=2003&city=London
```

## LEP vs NUTS2

The current aims is at documenting indicators using NUTS2 regions.

To avoid confusion, please put datasets using LEPs (with the correspondent schema) in `data/processed/<indicator_dir>/LEP`
