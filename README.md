# nas
**1) Features**

Phase 1 : OK

Phase 2 : OK

Phase 3 : OK

Phase 4 : 

- Manageability (config ghosting) OK
        mostly done, there might be unforeseen undesirable behaviours. If the router is turned off or reloaded you must manually remove the configuration files in "./old_configs".
- Internet services OK
        PE routers can now also handle standard internet, meaning they don't necessarily have vrfs. The adjAS matrix handles the border router connections.
- Ingress TE multi-connected CE routers OK
        each PE associates a MED and a BGP community to the routes it shares with its client, allowing the latter to modify those and perform TE based on them
- Site sharing OK
        route target imports are handled by the "Clients" structure. The self import is always implicit, other imports can be made to connect different VPN clients.


**2) JSON File**

Each AS has a mask, an AS Number, a router type (not used but could be if we needed to), the internal protocol (OSPF or RIP), the number of the router which serves as the route reflector and the border protocol (BGP). 

The inside matrix is an adjacency matrix where each cell holds the following information : the interface on which the router is connected and the metric of the link (for OSPF).

The port list is used for Telnet to specify where to send the configs.

The PE list is organized as follows : [[router_1, [VRF1], [VRF2], ...], [router_2, [VRF1], [VRF2], ...]]. Each PE can have several VRFs **or none** (Internet Services, necessary in order to open BGP sesson with Route Reflector).

The VRFs are defined as : [interface_name, vrf_name, route_target, net_ip@, ce_ip@, client_as_number, med_client]

Each client can communicate with a list of other clients : "Client A" can communicate with [["Client_B", route_target_client_b], ["Client_C", route_target_client_c]]

Finally adjAS is an adjacency matrix used if we have several AS. For four AS, it would look like this : 

"adjAS": 

        [[0, [5,"FastEthernet0/0", "1000:1:", 6, "FastEthernet0/0", "1000:2:", "peer"], 0, 0],
        
        [[5, "FastEthernet0/0", "1000:1:", 6, "FastEthernet0/0", "1000:2:", "peer"] ,  0, [2, "GigabitEthernet3/0", "1000:3:", "client"], [1, "GigabitEthernet3/0", "1000:4:", "provider"]],
        
        [0, [0, "GigabitEthernet3/0", "1000:3:", "provider"], 0, 0],
        
        [0, [0, "GigabitEthernet3/0", "1000:4:","client"], 0, 0]]

AS 1 is connected to AS 2 with two routers by AS (router 5 and router 6). For each cell, the syntax is the following : [border_router_number, inteface_name, subnet_address, border_router_number_2, inteface_name_2, ..., relationship]. The relationship (peer, client or provider) is always at the end of the cell.

**3) Run the code**

* python3 main.py


**4) Bonus : modify the matrix of an AS**

To modify the inside matrix of an AS in the JSON, type :
* python3 modif_matrix.py _AS_number_of_the_matrix_to_modify_

You'll then be able to add/delete routers and create connections between them. The resulting matrix will be printed in the terminal, and all you have to do is copy paste it in the JSON file. 
