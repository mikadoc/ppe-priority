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





###################
## Urgency score ##
###################

urgency_score = 0

"""
Assign urgency points based on how long current supply is predicted to last.
----------------------------------------------------------------------------
Beyond type of facility and level of exposure, perhaps the most important factor to consider when 
allocating limited suppleis of PPE is the urgency with which a facilitiy requires a re-supply.

Implementation: Facilities are required to report how long they expect their current suupply to 
last for each type of PPE. Higher numbers of points are assigned to facilities who expect to run
out sooner."

Justification: Priority should be given to facilities with the most limited supply of PPE relative 
to their burn rate.
"""

# Assign points based on how long current supply is predicted to last.
if dat.loc[row_idx,"Current Supply"] is "No supply remaining": # critical need
    urgency_score += 5
elif dat.loc[row_idx,"Current Supply"] is "2 days or less": # dire need; future data will be "1–3 days"
    urgency_score += 4
elif dat.loc[row_idx,"Current Supply"] is "1 week or less": # urgent need; future data will be "4–7 days"
    urgency_score += 3
elif dat.loc[row_idx,"Current Supply"] is "2 weeks or less": # high need; future data will bee "1–2 weeks"
    urgency_score += 2
elif dat.loc[row_idx,"Current Supply"] is "More than 2 weeks": # moderate need
    urgency_score += 1

"""
Weight supply-based urgency by PPE practices.
---------------------------------------------
Many facilities have (by choice or necessity) implemented practices to conserve limited supplies of PPE. The CDC
provides a list of suggested strategies to be applied to conserve respirators and face masks at three increasingly 
severe levels of surge capacity:

Conventional capacity - Measures consist of providing patient care without any change in daily contemporary 
practices. This set of measures, consisting of engineering, administrative, and personal protective equipment 
(PPE) controls should already be implemented in general infection prevention and control plans in healthcare 
settings.

Contingency capacity – Measures may change daily standard practices but may not have any significant impact on the
care delivered to the patient or the safety of healthcare personnel (HCP). These practices may be used temporarily
during periods of expected facemask shortages.

Crisis capacityn - Strategies that are not commensurate with U.S. standards of care. These measures, or a combination
of these measures, may need to be considered during periods of known facemask shortages.

In our framework, we adapt and extend these categories (originally developed for surge planning in general, rather
than specifically for PPE conservation; Hick et al., 2009) to other kinds of PPE. We require facilities to report
what level of surge practices they have implemented for PPE conservation, and use this information to contextualize
and scale the provided estimates of how long existing supplies will last.

Implementation: Urgency scores for facilities in contingency or crisis capacity are scaled by 1 and 2 orders of
magnitude, respectively. This effectively stratifies urgency scores by surge severity, thus ensuring that, for
example, a facility implementing crisis capacity strategies will always receive a higher urgency score than facilities
implementing less severe conservation strategies, even if those facilities predict their supply to run out sooner.

Justification: Priority should be given to facilities where PPE practices have been most severely impacted, and 
where implementing additional PPE conservation strategies is impossible without significantly increased risk to workers.
"""

if dat.loc[row_idx,"Item Surge Capacity"] is "Conventional": # critical need
    need_score *= 1
elif dat.loc[row_idx,"Item Surge Capacity"] is "Contingency": # dire need; future data will be "1–3 days"
    need_score *= 10
elif dat.loc[row_idx,"Item Surge Capacity"] is "Crisis": # urgent need; future data will be "4–7 days"
    need_score *= 100

urgency_score = urgency_score * URGENCY_WEIGHT

#########################
## Vulnerability score ##
#########################

"""
For purposes of our framework, we define vulnerability as the extent to which a facility or organization provides
services to populations or groups who have limited access to healthcare due to socioeconimic and/or geographic factors.

Overall justification: In the United States, many groups face significant barriers to accessing both preventative and 
[acute] healthcare services. Even in normal times, these barriers manifest as increased morbidity and mortality for
members of these groups [CITE], and local and national statitics suggest that individuals in these groups are dying
from COVID-19 at much greater rates than other segments of the population [CITE]. The already-under resourced 
facilities that serve these populations will thus be most likely to experience a disproportionately large surge
of very sick patients, while simultaneously having fewer of the staff and equipment resoruces necessary to care for
these vulnerable patients. Thus, our framework prioritizes PPE allocation to facilities that serve vulnerable
groups, with the goal of reducing the extent to which the COVID-19 pandemic magnifies existing healthcare disparities.

Facility-level vulnerability
----------------------------
Implementation: We use categories and designations from the Center for Medicare and Medicaid Services (CMS) to
identify facilities which provide services services to vulnerable populations.

Indicator justification: While facility types and designations are admittednly an imperfect proxy for the indicator of interest,
this allows us to assign vulnerability scores based on characteristics of individual facilities rather than relying
exclusively on coarse geographic data (which often lacks the spatial resolution necessary to differentiate levels of
vulnerability within a region).

"""

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
