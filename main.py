import boto3
from pprint import pprint
from modules import Instance, from_raw_data_to_instance
from typing import List
import logging.config


def describe_instances_paginated(client) -> List[dict]:
    """
     The method pulls all the instances from aws, extracts the instances from the response and returns them
    :param client: a botocore.client.EC2 object
    :return: list of dictionaries each describing an instance
    """

    instances = []
    # Pulling all instances from aws.
    response = client.describe_instances()
    for reservation in response["Reservations"]:
        # Extract the Instances from the response dictionary.
        instances.extend(reservation['Instances'])

    while "NextToken" in response:
        # As long as "NextToken is in the response (there are still instances to pull) keep pulling the next instances.
        response = client.describe_instances(NextToken=response["NextToken"])
        for reservation in response["Reservations"]:
            instances.extend(reservation['Instances'])
    return instances


def get_all_aws_instances(specific_regions=None) -> List[Instance]:
    """
    The method pulls the instances from aws, parses them into human readable objects and returns them
    :param specific_regions: A list of aws regions to pull instances from
    :return: A list of Instances objects extracted and parsed from aws.
    """
    all_aws_instances = []
    all_aws_regions = ["us-east-2", "us-east-1", "us-west-1", "us-west-2", "af-south-1", "ap-east-1", "ap-south-1",
                       "ap-northeast-3", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1",
                       "ca-central-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-south-1", "eu-west-3",
                       "eu-north-1", "me-south-1", "sa-east-1"]
    # By default the method pulls the instances from all regions but if specific regions were given it pulls from them
    if specific_regions:
        regions = specific_regions
    else:
        regions = all_aws_regions
    logging.info("started pulling instances")
    for region in regions:

        ec2 = boto3.client('ec2', region_name=region)
        try:
            regions_instances = describe_instances_paginated(ec2)
            all_aws_instances.extend(regions_instances)
            logging.debug(f"pulled instances from region {region}")
        except Exception:
            # skips on all regions that the given credentials have no permissions to access.
            logging.error(f"Could not pull instances from region {region}")
            pass
    parsed_instances = []
    logging.info("finished successfully pulling instances")
    logging.info("processing raw data into objects")
    for instance_dict in all_aws_instances:
        # parse all instances pulled from aws into Instance objects

        instance = from_raw_data_to_instance(instance_dict)
        parsed_instances.append(instance)
    logging.info("finished processing the raw data")
    return parsed_instances


if __name__ == '__main__':
    # disabling all loggers from imported modules to not spam the root logger.
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
    })
    # configuring the root logger.
    logging.basicConfig(level=logging.DEBUG)

    active_regions = ["us-east-2", "us-west-2"]
    all_aws_instances = get_all_aws_instances(specific_regions=active_regions)

