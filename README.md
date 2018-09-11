# README #

Python script for exporting gemini compliant metadata from a csv file to individual xml files.

### How do I get set up? ###

* Create a virtual environment in the root directory
* Activate the virtual environment
* Install dependencies by running pip install -r requirements.txt
* See the sample csv file for the correct layout- alternatively change the column mappings in metadata_import.py to match your layout
* Place your csv file in the input folder
* Change to the python directory
* Count the total number of rows in your CSV including the header row and edit the numrows line (28) in metadata_import_.py to match
* Run python metadata_import_.py
* Your xml files will miraculously appear in the output folder
* Check error.log in the python folder for details of any records that failed- these will be listed by title with the details of the error
* Encoding errors in the source CSV may currently cause the script to fail. The offending bytecode will be shown in the error message so you can replace it in the source data with the correct symbol

### Data Specifics ###

* Creation Date and Revision Date can be of the form YYYY-MM-DD or DD/MM/YYYY
* Descriptive Keywords can be a comma-separated list
* Topic Category must be one of the following (case-sensitive), but can be a comma-separated list:
  * farming
  * biota
  * boundaries
  * climatologyMeteorologyAtmosphere
  * economy
  * elevation
  * environment
  * geoscientificInformation
  * health
  * imageryBaseMapsEarthCover
  * intelligenceMilitary
  * inlandWaters
  * location
  * oceans
  * planningCadastre
  * society
  * structure
  * transportation
  * utilitiesCommunication
* West, East, North, South bounding coordinates must be in WGS84 format (lat/lon)
* Temporal Extent can be a comma-separated list (begin date, end date) but dates must be in form YYYY-MM-DD or DD/MM/YYYY
* Data Format and Version can be comma-separated lists but must come from provided lists of formats and versions, see [iso19139.gemini22/loc/eng/labels.xml](https://github.com/AstunTechnology/iso19139.gemini22_GN3/blob/3.4.x/src/main/plugin/iso19139.gemini22/loc/eng/labels.xml#L1595)
* Data Quality Info must be one of dataset or nonGeographicDataset (case-sensitive)
* Inspire theme (case-sensitive) must come from the INSPIRE Themes Thesaurus in Geonetwork (choose one only)
* Update Frequency is case-sensitive, choose from the following codes:
  * continual
  * daily
  * weekly
  * fortnightly
  * monthly
  * quarterly
  * biannually
  * annually
  * asNeeded
  * irregular
  * notPlanned
* If the record is OpenData, modify the script to use the opendata template, DO NOT include it in the list of keywords
* The copyright statement should not include the copyright symbol, a correctly encoded version of this will be included automatically

### Who do I talk to? ###

* jocook@astuntechnology.com
* Other Astun personnel
* Based on code originally written by Brian O'Hare