# Containerlab - Network Topology Lab Setup

This directory contains a Containerlab topology with 3 Arista cEOS devices for network automation testing and development.

---

## Lab Topology

```
                    ┌─────────────────────────────────┐
                    │   Containerlab 3-Node Topology  │
                    └─────────────────────────────────┘

        ┌──────────────────────────────────────────────────┐
        │          Management Network (172.20.20.0/24)     │
        └──────────────────────────────────────────────────┘
                 │              │              │
            ┌────┴────┐    ┌────┴────┐   ┌────┴────┐
            │ ceos1   │    │ ceos2   │   │ ceos3   │
            │ .2      │    │ .4      │   │ .3      │
            └─────────┘    └─────────┘   └─────────┘
                 │eth1────────eth1│           │
                 │                │           │
                 │eth2            │eth2       │
                 │                │           │
                 └────────────eth1│           │
                          └────────────────eth2┘

            Data Plane Links:
            • ceos1:eth1 ←→ ceos2:eth1 (10.0.12.0/24)
            • ceos2:eth2 ←→ ceos3:eth1
            • ceos3:eth2 ←→ ceos1:eth2

            OSPF Area 0 configured on all data links
```

**Device Information:**

| Device | Management IP | Router ID | OS Version |
|--------|---------------|-----------|------------|
| ceos1  | 172.20.20.2   | 1.1.1.1   | EOS 4.32.0F |
| ceos2  | 172.20.20.4   | 2.2.2.2   | EOS 4.32.0F |
| ceos3  | 172.20.20.3   | 3.3.3.3   | EOS 4.32.0F |

**Default Credentials:** `admin / admin`

---

## Prerequisites

Install Containerlab using the provided script from the project root:

```bash
cd ..
./clab.sh
```

This installs:
- **Containerlab** - Container-based network lab orchestration
- **Docker** - Container runtime (if not already installed)

---

## Containerlab Commands

### Deploy the Lab

Start all devices and links defined in the topology:

```bash
sudo containerlab deploy -t topology.clab.yaml
```

Output shows:
- Container names
- Management IPs
- Connection status

### Inspect the Lab

View running lab status:

```bash
sudo containerlab inspect -t topology.clab.yaml
```

### Access Device Console

Connect to a device's CLI:

```bash
sudo docker exec -it clab-test_network-ceos1 Cli
```

Replace `ceos1` with `ceos2` or `ceos3` for other devices.

### Destroy the Lab

Stop and remove all lab containers:

```bash
sudo containerlab destroy -t topology.clab.yaml
```

**Note:** This does NOT delete startup configs in `backup_configs/`.

### Save Device Configurations

Export running configs from devices:

```bash
sudo containerlab save -t topology.clab.yaml
```

Configs are saved to the directories specified in the topology file.

### Graph Topology

Generate a topology diagram:

```bash
sudo containerlab graph -t topology.clab.yaml
```

---

## Lab Files

- **`topology.clab.yaml`** - Defines 3 cEOS nodes and links
- **`testbed_containerlab.yaml`** - pyATS testbed for device automation
- **`devices.csv`** - Device inventory (used to generate testbed)
- **`backup_configs/`** - Startup configuration files for each device

---

## pyATS Testbed Management

### Create Testbed from CSV

Generate a pyATS testbed file from the device inventory:

```bash
pyats create testbed file --path devices.csv --output testbed_containerlab.yaml
```

### Validate Testbed

Test connectivity to all devices:

```bash
pyats validate testbed testbed_containerlab.yaml
```

---

## Arista cEOS Command Reference

### Basic Commands

| Command | Description |
| --- | --- |
| `enable` | Enter privileged EXEC mode |
| `configure terminal` | Enter global configuration mode |
| `show version` | Display software version and hardware details |
| `show running-config` | View current running configuration |
| `show startup-config` | View startup configuration |
| `copy running-config startup-config` | Save configuration |
| `write memory` | Save configuration (short form) |
| `reload` | Reboot the device |

### Interface Configuration

| Command | Description |
| --- | --- |
| `show interfaces status` | View interface status |
| `show ip interface brief` | Display interface IP summary |
| `interface Ethernet1` | Enter interface configuration mode |
| `description <text>` | Add interface description |
| `no switchport` | Configure as Layer 3 interface |
| `ip address <ip>/<mask>` | Assign IP address |
| `no shutdown` | Enable interface |
| `shutdown` | Disable interface |

### VLAN Configuration

| Command | Description |
| --- | --- |
| `show vlan` | Display VLAN information |
| `vlan <vlan_id>` | Create VLAN and enter config mode |
| `name <vlan_name>` | Assign VLAN name |
| `switchport mode access` | Configure as access port |
| `switchport access vlan <id>` | Assign port to VLAN |
| `switchport mode trunk` | Configure as trunk port |
| `switchport trunk allowed vlan <list>` | Specify allowed VLANs on trunk |

### Routing Configuration

| Command | Description |
| --- | --- |
| `show ip route` | Display routing table |
| `ip routing` | Enable IP routing |
| `ip route <network>/<mask> <next-hop>` | Create static route |
| `router ospf <process-id>` | Enter OSPF configuration |
| `router bgp <asn>` | Enter BGP configuration |
| `network <network> area <area-id>` | Add network to OSPF (in router config) |

### Troubleshooting Commands

| Command | Description |
| --- | --- |
| `ping <ip_address>` | Send ICMP echo requests |
| `traceroute <ip_address>` | Trace path to destination |
| `show lldp neighbors` | Display LLDP neighbor information |
| `show mac address-table` | Display MAC address table |
| `show arp` | Display ARP table |
| `show logging` | View system logs |
| `show tech-support` | Gather diagnostic information |

---

## Example: Manual Device Configuration

```bash
# Connect to device
sudo docker exec -it clab-test_network-ceos1 Cli

# Configure interface
enable
configure terminal
interface Ethernet1
description Link to ceos2
no switchport
ip address 10.0.12.1/24
no shutdown
exit

# Save config
write memory
exit
```

---

## Topology Details

The `topology.clab.yaml` defines:
- **3 cEOS nodes** running Arista EOS 4.32.0F
- **Startup configs** mounted from `backup_configs/`
- **Links** connecting devices in a mesh topology
- **Management network** for SSH access

Each device boots with:
- Management IP addresses
- Interface descriptions and IP assignments

---

## Tips

- Device names follow pattern: `clab-<lab-name>-<device-name>`
- SSH access: `ssh admin@172.20.20.2` (password: `admin`)
- Check Docker status: `sudo docker ps`
- View device logs: `sudo docker logs clab-test_network-ceos1`

---