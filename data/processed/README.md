# Processed Indicators
This folder contains datasets for processed indicators. Each sub folder is identified by the data source (e.g. Eurostat) and contains the indicators obtained from that source. Every indicator is stored a separate file (.csv) and is accompanied by a schema (.yaml) which describes the dataset and the fields.

Each indicator csv contains four columns, with each row representing the indicator value for a specific region and point in time. The fields are:

- `year`: the year for this indicator value
- `<region_id>`: the code of the region for this indicator value e.g. UKI1- `<region_year_spec>`: the version of the regions being used for for this indicator value e.g. NUTS 2016
- `<value>`: abbreviated name of the indicator

The full set of available indicators is listed below.

Last updated: 02/25/20 UTC

## Existing capability to perform public R&D
### Total number of full-time students enrolled in STEM subjects in the area
- **Description:** Number of students enrolled full-time in STEM subjects in a NUTS2 region (definition of STEM subjects in aux folder) in the starting academic year.
- **Source:** HESA (Higher Education Statistical Agency) https://www.hesa.ac.uk/
- **Years Available:** 2014 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/total_stem_students.csv)


### Total number of buildings in the area
- **Description:** Number of university buildings in a NUTS2 region
- **Source:** HESA (Higher Education Statistical Agency) https://www.hesa.ac.uk/
- **Years Available:** 2015 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/total_university_buildings.csv)


### Total number of full-time students enrolled for postgraduate qualifications in universities in the area
- **Description:** Number of postgraduate (research) students enrolled full-time in universities in a NUTS2 region in the starting academic year.
- **Source:** HESA (Higher Education Statistical Agency) https://www.hesa.ac.uk/
- **Years Available:** 2014 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/total_postgraduates.csv)


### Research income for universities in the region
- **Description:** Research income received by universities in the NUTS2 region
- **Source:** HESA (Higher Education Statistical Agency) https://www.hesa.ac.uk/
- **Years Available:** 2015 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/gbp_research_income.csv)


### Full Time Equivalent (FTE) research students
- **Description:** Aggregate of Full Time Equivalent (FTE) of research students enrolled in universities in the NUTS2 region
- **Source:** HESA (Higher Education Statistical Agency) https://www.hesa.ac.uk/
- **Years Available:** 2015 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/fte_research_students.csv)


### Site Area (hectares) of university sites
- **Description:** Area of university sites for universities in the NUTS2 region
- **Source:** HESA (Higher Education Statistical Agency) https://www.hesa.ac.uk/
- **Years Available:** 2015 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/area_university_site.csv)


### Total number of full-time postgraduate students enrolled in STEM subjects in the area (definition of STEM subjects in aux folder)
- **Description:** Number of postgraduate (research) students enrolled full-time in STEM subjects in a NUTS2 region (definition of STEM subjects in aux folder) in the starting academic year.
- **Source:** HESA (Higher Education Statistical Agency) https://www.hesa.ac.uk/
- **Years Available:** 2014 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hesa/total_stem_postgraduates.csv)


## Business absorptive capacity and private R&D investment
### Total amount of venture capital invested in organisations in the location
- **Description:** Level of venture capital investment in ventures based on a region based on data from CrunchBase. A small number of deals have been converted to GBP at the date when they were announced.
- **Source:** https://www.crunchbase.com/
- **Years Available:** 2011 - 2019
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/crunchbase/gbp_venture_capital_received.csv)


## Knowledge exchange and commercialisation
### Total number of unique inventions involving organisations in the NUTS2 region in a year (we consider the earliest application year for all patents in the family)
- **Description:** Total number of unique inventions involving organisations in the NUTS2 region in a year (we consider the earliest application year for all patents in the family)
- **Source:** PATSTAT (https://www.epo.org/searching-for-patents/business/patstat.html)
- **Years Available:** 2013 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/patents/total_inventions.csv)


### Total income from IP licensing in universities located in the NUTS2 region in the academic year starting in year
- **Description:** Total income from IP licensing in universities located in the NUTS2 region in the academic year starting in year
- **Source:** HESA (https://www.hesa.ac.uk/)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_ip_revenues.csv)


### Contract research income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Description:** Contract research income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Source:** HESA (https://www.hesa.ac.uk/)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_business_contract_research.csv)


### Consultancy income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Description:** Consultancy income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Source:** HESA (https://www.hesa.ac.uk/)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_business_consulting.csv)


### Contract research income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Description:** Total external investment in active spinoffs involving local universities in academic year starting in year
- **Source:** HESA (https://www.hesa.ac.uk/)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_investment_per_active_spinoff.csv)


### Total current turnover of active spinoffs involving local universities in academic year starting in year
- **Description:** Total current turnover of active spinoffs involving local universities in academic year starting in year
- **Source:** HESA (https://www.hesa.ac.uk/)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_turnnover_per_active_spinoff.csv)


### Contract research income with businesses for universities in the NUTS2 region in the academic year starting in year
- **Description:** Total number of active startup companies involving graduates from universities in the region in the academic year that starts in year
- **Source:** HESA (https://www.hesa.ac.uk/)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/total_active_graduate_spinouts.csv)


### Consultancy income with public sector and third sector organisatoins involving universities in the NUTS2 region in the academic year starting in year
- **Description:** Consultancy income with public sector and third sector organisatoins involving universities in the NUTS2 region in the academic year starting in year
- **Source:** HESA (https://www.hesa.ac.uk/)
- **Years Available:** 2014 - 2017
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/hebci/gbp_non_business_consulting.csv)


### Total number of trademarks in scientific and technological product fields published by organisations in the region based on the IPO open trademark dataset
- **Description:** Total number of trademarks in scientific and technological product fields published by organisations in the region based on the IPO open trademark dataset
- **Source:** IPO (https://www.gov.uk/government/organisations/intellectual-property-office)
- **Years Available:** 2010 - 2027
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/trademarks/total_trademarks_scientific.csv)


### Total number of trademarks published by organisations in the region based on the IPO open trademark dataset
- **Description:** Total number of trademarks published by organisations in the region based on the IPO open trademark dataset
- **Source:** IPO (https://www.gov.uk/government/organisations/intellectual-property-office)
- **Years Available:** 2010 - 2027
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/trademarks/total_trademarks.csv)


## Place potential to attract researchers and innovators
### mean pm10 particulate pollution value
- **Description:** Mean PM10 particulate background pollution data at NUTS 2 regions aggregated from 1km x 1km resolution UK data modelled by DEFRA.
- **Source:** DEFRA
- **Years Available:** 2007 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/defra/air_pollution_mean_pm10.csv)


### Total employment in cultural, entertainment and leisure industries
- **Description:** This indicator measures level of employment in cultural, entertainment and leisure industries based on the Business Register Employment Survey. Those sectors are identified as clusters of SIC-4 (industry) codes
- **Source:** ONS (https://www.nomisweb.co.uk)
- **Years Available:** 2016 - 2018
- **Experimental:** Yes
- [Download](https://raw.githubusercontent.com/nestauk/beis-indicators/dev/data/processed/industry/employment_culture_entertainment_recreation.csv)


## Challenge oriented activity
