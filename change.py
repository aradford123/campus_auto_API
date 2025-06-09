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
from task import wait_for_task, wait_for_activity

logger = logging.getLogger(__name__)


def intended_config(dnac, deviceid):

    payload =  {
    "switchportInterfaceConfig": {
      "items": [
        {
          "configType": "SWITCHPORT_INTERFACE",
          "interfaceName": "FortyGigabitEthernet1/1/1",
          "mode": "DYNAMIC_AUTO",
          #"accessVlan": 20,
          "accessVlan": 10,
          "accessVlan": 1,
          "adminStatus": "UP",
          "trunkAllowedVlans": "1",
          "nativeVlan": 1
        }
        ]}}
    #url= f"dna/intent/api/v1/wired/networkDevices/{deviceid}/configFeatures/intended/layer2"
    url = f'dna/intent/api/v1/wired/networkDevices/{deviceid}/configFeatures/intended/layer2/switchportInterfaceConfig'
    # need to stop the exception being caught as this is how the errors in payload are handled
    #response = dnac.custom_caller.call_api(raise_exception=False, method="POST", resource_path=url, data=json.dumps(payload))
    response = dnac.custom_caller.call_api(raise_exception=False, method="PUT", resource_path=url, data=json.dumps(payload))
    return response

def generate_vcr(dnac,deviceid):
    url= f"/dna/intent/api/v1/wired/networkDevices/{deviceid}/configFeatures/intended/configurationModels"
    response = dnac.custom_caller.call_api(raise_exception=False, method="POST", resource_path=url, data=json.dumps({}))
    return response

def generate_preview(dnac,deviceid,previewid):
    url=f"dna/intent/api/v1/wired/networkDevices/{deviceid}/configFeatures/intended/configurationModels/{previewid}/config"
    response =  dnac.custom_caller.call_api(raise_exception=False, method="POST", resource_path=url, data=json.dumps({}))
    return response

def deploy(dnac, deviceid):
    url= f"dna/intent/api/v1/wired/networkDevices/{deviceid}/configFeatures/intended/deploy"
    response = dnac.custom_caller.call_api(raise_exception=False, method="POST", resource_path=url, data=json.dumps({}))
    print(response)
    return response

def get_deployment_status(dnac,deviceid,deploymentid):
    url = f'dna/intent/api/v1/wired/networkDevices/{deviceid}/configFeatures/intended/deviceDeployments'
    response = dnac.custom_caller.call_api(raise_exception=False, method="GET", resource_path=url)
    for configchange in response.response:
        #print(configchange)
        line = f'{configchange.get("deployActivityId",""):37s} {configchange.configGroupName:62s} {configchange.status}'
        print(line)
    return response

def get_activity(dnac,activityid):

    #url = f'/dna/intent/api/v1/activities/{activityid}'
    #response = dnac.custom_caller.call_api(raise_exception=False, method="GET", resource_path=url)
    response = wait_for_activity(dnac,activityid)
    print(response)
    return response

def show_cli(dnac,deviceid,previewid):
    url=f"dna/intent/api/v1/wired/networkDevices/{deviceid}/configFeatures/intended/configurationModels/{previewid}/config"
    response = dnac.custom_caller.call_api(raise_exception=False, method="GET", resource_path=url)
    return response

def deploy_vcr(dnac,deviceid,previewid):
    url = f"dna/intent/api/v1/wired/networkDevices/{deviceid}/configFeatures/intended/configurationModels/{previewid}/deploy"
    response = dnac.custom_caller.call_api(raise_exception=False, method="POST", resource_path=url, data=json.dumps({}))
    return response

def do_vcr(dnac, deviceid):

    print("\n******\nGENERATE VCR\n******")
    response = generate_vcr(dnac, deviceid)
    print(response)
    if 'errorCode' in response.response:
        print(json.dumps(response.response,indent=2))
        sys.exit(1)

    result = wait_for_task(dnac, response.response.taskId)
    print(result)
    previewid = response.response.taskId
    response = wait_for_activity(dnac,previewid)
    print(response)
    print("\n**GENERATE PREVIEW")
    response = generate_preview(dnac,deviceid,previewid)
    print(response)
    response = wait_for_task(dnac, response.response.taskId)
    print(response)
    print("\n**SHOW CLI")
    response = show_cli(dnac,deviceid,previewid)
    print(json.dumps(response.response,indent=2))
    
    response = deploy_vcr(dnac,deviceid,previewid)
    print(response)
    response = wait_for_task(dnac, response.response.taskId)
    print(response)
    response = wait_for_activity(dnac,response.response.id)
    print(response)
    
    print("\n******\nEND VCR\n******")
    
def main(dnac):
    VCR = True
    deviceid = "ec24581b-6e40-4a64-b47b-41e08aefa4f3"
    response = intended_config(dnac, deviceid)
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

    if VCR:
        do_vcr(dnac,deviceid) 
    else:
        response = deploy(dnac,deviceid)
        if not 'taskId' in response.response:
            print(f"Error {json.dumps(response.response,indent=2)}")
            sys.exit(1)
        result = wait_for_task(dnac, response.response.taskId)
        print(result)

        if not 'Successfully' in result.response.progress:
            print(f"failed: {json.dumps(result,indent=2)})")
            sys.exit(1)

        activityid = result.response.id
        status = get_activity(dnac, activityid)
        # no need to do this
        #status = get_deployment_status(dnac, deviceid,activityid)
        


if __name__ == "__main__":
    if True:
        root_logger=logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        root_logger.addHandler(ch)
        logger.debug("logging enabled")
    
    dnac = api.DNACenterAPI(base_url='https://{}:443'.format(DNAC),
                                username=DNAC_USER,password=DNAC_PASSWORD,verify=False)

    main(dnac)


