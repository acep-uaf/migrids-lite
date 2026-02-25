# MiGRIDS-lite
Welcome to MiGRIDS Lite! MiGRIDS Lite is a smaller and easier to use version of [MiGRIDS](https://github.com/acep-uaf/MiGRIDS), which stands for **Mi**cro**G**rid **R**enewable **I**ntegrattion **D**ispatch and **S**izing.

MiGRIDS Lite is a Python package that is used to model hourly electricity usage when a renewable energy source is added and, optionally, with battery storage. The energy balance calculations take into consideration diesel generator minimum operating load, spinning reserve limits, and more. The renewable energy source is technology agnostic; as long as there is an hourly time series, it can be modeled. Batteries can be user defined, and options for adding multipliers to explore various scenarious is optional.

This software is meant to be a first order estimation of the effect of adding renewable energy and storage. For more information regarding how this is calculated, please see the [wiki](https://github.com/acep-uaf/migrids-lite/wiki).

## What's new in version 1.2?
The previous version only worked with electric loads above the minimum operating load of the powerhouse. This new version rectifies that and allows for the option of having excess diesel energy charge the storage. It also accepts 0 load scenarios.

## MiGRIDS Lite History

MiGRIDS was developed by a research team at the University of Alaska Fairbanks [Alaska Center for
Energy and Power (ACEP)](https://acep.uaf.edu). MiGRIDS was originally developed
as a set of tools under the name Grid Bridging System Tool (GBSTool) by Jeremy VanderMeer and [Marc Mueller-Stoffles](https://github.com/mmuellerstoffels). The GBSTool was then expanded and updated into the MiGRIDS package.

MiGRIDS Lite MATLAB was then created as a one-off MATLAB script by Nathan Green, which then was generalized by Bax Bond in Python utilizing [pandas](https://pandas.pydata.org). This approach uses dataframe manipulations and minimizes the use of loops.

## License

This software is licensed under the  GNU Affero General Public License. See the [LICENSE](LICENSE) for more information.

## Contributors
- Bax Bond - [@b0ndman](https://github.com/b0ndman)
    - Lead developer for MiGRIDS Lite
- Nathan Green - [@njgreen3](https://github.com/njgreen3)
    - Contributor
- Jeremy Vandermeer - [@jbvandermeer](https://github.com/jbvandermeer)
    - Consultant, lead developer of MiGRIDS

 ## Funding
 This research and development was funded by the National Science Foundation under award number 2226015 [NNA Research: Reducing Fuel Oil Consumption in Rural Arctic Communities](https://nna-co.org/research/projects/reducing-fuel-oil-consumption-rural-arctic-communities).
