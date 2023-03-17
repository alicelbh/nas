import sys
import json
import copy
import time
import telnetlib
import io

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

def configureInsideProtocols(asName, uB, lAS):
    listR = [] #list of routers in the AS
    listC = [] #list of the commands for each router in the AS

    asMask = "/" +net[asName]['mask']
    asMat = net[asName]['inMatrix']
    asNb = str(net[asName]['asNumber']) 
    asProt = net[asName]['protocol']
    asPrefix = str(net[asName]['prefix'])
    matLen = len(net[asName]['inMatrix'])
    linkNumber = 0

    for i in range (0, matLen): #for each router
        routerName = asNb + str(i+1)
        routerID = asNb + '.0.0.' + str(i+1)
        loopBackAddress = asNb + "::" + str(i+1)
        routerDefinition = {
            "routerName" : routerName,
            "routerID" : routerID,
            "loopBackAddress" : loopBackAddress
        }

        listR.append(routerDefinition) #add router number, name and loopback address to the list of routers. This list of routers will then be added to the global variable "listAS" so that we can access it from outside the function

        borderAsDic = {}
        textBorder = ""

        #configure the interfaces of the border routers in their small subnets
        textBorder+= ipForBorderRouters(borderMat, asNb, asMask, uB, i)

        #configure the interfaces of the rest of the routers
        for j in range(i, matLen): #we only go through half of the matrix since we can get the two routers on a link by getting asMat[i][j] and asMat[j][i] 
            if asMat[i][j] != 0:
                subNetAddress = asPrefix +  asNb + ":" + str(linkNumber) + "::"
                inAddress = asPrefix +  asNb + ":" + str(linkNumber) + "::" + "1"
                inAddressNeighbor = asPrefix +  asNb + ":" + str(linkNumber) + "::" + "2"

                asMatDic = {
                    "interface" : asMat[i][j][0],
                    "@ip" : inAddress,
                    "@subnet" :  subNetAddress,
                    "metric" : asMat[i][j][1]
                }
                asMatDicNeighbor = {
                    "interface" : asMat[j][i][0],
                    "@ip" : inAddressNeighbor,
                    "@subnet": subNetAddress,
                    "metric" : asMat[j][i][1]
                }
            
                # progressively replace the raw adjacency matrix data by a dictionary that'll make easier to find the variables we need (subnet address, interface, ip address, etc) 
                asMat[i][j] = asMatDic
                asMat[j][i] = asMatDicNeighbor
                linkNumber += 1


        #generate the written configurations
        text = "enable\nconfigure terminal\nipv6 unicast-routing\nip bgp-community new-format\n"
        if(asProt == 'RIP'):
            text += 'ipv6 router rip ' + routerName + "\nexit\n"
            for a in range (0, matLen): #configure all of the physical interfaces
                if asMat[i][a] !=0:
                    text += "interface " + asMat[i][a]["interface"] + "\nipv6 enable" + "\nipv6 address " + asMat[i][a]["@ip"] + asMask + "\nno shutdown\nipv6 rip " + routerName + " enable \nexit\n"
            text+= "interface loopback 0\nipv6 enable\nipv6 address " + loopBackAddress + "/128" + "\nno shutdown\nipv6 rip " + routerName + " enable \nexit\n"
            text+= textBorder
            if borderAsDic != {}:
                text+= ""

        elif(asProt == 'OSPF'):
            text += 'ipv6 router ospf 1\nrouter-id ' + routerID + "\nexit\n"
            for a in range (0, matLen): #configure all of the physical interfaces
                if asMat[i][a] !=0:
                    text+= "interface " + asMat[i][a]["interface"] + "\nipv6 enable" + "\nipv6 address " + asMat[i][a]["@ip"] + asMask + "\nip ospf cost " + str(asMat[i][a]["metric"])+"\nno shutdown\nipv6 ospf 1 area 0\nexit\n"
            text+= "interface loopback 0\nipv6 enable\nipv6 address " + loopBackAddress + "/128" + "\nno shutdown\nipv6 ospf 1 area 0 \nexit\n"
            text+= textBorder

        listC.append(text) #add command to list

    asSpecifications = {
        "routers" : listR,
        "config" : listC,
        "matrix" : asMat
    }

    lAS.append(asSpecifications)

