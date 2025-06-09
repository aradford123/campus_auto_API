#!/usr/bin/env python
from argparse import ArgumentParser
from dnacentersdk import api
from dnacentersdk.exceptions import ApiError
import logging
import json
from  time import sleep, time, strftime, localtime
from dnac_config import DNAC, DNAC_USER, DNAC_PASSWORD
import sys
logger = logging.getLogger(__name__)
timeout = 10

def get_device_id(dnac, deviceip):
    try:
        response = dnac.devices.get_network_device_by_ip(ip_address=deviceip)
    except ApiError as e:
        print("Device {} not found".format(deviceip))
        sys.exit(1)
    return response.response.id

def get_features_supported(dnac,uuid):
    url = f'dna/intent/api/v1/wired/networkDevices/{uuid}/configFeatures/supported/layer2'
    print(url)
    response = dnac.custom_caller.call_api(method="GET",
                                               resource_path=url)
    features = [ feature.get('name') for feature in response.response]
    print(", ".join(features))

def get_feature(dnac,uuid,feature):
    url = f'dna/intent/api/v1/wired/networkDevices/{uuid}/configFeatures/deployed/layer2/{feature}'
    print(url)
    response = dnac.custom_caller.call_api(method="GET",
                                               resource_path=url)

    print(json.dumps(response,indent=2))
def update_interface(dnac,uuid):
    payload = {
                "switchportInterfaceConfig": {
                "items": [
                    {
                "configType": "string",
                "interfaceName": "string",
                "description": "string",
                "mode": "string",
                "accessVlan": "integer",
                "voiceVlan": "integer",
                "adminStatus": "string",
                "trunkAllowedVlans": "string",
                "nativeVlan": "integer"
                }
            ]
            }
            }

def main(dnac,device,feature):
    # get all devices that are wlc
    uuid = get_device_id(dnac,device)

    get_features_supported(dnac, uuid)
    if feature is not None:
        get_feature(dnac,uuid,feature)



if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument('-v', action='store_true',
                        help="verbose")
    parser.add_argument('--password',  type=str, required=False,
                        help='new passowrd')
    parser.add_argument('--dnac',  type=str,default=DNAC,
                        help='dnac IP')
    parser.add_argument('--device',  type=str,
                        help='device IP')
    parser.add_argument('--feature',  type=str,
                        help='feature name')
    args = parser.parse_args()

    if args.v:
        root_logger=logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        root_logger.addHandler(ch)
        logger.debug("logging enabled")

    #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    DNAC = args.dnac
    print(f"User:{DNAC_USER}")
    dnac = api.DNACenterAPI(base_url='https://{}:443'.format(DNAC),
                                #username=DNAC_USER,password=DNAC_PASSWORD,verify=False,debug=True)
                                username=DNAC_USER,password=DNAC_PASSWORD,verify=False)
    main(dnac,args.device,args.feature)
