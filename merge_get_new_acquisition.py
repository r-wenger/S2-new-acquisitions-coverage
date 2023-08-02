"""
File: merge_get_new_acquisition.py
Author: Romain Wenger
Email: romain.wenger@live-cnrs.unistra.fr
Github: https://github.com/r-wenger
Description: Script to calculate the intersection and coverage percentage between tiles and orbits. It also check if new acqusition plans are avaiblable.
To get the acquisition plan : https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2/acquisition-plans
We are only taking into account Nominal data, as it is the only data distributed to Users.
Be aware that you your Sentinel-2 tiling grid should be in WGS84 format.
"""
from bs4 import BeautifulSoup
import requests
import os
import geopandas as gpd
from shapely.geometry import Polygon
import pandas as pd
from tqdm import tqdm
import subprocess

def process_kml_file(sat, kml_file_path):
    # Run the ogr2ogr command
    shp_path = '/Users/rwenger/Documents/postdoc/get_orbit/' + str(sat) + '_orbit_polygons.shp'
    subprocess.run(["ogr2ogr", "-f", "ESRI Shapefile", shp_path, kml_file_path, "NOMINAL"], check=True)

    # Load the shapefiles
    tiles_s2 = gpd.read_file('/Users/rwenger/Documents/postdoc/get_orbit/Tiles_S2_earth.shp')
    orbit_polygons = gpd.read_file(shp_path)

    # Initialize an empty dataframe to store results
    results = pd.DataFrame(columns=['Tile', 'Orbit', 'IntersectionArea', 'TileArea', 'Percentage', 'BeginTime', 'EndTime', 'Satellite', 'link'])

    # Iterate through each tile
    for i, tile in tqdm(tiles_s2.iterrows(), total=tiles_s2.shape[0], desc="Processing tiles"):
        # Get tile area
        tile_area = tile.geometry.area

        # Iterate through each orbit
        for j, orbit in orbit_polygons.iterrows():
            # Get intersection of tile and orbit
            intersection = tile.geometry.intersection(orbit.geometry)
            
            # Only consider intersections that are non-empty and are polygons (to exclude lines/points)
            if not intersection.is_empty and isinstance(intersection, Polygon):
                # Get intersection area
                intersection_area = intersection.area
                
                # Calculate percentage of tile covered by orbit
                percentage = (intersection_area / tile_area) * 100
                
                # Sauvegardez l'intersection sous forme de fichier GeoPackage
                filename = f"{tile.Name}_{orbit.OrbitRelat}_{orbit.begin}_{sat}.gpkg"
                filepath = f"intersections/{filename}"
                gpd.GeoDataFrame(geometry=[intersection]).to_file(filepath, driver="GPKG")

                # Créez le lien de téléchargement pour le fichier gpkg
                download_link = f"http://romainwenger.fr/getCoverage/intersections/{filename}"

                # Append result to dataframe including the link
                results = results.append({
                    'Tile': tile.Name,
                    'Orbit': orbit.OrbitRelat,
                    'IntersectionArea': intersection_area,
                    'TileArea': tile_area,
                    'Percentage': percentage,
                    'BeginTime': orbit.begin,
                    'EndTime': orbit.end,
                    'Satellite' : sat,
                    'link': download_link
                }, ignore_index=True)

    # Extract the timestamp from the KML file name
    kml_file_basename = os.path.basename(kml_file_path)
    start_timestamp = kml_file_basename.split('_')[5][:8]
    end_timestamp = kml_file_basename.split('_')[6][:8]
    timestamp = start_timestamp + '_' + end_timestamp

    # Save the result to a csv file with timestamp in the filename
    results.to_csv('results_' + str(sat) + '_' + timestamp + '.csv', index=False)


# URL of the webpage
url = 'https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2/acquisition-plans'
path_my_directory = '/Users/rwenger/Documents/postdoc/get_orbit/acquisition_plans'

# Send HTTP request to URL and save the response from server in a response object called r
r = requests.get(url)

# Create a BeautifulSoup object and specify the parser library
soup = BeautifulSoup(r.text, 'html.parser')

# Find the Sentinel-2A and Sentinel-2B divs
divs = soup.find_all('div', {'class': ['sentinel-2a', 'sentinel-2b']})

# Loop through all divs
for div in divs:
    # Get the satellite name
    sat = div.find('h4').text.strip()
    
    # Find all 'a' tags (which define hyperlinks) within the div
    links = div.find_all('a')

    # Loop through all links
    for link in links:
        # Get the href attribute of the link
        kml_file_link = link.get('href')

        # Split the link into parts
        kml_file_link_parts = kml_file_link.split('/')

        # Uppercase the last part of the link
        kml_file_link_parts[-1] = kml_file_link_parts[-1].upper()

        # Join the parts back together to form the new link
        kml_file_link = '/'.join(kml_file_link_parts)

        # Construct the full URL for the KML file
        full_kml_file_url = "https://sentinels.copernicus.eu" + kml_file_link

        # If this KML file is not downloaded yet
        if not os.path.exists(os.path.join(path_my_directory, os.path.basename(kml_file_link))):
            # Download the KML file
            print(full_kml_file_url)
            r = requests.get(full_kml_file_url, allow_redirects=True)
            kml_file_path = os.path.join(path_my_directory, os.path.basename(kml_file_link))
            open(kml_file_path, 'wb').write(r.content)

            # Process the downloaded KML file
            process_kml_file(sat, kml_file_path)
        else:
            print('Files are up to date !')
