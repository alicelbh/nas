
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit
import sys
import json

def window(jsonObj, finalMatrix):
    app = QApplication(sys.argv)
    widget = QWidget()

    howManyRouter = QLineEdit(widget)
    howManyRouter.move(20, 100)
    howManyRouter.setPlaceholderText(" Nb of routers to add")
    howManyRouter.resize(150,40)

    toDelete = QLineEdit(widget)
    toDelete.move(20, 300)
    toDelete.setPlaceholderText(" Which router to delete")
    toDelete.resize(150,40)

    routerConnections = QLineEdit(widget)
    routerConnections.move(20, 500)
    routerConnections.setPlaceholderText(" ex : 5 GigabitEthernet1/0 7 FastEthernet0/0 10")
    routerConnections.resize(330,40)

    add = QPushButton(widget)
    add.setText("Add router")
    add.move(20, 160)
    add.clicked.connect(lambda:addRouter(howManyRouter, finalMatrix))

    rm = QPushButton(widget)
    rm.setText("Remove router")
    rm.move(20, 360)
    rm.clicked.connect(lambda:removeRouter(toDelete, finalMatrix))

    co = QPushButton(widget)
    co.setText("Add connection")
    co.move(20, 560)
    co.clicked.connect(lambda:connectRouter(routerConnections, finalMatrix))
    

    widget.setGeometry(50,50,500,700)
    widget.setWindowTitle("Matrix modification")
    widget.show()
    sys.exit(app.exec_())

def addRouter(howManyRouter, fM):
    try:
        nbRouter = int(howManyRouter.text())
    except:
        print("This is not an integer !")
        return 0
    zeroToList(fM)
    n = len(fM)
    for a in range(0, nbRouter):
        fM.append([])
        fM[n].append([])
        for i in range (0, n):
            fM[n].append([])
            fM[n][i] = 0 #we can't directly append a 0 so we add an empty list then turn it into a 0
            fM[i].append([])
            fM[i][n] = 0
        fM[n][n] = 0
        n = n+1
    listToZero(fM)
    printPretty(fM)

def removeRouter(toDelete, fM):
    try:
        routerNumber = int(toDelete.text())
    except:
        print("This is not an integer !")
        return 0
    n = len(fM)
    if routerNumber>n:
        print("This router does not exist.")
        return 0

    zeroToList(fM)
    if n !=1:
        for i in range (0,n):
            fM[i].pop(routerNumber-1)
        fM.pop(routerNumber-1)
    else:
        print("You need at least 1 router !")
        return 0
    listToZero(fM)
    printPretty(fM)

def connectRouter(rCo, fM):
    connections = rCo.text()
    l = [str(num) for num in connections.split()]
    try: 
        router1 = int(l[0]) -1
        if1 = l[1]
        router2 = int(l[2]) -1
        if2 = l[3]
        weight = int(l[4])
    except:
        print("Wrong format. Try again.")
        return 0

    if(router1> len(fM)-1 or router2>len(fM)-1):
        print("Out of bounds. Try again")
        return 0

    fM = zeroToList(fM)

    for i in range (0, len(fM[router1])):
        if fM[router1][i] != [] :
            if fM[router1][i][0] == if1:
                print(if1 + "is already attributed towards " + str(i+1))
                return 0
    for i in range (0, len(fM[router2])):
        if fM[router2][i] != [] :
            if fM[router2][i][0] == if2:
                print(if2 + "is already attributed towards " + str(i+1))
                return 0
    fM[router1][router2]=[if1,weight]
    fM[router2][router1]=[if2,weight]
    listToZero(fM)
    printPretty(fM)

def zeroToList(m):
    for i in range(0, len(m)):
        for j in range(0, len(m)):
            if m[i][j]==0:
                m[i][j]=[]
    return m

def listToZero(m):
    for i in range(0, len(m)):
        for j in range(0, len(m)):
            if m[i][j]==[]:
                m[i][j]=0
    return m

def printPretty(m):
    toPrint = "["
    for r in range(0, len(m[0])):
        if r == len(m[0])-1:
            toPrint += (str(m[r]).replace("'","\"")) + "]"
        else:
            toPrint += (str(m[r]).replace("'","\"") + ",\n")
    print(toPrint)
    print("\n")

if __name__ == "__main__":
    with open('network.json', 'r') as openfile:
        j = json.load(openfile)
    finalMatrix = j["AS" + str(sys.argv[1])]['inMatrix']
    window(j, finalMatrix)


