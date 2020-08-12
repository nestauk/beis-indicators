# 0.0.12 (next)

- Barchart to automatically scroll to the focused key (#275)

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
