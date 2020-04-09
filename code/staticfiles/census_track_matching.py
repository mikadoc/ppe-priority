import os
import censusgeocode as cg


# Retrieve API key from env. variables
CENSUS_API_KEY = os.environ['US_CENSUS_API_KEY']

results = cg.address('1600 Pennsylvania Avenue', city='Washington', state='DC', zipcode='22052')
results