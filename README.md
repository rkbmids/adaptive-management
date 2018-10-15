#Getting Started
##Dependencies
###Install SQLite
Create a folder for sqlite using a shell or File Explorer.

Download SQLite from the following URL: https://www.sqlite.org/download.html

I downloaded the precompiled binary bundle for Windows. 

Using the Windows File Explorer, unzip the folder and copy the files into your sqlite directory. 

Verify the installation by typing sqlite3 into the Windows Command Prompt - this should start the SQLite interpreter.

###Python Dependencies
The following libraries are required and should be installed through pip:
```
pip install pandas
pip install urlib
```

##Process
###Download and Process Data
Using your command prompt, run the extract_transform.py file.
```
python extract_transform.py
```
This will show a warning message but everything works as expected. You should expect to see two files created, population.csv and unemployment_rate.csv.

###Create Database
Using your command prompt, navigate to the folder where you ran extract_transform.py and enter:
```
sqlite3 adaptive.db
```

This will create a new database and start the interpreter.
Create tables using the following DDL:
```
CREATE TABLE population(
	YEAR INTEGER NOT NULL,
	AREA_NAME TEXT NOT NULL,
	AREA_TYPE TEXT NOT NULL,
	POPULATION INTEGER NOT NULL);

CREATE TABLE unemployment_rate(
	COUNTY_NAME TEXT NOT NULL, 
	YEAR INTEGER NOT NULL,
	UNEMPLOYMENT_RATE REAL NOT NULL);
```
You can verify this worked by running:
```
.schema population
.schema unemployment_rate
```
To load the data, run:
```
.mode csv
.import unemployment_rate.csv unemployment_rate
.import population.csv population
```
You can verify the load worked by running:
```
SELECT * FROM unemployment_rate limit 5;
SELECT * FROM population limit 5;
```
###Using the Database
To reopen the database from the file using the SQLite command line, run the following within the SQLite interpreter:
```
.open adaptive.db
```

####Customer Queries
Many options are available to connect to, query and extract dat from an SQLite DB. 

The customer who wants to study the annual population data for major metropolitan areas can use data extracted with the following query:
```
SELECT * FROM population WHERE AREA_TYPE = "Metropolitan Statistical Area";
```
The customer who wants to study the population and unemployment rate per county can use data extracted with the following query:
```
SELECT COUNTY_NAME, unemployment_rate.YEAR, UNEMPLOYMENT_RATE, POPULATION FROM unemployment_rate LEFT JOIN population ON unemployment_rate.COUNTY_NAME=population.AREA_NAME AND unemployment_rate.YEAR=population.YEAR;
```
#References

## Data Source Pages
Population: https://www2.census.gov/programs-surveys/popest/datasets/

Unemployment: https://www.bls.gov/lau/

