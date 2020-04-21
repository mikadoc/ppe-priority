from code.priority_algorithm import get_radius_tracts, miles_to_meters
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
    parser.add_argument('--radius')

    args = parser.parse_args()

    facility_address = (
        args.street_name_num,
        args.city,
        args.state,
        args.zipcode
    )

    intersecting_tracts = get_radius_tracts(
        census_tract_geom_fp,
        facility_address,
        radius=miles_to_meters(5)
    )

    print(intersecting_tracts)
