import socket
import time

s = socket.socket()
s.connect(('192.168.1.222', 5025))
time.sleep(1)
s.send("\r\n")
s.send(":SOURCE:CLOOP1:SPOINT 100\r\n")
time.sleep(1)
s.send(":SOURCE:CLOOP1:SPOINT?\r\n")
time.sleep(1)
print s.recv(256)
s.close()

