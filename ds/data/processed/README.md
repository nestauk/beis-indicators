# Processed Indicators
This folder contains datasets for processed indicators. Each sub folder is identified by the data source (e.g. Eurostat) and contains the indicators obtained from that source. Every indicator is stored a separate file (.csv) and is accompanied by a schema (.yaml) which describes the dataset and the fields.

Each indicator csv contains four columns, with each row representing the indicator value for a specific region and point in time. The fields are:

- `year`: the year for this indicator value
- `<region_id>`: the code of the region for this indicator value e.g. UKI1- `<region_year_spec>`: the version of the regions being used for for this indicator value e.g. NUTS 2016
- `<value>`: abbreviated name of the indicator

The full set of available indicators is listed below.

Last updated: 04/30/20 UTC

## Public R&D capability
### The total number of excellent researchers (4* score) submitted by universities in the NUTS-2 region for the 2014 REF
- **Description:** These are the results of the Research Excellence Framework, where university departments in various disciplines are assessed on the quality of their research. The latest REF was conducted in 2014 so data is available only for one year
- **Source:** REF (Research Excellence Framework)
- **Years Available:** 2014 - 2014
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/ref/total_4_fte.csv)


### The mean REF score for the NUTS2 area considering only STEM subjects (see aux/ref_stem.txt) for the subjects that we selected. This is the average of the scores in all departments weighted by the Full time equivalents submitted in each category (4*, 3*, 2* with higher scores representing better assessments)
- **Description:** These are the results of the Research Excellence Framework, where university departments in various disciplines are assessed on the quality of their research. The latest REF was conducted in 2014 so data is available only for one year
- **Source:** REF (Research Excellence Framework)
- **Years Available:** 2014 - 2014
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/ref/mean_ref_stem.csv)


### The mean REF score for the NUTS2 area. This is the average of the scores in all departments weighted by the Full time equivalents submitted in each category (4*, 3*, 2* with higher scores representing better assessments)
- **Description:** These are the results of the Research Excellence Framework, where university departments in various disciplines are assessed on the quality of their research. The latest REF was conducted in 2014 so data is available only for one year
- **Source:** REF (Research Excellence Framework)
- **Years Available:** 2014 - 2014
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/ref/mean_ref.csv)


### Total number of full-time students enrolled in STEM subjects in the area
- **Description:** Number of students enrolled full-time in STEM subjects in a NUTS2 region (definition of STEM subjects in aux folder) in the starting academic year.
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2014 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/total_stem_students.csv)


### Total number of buildings in the area
- **Description:** Number of university buildings in a NUTS2 region
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2015 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/total_university_buildings.csv)


### Total number of full-time students enrolled for postgraduate qualifications in universities in the area
- **Description:** Number of postgraduate (research) students enrolled full-time in universities in a NUTS2 region in the starting academic year.
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2014 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/total_postgraduates.csv)


### Research income for universities in the region
- **Description:** Research income received by universities in the NUTS2 region
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2015 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/gbp_research_income.csv)


### Full Time Equivalent (FTE) research students
- **Description:** Aggregate of Full Time Equivalent (FTE) of research students enrolled in universities in the NUTS2 region
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2015 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/fte_research_students.csv)


### Site Area (hectares) of university sites
- **Description:** Area of university sites for universities in the NUTS2 region
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2015 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/area_university_site.csv)


### Total number of full-time postgraduate students enrolled in STEM subjects in the area (definition of STEM subjects in aux folder)
- **Description:** Number of postgraduate (research) students enrolled full-time in STEM subjects in a NUTS2 region (definition of STEM subjects in aux folder) in the starting academic year.
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2014 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/total_stem_postgraduates.csv)


### Total number of projects led by organisations in the NUTS area in STEM subjects (see aux/gtr_stem_disciplines for the stem disciplines we are considering)
- **Description:** Total number of projects led by organisations in the NUTS area in STEM subjects (see aux/gtr_stem_disciplines for the stem disciplines we are considering)
- **Source:** UKRI (UK Research and Innovation)
- **Years Available:** 2010 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/gtr/total_gtr_projects_stem.csv)


