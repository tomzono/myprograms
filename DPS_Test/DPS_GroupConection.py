# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from azure.iot.device import IoTHubDeviceClient
import time
import socket
import derive_device_key as devicekey
import register_device as registerdevice

import DPSconfig
group_symmetric_key = DPSconfig.group_symmetric_key


device_id = socket.gethostname()
results = {}

derived_device_key = devicekey.derive_device_key(device_id, group_symmetric_key)
registration_result =registerdevice.register_device(device_id,derived_device_key)

print(registration_result)
print("The status was :-")
print(registration_result.status)
print("The etag is :-")
print(registration_result.registration_state.etag)
print("\n")
if registration_result.status == "assigned":
    print("Will send telemetry from the provisioned device with id {id}".format(id=device_id))
    device_client = IoTHubDeviceClient.create_from_symmetric_key(
        symmetric_key=derived_device_key,
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
