# Sentinel-2 Acquisition Plans Analysis

This project provides a Python script to automatically download KML files of Sentinel-2A and 2B acquisition plans, convert them to Shapefiles, and analyze the intersection and coverage percentage between tiles and orbits. The results are saved to a CSV file.

## Script

The project consists of a single main script `merge_get_new_acquisition.py` which does the following:

- Checks a specific webpage for new KML files of Sentinel-2A and 2B acquisition plans.
- Downloads any new KML files found and saves them locally.
- Converts each KML file to a Shapefile.
- Calculates the intersection and coverage percentage between each Sentinel-2 tile and each orbit in the acquisition plan.
- Saves the results to a CSV file for each satellite and timestamp.

## Website

You can view the results on the project's website at [http://romainwenger.fr/getCoverage/output.html](http://romainwenger.fr/getCoverage/output.html). The website hosts all the CSV files produced by the script and provides a user-friendly interface to filter and view the data.

## Usage

Run the `merge_get_new_acquisition.py` script to download the latest KML files and process them:

```bash
python merge_get_new_acquisition.py
```

## Dependencies

This project uses the following Python libraries:

- `BeautifulSoup4`: For parsing the webpage to find KML file links.
- `requests`: For sending HTTP requests to download the KML files.
- `geopandas`: For handling geospatial data.
- `shapely`: For geometric operations.
- `pandas`: For data manipulation and analysis.
- `tqdm`: For showing progress bars.
- `subprocess`: For running ogr2ogr command to convert KML files to Shapefiles.

Make sure to install all dependencies before running the script:

```bash
pip install beautifulsoup4 requests geopandas shapely pandas tqdm
```

## Note

The Sentinel-2 tiling grid should be in WGS84 format. This script only takes into account nominal data, as it is the only data distributed to users.
