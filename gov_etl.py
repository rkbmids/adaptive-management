#!/usr/bin/python

import pandas as pd
import urllib
import sqlite3
import csv
import sys

def get_population(url, years, outfile):
    '''Inputs a URL for a census bureau population estimate data set and a range
     of years and outputs a cleaned data frame in the desired format, so that it
      can be reused when the data is updated for 2018, 2019, etc.'''

    #Pull data and write to temp csv
    response = urllib.request.urlretrieve(url, 'temp.csv')

    #Convert to utf-8 encoding
    with open('temp.csv', 'rt', encoding = "ISO-8859-1") as f:
        with open('temp2.csv', 'wt', encoding = "utf-8") as f2:
            for line in f:
                f2.write(line)

    #Read as pandas df and pull out relevant columns and rows
    df = pd.read_csv('temp2.csv')
    base_cols = ['NAME', 'LSAD']
    col_list = base_cols + ['POPESTIMATE%d'%i for i in years]
    df = df[col_list][(df['LSAD'] == 'Metropolitan Statistical Area') |
        (df['LSAD'] == 'County or equivalent')]

    #Convert yearly columns to year & population fields, rename descriptively.
    cols_rename = ['AREA_NAME', 'AREA_TYPE', 'POPULATION', 'YEAR']
    df_final = pd.DataFrame()
    for i in years:
        col = 'POPESTIMATE%d'%i
        temp_df = df[base_cols + [col]].copy()
        temp_df['YEAR'] = i
        temp_df.columns = cols_rename
        df_final = pd.concat([df_final, temp_df])

    #Write to csv
    df_final.to_csv(outfile, header=True, index=False)

def get_unemployment(url_list, outfile):
    '''For a list of URLs to excel files hosted by the Bureau of Labor
    Statistics, extracts the per county annual unemployment
    rate, cleans and writes to a single csv file.'''

    #For each URL, pulls desired columns and adds to single pandas data frame.
    df = pd.DataFrame()
    for url in url_list:
        urllib.request.urlretrieve(url, "temp.xlsx")
        df_temp = pd.read_excel('temp.xlsx', skiprows = range(0, 5))
        df_temp = df_temp[[df_temp.columns[i] for i in [3,4,9]]]
        df = pd.concat([df, df_temp])

    #Name columns more descriptively
    df.columns = ['COUNTY_NAME', 'YEAR', 'UNEMPLOYMENT_RATE']

    #Remove rows with NaN.
    df = df.dropna(how = 'any')

    #Recast YEAR from float to int.
    df['YEAR'] = df['YEAR'].astype(int)

    #Write to outfile.
    df.to_csv(outfile, header=True, index=False)

def write_to_db(db_file, pop_file, unemp_file):
    '''Creates and/or connects to an SQLite database and creates tables named
    POPULATION and UNEMPLOYMENT_RATE loading from two specified csv files.'''
    try:
        #Connect to SQLite
        c = sqlite3.connect(db_file)
        print('\nConnected to %s using SQLite Version %s...\n'%(db_file,
            sqlite3.version))
    except sqlite3.Error as e:
        print("Connection to %s failed:"%db_file)
        print(e)
        quit()
    try:
        #Create schema
        c.execute("CREATE TABLE POPULATION("+\
            "YEAR INTEGER NOT NULL," +\
            "AREA_NAME TEXT NOT NULL," +\
            "AREA_TYPE TEXT NOT NULL," +\
            "POPULATION INTEGER NOT NULL," +\
            "PRIMARY KEY (YEAR, AREA_NAME, AREA_TYPE));")
        c.execute("CREATE TABLE UNEMPLOYMENT_RATE(" +\
            "YEAR INTEGER NOT NULL," +\
            "COUNTY_NAME TEXT NOT NULL," +\
            "UNEMPLOYMENT_RATE REAL NOT NULL," +\
            "PRIMARY KEY (YEAR, COUNTY_NAME));")
        #Load data
        with open(pop_file,'rt') as file:
            dr = csv.DictReader(file) # comma is default delimiter
            to_db = [(i['YEAR'], i['AREA_NAME'], i['AREA_TYPE'],
                i['POPULATION']) for i in dr]
            c.executemany("INSERT INTO POPULATION (YEAR, AREA_NAME, AREA_TYPE," +\
                " POPULATION) VALUES (?, ?, ?, ?);", to_db)
        with open(unemp_file,'rt') as file:
            dr = csv.DictReader(file) # comma is default delimiter
            to_db = [(i['YEAR'], i['COUNTY_NAME'], i['UNEMPLOYMENT_RATE'])
                for i in dr]
            c.executemany("INSERT INTO UNEMPLOYMENT_RATE (YEAR, COUNTY_NAME, "+\
                "UNEMPLOYMENT_RATE) VALUES (?, ?, ?);", to_db)
        print("\nData Loaded...\n")
        c.commit()
        c.close()
        print("\nDB connection committed and closed. Job complete.\n")
    except sqlite3.Error as e:
        #If data tables already exist and throw error, ends process.
        #To update rather than recreate table this would need to be modified.
        print("\nTables already populated. Load aborted.")
        c.close()

def main():
    #Call population function
    pop_url = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2017/metro/totals/cbsa-est2017-alldata.csv'
    pop_years = range(2010, 2018)
    pop_file = 'population.csv'
    get_population(pop_url, pop_years, pop_file)
    print('\n\nPopulation File Populated...\n')

    #Call unemployment function
    urls = ['https://www.bls.gov/lau/laucnty%d.xlsx'%i for i in range(10, 18)]
    unemp_file = 'unemployment_rate.csv'
    get_unemployment(urls, unemp_file)
    print('\nUnemployment File Populated...\n')

    #Create/connect to and write to DB file passed in command line args
    write_to_db(sys.argv[1], pop_file, unemp_file)

if __name__ == "__main__":
    main()
