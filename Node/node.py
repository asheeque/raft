# coding=utf-8
import random
import time
import os
import socket
import threading
import json
import traceback
import sys
####

from flaskapp import FlaskApp

class Node():

    def __init__(self):
        self.currentTerm = 0
        self.status="FOLLOWER"
        self.voteCount=0
        self.log = []
        self.timeout = None
        self.heartBeat = None
        self.leaderEligible=3
        self.udpPort=5555
        self.timeout_thread = None
        self.currentNode = os.getenv('name')
        self.serverList=["Node1","Node2","Node3","Node4","Node5"]
        self.count=0
        self.nodeActiveDict = {
            "Node1":"ACTIVE",
            "Node2":"ACTIVE",
            "Node3":"ACTIVE",
            "Node4":"ACTIVE",
            "Node5":"ACTIVE"
        }
        self.heartBeatInterval = 100
        self.state = 'ACTIVE'
        self.leaderName=None
        self.termDetails={
        "votedFor": None,
        "request": None,
        "term": 0,
        "key": None,
        "value": None
        }
        self.nextIndex = {}
        self.db=[]
        self.logIndex=0

    def init_timeout(self):
        self.getRandomElectionTime()
        # safety guarantee, timeout thread may expire after election
        if self.timeout_thread and self.timeout_thread.isAlive():
            return
        self.startTimerNew = threading.Thread(target=self.startTimer)
        self.startTimerNew.start()
    
    def init_socket(self):
        SERVER = os.getenv('name')
        ADDR = (SERVER,self.udpPort)
        UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDP_Socket.bind((ADDR))
        return UDP_Socket

    def getRandomElectionTime(self):
        LOW_TIMEOUT = 150
        HIGH_TIMEOUT = 300
        self.timeout = (random.randrange(LOW_TIMEOUT, HIGH_TIMEOUT) / 1000) + time.time()
        # return electionTime

    def startTimer(self):
        
        while self.status != 'LEADER' and self.state=='ACTIVE':
            delta = self.timeout - time.time()
            if delta < 0 :
                self.startElection()
            else:
                time.sleep(delta)

    def startElection(self):

        self.currentTerm=self.currentTerm+1
        self.status="CANDIDATE"
        self.voteCount=0
        self.init_timeout()
        self.increaseVote()
        self.voteRequest()
        

    def increaseVote(self):
        self.voteCount+=1
        if self.voteCount >= self.leaderEligible:

            self.status="LEADER"
            self.leaderName=self.currentNode
            for servers in self.serverList:

                self.nextIndex[servers] =  len(self.db)+1 
            print(self.nextIndex)
            print("Leader Selected",self.leaderName,flush=True)
            empty_hb ={
                        "term": self.currentTerm,
                        "leaderId":self.currentNode,
                        "entries":[],
                        "prevLogIndex":0,
                        "prevLogTerm":0,
                    }
            self.startHeartbeat(empty_hb)

    
        
    
    def startHeartbeat(self,value):

        while self.status == 'LEADER' and self.state=='ACTIVE':

            start_time = time.time()
            for i in self.serverList:
                if i!=self.currentNode:
                    
                    message={
                        "sender_name": self.currentNode,
                        "request": "APPEND_RPC",
                        "term": self.currentTerm,
                        "key": 'key',
                        "value": value
                        }
                    threading.Thread(target=self.sender, args=[i,message]).start()
            delta = time.time() - start_time
            time.sleep((self.heartBeatInterval - delta) / 1000)


    def voteRequest(self):
        for i in self.serverList:
            if i!=self.currentNode :
                mess={
                    "term": self.currentTerm,
                    "voteCount": self.voteCount,
                    "candidateId":self.currentNode,
                    "lastLogIndex":0,
                    "lastLogTerm":0,
                }
                message={
                    "sender_name": self.currentNode,
                    "request": "VOTE_REQUEST",
                    "term": self.currentTerm,
                    "key": 'key',
                    "value": mess
                    }
                threading.Thread(target=self.sender, args=[i,message]).start()
        

    def sender(self,target,message):
        try:
            msg_bytes = json.dumps(message).encode('utf-8')
            self.sock.sendto(msg_bytes, (target,self.udpPort))
        except KeyboardInterrupt:
            self.printwt('Shutting down server...')
            self.sock.close()


    def startListener(self):        
        threading.Thread(target=self.listener).start()

    
    def listener(self):
        print(f"Starting Listener ",file=sys.stderr)
        while True:
            try:
                msg, addr = self.sock.recvfrom(1024)
                decoded_msg = json.loads(msg.decode('utf-8'))
                threading.Thread(target=self.listener_thread_handler, args=[msg,decoded_msg]).start()
            except:
                print(f"ERROR while fetching from socket : {traceback.print_exc()}")


    def listener_thread_handler(self,msg,decoded_msg):
        
        # if decoded_msg['sender_name'] == 'Controller':
            
        # self.termDetails['votedFor']=decoded_msg['sender_name']
        # self.termDetails['term']=decoded_msg['term']
        # self.termDetails['log']=[],
        # self.termDetails['heartbeatInterval']=100
        # self.termDetails['timeoutInterval']=self.timeout
        # # print(msg)
        # # print(self.termDetails)
        # json_string = json.dumps(self.termDetails)
        # with open('json_data.json', 'w') as outfile:
        #     json.dump(json_string, outfile)


        if decoded_msg['request'] == 'VOTE_REQUEST' and self.state=='ACTIVE':
            self.grantVote(decoded_msg)
        elif decoded_msg['request'] == 'APPEND_RPC' and self.state=='ACTIVE':
            self.receive_heartbeat(decoded_msg)
        elif decoded_msg['request'] == 'CONVERT_FOLLOWER' and self.state=='ACTIVE':
            # print(self.termDetails)
            self.convertLeaderToFollower()
            # print(decoded_msg)
        elif decoded_msg['request'] == 'LEADER_INFO' and self.state=='ACTIVE':
            self.getLeaderInfo()
        elif decoded_msg['request'] == 'SHUTDOWN' and self.state=='ACTIVE':
            self.shutdownNode()
        elif decoded_msg['request'] == 'STATE_REQ' :
            self.getNodeStatus(decoded_msg)
        elif decoded_msg['request'] == 'TIMEOUT' and self.state=='ACTIVE':
            self.forceTimeout()
        elif decoded_msg['request'] == 'STATE_RES':
            self.updateNodeActiveList(decoded_msg)
        elif decoded_msg['request'] == 'VOTE_ACK' and decoded_msg['sender_name'] != self.currentNode:
            self.increaseVote()
        elif decoded_msg['request']=='UPDATELEADERELIGIBLE':
            self.leaderEligible=decoded_msg['value']
        elif decoded_msg['request']=='PUT':
            self.handlePut(decoded_msg)
        elif decoded_msg['request']=='STORE':
            self.controller_store(decoded_msg)
    
    def controller_store(self,data):
        # print(data)

        if self.status == "LEADER":

            # if self.currentTerm not in self.db:
            #     self.db[self.currentTerm] = []


            single_log = {
                "term":self.currentTerm,
                "key" : data['key'],
                "value" : data['value']
            }
            self.db.append(single_log)
            print(self.db)
            self.broadcastLogs(single_log)
        else :
            store_reply = {
                "sender_name": self.currentNode,
                "request": "LEADER_INFO",
                "term": self.currentTerm,
                "key": 'LEADER',
                "value": self.leaderName
            }

            reply = json.dumps(store_reply).encode('utf-8')
            threading.Thread(target=self.sendAck,args=[data['sender_name'],reply]).start()





    def updateNodeActiveList(self,decoded_msg):
        node = decoded_msg['sender_name']
        nodeState = decoded_msg['value']
        if node in self.nodeActiveDict :
            self.nodeActiveDict[node] = nodeState
        

    def forceTimeout(self):
        # self.leaderName=None
        msg={
            "sender_name":self.currentNode,
            "request":"CONVERT_FOLLOWER",
            "term": self.currentTerm
        }
        self.sock.sendto(json.dumps(msg).encode('utf-8'), (self.leaderName, self.udpPort))
        print(self.currentNode," ", self.leaderName)
        self.startElection()



    def getNodeStatus(self,decoded_msg):
        
        # self.currentTerm=decoded_msg['term']
      
        message={
        "sender_name": self.currentNode,
        "request": "STATE_RES",
        "term": self.currentTerm,
        "key": 'STATE',
        "value": self.state
            }
        reply = json.dumps(message).encode('utf-8')
        threading.Thread(target=self.sendAck,args=[decoded_msg['sender_name'],reply]).start()


    def shutdownNode(self):
        if self.state == 'ACTIVE':
            eligible = 0
            if(self.leaderEligible%2==0):
                eligible=self.leaderEligible
            else:
                eligible=self.leaderEligible+1

            totalcount=2*(eligible-1)
            val=(totalcount-1)/2+1
            message={
            "sender_name": self.currentNode,
            "request": "UPDATELEADERELIGIBLE",
            "term": self.currentTerm,
            "key": 'leaderEligible',
            "value": val
            }
            # reply=json.dumps(message).encode('utf-8')
            threading.Thread(target=self.sender,args=[self.currentNode,message]).start()
            print("Shutdown::")
            self.state = 'INACTIVE'


    def getLeaderInfo(self):
        message={
                "sender_name": self.currentNode,
                "request": "LEADER_INFO",
                "term": self.currentTerm,
                "key": 'LEADER',
                "value": self.leaderName
                }
        print(message,flush=True)

    
    def convertLeaderToFollower(self):
        # print(self.termDetails)
        if self.status == 'LEADER':
            self.status = 'FOLLOWER'
            
            self.init_timeout()
    

    def receive_heartbeat(self,message):
        if message['term'] >= self.currentTerm :
            self.getRandomElectionTime()
            leader = message['value']['leaderId']
            self.leaderName = leader
            if self.status == 'CANDIDATE':
                self.status == 'FOLLOWER'
                # print('Can-Follow')
            elif self.status == 'LEADER':
                self.status == 'FOLLOWER'
                self.init_timeout()
            self.voteCount = 0
            if message['term'] > self.currentTerm :
                self.currentTerm = message['term']


    def grantVote(self,decoded_msg):
        if decoded_msg['term'] > self.currentTerm:
            # print(decoded_msg['term'],decoded_msg['sender_name'])
            self.currentTerm=decoded_msg['term']
            self.termDetails['votedFor']= decoded_msg['sender_name']
            print("in grant_vote::",self.termDetails['votedFor'])
            self.voteCount = 0
            self.getRandomElectionTime()
            message={
            "sender_name": self.currentNode,
            "request": "VOTE_ACK",
            "term": self.currentTerm,
            "key": 'key',
            "value": []
             }
            reply=json.dumps(message).encode('utf-8')
            threading.Thread(target=self.sendAck,args=[decoded_msg['sender_name'],reply]).start()



    def sendAck(self,server_name,ack):
        self.sock.sendto(ack,(server_name,self.udpPort))

    def handlePut(self,content):
        
        # print(content)
        self.checkLogging(content)
    
    def checkLogging(self,content):
        if(self.status=="LEADER"):
            
            temp={}
        
            temp["Status"]=self.status
            temp["LogIndex"]=self.logIndex-1
            temp["CurrentNode"]=self.currentNode
            temp["PUT"]=content
            if self.currentTerm not in self.db:

                self.db[self.currentTerm] = []
            self.db[self.currentTerm].append(temp)
        # self.db[self.currentTerm].append(temp)
        # print(self.db)
        # confirmat

    def broadcastLogs(self,log):

        
        start_time = time.time()
        for i in self.serverList:
            if i!=self.currentNode:

                nextIndex = self.nextIndex[i]
                prevLogIndex = nextIndex - 1

                prevLogTerm = -1
                if prevLogIndex >=0:
                    prevLogTerm = self.db[prevLogIndex] - 1

                appendRPCMsg = {
                        "term": self.currentTerm,
                        "leaderId":self.currentNode,
                        "entries":log,
                        "prevLogIndex":0,
                        "prevLogTerm":0,
                    }
                message={
                    "sender_name": self.currentNode,
                    "request": "APPEND_RPC",
                    "term": self.currentTerm,
                    "key": 'key',
                    "value": appendRPCMsg
                    }
                threading.Thread(target=self.sender, args=[i,message]).start()
        delta = time.time() - start_time
        time.sleep((self.heartBeatInterval - delta) / 1000)
        

      
# if __name__ == "__main__":
#     n = Node()

#     n.getRandomElectionTime()  
#     n.init_timeout()
#     print("76",file=sys.stderr)
#     n.sock = n.init_socket()
#     n.startListener()
#     PORT = os.getenv('PORT')
#     print(PORT,file=sys.stderr)
#     print("76",file=sys.stderr)
#     ip = os.getenv('IP')
#     f = FlaskApp(PORT)
    