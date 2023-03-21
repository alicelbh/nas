## Phase 1: Core MPLS Routing
### Enable LDP
```
(config)# ip cef (distributed)
(config)# mpls ip
(config)# mpls label protocol ldp
(config)# interface ...
└ (config-if)# mpls ip
```

Verify:
```
# show ip cef
# show ip mpls
# show mpls ldp bindings
# show mpls forwarding
# show mpls interfaces ...
# show mpls ldp discovery
# show mpls ldp neighbor
```

## Phase 2: Core BGP/MPLS VPN Routing
### Configure iBGP for VPNv4 address family
Between each PE and Route Reflector:
```
(config)# router bgp <as>
└ (config-rtr)# address-family vpnv4
  └ (config-rtr-af)# neighbor ... activate
  └ (config-rtr-af)# neighbor ... send-community both/extended
```

### Loopback to Loopback iBGP sessions
```
(config)# router bgp <as>
└ (config-rtr)# neighbor <ip> remote-as <as>
└ (config-rtr)# neighbor <ip> update-source loopback <number>
```

## Phase 3: Customer Onboarding
### Configure VRF on PE Routers
On each PE router and for each VPN:
```
(config)# vrf definition <VRF name>
└ (config-vrf)# rd <route distinguisher>
└ (config-vrf)# route-target import <community>
└ (config-vrf)# route-target export <community>
```

### Associate VRF to the PE-CE Interfaces
For each PE-CE interface on PEs:
```
(config)# interface ...
└ (config-if)# vrf forwarding <VRF name>
```

### Configure eBGP as the PE-CE Routing Protocol
Config on the CE:
```
(config)# router bgp <as>
└ (config-rtr)# neighbor ... remote-as ...
└ (config-rtr)# address-family ipv4 unicast
  └ (config-rtr-af)# neighbor ... activate
```

Config on the PE:
```
(config)# router bgp <as>
└ (config-rtr)# neighbor ... remote-as ...
└ (config-rtr)# address-family ipv4 vrf <VRF name>
  └ (config-rtr-af)# neighbor ... activate
```