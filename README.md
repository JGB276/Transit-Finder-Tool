# TESS Transit Finder Script

A Python script for retrieving and filtering transit observation data from the Swarthmore TESS Transit Finder tool. This script helps observers identify potential exoplanet transit observations based on customizable parameters and filtering criteria.

## Features

- Retrieves transit data from the Swarthmore TESS Transit Finder web interface
- Configurable filtering options for:
  - Visual magnitude
  - Transit depth
  - Planet radius
  - Time windows
- Automatically excludes targets marked as "No more observations needed"
- Ensures 100% transit observability
- Exports filtered results to CSV format

## Prerequisites

The script requires the following Python packages:
- BeautifulSoup4
- requests
- pandas
- datetime
- lxml

You can install these dependencies using pip:
```bash
pip install beautifulsoup4 requests pandas lxml
```

## Configuration

The script uses several configuration parameters that can be modified at the top of the file:

### Basic Settings
```python
date = '02-05-2025'  # Night of observations in local time
filename_save = 'TESS_Targets-' + date + '.csv'  # Output filename
```

### Filter Parameters
```python
apply_v_mag_cut = [True, 10]  # [Enable filter, Maximum magnitude]
apply_depth_cut = [False, 5.0]  # [Enable filter, Maximum depth in ppt]
apply_radius_cut = [True, 0.1, 8]  # [Enable filter, Min radius (Re), Max radius (Re)]
apply_time_cut = [False, time(12, 0), time(14, 0)]  # [Enable filter, Start time, End time]
```

### Observatory Parameters
The script is configured with default parameters for the Palomar Observatory:
- Latitude: 33.3558°N
- Longitude: 116.865°W
- Timezone: America/Los_Angeles
- Minimum elevation: 19°
- Maximum airmass: 3.0
- Twilight angle: -12° (Astronomical twilight)

## Usage

1. Configure the desired parameters in the script
2. Run the script:
```bash
python transit_finder.py
```
3. The script will:
   - Connect to the Swarthmore TESS Transit Finder
   - Retrieve transit data based on the specified parameters
   - Apply the configured filters
   - Save the results to a CSV file

## Output

The script generates a CSV file containing the following information for each transit:
- Object Name (TOI designation)
- Visual magnitude
- Orbital period (days)
- Transit depth (parts per thousand)
- Planet radius (Earth radii)
- Local evening date
- Start, mid, and end times (UTC)
- Transit duration and uncertainty
- Percentage of transit observable
- Percentage of baseline observable
- Comments and followup status

## Notes

- The script automatically excludes targets marked as "No more observations needed" or "No more SG1 observations needed"
- Only transits with 100% observability are included in the final output
- Missing radius values are set to 0 and logged to the console
- Time filters use UTC