def ipForBorderRouters(borderMat, asNb, asMask, uB, i):
    t = ""
    for b in range (0, len(borderMat)):
                if borderMat[int(asNb)-1][b] != 0: #check if there exist a connection betwteen our AS and another one
                    l = []
                    for z in range (0,len(borderMat[int(asNb)-1][b]), 3): #if there exists one, check if the number of the router i is in the border matrix
                        if borderMat[int(asNb)-1][b][z] == i: 
                            borderAsDic = {
                                "router" : i,
                                "interface" : borderMat[int(asNb)-1][b][z+1],
                                "@ip" : str(borderMat[int(asNb)-1][b][z+2])  + ":" + asNb,
                                "@subnet" :  borderMat[int(asNb)-1][b][z+2] + ":" + asMask
                            }
                            uB[int(asNb)-1][b].append(borderAsDic)
                            t += "interface " + borderAsDic["interface"] + "\nipv6 enable" + "\nipv6 address " + borderAsDic["@ip"] + asMask + "\nno shutdown\nexit\n" 
    return t


def configureBorderProtocol(lAS, uB):
    adjAS = net['adjAS']
    for n in range(0, len(lAS)):
        mask = "/" + str(net['AS' + str((n+1))]['mask'])
        ####### configure iBGP
        for i in range(0, len(lAS[n]["routers"])):
            lAS[n]["config"][i] += "router bgp " + str(n+1) +"\nno bgp default ipv4-unicast\nbgp router-id " + lAS[n]["routers"][i]["routerID"] + "\n"
            for j in range(0, len(lAS[n]["routers"])):
                if i != j:
                    lAS[n]["config"][i] += "neighbor " + lAS[n]["routers"][j]["loopBackAddress"] +" remote-as " +str(n+1)+"\nneighbor " + lAS[n]["routers"][j]["loopBackAddress"] +" update-source Loopback0\n"
            lAS[n]["config"][i] += "address-family ipv6 unicast\n"
            for j in range(0, len(lAS[n]["routers"])):
                if i!=j:
                    lAS[n]["config"][i] += "neighbor " + lAS[n]["routers"][j]["loopBackAddress"] +" activate\nneighbor " + listAS[n]["routers"][j]["loopBackAddress"] +" send-community\n"
            for j in range(0, len(lAS[n]["matrix"][i])):
                if lAS[n]["matrix"][i][j] != 0:
                    lAS[n]["config"][i] += "network " + lAS[n]["matrix"][i][j]["@subnet"] + mask +"\n"
            lAS[n]["config"][i] += "exit\n"
        ####### configure eBGP
        for i in range(0, len(adjAS[n])):
            if (adjAS[n][i]) != 0:
                for y in range(0, len(uB[i][n])):
                    localRouter = uB[n][i][y]['router'] #get number of the border router in our AS 
                    neighborAddress =  uB[i][n][y]['@ip']#get the ip of the border router we are connected to 
                    lAS[n]["config"][localRouter] += "neighbor " + neighborAddress + " remote-as " + str(i+1) + "\naddress-family ipv6 unicast\nneighbor " + neighborAddress + " activate\nneighbor " + neighborAddress + " \nnetwork " + uB[i][n][y]['@subnet'] + "\nexit\n"

    routemap_configuration(lAS, uB, adjAS)
