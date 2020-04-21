import numpy as np
import pandas as pd
import geopandas as gpd
from scipy import stats
import zipcodes


"""
Overview
--------
The primary goal of this algorithm is to priorizie allocation of scarce PPE resources to healthcare workers who provide
acute care for patients with COVID-19 and who are most at risk of infection. This goal is consistent with all
currently published government allocation guidelines [1], and has strong ethical and pragmatic justifications. An
in-depth treatment of the ethical justificaitons for this choice of priority can be found in ref 2, but based
on the assummption that "Harm to health care workers in key sectors of the health care system (i.e., acute and
critical care, specialty services) could greatly impact the ability of the health care system to respond to any
acutely ill patient, including those who acquire COVID-19." [2] and is justified through appeal to maximizing the common
good of public saftey and ensuring reciprocity for healthcare workers who "face a disproportionate buren in protecting
the public good" [2]. Highest prioritization of healthcare workers and justification for this priority based on
reciprocity and maximizing public good have been echoed by both other bioethics experts [3,4,5] as well as the public at large [5].

Beyond prioritization of front-line healthcare workers, a second important goal of this algorithm is to facilitate
equitable access to PPE by prioritizing facilities that serve vulnerable populations. Unlike many existing allocation
guidlines, our algorithm explicitly considers vulnerability and equity alongside factors such as worker exposure and
remaining supply. A full discussion of how and why we consider equity and vulnerability can be found below.

References
----------
1. Survey of PPE allocation guidelines in the context of COVID-19.
GetUsPPE 2020 https://docs.google.com/document/d/1PjTXkOVK1SZpb1Yx2gPBdkemWxjsJFs28jDjNR3VNTY/edit?usp=sharing

2. "COVID-19: Emergency Prioritization in a Pandemic Personal Protective Equipment (PPE) Allocation Framework"
British Columbia Ministry of Health
https://www2.gov.bc.ca/assets/gov/health/about-bc-s-health-care-system/office-of-the-provincial-health-officer/covid-19/ppe_allocation_framework_march_25_2020.pdf

3. "Fair Allocation of Scarce Medical Resources in the Time of Covid-19", NEJM 2020
https://www.nejm.org/doi/full/10.1056/NEJMsb2005114

4. "Responding to COVID‐19: How to Navigate a Public Health Emergency Legally and Ethically", The Hastings Center Report 2020
https://onlinelibrary.wiley.com/doi/10.1002/hast.1090

5. "Citizen Voices on Pandemic Flu Choices: A Report of the Public Engagement Pilot Project on Pandemic Influenza"
Publications of the University of Nebraska Public Policty Center, 2005
https://digitalcommons.unl.edu/publicpolicypublications/2/

Sources of indicator data
-------------------------
Information used by the algorithm to assign priority scores is taken primarily from self-reports from
requesting facilities. We chose to focus on self-reported data for two primary reasons. First, self-report
data can be updated essentially in real time, which is critical for allocation decisions being made during
a rapidly evolving public health crisis. Second, this allows us to collect the same set of indicators from
every requesting facility while minimizing systemic measurement biases such as availability of COVID testing
or lack of universal representation in existing publicly available facility-level data sets.

To the extent that we utilize existing indicator data, we considered only datasets that:
    1) Are publicly available and free to access.
    2) Include recently updated information for all (or almost all) facilities and/or areas in the US.
    2) Have sufficient spatial resolution to allow comparisons across facilities in the same region.
    3) Publicly report all relevant data collection and analysis methods.
"""

##############################################
## Scoring, grouping, and weighting options ##
##############################################

# Set of facility types serving vulnerable or underserved populations
VULN_FACILITIES = ['fqhc', # federally qualified health centers (and look-alikes)
                   'dsh', # medicaid disproportionate share hospital
                   'rhc', # rural health clinic
                   'cah', # critical access hospital
                   'indian_tribal', # indian or tribal healthcare facility
                   'chc', # community health center
                   'hs', # homeless shelter
                   'cf_dt'] # correctional facility or detention center