### Percentage of population employed in professional occupations.
- **Description:** Percentage of population employed in professional occupations by NUTS 3 regions.
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2012 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/aps/aps_pro_occupations_data.csv)


### Percentage of population employed in professional occupations.
- **Description:** Percentage of population employed in professional occupations by NUTS 2 regions.
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2012 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/aps/aps_pro_occupations_data.csv)


### Percentage of population employed in professional occupations.
- **Description:** Percentage of economically active persons in professional occupations by NUTS 2 regions.
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2012 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/aps/aps_nvq4_education_data.csv)


### Number of Science, Research, Engineering and Technology associated professionals.
- **Description:** Number of Science, Research, Engineering and Technology associated professionals by NUTS 2 regions.
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2012 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/aps/aps_econ_active_stem_associate_profs_data.csv)


### Number of Science, Research, Engineering and Technology associated professionals.
- **Description:** Number of Science, Research, Engineering and Technology associated professionals by NUTS 3 regions.
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2012 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/aps/aps_econ_active_stem_associate_profs_data.csv)


### Percentage of population employed in professional occupations.
- **Description:** Percentage of economically active persons in professional occupations by NUTS 3 regions.
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2012 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/aps/aps_nvq4_education_data.csv)


### Number of Science, Research, Engineering and Technology professionals.
- **Description:** Number of Science, Research, Engineering and Technology professionals by NUTS 2 regions.
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2012 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/aps/aps_econ_active_stem_profs_data.csv)


### Number of Science, Research, Engineering and Technology professionals.
- **Description:** Number of Science, Research, Engineering and Technology professionals by NUTS 3 regions.
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2012 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/aps/aps_econ_active_stem_profs_data.csv)


### Private non-profit sector R&D expenditure in euros (to the nearest 1000)
- **Description:** Private non-profit sector enterprise research & development (R&D) expenditure by NUTS 2 regions.
- **Source:** Eurostat (European Statistical Office)
- **Years Available:** 2012 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/eurostat/eurostat_private_non_profit_rd_workforce_data.csv)


### Higher education sector R&D expenditure in euros (to the nearest 1000)
- **Description:** Higher education sector enterprise research & development (R&D) expenditure by NUTS 2 regions.
- **Source:** Eurostat (European Statistical Office)
- **Years Available:** 2012 - 2016
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/eurostat/eurostat_higher_ed_rd_workforce_data.csv)


### government performed R&D expenditure in euros (to the nearest 1000)
- **Description:** Government performed research & development (R&D) expenditure by NUTS 2 regions.
- **Source:** Eurostat (European Statistical Office)
- **Years Available:** 2012 - 2016
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/eurostat/eurostat_gov_rd_workforce_data.csv)


## Business R&D capacity
### Total amount of venture capital invested in organisations in the location
- **Description:** Level of venture capital investment in ventures based on a region based on data from CrunchBase. A small number of deals have been converted to GBP at the date when they were announced.
- **Source:** Crunchbase (business information about companies)
- **Years Available:** 2010 - 2019
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/crunchbase/gbp_venture_capital_received.csv)


### Percentage of population employed in professional occupations.
- **Description:** Percentage of population employed in science, research, engineering and technology professional by NUTS 3 regions.
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2012 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/aps/aps_econ_active_stem_density_data.csv)


### Percentage of population employed in professional occupations.
- **Description:** Percentage of population employed in science, research, engineering and technology professional by NUTS 2 regions.
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2012 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/aps/aps_econ_active_stem_density_data.csv)


### Economic complexity Index
- **Description:** This indicator measures the economic complexity of a location based on an analysis of its industrial composition ((based on Nesta sectoral definition, which clusters 4-digit SIC codes based on their similarity))
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2016 - 2019
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/industry/economic_complexity_index.csv)


### Full time equivalent of workforce
- **Description:** Full time equivalent (FTE) of private sector research & development (R&D) workforce-  by NUTS 2 regions.
- **Source:** Eurostat (European Statistical Office)
- **Years Available:** 2012 - 2016
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/eurostat/eurostat_private_rd_fte_workforce_data.csv)


