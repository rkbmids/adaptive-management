# Getting Started
## Dependencies
### Install SQLite
Create a folder for sqlite using a shell or File Explorer. Download SQLite from the following URL: https://www.sqlite.org/download.html
I downloaded the precompiled binary bundle for Windows. Unzip the folder and copy the files into your sqlite directory.
Verify the installation by typing sqlite3 into the Windows Command Prompt - this should start the SQLite interpreter.

### Python Dependencies
Program uses Python 3.
You should install pandas through pip if you do not already have it:
```
pip install pandas
```

## Extract from Data.gov, Transform and Load the SQLite DB
Using your command prompt, run the Python script and specify the name of your desired SQLite database.
The database will be created if it does not already exist.
```
python gov_etl.py 'adaptive.db'
```
This will show a few status messages.
If the tables already exist in the database, they will not be reloaded and the last message will be:
"Tables already populated. Load aborted." This error handling would need to be enhanced to handle repeated loads.
The program will never create an empty table and save it to the database.
If the tables do not exist, they will be created and loaded and the last message will be:
"DB connection committed and closed. Job complete."

## Customer Queries
Many options are available to connect to, query and extract data from an SQLite DB.

The customer who wants to study the annual population data for major metropolitan areas can use data extracted with the following query, which could be saved as a view for their convenience:
```
SELECT * FROM population WHERE AREA_TYPE = "Metropolitan Statistical Area";
```
The customer who wants to study the population and unemployment rate per county can use data extracted with the following query, which could be saved as a view for their convenience:
```
SELECT COUNTY_NAME, unemployment_rate.YEAR, UNEMPLOYMENT_RATE, POPULATION FROM unemployment_rate LEFT JOIN population ON unemployment_rate.COUNTY_NAME=population.AREA_NAME AND unemployment_rate.YEAR=population.YEAR;
```
# Data Sources
##Parent Folders
Population: https://www2.census.gov/programs-surveys/popest/datasets/
Unemployment: https://www.bls.gov/lau/
##Note
Data included from 2010-2017- while the unemployment data function can easily pull
all years of data, I mistakenly used a format for the population data not available
prior to 2010, and would have to rework that part of the code to extend the range
of data.
