import socket
import sys

try:
	cli = socket.socket()
	assert (len(sys.argv) == 3 or len(sys.argv) == 4), 'Usage: client <host> <port> [what]'
	cli.connect((sys.argv[1], int(sys.argv[2])))
	if (len(sys.argv) == 4):
		cli.sendall(sys.argv[3].encode())
	else:
		cli.sendall('exit'.encode())
except AssertionError as err:
	print(err)
except socket.error as serr:
	print(serr)
	
	
