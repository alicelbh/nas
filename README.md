# nas
1) Features
Phase 1 : OK
Phase 2 : OK
Phase 3 : OK
Phase 4 : 
- Manageability (config ghosting) OK
- Internet services OK
- Ingress TE r multi-connected CE routers

2) JSON File
Each AS has a mask, an AS Number, a router type (not used but could be if we needed to), the internal protocol (OSPF or RIP), the number of the router which serves as the route reflector and the border protocol (BGP). 

The inside matrix is an adjacency matrix where each case holds the following information : the interface on which the router is connected and the metric of the link (for OSPF).

The port list is used for Telnet to specify where to send the configs.

The PE list is organized as follows : [[router_1, [VRF1], [VRF2], ...], [router_2, [VRF1], [VRF2], ...]]

The VRFs are defined as : [interface_name, vrf_name, route_target, net_ip@, ce_ip@, client_as_number, med_client]

Each client can communicate with a list of other clients : "Client A" can communicate with [["Client_B", route_target_client_b], ["Client_C", route_target_client_c]]

3) Run the code
* python3 main.py

4) Bonus : modify the matrix of an AS
To modify the inside matrix of an AS in the JSON, type :
* python3 modif_matrix.py _AS_number_of_the_matrix_to_modify_
You'll then be able to add/delete routers and create connections between them. The resulting matix will be printed in the terminal, and all you have to do is copy paste it in the JSON file. 
