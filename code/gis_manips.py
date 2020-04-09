
import geopandas as gpd
from geopy.geocoders import Nominatim
import shapely.geometry
import geog
import numpy as np
import re


FIPS_TRACT_NUM = {
       "01":         "ALABAMA",
       "02":         "ALASKA",
       "04":         "ARIZONA",
       "05":         "ARKANSAS",
       "06":         "CALIFORNIA",
       "08":         "COLORADO",
       "09":         "CONNECTICUT",
       "10":         "DELAWARE",
       "11":         "DISTRICT OF COLUMBIA",
       "12":         "FLORIDA",
       "13":         "GEORGIA",
       "15":         "HAWAII",
       "16":         "IDAHO",
       "17":         "ILLINOIS",
       "18":         "INDIANA",
       "19":         "IOWA",
       "20":         "KANSAS",
       "21":         "KENTUCKY",
       "22":         "LOUISIANA",
       "23":         "MAINE",
       "24":         "MARYLAND",
       "25":         "MASSACHUSETTS",
       "26":         "MICHIGAN",
       "27":         "MINNESOTA",
       "28":         "MISSISSIPPI",
       "29":         "MISSOURI",
       "30":         "MONTANA",
       "31":         "NEBRASKA",
       "32":         "NEVADA",
       "33":         "NEW HAMPSHIRE",
       "34":         "NEW JERSEY",
       "35":         "NEW MEXICO",
       "36":         "NEW YORK",
       "37":         "NORTH CAROLINA",
       "38":         "NORTH DAKOTA",
       "39":         "OHIO",
       "40":         "OKLAHOMA",
       "41":         "OREGON",
       "42":         "PENNSYLVANIA",
       "44":         "RHODE ISLAND",
       "45":         "SOUTH CAROLINA",
       "46":         "SOUTH DAKOTA",
       "47":         "TENNESSEE",
       "48":         "TEXAS",
       "49":         "UTAH",
       "50":         "VERMONT",
       "51":         "VIRGINIA",
       "53":         "WASHINGTON",
       "54":         "WEST VIRGINIA",
       "55":         "WISCONSIN",
       "56":         "WYOMING"
}


def get_sourrounding_census_tracts(address, mile_radius=10, use_url=True):
    """ Give names of census tracts within a radius around address

    Note that as of now, the lookup is only performed on a state basis, this
    addresses at state borders will have a "clipped" ball.

    Parameters
    ----------
    address : String
        String containgin address, for instance: 77 Massachusetts Avenue, Cambridge
    mile_radius : Float
        Number of miles around whic census tracts should be included
    use_url: Boolean
        If True, use tract .geojson files on github and not local copies (might be slower)

    Returns
    -------
    census_tract_names : ndarray
        Array of census tract names within radius.
    census_tract_geoids: ndarray
        Array of GEOIDs of census tracts in radius.
    """

    # Geocode address (find coordinates).
    locator = Nominatim(user_agent="ppe", country_bias="US")
    location = locator.geocode(address)

    # Read address coordinates.
    try:
        coords = [location.longitude, location.latitude]
    except AttributeError:
        print(" No valid coordinates found for this address.")

    # Use regex to read out state.
    state = re.search(r", ([^,]+), ([^,]+), ([^,]+)$", location.address).group(1)

    # Read FIPS tract number.
    fips_tract_num = [key for key, val in FIPS_TRACT_NUM.items() if val == state.upper()][0]

    # We now read in the census tract polygons for the corresponding state by using 
    # the .geojson files provided here: https://github.com/arcee123/GIS_GEOJSON_CENSUS_TRACTS
    # or a local copy of these files.
    if use_url:
        url = f"https://raw.githubusercontent.com/arcee123/GIS_GEOJSON_CENSUS_TRACTS/master/{fips_tract_num}.geojson"
        state_dataframe = gpd.read_file(url)
    else:
        # Must have a local copy of the repository above in folder staticfiles.
        state_dataframe = gpd.read_file(f'code/staticfiles/GIS_GEOJSON_CENSUS_TRACTS-master/{fips_tract_num}.geojson')

    # Generate GEOJSON file corresponding to a circle of corresponding radius around address.
    p = shapely.geometry.Point(coords)
    n_points = 20
    d = mile_radius * 1609  # meters
    angles = np.linspace(0, 360, n_points)
    radius_ball_array = geog.propagate(p, angles, d)

    # For debugging purposes, uncomment the following line and inspect the geojson.
    # radius_ball_geojson = json.dumps(shapely.geometry.mapping(shapely.geometry.Polygon(radius_ball_array)))

    # Find intersection between circle and census tract polygons
    radius_ball_geoseries = gpd.GeoSeries([shapely.geometry.Polygon(radius_ball_array)])
    radius_ball_dataframe = gpd.GeoDataFrame({"geometry": radius_ball_geoseries})
    res_intersection = gpd.overlay(state_dataframe, radius_ball_dataframe, how="intersection")

    # For debugging purposes, export this intersection to geojson file and view
    # res_intersection.to_file("diff.geojson", driver="GeoJSON")

    # Now, read out the GEODIS and census tract names of the census tracts in the intersection.
    census_tract_names = res_intersection["NAMELSAD"]
    census_tract_geoids = res_intersection["GEOID"]

    return census_tract_geoids, census_tract_names


def demo():
    """Demo the functionality of get_sourrounding_census_tracts"""

    address = "77 Massachusetts Avenue, Cambridge"
    radius = 10
    census_tract_geoids, census_tract_names = get_sourrounding_census_tracts(address)
    print(f"The census tract names surounding a {radius}-mile radius around {address} are:")
    print(census_tract_names)

if __name__ == "__main__":
    # execute only if run as a script
    demo()