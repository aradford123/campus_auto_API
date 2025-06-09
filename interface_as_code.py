#!/usr/bin/env python
from argparse import ArgumentParser
from dnacentersdk import api
from dnacentersdk.exceptions import ApiError
import logging
import sys
import json
import requests
from  time import sleep, time, strftime, localtime
from dnac_config import DNAC, DNAC_USER, DNAC_PASSWORD
from change import do_vcr
from task import wait_for_task, wait_for_activity
logger = logging.getLogger(__name__)

def transform_payload(payload):
    # strip description:'' as causes an error
    # switchportInterfaceConfig.items[28].description: Must match ASCII characters
    for d in payload['switchportInterfaceConfig']['items']:
        if d.get('description', '') == '':
            d.pop('description', None)

def intended_config(dnac,deviceid,payload):
    transform_payload(payload)
    print(payload)
    url = f'dna/intent/api/v1/wired/networkDevices/{deviceid}/configFeatures/intended/layer2/switchportInterfaceConfig'
    response = dnac.custom_caller.call_api(raise_exception=False, method="PUT", resource_path=url, data=json.dumps(payload))
    return response

def process_device(dnac,deviceip,payload):
#    deviceid = "ec24581b-6e40-4a64-b47b-41e08aefa4f3"
    device_response = dnac.devices.get_device_list(managementIpAddress=deviceip) 
    deviceid = device_response.response[0].get('id')
    print(deviceid)

    response = intended_config(dnac, deviceid,payload)
    print(response)
    if 'errorCode' in response.response:
        print(json.dumps(response.response,indent=2))
        sys.exit(1)

    result = wait_for_task(dnac, response.response.taskId)
    print(result)
    
    # need to check progress for success
    # can data have mulitple entries?
    if 'data' in result.response:
        data = json.loads(result.response.data)
        print(data)
        print(data[0].keys())
    
    do_vcr(dnac,deviceid)

def main(dnac,filename):
    f=open(filename,"r")
    data = json.load(f)
    for device, config in data.items():
        process_device(dnac,device,config)


if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument('-v', action='store_true',
                        help="verbose")
    parser.add_argument('--file', type=str, required=True,
                        help="filename data/switchport-state.json")
    args = parser.parse_args()

    if args.v:
        root_logger=logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        root_logger.addHandler(ch)
        logger.debug("logging enabled")

    dnac = api.DNACenterAPI(base_url='https://{}:443'.format(DNAC),
                                username=DNAC_USER,password=DNAC_PASSWORD,verify=False)

    main(dnac, args.file)


