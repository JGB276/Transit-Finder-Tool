from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime, time

"""
TESS Transit Finder Script
This script scrapes and processes transit data from the Swarthmore TESS Transit Finder tool.
It retrieves information about potential transit observations based on specified parameters
and filters the results according to various criteria. The filtered data is saved as a csv file.
"""

# Configuration parameters
date = '02-05-2025' # the night of the observations in local time
filename_save = 'TESS_Targets-' + date + '.csv' # name for saving the retrieved data

# Filter settings
apply_v_mag_cut = [True, 10] # Visual magnitude filter: [Apply?, Maximum magnitude]
apply_depth_cut = [False, 5.0] # Transit depth filter: [Apply?, Maximum depth in parts per thousand]
apply_radius_cut = [True, 0.1, 8] # Planet radius filter: [Apply?, Min radius (Re), Max radius (Re)]
apply_time_cut = [False, time(12, 0), time(14, 0)] # Time window filter: [Apply?, Start time, End time]

# Parameters for the Swarthmore Transit Finder query
params = {
    'observatory_string': '33.3558;-116.865;America/Los_Angeles;Palomar Observatory;Palomar Observatory',
    'use_utc': '1',
    'observatory_latitude': '33.3558',
    'observatory_longitude': '-116.865',
    'timezone': 'UTC',
    'start_date': date, # Can be 'today' or specific date
    'days_to_print': '1', # Number of days to look ahead
    'days_in_past': '0',
    'minimum_start_elevation': '19', # Minimum elevation at transit start
    'and_vs_or': 'or',
    'minimum_end_elevation': '19',
    'minimum_ha': '-6.4',
    'maximum_ha': '6.4',
    'baseline_hrs': '10.1',
    'maximum_priority': '4',
    'minimum_depth': '0.2',
    'maximum_V_mag': '',
    'target_string': '',
    'lco_only': '0',
    'single_object': '0',
    'ra': '',
    'dec': '',
    'epoch': '',
    'period': '',
    'duration': '',
    'target': '',
    'show_ephemeris': '0',
    'print_html': '1',
    'twilight': '-12', # Astronomical twilight angle
    'max_airmass': '3.0', # Maximum allowable airmass
    'fovWidth': '',
    'fovHeight': '',
    'fovPA': '',
}

# HTTP request headers including authentication
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Authorization': 'Basic dGVzc19uZGFfb2JzZXJ2ZXI6RjFuZF9URSRTX1BsYU5ldHMh', # unique to the user
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}

# Make HTTP request to fetch transit data
response = requests.get(
    'https://astro.swarthmore.edu/telescope/tess-secure/print_eclipses.cgi',
    params=params,
    headers=headers,
)

if response.status_code == 200:
    print('Success! Data has been accessed')


# Parse the HTML response using BeautifulSoup
soup = BeautifulSoup(response.text, 'lxml')
table1 = soup.find('table', id='target_table') # Find the main data table

# Extract table headers
headers = []
for i in table1.find_all('th'): # get headers from table
    title=i.text
    headers.append(title)


headers[1] = 'Name' # let's change the name for convenience

my_data = pd.DataFrame(columns=headers) # create dataframe to fill in

for j in table1.find_all('tr')[1:]: # loop to get data of each row in the table
    row_data = j.find_all('td')
    row = [i.text for i in row_data]
    length = len(my_data)
    my_data.loc[length] = row

# let's split the info in the rows into strings to make it easier to parse the data we want
my_data[' Local evening date '] = my_data[' Local evening date '].str.split()
my_data['Name'] = my_data['Name'].str.split()
my_data[' V mag '] = my_data[' V mag '].str.split()
my_data[' Start—Mid —End '] = my_data[' Start—Mid —End '].str.split()
my_data[' Duration '] = my_data[' Duration '].str.split()
my_data[' % of transit (baseline) observable, Suggested\n\t    obs. start, end '] = my_data[' % of transit (baseline) observable, Suggested\n\t    obs. start, end '].str.split()

nrows = len(my_data.index) # we will needs this for the following loops