def routemap_configuration(lAS, uB, adjAS):
    for i in range(0, len(adjAS)):
        for j in range(0, len(adjAS[i])):
            if (adjAS[i][j] != 0) :
                for k in range(0, len(uB[j][i])):                    
                    router = uB[i][j][k]['router']
                    address =  uB[j][i][k]['@ip']
                    #set up access-lists
                    alist = ""
                    if(len(uB[j][i]) > 1):
                        lAS[i]["config"][router] += "end\nconfigure terminal\n ipv6 access-list other_link_filter\n"
                        alist = "route-map non_client_out deny 5\nmatch ipv6 address other_link_filter\nexit\n"
                    for t in range(0,len(uB[j][i])):
                        if (t != k):
                            lAS[i]["config"][router] += "permit " + uB[j][i][t]['@subnet'] + " any\n"
                    #set up route-maps
                    l = len(adjAS[i][j])-1
                    rship = adjAS[i][j][l]
                    match rship:
                        case "peer":
                            lAS[i]["config"][router] += "end\nconfigure terminal\nip community-list standard provider_filter permit " + str(i+1)+":10\nip community-list standard peer_filter permit " + str(i+1)+":20\n"+alist+"route-map non_client_out deny 10\nmatch community provider_filter\nexit\nroute-map non_client_out deny 20\nmatch community peer_filter\nexit\nroute-map non_client_out permit 100\nexit\nroute-map peer_handler permit 10\nset community "+str(i+1)+":20\nset local-preference 200\nexit\nrouter bgp " + str(i+1) + "\naddress-family ipv6 unicast\nneighbor " + address + " route-map non_client_out out\nneighbor " + address + " route-map peer_handler in\nend\n"
                        case "provider":
                            lAS[i]["config"][router] += "end\nconfigure terminal\nip community-list standard provider_filter permit " + str(i+1)+":10\nip community-list standard peer_filter permit " + str(i+1)+":20\n"+alist+"route-map non_client_out deny 10\nmatch community provider_filter\nexit\nroute-map non_client_out deny 20\nmatch community peer_filter\nexit\nroute-map non_client_out permit 100\nexit\nroute-map provider_handler permit 10\nset community "+str(i+1)+":10\nset local-preference 50\nexit\nrouter bgp " + str(i+1) + "\naddress-family ipv6 unicast\nneighbor " + address + " route-map non_client_out out\nneighbor " + address + " route-map provider_handler in\nend\n"
                        case "client":
                            lAS[i]["config"][router] += "end\nconfigure terminal\nroute-map client_handler permit 10\nset community " + str(i+1)+":37\nset local-preference 300\nexit\nrouter bgp " + str(i+1) + "\naddress-family ipv6 unicast\nneighbor " + address + " route-map client_handler in\nend\n"
                    lAS[i]["config"][router] += "clear bgp ipv6 unicast *"

def telnetHandler(lAS):
    for i in range(len(net.keys()) - 1):
        nbRouters = len(net["AS" + str(i+1)]['inMatrix'])
        for j in range(nbRouters): 
            time.sleep(0.1)
            
            port = net["AS" + str(i+1)]["listPorts"][j]
            print(port)
            tn = telnetlib.Telnet("localhost", port)
            buf = io.StringIO(lAS[i]["config"][j])
            read_lines = buf.readlines()

            for line in read_lines:
                print(line)
                #we write each line in the router's console
                tn.write(b"\r\n")
                tn.write(line.encode('utf_8') + b"\r\n")
                time.sleep(0.1)
    print("Done")

def generateTextFiles(lAS):
    for i in range (0, len(lAS)):
        for r in range (0, len(lAS[i]['config'])):
            f = open("configs/as"+ str(i+1) + "_router" + str(r+1) +".txt", "w")
            f.write(lAS[i]['config'][r])

def button1_clicked(lAS, uB):
   #implement the inner protocols of each AS
    for key in net: #for each 
        if (key!="adjAS"):
            configureInsideProtocols(key, uB, lAS)

    configureBorderProtocol(lAS, uB) #implement the border protocols between all the connectes AS

    generateTextFiles(lAS) #generate writter config
    
    #telnetHandler(lAS) #send the config to telnet

    print(uB)

def window(lAS, uB):
    app = QApplication(sys.argv)
    widget = QWidget()

    button1 = QPushButton(widget)
    button1.setText("Generate files")
    button1.move(20,32)
    button1.clicked.connect(lambda:button1_clicked(lAS, uB))

    widget.setGeometry(50,50,200,100)
    widget.setWindowTitle("Dudu")
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    listAS = [] #mother list that will contain the router list, config list and matrix of each AS
    with open('network_multi.json', 'r') as openfile:
        net = json.load(openfile)

    #generate an array to store the new information about border router (ip, subnet, etc)
    borderMat = net['adjAS']
    updatedBorder = copy.deepcopy(borderMat)
    for u in range (0, len(updatedBorder)):
        for v in range (0, len(updatedBorder)):
            if updatedBorder[u][v] != 0 :
                updatedBorder[u][v] = [] #every list in the array is replaced by an empty one (we'll need them after)
    
    window(listAS, updatedBorder)