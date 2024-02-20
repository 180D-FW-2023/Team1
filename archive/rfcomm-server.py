
import bluetooth
import time

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)
port = server_sock.getsockname()[1]
print("Waiting for connection on RFCOMM channel", port)
client_sock,address = server_sock.accept()
print("Accepted connection from ",address)
client_sock.send("start")
while True:
    time.sleep(1)
    data = client_sock.recv(1024)
    print ("received [%s]" % data)

client_sock.close()
server_sock.close()