evening_dates = []
for i in range(nrows):
    date = my_data[' Local evening date '][i][0] + ' ' + my_data[' Local evening date '][i][1]
    evening_dates.append(date)

tois = []
for i in range(nrows):
    toi_name = my_data['Name'][i][2].replace('(', '') + ' ' + my_data['Name'][i][3].replace(')', '')
    tois.append(toi_name)

vmags = []
for i in range(nrows):
    v_mag = float(my_data[' V mag '][i][0])
    vmags.append(v_mag)

start = []
mid = []
end = []
for i in range(nrows):
    times = my_data[' Start—Mid —End '][i][1:4]
    s = times[0].replace('—', '')
    m = times[1]
    e = times[2].replace('—', '')
    start.append(s)
    mid.append(m)
    end.append(e)

dur = []
uncer = []
for i in range(nrows):
    duration = my_data[' Duration '][i][0]
    dur_uncer = my_data[' Duration '][i][1].replace('±', '')
    dur.append(duration)
    uncer.append(dur_uncer)

percent_trans = []
percent_base = []
for i in range(nrows):
    per_trans = my_data[' % of transit (baseline) observable, Suggested\n\t    obs. start, end '][i][0]
    per_base = my_data[' % of transit (baseline) observable, Suggested\n\t    obs. start, end '][i][1].replace('(','').replace(')','')
    percent_trans.append(per_trans)
    percent_base.append(per_base)


radius_array = my_data[' Rplanet(R⊕)'].to_numpy() # need to deal with empty radii sometimes.

for i in range(len(radius_array)):
    if radius_array[i] == ' ':
        radius_array[i] = 0
        print('No radius available for ' + str(tois[i]))
    else:
        radius_array[i] = float(radius_array[i])

clean_data = {'Object Name':tois,
             'Vmag':vmags,
             'Period (days)':my_data[' Period (days) '],
             'Depth (ppt)':my_data[' Depth (ppt) '].astype(float),
             'Radius (Re)':radius_array,
             'Local Evening Date':evening_dates,
             'Start Time (UTC)':start,
             'Mid Time (UTC)':mid,
             'End Time (UTC)':end,
             'Duration (hours)':dur,
             'Uncert. Duration (hours)':uncer,
             'Percent Trans Obs.':percent_trans,
             'Percent Base Obs.':percent_base,
             'Comments':my_data[' Comments and followup status ']}

df_clean = pd.DataFrame(clean_data)

# This is where we apply the filters to the DataFrame. E.g., if you want only bright giant planets
# modify the v_mag_cut and the radius_cut.
# Here's where you can also apply more cuts to the data.

# Apply the start time filter if enabled
if apply_time_cut[0]:
    df_clean['Start Time'] = pd.to_datetime(df_clean['Start Time (UTC)'], format='%H:%M').dt.time
    df_clean = df_clean[df_clean['Start Time'] > apply_time_cut[1]]
    df_clean = df_clean[df_clean['Start Time'] < apply_time_cut[2]]
    df_clean = df_clean.drop('Start Time', axis=1)

if apply_v_mag_cut[0] == True:
    df_clean = df_clean[df_clean.Vmag > apply_v_mag_cut[1]] # we really only want dim sources in the optical for wirc

if apply_depth_cut[0] == True:
    df_clean = df_clean[df_clean['Depth (ppt)'] <= apply_depth_cut[1]]

if apply_radius_cut[0] == True:
    df_clean = df_clean[df_clean['Radius (Re)'] <= apply_radius_cut[2]]
    df_clean = df_clean[df_clean['Radius (Re)'] >= apply_radius_cut[1]]

# Exclude rows with 'No more observations needed' in the Comments column
df_clean = df_clean[~df_clean['Comments'].str.contains('No more observations needed', case=False, na=False)]
df_clean = df_clean[~df_clean['Comments'].str.contains('No more SG1 observations needed', case=False, na=False)]
# Include only rows with 100% under the Percent Trans Obs. column
df_clean = df_clean[df_clean['Percent Trans Obs.'] == '100%']

df_clean.to_csv(filename_save, index=False)
print('Data written to file' + ' ' + filename_save)