### business enterprise R&D expenditure in euros (to the nearest 1000)
- **Description:** Business enterprise research & development (R&D) expenditure by NUTS 2 regions.
- **Source:** Eurostat (European Statistical Office)
- **Years Available:** 2012 - 2016
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/eurostat/eurostat_berd_data.csv)


### Head count of workforce
- **Description:** Head count (HC) OF private sector research & development (R&D) workforce by NUTS 2 regions.
- **Source:** Eurostat (European Statistical Office)
- **Years Available:** 2012 - 2016
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/eurostat/eurostat_private_rd_headcount_workforce_data.csv)


## Knowledge exchange
### Total number of unique inventions involving organisations in the NUTS2 region in a year (we consider the earliest application year for all patents in the family)
- **Description:** Total number of unique inventions involving organisations in the NUTS2 region in a year (we consider the earliest application year for all patents in the family)
- **Source:** EPO (European Patent Office)
- **Years Available:** 2013 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/patents/total_inventions.csv)


### Total income from IP licensing in universities located in the NUTS2 region in the academic year starting in year
- **Description:** Total income from IP licensing in universities located in the NUTS2 region in the academic year starting in year
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_ip_revenues.csv)


### Contract research income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Description:** Contract research income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_business_contract_research.csv)


### Consultancy income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Description:** Consultancy income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_business_consulting.csv)


### Contract research income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Description:** Total external investment in active spinoffs involving local universities in academic year starting in year
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_investment_per_active_spinoff.csv)


### Total current turnover of active spinoffs involving local universities in academic year starting in year
- **Description:** Total current turnover of active spinoffs involving local universities in academic year starting in year
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_turnover_per_active_spinoff.csv)


### Contract research income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Description:** Total number of active startup companies involving graduates from universities in the region in the academic year that starts in year
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/total_active_graduate_startups.csv)


### Consultancy income with public sector and third sector organisatoins involving universities in the NUTS2 region in the academic year starting in year
- **Description:** Consultancy income with public sector and third sector organisatoins involving universities in the NUTS2 region in the academic year starting in year
- **Source:** HESA (Higher Education Statistical Agency)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_non_business_consulting.csv)


### Total number of trademarks in scientific and technological product fields published by organisations in the region based on the IPO open trademark dataset
- **Description:** Total number of trademarks in scientific and technological product fields published by organisations in the region based on the IPO open trademark dataset
- **Source:** IPO (Intellectual Property Office)
- **Years Available:** 2010 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/trademarks/total_trademarks_scientific.csv)


### Total number of trademarks published by organisations in the region based on the IPO open trademark dataset
- **Description:** Total number of trademarks published by organisations in the region based on the IPO open trademark dataset
- **Source:** IPO (Intellectual Property Office)
- **Years Available:** 2010 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/trademarks/total_trademarks.csv)


## Place potential
### mean pm10 particulate pollution value
- **Description:** Mean PM10 particulate background pollution data at NUTS 2 regions aggregated from 1km x 1km resolution UK data modelled by DEFRA.
- **Source:** DEFRA (Department for Environment Food & Rural Affairs)
- **Years Available:** 2007 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/defra/air_pollution_mean_pm10.csv)


### mean pm10 particulate pollution value
- **Description:** Mean PM10 particulate background pollution data at NUTS 3 regions aggregated from 1km x 1km resolution UK data modelled by DEFRA.
- **Source:** DEFRA
- **Years Available:** 2007 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/defra/air_pollution_mean_pm10.csv)


### mean pm10 particulate pollution value
- **Description:** Mean PM10 particulate background pollution data for LEP regions aggregated from 1km x 1km resolution UK data modelled by DEFRA.
- **Source:** DEFRA
- **Years Available:** 2007 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/defra/air_pollution_mean_pm10.csv)


### Total employment in cultural, entertainment and leisure industries
- **Description:** This indicator measures level of employment in cultural, entertainment and leisure industries based on the Business Register Employment Survey. Those sectors are identified as clusters of SIC-4 (industry) codes
- **Source:** NOMIS (official labour market statistics)
- **Years Available:** 2016 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/industry/employment_culture_entertainment_recreation.csv)


## Challenge oriented activity
