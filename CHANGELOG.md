# 0.0.18 (next release)

## Indicators

- Added high tech patent applications indicator (#431)
- Added high tech employment indicator (#428)
- Added location quotient of high tech employment indicator (#429)

## Tool

- Refactor:
	- split utils (#437)
	- Use `@svizzle/ui`'s icons (#441)
	- Use `@svizzle/time_region_value` (#443)
- Add `<meta>` descriptions (#445)
- Make the app skeleton responsive (#448)

# 0.0.17 (staging release)

## Indicators

- Rename/reorder groups and regroup some indicators (#432):
  - Rename groups like this:

    Old name | New name
    -- | --
    Public R&D Capability | Public R&D
    Business R&D capacity | Private R&D
    Knowledge exchange | Knowledge exchange and university commercialisation
    Place potential | Places attracting R&D firms and workers

  - Reordered the four dimensions of the framework like this:
    - Public R&D
    - Knowledge exchange and university commercialisation
    - Private R&D
    - Places attracting R&D firms and workers

  - Moved two indicators to Private R&D:
    - STEM professionals (was in Public R&D)
    - STEM associate professionals (was in Public R&D)


# 0.0.16

## Indicators

- add ASHE mean salary indicators and schemas (#94)
- Correction in framework group for APS (STEM associate professionals) indicators (#416)
- Corrected NUTS spec year in for ASHE Mean Salary data collection script and indicators (#424)

## Tool

- The timeline navigation buttons support uneven distributions (#403)
- Fix the `/guide` page title (#419)
- Add a staging banner (#422)
- Updated Svizzle dependencies (#422)

# 0.0.15

## Indicators

- add GDP per capita indicators (#402)
- add Travel to- indicators (#369 & #329)
- add changes in APS indicator, corrections in framework groups and observation year starts from 2010 (#407)

# 0.0.14

## Indicators

- Eurostat indicators now start from observation year 2007 (except where earliest data after 2007 is available)

## Tool

- Update the color scale to green-blue (#390)
- Fix: the map shows the current year again (#389)
- Use red for the focused region (#389)
- Show a colored globe icon when some NUTS1 regions are deselected (#395)
- Provide two color scales that can be toggled at will (#397)
- Provide timeline navigation buttons (#399)
- Dynamic download URLs (#390).
  Indicators files are available at these locations:
  - `/download`: versioned zip file of all indicators CSV files
  - `/download/LEP`: versioned CSV file of all indicators for LEP regions
  - `/download/NUTS2`: versioned CSV file of all indicators for NUTS2 regions
  - `/download/NUTS3`: versioned CSV file of all indicators for NUTS3 regions

# 0.0.13

## Indicators

- add Number of technology companies (Crunchbase) (#63)
- add additional HE-BCI indicators (#347)
- add Travel connectivity indicators: to airport, to rail station, road junction times (#329)
- add international and internal migration indicator (#327)
- export all data in single tables for each region type (#370).
  Note that `/data/beis_indicators_0_0_13_LEP.csv` and `/data/beis_indicators_0_0_13_NUTS3.csv` are available as direct download but they're not reachable from within the tool.

## Tool

- Add a link to the indicators page in all pages (#335)
- Update Svizzle packages (#364)
- Update the color scale to blue-yellow-red (#358, #382)
- Fix: deselecting all regions was hiding cities (#366)
- Sort indicators in the sidebar (#385)

## Specs

- Description* fields (#365, #377)
	- renamed `description_long` -> `description`
	- renamed `description_short` -> `title`
	- renamed `description` -> `subtitle`
	- removed `schema.value.description`


# 0.0.12

## Indicators

- add patent and trademark indicators based on Eurostat data (#282)
- add Innovate UK funding data (#295)
- add housing cost indicator (#285)
- add Horizon 2020 funding data (#326)

## Tool

- Barchart to automatically scroll to the focused key (#275)
- Add a color legend to the map view (#269)
- Add major cities labels (#286, #335)
- Automatically scroll the sidebar to the current indicator (#219)
- Added regional selection for the trends route (#298)
- Added regional selection for the year route (#316)
- Show national average on the barchart (#290)
- Show long descriptions in the info panel (#273)
- Show the `warning` field in the info panel (#288)
- The downloadable zip contains a CSV file with all the datapoints of all of the indicators (#243)
- Add a color scale to the trends page (#268)
- Add a guide page (#268)

## Specs

- Add the `description_long` field to the spec template (#272)
- Add the `warning` field to the spec template (#288)
- Removed the `year_range` field, now derived automatically (#218)
- Some more field can have different shape: `api_type`, `source_name`, `source_url` (#287)


# 0.0.11

- Fixed code and data for broadband data (#250)
- Fixed code and data for HEBCI (#249)

# 0.0.10

- add buttons to download the complete dataset (#239)
- add the changelog and link the version in the header to the changelog on Github (#238)
- add links in /methodology

# 0.0.9

Add a button to download the data we see in a specific route (#236)

# 0.0.8

Add Broadband speed data (#233, #234)
Air pollution indicator data at the NUTS3 and LEPs level (#108)

# 0.0.7

- UI: add percentage unit strings (#230)
- Serve data from /static/data and fixes exporting /indicators/[id]/[year] (#228)

# 0.0.6

- Serve data from /static/data and fixes exporting /indicators/[id]/[year] (#228)

# 0.0.5

- UI: show units and axes labels (#224)

# 0.0.4

- UI: show descriptions and data provenance (#199)
- Various fixes (#221, dea27f3)

# 0.0.3

- Add indicator trends (#198)
- Various fixes:
  - `indicators/[id]/[year].svelte`:
    - barchart: reset the scroll when we select a new year
    - fixed a glitch in the map tooltip not showing zeroes
    (e.g. regions at the bottom of the barchart at [1] are zeroes: hovering them on the map wasn't showing the value)
  - `indicators/index.svelte`: add a white background to labels to ease readability
  - schemas:
    - fixed `year_range` for:
      - `eurostat_private_non_profit_rd_workforce_data`
      - `total_trademarks`
      - `total_trademarks_scientific`
    - added `format` for `total_gtr_projects_stem`
  - `methodology.svelte`: add links for Crunchbase and PATSTAT

# 0.0.2

- UI: add some copy and embed the user testing survey  (#202)
- Various fixes (#215)

# 0.0.1

Development of the tool pre-version:
- Collected mostly all [key indicators](https://github.com/nestauk/beis-indicators/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc+label%3Akey)
- Developed a web app
