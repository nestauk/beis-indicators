# BEIS indicator folder content

Last update: 15 November 2019

All tables provide indicators of activity by NUTS 2 region,

## GTR

Source: GtR

Period: all

[Notebook link](https://github.com/nestauk/beis-indicators/blob/master/notebooks/dev/07_jmg_gtr_collection.ipynb)

* `2019_11_14_nuts_discipline_activity.csv`
  * Content: Levels of UKRI project activity and funding by discipline (in projects led by organisation in NUTS)
* `2019_11_14_research_act_collab.csv`
  * Content: Levels of participation in UKRI funded research (all participations) and number of local pairwise collaborations funded by UKRI

## HESA

Source: HESA website / HE-BCI survey

Period: Most recent year available

* `7_11_2019_hesa_data_nuts_2.csv`
 * [Notebook link](https://github.com/nestauk/beis-indicators/blob/master/notebooks/dev/01_jmg_hesa_data.ipynb)
 * Content: HESA indicators such as research income, academic staff, site area and number of buildings, graduates by discipline and research students
* `2019-11-08_hebci_nuts.csv`
 * [Notebook link](https://github.com/nestauk/beis-indicators/blob/master/notebooks/dev/03_jmg_hebci.ipynb)
 * Content: HE-BCI indicators such as spin outs from different sources, income from knowledge exchange etc

## Industry

Source: Nomis

Period: Most recent year available

[Notebook link](https://github.com/nestauk/beis-indicators/blob/master/notebooks/dev/08_jmg_bres_idbr.ipynb)

* `2019_11_15_BRES_2018_industry_salary.csv`
  * Content: Employment by sector and share of employment in high / low salary industries
* `2019_11_15_IDBR_2018_industry_salary.csv`
  * Content: Establishment by sector and share of establishments in high / low salary industries

## Migration

Source: ONS

Period: All years

[Notebook link](https://github.com/nestauk/beis-indicators/blob/master/notebooks/dev/02_jmg_migration.ipynb)

* `7_11_2019_migration_nuts.csv`
  * Content: internal and international migration inflows and outflows and population estimates

## Official

Source: Nomis

Period: 2010-2018

* `2019_11_15_ashe_rankings.csv`
  * [Notebook link](https://github.com/nestauk/beis-indicators/blob/master/notebooks/dev/0-jmg-ashe_sectoral.ipynb)
  * Content: median salary and decile by industry (used in the industry analysis)
* `nomis_BRES_YEAR_TYPE450.csv`
  * No notebook (data downloaded from command line)
  * Content: SIC 4 levels of employment by NUTS 2 (used in the industry analysis) 
* `nomis_IDBR_YEAR_TYPE450.csv`
  * No notebook (data downloaded from command line)
  * Content: SIC 4 establishment counts by NUTS 2 (used in the industry analysis)

## Patents

Source: PATSTAT

Period: After 2015

[Notebook link](https://github.com/nestauk/beis-indicators/blob/master/notebooks/dev/06_jmg_patents.ipynb)

* `2019_11_14_patent_nuts.csv`
  * Content: Number of patent inventors and applications in NUTS

## Trademarks

Source: IPO

Period: Since 2015

[Notebook link](https://github.com/nestauk/beis-indicators/blob/master/notebooks/dev/05-jmg-trademarks.ipynb)

* `12_11_2019_nuts_trademarks.csv`
  * Content: Number of trademarks and trademarks in scientific good and service codes

## REF (Research Excellence Framework)

Source: Research England

Period: 2014

[Notebook link](https://github.com/nestauk/beis-indicators/blob/master/notebooks/dev/04-jmg-ref.ipynb)

* `9_11_2019_ref_nuts.csv`
  * FTE submissions in different categories

## APS

Source: NOMIS

Period: 2012-2018

[Notebook link](https://github.com/nestauk/beis-indicators/blob/master/notebooks/dev/09_ao_aps_data.ipynb)
(Raw data collected via command line)

* `aps_pro_occupations_data.csv`
  * Content: Percentage of employment in occupation categories - NUTS2 level

* `aps_tertiary_education_data.csv`
  * Content: Percentage of the employed (aged 16-64) with NVQ4+ - NUTS2 level