# Facilities providing life-saving care to the sickest COVID-patients
GROUP_1_FACILITIES = ['ach', # acute care hospital
                     'fs_er', #freestanding emergency room
                     'fh', # field hospital
                     'hof', # hospital overflow facility
                     'ems'] # emergency medical services / fire department


# Residential facilities with limited social distancing and patients at high risk of serious illness
GROUP_2_FACILITEIS = ['nach', # non-acute care hospitals
                     'rp', # residential/inpatient psychiatric facilities
                     'ir', # inpatient rehabilitaiton facilities
                     'rs', # residential substance treatment centers
                     'nh_sn_al', # nursing homes, skilled nursing, and assisted living facilities
                     'ltc', # long term care facilities
                     'gh', # group homes
                     'hs', # homeless shelters
                     'cf_dt'] # correctional facilities and detention centers

# Domain weighting multipliers
NEED_WEIGHT = 1
VULN_WEIGHT = 1
EXPOSURE_WEIGHT = 1
CAPCITY_WEIGHT = 1

###################
## Urgency score ##
###################

urgency_score = 0

# Assign base urgency points based on how long current supply is predicted to last.
# if dat.loc[row_idx,"Current Supply"] is "No supply remaining": # critical need
#     urgency_score += 5
# elif dat.loc[row_idx,"Current Supply"] is "2 days or less": # dire need; future data will be "1–3 days"
#     urgency_score += 4
# elif dat.loc[row_idx,"Current Supply"] is "1 week or less": # urgent need; future data will be "4–7 days"
#     urgency_score += 3
# elif dat.loc[row_idx,"Current Supply"] is "2 weeks or less": # high need; future data will bee "1–2 weeks"
#     urgency_score += 2
# elif dat.loc[row_idx,"Current Supply"] is "More than 2 weeks": # moderate need
#     urgency_score += 1
#
# # Assign Surge Points based on PPE conservation practices
# if dat.loc[row_idx,"Item Surge Capacity"] is "Conventional":
#     need_score *= 1
# elif dat.loc[row_idx,"Item Surge Capacity"] is "Contingency":
#     need_score *= 10
# elif dat.loc[row_idx,"Item Surge Capacity"] is "Crisis":
#     need_score *= 100

########################
# Vulnerability score ##
########################

# vuln_score = 0
#
# for vuln_type in VULN_FACILITIES:
#     if vuln_type in facility_type:
#         vuln_score += 1

# Vulnerability score based on local CDC SVI



def point_from_zip(zcode):
    """
    Get a geopandas point geodataframe from a (valid) zipcode
    """

    z = zipcodes.matching(zcode)[0]
    pdf = pd.DataFrame({
        'zip': [z['zip_code']],
        'lat': [np.float(z['lat'])],
        'lon': [np.float(z['long'])]
    })

    point = gpd.GeoDataFrame(pdf, geometry=gpd.points_from_xy(pdf.lon, pdf.lat), crs=4326)

    return point


def miles_to_meters(miles):
    return miles / 0.00062137


def get_radius_tracts(census_tract_geoms, facility_address, radius):
    """
    Return an array containing 11-digit FIPS codes for each census tract within RADIUS of facility_address.

    Parameters
    ----------
    census_tract_geoms : sting
        file path to shapefile of census tract geometries `tracts_usna.shp` - tracts
        have been projected to US National Atlas Equal Area (EPSG:2163)

    facility_address : tuple
        Tuple of strings in the following format (street_name_and_number, city, state, zip)
        Assumes valid zipcode

    radius : float
        Radius facility address to create a buffer for identifying local census tracts
        in meters (use `miles_to_meters` to convert)

    Returns
    -------
    tract_array : ndarray
        1-dimensional array containing 11-digit FIPS codes for all census tracts within radius
    """

    # Geopandas object for census tracts
    tracts = gpd.read_file(census_tract_geoms)

    zip_code = facility_address[3]

    point = point_from_zip(zip_code)
    point = point.to_crs(tracts.crs)

    # Buffer to radius around point
    point['geometry'] = point.geometry.buffer(radius)

    # Find intersecting census tracts
    intersecting_tracts = gpd.sjoin(tracts, point, how='inner', op='intersects')

    # Get intersecting FIPS codes
    fips = intersecting_tracts['FIPS'].values

    return fips


