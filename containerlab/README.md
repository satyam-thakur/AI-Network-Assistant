### arista_ceos Commands
#### **Basic Commands**

| Command | Description |
| --- | --- |
| `enable` | Enter privileged EXEC mode. |
| `configure terminal` | Enter global configuration mode. |
| `show version` | Display the switch's software version and hardware details. |
| `show running-config` | View the current running configuration. |
| `show startup-config` | View the configuration that will be loaded on the next reboot. |
| `copy running-config startup-config` | Save the current configuration to the startup configuration. |
| `write memory` | A shorter alias for saving the running configuration. |
| `reload` | Reboot the switch. |
| `erase startup-config` | Delete the startup configuration file. |

#### **Interface Configuration**

| Command | Description |
| --- | --- |
| `show interfaces status` | View the status of all interfaces. |
| `show ip interface brief` | Display a summary of interface IP addresses and status. |
| `interface <interface_name>` | Enter interface configuration mode (e.g., `interface Ethernet1`). |
| `description <string>` | Add a description to an interface. |
| `no switchport` | Convert a layer 2 interface to a layer 3 (routed) interface. |
| `ip address <ip_address>/<prefix>` | Assign an IP address to a routed interface. |
| `shutdown` / `no shutdown` | Disable or enable an interface. |

#### **VLAN and Switching**

| Command | Description |
| --- | --- |
| `show vlan` | Display VLAN information. |
| `vlan <vlan_id>` | Create a VLAN and enter VLAN configuration mode. |
| `name <vlan_name>` | Assign a name to a VLAN. |
| `interface <interface_name>` | Enter interface configuration mode. |
| `switchport mode access` | Configure the interface as an access port. |
| `switchport access vlan <vlan_id>` | Assign an access port to a VLAN. |
| `switchport mode trunk` | Configure the interface as a trunk port. |
| `switchport trunk allowed vlan <vlan_list>` | Specify which VLANs are allowed on a trunk port. |

#### **Routing**

| Command | Description |
| --- | --- |
| `show ip route` | Display the IP routing table. |
| `ip routing` | Enable IP routing globally. |
| `ip route <destination_network>/<prefix> <next_hop_ip>` | Create a static route. |
| `router bgp <asn>` | Enter BGP routing process configuration mode. |
| `router ospf <process_id>` | Enter OSPF routing process configuration mode. |

#### **Troubleshooting and Verification**

| Command | Description |
| --- | --- |
| `ping <ip_address>` | Send ICMP echo requests to a destination. |
| `traceroute <ip_address>` | Trace the path to a destination. |
| `show lldp neighbors` | Display information about directly connected LLDP neighbors. |
| `show mac address-table` | Display the MAC address table. |
| `show arp` | Display the ARP table. |
| `show logging` | View system log messages. |
| `show tech-support` | Gathers a large amount of diagnostic information for troubleshooting. |

### pyATS command to get test_bed
| `pyats create testbed file --path devices.csv --output testbed_containerlab.yaml` | Create test_bed.yaml from .csv file.