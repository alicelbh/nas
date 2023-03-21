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
```
address-family vpnv4
└ neighbor ... activate
└ neighbor ... send-community both
```

### Loopback to Loopback iBGP sessions
Re-use code

