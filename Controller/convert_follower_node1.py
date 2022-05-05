from base64 import decode
import json
import socket
import traceback
import time
import threading
# Wait following seconds below sending the controller request
time.sleep(8)

# Read Message Template
msg = json.load(open("Message.json"))

# Initialize
sender = "Controller"
target = "Node1"
port = 5555

# Request
# msg['sender_name'] = sender
# msg['request'] = "PUT"
# msg['key']=0
# msg['value']="test_log"


msg1 = {
    'sender_name':sender,
    'request':"PUT",
    "key":"k1",
    "value":"test_log"
}

msg2 = {
    'sender_name':sender,
    'request':"STORE",
    "key":"k1",
    "value":"value1"

}
print(f"Request Created : {msg}")
# Socket Creation and Binding
skt = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
skt.bind((sender, port))

# Send Message
try:
    # Encoding and sending the message
    skt.sendto(json.dumps(msg2).encode('utf-8'), (target, port))
except:
    #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
    print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")

def startListener():        
        threading.Thread(target=listener).start()

def listener():
        print(f"Starting Listener ")
        while True:
            try:
                msg, addr = skt.recvfrom(1024)
                decoded_msg = json.loads(msg.decode('utf-8'))
                threading.Thread(target=listener_thread_handler, args=[msg,decoded_msg]).start()
            except:
                print(f"ERROR while fetching from socket : {traceback.print_exc()}")

def listener_thread_handler(msg,decoded_msg):

    print(decoded_msg)
    if decoded_msg['request'] == 'LEADER_INFO':
        current_leader = decoded_msg['value']
        msg2 = {
            'sender_name':sender,
            'request':"STORE",
            "key":"k1",
            "value":"value1"
        }
        try:
            # Encoding and sending the message
            skt.sendto(json.dumps(msg2).encode('utf-8'), (current_leader, port))
        except:
            #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
            print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")



      
if __name__ == "__main__":
    startListener()
