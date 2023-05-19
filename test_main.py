import unittest

from PyQt5.sip import delete
import main

class MainTest(unittest.TestCase):

    def test_collapse_parsed_data(self):
        lst = ['end', ['configure terminal', ['router bgp 1', 'neighbor 1.1.1.1 ...', ['address-family ipv6', 'neighbor ...', ['router bgp 2', 'neighbor 1.1.1.1 ...', 'neighbor 2.2.2.2 ...', 'exit'], ['vrf definition blabla', 'test', 'exit'], 'exit'], ['address-family enplus', 'neighbor ...', 'exit'], ['address-family ipv6', 'neighbor 555', 'exit'], 'end']], ['configure terminal', ['router bgp 1', 'neighbor 4.4.4.4 ...', 'exit'], 'exit']]
        self.assertEqual(main.collapse_parsed_data(lst), ['end', ['configure terminal', ['router bgp 1', 'neighbor 1.1.1.1 ...', ['address-family ipv6', 'neighbor ...', ['router bgp 2', 'neighbor 1.1.1.1 ...', 'neighbor 2.2.2.2 ...', 'exit'], ['vrf definition blabla', 'test', 'exit'], 'neighbor 555', 'exit'], ['address-family enplus', 'neighbor ...', 'exit'], 'neighbor 4.4.4.4 ...', 'end']]])


    def test_parse_cfg_data(self):
        data = ["end", "router bgp 1", "neighbor 1.1.1.1 ...", "address-family ipv6", "neighbor ...", "router bgp 2", "neighbor 1.1.1.1 ...", "neighbor 2.2.2.2 ...", "exit", "vrf definition blabla", "test", "exit", "exit", "address-family enplus", "neighbor ...", "exit", "exit", "router bgp 1", "neighbor 4.4.4.4 ...", "exit"]
        self.assertEqual(main.parse_cfg_data(data), ["end", ["router bgp 1", "neighbor 1.1.1.1 ...", ["address-family ipv6", "neighbor ...", ["router bgp 2", "neighbor 1.1.1.1 ...", "neighbor 2.2.2.2 ...", "exit"], ["vrf definition blabla", "test", "exit"], "exit"], ["address-family enplus", "neighbor ...", "exit"], "neighbor 4.4.4.4 ...", "exit"]])


    def test_compare_cfg_data(self):
        old_parsed_data = ['end', 'enable', ['configure terminal', ['router ospf 1', 'mpls ldp autoconfig', 'router-id 1.0.0.1', 'exit'], 'mpls ip', ['interface FastEthernet0/0', 'ip address 1.0.1.1 255.255.255.248', 'ip ospf cost 10', 'no shutdown', 'ip ospf 1 area 0', 'mpls ip', 'exit'], ['router bgp 1', 'neighbor 3.3.3.3 remote-as 1', 'neighbor 3.3.3.3 update-source Loopback0', ['address-family vpnv4', 'neighbor 3.3.3.3 activate', 'neighbor 3.3.3.3 send-community both', 'exit-address-family'], 'end']]]
        new_parsed_data = ['end', 'enable', ['configure terminal', ['router ospf 1', 'mpls ldp autoconfig', 'router-id 1.0.0.1', 'exit'], 'mpls ip', ['interface GigabitEthernet0/0', 'ip address 1.0.1.1 255.255.255.248', 'ip ospf cost 10', 'no shutdown', 'ip ospf 1 area 0', 'mpls ip', 'exit'], ['router bgp 1', 'neighbor 3.3.3.3 remote-as 1', 'neighbor 3.3.3.3 update-source Loopback0', ['address-family vpnv4', 'neighbor 4.4.4.4 activate', 'neighbor 3.3.3.3 send-community both', 'exit-address-family'], '', 'end']]]

        added, deleted = main.compare_cfg_data(old_parsed_data, new_parsed_data)
        added = main.magic_replace_end(added)
        deleted = main.magic_replace_end(deleted)

        self.assertEqual(added, ['enable', ['configure terminal', ['router bgp 1', ['address-family vpnv4', 'neighbor 4.4.4.4 activate', 'exit-address-family'], 'exit'], ['interface GigabitEthernet0/0', 'ip address 1.0.1.1 255.255.255.248', 'ip ospf cost 10', 'no shutdown', 'ip ospf 1 area 0', 'mpls ip', 'end']]])
        self.assertEqual(deleted, ['enable', ['configure terminal', ['interface FastEthernet0/0', 'ip address 1.0.1.1 255.255.255.248', 'ip ospf cost 10', 'no shutdown', 'ip ospf 1 area 0', 'mpls ip', 'exit'], ['router bgp 1', ['address-family vpnv4', 'neighbor 3.3.3.3 activate', 'exit-address-family'], 'end']]])


    def test_magic_replace_end(self):
        lst = ['enable', ['configure terminal', ['router bgp 1', 'neighbor 1.1.1.1 ...', 'end'], ['vrf definition Client_A', 'test', 'exit']], ['configure terminal', ['vrf definition Client_B', 'test', 'end'], ['bgp router 2', 'blabla', 'end']]]
        self.assertEqual(main.magic_replace_end(lst), ['enable', ['configure terminal', ['router bgp 1', 'neighbor 1.1.1.1 ...', 'exit'], ['vrf definition Client_A', 'test', 'end']], ['configure terminal', ['vrf definition Client_B', 'test', 'exit'], ['bgp router 2', 'blabla', 'end']]])

if __name__ == "__main__":
    unittest.main()
