import pandas as pd
import urllib

def get_population(url, years, outfile):
    '''Inputs a URL for a census bureau population estimate data set and a range of years and outputs a cleaned data frame in the desired
    format, so that it can be reused when the data is updated for 2018, 2019, etc.'''

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
    df = df[col_list][(df['LSAD'] == 'Metropolitan Statistical Area') | (df['LSAD'] == 'County or equivalent')]

    #Convert yearly columns to year and population fields, rename columns more descriptively.
    cols_rename = ['AREA_NAME', 'AREA_TYPE', 'POPULATION', 'YEAR']
    df_final = pd.DataFrame()
    for i in years:
        col = 'POPESTIMATE%d'%i
        temp_df = df[base_cols + [col]]
        temp_df['YEAR'] = i
        temp_df.columns = cols_rename
        df_final = pd.concat([df_final, temp_df])

    #Reorder the columns to fit dimensional format
    cols_reorder = ['YEAR', 'AREA_NAME', 'AREA_TYPE', 'POPULATION']
    df_final = df_final[cols_reorder]

    #Write to csv
    df_final.to_csv(outfile, header=False, index=False)

def get_unemployment(url_list, outfile):
    '''For a list of URLs to excel files hosted by the Bureau of Labor Statistics, extracts the per county annual unemployment
    rate, cleans and writes to a single csv file.'''

    #For each URL, pulls desired columns and adds to single data frame.
    df = pd.DataFrame()
    for url in urls:
        urllib.request.urlretrieve(url, "temp.xlsx")
        df_temp = pd.read_excel('temp.xlsx', skiprows = range(0, 5))
        df_temp = df_temp[[df_temp.columns[i] for i in [3,4,9]]]
        df = pd.concat([df, df_temp])

    #Name columns more descriptively.
    df.columns = ['COUNTY_NAME', 'YEAR', 'UNEMPLOYMENT_RATE']

    #Remove rows with NaN.
    df = df.dropna(how = 'any')

    #Recast YEAR from float to int.
    df['YEAR'] = df['YEAR'].astype(int)

    #Write to outfile.
    df.to_csv(outfile, header=False, index=False)

#Call population function
pop_url = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2017/metro/totals/cbsa-est2017-alldata.csv'
pop_years = range(2010, 2018)
get_population(pop_url, pop_years, 'population.csv')

#Call unemployment function
urls = ['https://www.bls.gov/lau/laucnty%d.xlsx'%i for i in range(10, 18)]
get_unemployment(urls, 'unemployment_rate.csv')
