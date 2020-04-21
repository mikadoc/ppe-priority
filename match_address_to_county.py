from code.priority_algorithm import get_county
import code.config as cfg
import argparse
import os


census_tract_geom_fp = os.path.join(cfg.CENSUS_TRACT_GEOM_PATH, 'tracts_usna.shp')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--street_name_num', type=str)
    parser.add_argument('--city', type=str)
    parser.add_argument('--state', type=str)
    parser.add_argument('--zipcode', type=str)

    args = parser.parse_args()

    facility_address = (
        args.street_name_num,
        args.city,
        args.state,
        args.zipcode
    )

    county = get_county(census_tract_geom_fp, facility_address)

    # Prints the State-County FIPS code
    print(county)
