import numpy as np
import pandas as pd
from scipy import stats

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

Estimate vulnerability based on facility type
---------------------------------------------
Implementation: We use categories and designations from the Center for Medicare and Medicaid Services (CMS) to
identify facilities which provide services services to vulnerable populations.

Justification: While facility types and designations are admittednly an imperfect proxy indicator for the
vulnerability of a patient population, this allows us to assign vulnerability scores based on characteristics of 
individual facilities rather than relying exclusively on coarse geographic data (which often lacks the spatial 
resolution necessary to differentiate levels of vulnerability within a region).

Estimate vulnerability based on local SVI
-----------------------------------------
Implementation: We count the number of census tracts within an X mile radius of a facility which have a CDC Social
Vulnerability Index (SVI) in the top Nth percentile of SVI values in the surrounding county or region (set of counties).

Justification: The CDC SVI provides a measure of "the resilience of communities when confronted by external stresses 
on human health... such as natural or human-caused disasters, or disease outbreaks". In contrast to alternative mesures
of healthcare inequity [1] the SVI is provided at fine spatial resolution (per cenus tract) and has been 
recently updated (2018). We chose to count the number of vulnerable census tracts within in an area (rather than
taking the mean or median of SVI values) because socioeconomically disadvantaged areas are often geographically
compact and interspersed amongst more affluent and well-resourced communities [CITE] such that the overall regional
distribution of SVI values may not shift meaningfully even if an area contains a significant vulnerable population.
To account for regional differences in population density and the size of counties, our tool identifies vulnerable
census tracts relative to all other tracts in either the same county (for areas where a single county contains
an entire major population center) or same region (for areas where a popluation is distributed across multiple counties).

[1] The Health Resources & Services Administration (HRSA) designates geographic areas and specific populations within 
the United States as being either medically underserved or as having a shortage of health professionals 
(https://bhw.hrsa.gov/shortage-designation). Despite the close alignment of these designations with our definition 
of vulnerability, we chose not to use these designation for a number of important reasons. First, many of these
designations have not been reviwed or updated in over 20 years, even in major metropolitan areas. Second, geographic
designations are made the county level, which in many cities is too spatially coarse to provide information that could
inform decisions about PPE allocation across facilities. 

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
