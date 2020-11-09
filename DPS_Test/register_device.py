def register_device(registration_id):

    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=device_ids_to_keys[registration_id],
    )

    return provisioning_device_client.register()
