import bluetooth
import time

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
server_sock.connect(('B8:27:EB:17:25:B1',1))
sum = 0
bt_file = open("btl.csv", "a")
for i in range(100):
    time_start = time.time()
    server_sock.send("jump")
    data = server_sock.recv(1024)
    if data:
        bt_file.write(str(time.time()-time_start) + ",\n")
        sum += time.time() - time_start

bt_file.write("Average: " + str(sum/100))
bt_file.close()

