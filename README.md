# campus_auto_API
These scripts are examples of using the campus automation API for Catalyst Center


##  bf_switching.py
This script dumps out the features supported on a device.
```
 ./bf_switching.py --device 10.10.3.122
dna/intent/api/v1/wired/networkDevices/ec24581b-6e40-4a64-b47b-41e08aefa4f3/configFeatures/supported/layer2
cdpGlobalConfig, cdpInterfaceConfig, dhcpSnoopingGlobalConfig, dhcpSnoopingInterfaceConfig, dot1xGlobalConfig, dot1xInterfaceConfig, igmpSnoopingGlobalConfig, lldpGlobalConfig, lldpInterfaceConfig, mabInterfaceConfig, mldSnoopingGlobalConfig, portchannelConfig, stpGlobalConfig, stpInterfaceConfig, switchportInterfaceConfig, trunkInterfaceConfig, vlanConfig, vtpGlobalConfig, vtpInterfaceConfig
```
To see how a feature is configured
```
./bf_switching.py --device 10.10.3.122 --feature vtpGlobalConfig
dna/intent/api/v1/wired/networkDevices/ec24581b-6e40-4a64-b47b-41e08aefa4f3/configFeatures/supported/layer2
cdpGlobalConfig, cdpInterfaceConfig, dhcpSnoopingGlobalConfig, dhcpSnoopingInterfaceConfig, dot1xGlobalConfig, dot1xInterfaceConfig, igmpSnoopingGlobalConfig, lldpGlobalConfig, lldpInterfaceConfig, mabInterfaceConfig, mldSnoopingGlobalConfig, portchannelConfig, stpGlobalConfig, stpInterfaceConfig, switchportInterfaceConfig, trunkInterfaceConfig, vlanConfig, vtpGlobalConfig, vtpInterfaceConfig
dna/intent/api/v1/wired/networkDevices/ec24581b-6e40-4a64-b47b-41e08aefa4f3/configFeatures/deployed/layer2/vtpGlobalConfig
{
  "response": {
    "vtpGlobalConfig": {
      "items": [
        {
          "configType": "VTP_GLOBAL",
          "mode": "TRANSPARENT",
          "version": "VERSION_1",
          "isPruningEnabled": false
        }
      ]
    }
  },
  "version": "1.0"
}
```

