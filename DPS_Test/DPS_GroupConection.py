# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import base64
import hmac
import hashlib
from azure.iot.device import ProvisioningDeviceClient
from azure.iot.device import IoTHubDeviceClient
from azure.iot.device import Message
import uuid
import time
import DPSconfig
import socket
import derive_device_key as devicekey

provisioning_host = DPSconfig.provisioning_group_host
id_scope = DPSconfig.group_id_scope
group_symmetric_key = DPSconfig.group_symmetric_key

# These are the names of the devices that will eventually show up on the IoTHub
# Please make sure that there are no spaces in these device ids.
device_id = socket.gethostname()
# For computation of device keys
device_ids_to_keys = {}
# Keep a dictionary for results
results = {}
# NOTE : Only for illustration purposes.
# This is how a device key can be derived from the group symmetric key.
# This is just a helper function to show how it is done.
# Please don't directly store the master group key on the device.
# Follow the following method to compute the device key somewhere else.


def register_device(registration_id):

    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=device_ids_to_keys[registration_id],
    )

    return provisioning_device_client.register()


# derived_device_key has been computed already using the helper function somewhere else
# AND NOT on this sample. Do not use the direct master key on this sample to compute device key.
derived_device_key = devicekey.derive_device_key(device_id, group_symmetric_key)
device_ids_to_keys[device_id] = derived_device_key

for device_id in device_ids_to_keys:
    registration_result = register_device(registration_id=device_id)
    results[device_id] = registration_result

for device_id in device_ids_to_keys:
    # The result can be directly printed to view the important details.
    registration_result = results[device_id]
    print(registration_result)
    # Individual attributes can be seen as well
    print("The status was :-")
    print(registration_result.status)
    print("The etag is :-")
    print(registration_result.registration_state.etag)
    print("\n")
    if registration_result.status == "assigned":
        print("Will send telemetry from the provisioned device with id {id}".format(id=device_id))
        device_client = IoTHubDeviceClient.create_from_symmetric_key(
            symmetric_key=device_ids_to_keys[device_id],
            hostname=registration_result.registration_state.assigned_hub,
            device_id=registration_result.registration_state.device_id,
        )

        # Connect the client.
        device_client.connect()

        # Send 5 messages
        for i in range(1, 6):
            print("sending message #" + str(i))
            device_client.send_message("test payload message " + str(i))
            time.sleep(0.5)

        # finally, disconnect
        device_client.disconnect()

    else:
        print("Can not send telemetry from the provisioned device with id {id}".format(id=device_id))
