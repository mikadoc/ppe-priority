import numpy as np
import pandas as pd
from scipy import stats

###################################
## Scoring and weighting options ##
###################################

# Set of facility types serving vulnerable or underserved populations
VULN_FACILITIES = ['fqhc',
                   'dsh',
                   'rhc',
                   'cah',
                   'indian_tribal',
                   'chc']

# Domain weighting multipliers
NEED_WEIGHT = 1
VULN_WEIGHT = 1
EXPOSURE_WEIGHT = 1
CAPCITY_WEIGHT = 1





################
## Need score ##
################

need_score = 0

if need_level is critical: # critical need
    need_score += 5
elif need_level is dire: # dire need
    need_score += 4
elif need_level is urgent: # urgent need
    need_score += 3
elif need_level is high: # high need
    need_score += 2
elif need_level is moderate: # moderate need
    need_score += 1

need_score = need_score * NEED_WEIGHT

#########################
## Vulnerability score ##
#########################

vuln_score = 0

for vuln_type in VULN_FACILITIES:
    if vuln_type in facility_type:
        vuln_score += 1


# Vulnerability score based on local CDC SVI
# Incomplete, waiting on code to extract GIS data.

def get_radius_svis(svi_data, facility_address, radius):
"""
Return an array containing SVI values for each census tract within RADIUS of facility address

Parameters
----------
svi_data : <unknown GIS type>
    GIS data containing census tract shape files and SVI values for each tract.

facility_address : tuple
    Tuple of strings in the following format (street_name_and_number, city, state, zip)

radius : float
    Radius facility address to create a buffer for identifying local census tracts

Returns
-------
svi_array : ndarray
    1-dimensional array containing SVI values for all census tracts within radius
"""

def get_regional_svis(svi_data, counties_list)
"""
Return an array containing SVI values for each census tract within a set of counties.

Parameters
----------
svi_data : <unknown GIS type>
    GIS data containing census tract shape files and SVI values for each tract.

counties_array : list
    A list of <GIS unique county identifiers>

Returns
-------
svi_array : ndarray
    1-dimensional array containing SVI values for all census tracts within the set of counties
"""

local_svis = get_radius_svis(svi_data, facility_address, RADIUS)

# Local SVI extrema counts (relative to county and region)
regional_svis = get_regional_svis(svi_data, COUNTIES_LIST)
county = get_county(facility_address)
county_svis = get_county_svis(svi_data, county)
regional_top_quartile_count = np.sum(local_svis >= stats.scoreatpercentile(regional_svis, 75)) 
county_top_quartile_count = np.sum(local_svis >= stats.scoreatpercentile(county_svis, 75)) 

if SVI_COMPARISON is 'region':
    vuln_score += regional_top_quartile_count 
elif SVI_COMPARISON is 'county':
    vuln_score += county_top_quartile_count

vuln_score = vuln_score * VULN_WEIGHT

####################
## Exposure score ##
####################

exposure_score = 0

if has_covid is True:
    exposure_score += 10

if has_icu is True:
    exposure_score += 6

# Aerosol generating procedures but is not an ICU (e.g. freestanding ERs, paramedics)
if aerosols is True and has_icu is False:
    exposure_score += 3

exposure_score = exposure_score * EXPOSURE_WEIGHT

####################
## Capacity score ##
####################

capacity_score = 0

# Occupancy data is optional. 

if bed_occupancy is 100_150:    
    capacity_score += 1
elif bed_occupancy is 151_200:
    capacity_score += 2
elif bed_occupancy is over_200:
    capacity_score += 3
elif bed_occupancy is not_reported:
    capacity_score += regional_median_bed_occupancy_points

if has_icu:
    if icu_occupancy is 100_150:    
        capacity_score += 1
    elif icu_occupancy is 151_200:
        capacity_score += 2
    elif icu_occupancy is over_200:
        capacity_score += 3
    elif icu_occupancy is not_reported:
        capacity_score += regional_median_icu_occupancy_points

capacity_score = capacity_score * CAPACITY_WEIGHT

##########################
## Total Priority Score ##
##########################

priority_score = need_score + vuln_score + exposure_score + capacity_score
