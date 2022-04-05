





class Node():

    def __init__(self,ip):
        self.serverIp = ip
        self.currentTerm = None
        self.votedFor = None
        self.log = []
        self.timeout = None
        self.heartBeat = None
             
        self.startServer()


    def startServer(self):

        print('Hi')