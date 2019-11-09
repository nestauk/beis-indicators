# Lab notes

## HESA + HE-BCI

We access the HESA data by requesting tables from their website. The tables are generally long which makes them relatively easy to analyse, although we need to be careful when selecting categories to avoid double counting. The `filter_data` function takes care of that. 

We aggregate institutions into NUTS using a learning provider metadata file and the `nuts-finder` package developed by Joel. 

We could easily change the output indicators by modifying the code in the notebooks.

There is some repetition and overlaps between the HESA and HE-BCI notebooks because both of them are extracting information from the same website. There is much scope for refactoring.



