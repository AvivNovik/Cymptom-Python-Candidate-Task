from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from ipaddress import ip_address
import logging


@dataclass()
class Instance:
    # The class contains all useful information on an aws instance.

    image_id: str                             # The ID of the AMI used to launch the instance.
    instance_id: str                          # The ID of the instance.
    network_interfaces: list                  # The network interfaces for the instance.
    state: dict                               # The current state of the instance.
    launch_time: datetime                     # The time the instance was launched.
    tags: List[dict]                          # The tags assigned to the instance. consist of "Key" and "Value" as keys.
    cpu_details: dict                         # The details of the cpu of the instance. consist of "CoreCount" and "ThreadsPerCore" as keys.
    instance_type: str                        # The instance type.
    security_groups: List[dict]               # The security groups for the instance. Consist of 'GroupName' and 'GroupId' as keys.
    client_token: str                         # The idempotency token you provided when you launched the instance, if applicable.
    state_transition_reason: str              # The reason for the most recent state transition. This might be an empty string.
    root_device_name: str                     # The device name of the root device volume (for example, /dev/sda1 ).
    ram_disk_id: str = ""                     # The RAM disk associated with this instance, if applicable.]
    platform: str = ""                        # The platform details value for the instance. for example "Linux/UNIX"
    kernel_id: str = ""                       # The kernel associated with this instance, if applicable.
    Host_id: str = ""                         # The ID of the Dedicated Host on which the instance resides.


def from_raw_data_to_instance(raw_data: dict) -> Instance:
    """
    The function builds Instance object out of a dictionary describing an instance that was pulled from aws.
    :param raw_data: dictionary describing an instance pulled from aws
    :return: Instance object describing the instance from the input
    """

    # List of the NetworkInterface objects that will be used as one of Instance's properties.
    parsed_interfaces = []

    for interface in raw_data["NetworkInterfaces"]:
        # Create a NetworkInterface object from the response's dictionary.
        parsed_interface = from_raw_data_to_network_interface(interface)

        parsed_interfaces.append(parsed_interface)

    # create an Instance object from the response's dictionary.
    parsed_instance = Instance(image_id=raw_data["ImageId"], instance_id=raw_data["InstanceId"],
                               network_interfaces=parsed_interfaces, state=raw_data["State"],
                               launch_time=raw_data["LaunchTime"], tags=raw_data["Tags"],
                               cpu_details=raw_data["CpuOptions"], instance_type=raw_data["InstanceType"],
                               security_groups=raw_data["SecurityGroups"], client_token=raw_data["ClientToken"],
                               state_transition_reason=raw_data["StateTransitionReason"],
                               root_device_name=raw_data["RootDeviceName"])

    # check the response's dictionary for the fields that are optional and parse them into the Instance object.
    if "RamdiskId" in raw_data:
        parsed_instance.ram_disk_id = raw_data["RamdiskId"]
    if "PlatformDetails" in raw_data:
        parsed_instance.platform = raw_data["PlatformDetails"]
    if "KernelId" in raw_data:
        parsed_instance.kernel_id = raw_data["KernelId"]
    if "HostId" in raw_data:
        parsed_instance.Host_id = raw_data["HostId"]

    return parsed_instance


@dataclass()
class NetworkInterface:
    ip_owner_id: str
    public_dns_name: str
    mac_address: str                          # mac address of the interface. (type could be changed into mac_address but require installing a package.)
    network_interface_id: str
    owner_id: str
    private_dns_name: str
    subnet_id: str
    status: str
    public_ip_address: ip_address = None
    ipv6_address: ip_address = None
    private_ip_address: ip_address = None


def from_raw_data_to_network_interface(raw_data: dict) -> NetworkInterface:
    """
       The function builds NetworkInterface object out of a dictionary describing
       a network interface that was pulled from aws.
       :param raw_data: dictionary describing a network interface pulled from aws
       :return: NetworkInterface object describing the network interface from the input
       """

    association = raw_data["Association"]
    # Create a NetworkInterface from the raw data's dictionary.
    parsed_interface = NetworkInterface(ip_owner_id=association["IpOwnerId"],
                                        public_dns_name=association["PublicDnsName"],
                                        mac_address=raw_data["MacAddress"],
                                        network_interface_id=raw_data["NetworkInterfaceId"],
                                        owner_id=raw_data["OwnerId"],
                                        private_dns_name=raw_data["PrivateDnsName"],
                                        subnet_id=raw_data["SubnetId"], status=raw_data["Status"]
                                        )
    # check the input dictionary for optional fields, check if the input is vlad ip address and parse it into the object
    ipv6_address = raw_data["Ipv6Addresses"]
    public_ip = ip_address(association["PublicIp"])
    private_ip_address = raw_data["PrivateIpAddress"]
    if ipv6_address:
        try:
            parsed_interface.ipv6_address = ip_address(ipv6_address)
        except ValueError:
            logging.error(f"ipv6 address is not valid in network interface with the id "
                          f"{parsed_interface.network_interface_id}")

    if public_ip:
        try:
            parsed_interface.public_ip_address = ip_address(public_ip)
        except ValueError:
            logging.debug(f"public_ip address is not valid in network interface with the id "
                          f"{parsed_interface.network_interface_id}")

    if private_ip_address:
        try:
            parsed_interface.private_ip_address = ip_address(private_ip_address)
        except ValueError:
            logging.error(f"private_ip_address address is not valid in network interface with the id "
                          f"{parsed_interface.network_interface_id}")
    return parsed_interface
