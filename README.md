# BEIS Indicators

Regional indicators for BEIS to assess regional conditions needed for value for money of regional R&D spend.

## Introduction

In this project, Nesta have worked closely with BEIS to create an open repository of indicators capturing various dimensions of innovation and its drivers in regions across the UK.
​
We have also built a tool to visualise and explore these indicators with the goal of informing policies to drive innovation and growth across all of the UK.
​
All this work has been performed with support from BEIS.
​
Our indicators are arranged in four broad categories:
​
* Public R&D Capability, measuring the quantity and excellence of R&D activity taking place in higher education institutions in a region.
* Business R&D Capability, measuring the level of R&D activity and innovative outputs in the private sector in a region
* Knowledge exchange, measuring the connectivity between higher education institutions in a region and the wider economy
* Place potential, measuring wider infrastructures and framework conditions in a region that might drive - or hinder - its innovative performance.
Collapse

## Methodology

### Data sources
​
As much as possible we have used data from official sources such as ONS, Eurostat, HESA or UKRI. One reason to do this is to enable the reproducibility of our analysis, and to remove the reliance of the tool on proprietary sources.
​
Having said this, in a small number of instances we have used proprietary data sources such as PATSTAT for the analysis of patenting, and CrunchBase for the analysis of venture capital investment.
​
### Geographies
​
We use NUTS2 regions as our geographical unit of analysis. This has allowed us to collect data about regional R&D activity which is only available at that level. We note that were possible we have also calculated indicators at a higher level of granularity (NUTS3) as well as using policy-relevant LEPs boundaries. These will be released when the tool is published later in 2020.
​
In many cases we have reverse geocoded observations available at high level of geographical resolution (for example, the geographical coordinates of a higher education institution) using NUTS2 boundary files available from Eurostat. When doing this, we have assigned observations to regions in the NUTS2 version that was in use at the time when the data were collected / when the events captured in the data took place.
​
### Data processing
​
In general, we have avoided complex data processing beyond what was required to aggregate data at our preferred level of geographical resolution. There are however a couple of exceptions to this:
​
* We have calculated indices of economic complexity for UK regions used the algorithm developed by Hausman and Hidalgo (2009)
* We have measured levels of employment in entertainment and cultural sectors using an industrial segmentation based on the methodology developed by Delgado et al (2015)
* We have identified UKRI-funded research projects in STEM disciplines using a machine learning analysis of project descriptions presented in Mateos-Garcia (2017)
​
We indicate those indicators based on experimental methodologies or data sources where relevant.