def get_county(gis_data, facility_address):
    """
    Return the county containing the facility address.

    Parameters
    ----------
    gis_data : <unknown GIS type>
        <data needed to do the fancy GIS stuff>

    facility_address : tuple
        Tuple of strings in the following format (street_name_and_number, city, state, zip)

    Returns
    -------
    county_id : <unknown GIS type>
        <Unique GIS county id>
    """


def get_county(census_tract_geoms, facility_address):
    """
    Return the county containing the facility address.

    Parameters
    ----------
    census_tract_geoms : sting
        file path to shapefile of census tract geometries `tracts_usna.shp` - tracts
        have been projected to US National Atlas Equal Area (EPSG:2163)

    facility_address : tuple
        Tuple of strings in the following format (street_name_and_number, city, state, zip)

    Returns
    -------
    county_id : np.array
        STCOFIPS (State / County FIPS, e.g. 15007). First two numbers correspond to State,
        last 3 numbers correspond to county
    """

    # Geopandas object for census tracts
    tracts = gpd.read_file(census_tract_geoms)

    zip_code = facility_address[3]

    point = point_from_zip(zip_code)
    point = point.to_crs(tracts.crs)

    intersecting_county = gpd.sjoin(tracts, point, how='inner', op='intersects')

    st_county_fips = intersecting_county['STCOFIPS'].values

    return st_county_fips
    
#
# local_svis = get_radius_svis(svi_data, facility_address, RADIUS)
#
# # Local SVI extrema counts (relative to county and region)
# regional_svis = get_regional_svis(svi_data, COUNTIES_LIST)
# county = get_county(facility_address)
# county_svis = get_county_svis(svi_data, county)
# regional_top_quartile_count = np.sum(local_svis >= stats.scoreatpercentile(regional_svis, 75))
# county_top_quartile_count = np.sum(local_svis >= stats.scoreatpercentile(county_svis, 75))
#
# if SVI_COMPARISON is 'region':
#     vuln_score += regional_top_quartile_count
# elif SVI_COMPARISON is 'county':
#     vuln_score += county_top_quartile_count
#
# vuln_score = vuln_score * VULN_WEIGHT
#
# ####################
# ## Exposure score ##
# ####################
#
# exposure_score = 0
#
# if has_covid is True:
#     exposure_score += 10
#
# if has_icu is True:
#     exposure_score += 6
#
# # Aerosol generating procedures but is not an ICU (e.g. freestanding ERs, paramedics)
# if aerosols is True and has_icu is False:
#     exposure_score += 3
#
# exposure_score = exposure_score * EXPOSURE_WEIGHT
#
# ####################
# ## Capacity score ##
# ####################
#
# capacity_score = 0
#
# # Occupancy data is optional.
#
# if bed_occupancy is 100_150:
#     capacity_score += 1
# elif bed_occupancy is 151_200:
#     capacity_score += 2
# elif bed_occupancy is over_200:
#     capacity_score += 3
# elif bed_occupancy is not_reported:
#     capacity_score += regional_median_bed_occupancy_points
#
# if has_icu:
#     if icu_occupancy is 100_150:
#         capacity_score += 1
#     elif icu_occupancy is 151_200:
#         capacity_score += 2
#     elif icu_occupancy is over_200:
#         capacity_score += 3
#     elif icu_occupancy is not_reported:
#         capacity_score += regional_median_icu_occupancy_points
#
# capacity_score = capacity_score * CAPACITY_WEIGHT
#
# ##########################
# ## Total Priority Score ##
# ##########################
#
# priority_score = need_score + vuln_score + exposure_score + capacity_score
