import bluetooth


bd_addr = "F0:9E:4A:69:A9:41"
port = 4

sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))

sock.send("hello!!")

sock.close()
