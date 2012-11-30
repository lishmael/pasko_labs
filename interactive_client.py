#!/usr/bin/env python3

import socket
import sys

try:
	assert (len(sys.argv) == 3), 'Usage: interactive_client <host> <port>'
	work = True
	while work:
		cli = socket.socket()
		cli.connect((sys.argv[1], int(sys.argv[2])))	
		choice = input('Select option: \n 1. Login \n 2. Add user\n 3. Read data \n 4. Modify data \n 5. Add data\n 6. Quit\n')
		if (not (choice in '123456' and len(choice) == 1)):
			print('Incorrect choice!')
			continue
		querry = ''
		if (choice == '1'):
			querry = 'login ' + input('Enter login: ') + ' ' + input('Enter password: ')
		elif (choice == '2'):
			querry = 'adduser ' + input('Enter new login: ') + ' ' + input('Enter password: ') + ' ' + input('Security level: ')
		elif (choice == '3'):
			querry = 'read ' 
		elif (choice == '4'):
			querry = 'edit ' + input('What: ') + ' ' +  input('How: ')
		elif (choice == '5'):
			querry = 'add ' + input('What: ')
		elif (choice == '6'):
			querry = 'Done.'
			work = False
		cli.send(querry.encode())
		cli.shutdown(socket.SHUT_WR)
		answ = ''
		tmp = None
		while tmp is None or tmp != '':
			tmp = cli.recv(100).decode()
			answ = ''.join([answ, tmp])
		print(answ)
		cli.close()
except AssertionError as err:
	print(err)
except socket.error as serr:
	print(serr)
except KeyboardInterrupt:
	cli = socket.socket()
	cli.connect((sys.argv[1], int(sys.argv[2])))
	cli.send('Done.'.encode())
	cli.close()
	print('Interrupted from keyboard...')