#!/usr/bin/env python3

import socket
import sys
import time
import hashlib

def auth(login, password):
	"""Tryes to autentificate user according to 'users.secret' file.
	File line format: <username> <password> <access level(0-100)>
	Reurns pair of <result string>:<new accesslevel>"""
	hasher = hashlib.sha1()
	hasher.update(password.encode())
	pswd = hasher.hexdigest()
	with open('users.secret','r') as passfile:
		for line in passfile:
			sep = line.split()
			assert (len(sep) == 3), 'Error in "users.secret" file! File format: <username> <hashed password> <level> eol..,'
			if (sep[0] == login and sep[1] == pswd):
				return (login + ' - Login successed', int(sep[2]))
	return ('Login as {} failed'.format(login), -1)
def adduser(login, password, level = 0):
	with open('users.secret','r') as passfile:
		for line in passfile:
			sep = line.split()
			assert (len(sep) == 3), 'Error in "users.secret" file! File format: <username> <hased password> <level> eol..,'
			if (sep[0] == login):
				return 'Error adding user: such user already exists!'
	hasher = hashlib.sha1()
	hasher.update(password.encode())
	pswd = hasher.hexdigest()
	
	with open('users.secret','a') as passfile:
		passfile.writelines('{} {} {}\n'.format(login, pswd, level))
	return 'User added: {} with level {} '.format(login, level)
def log(data):
	"""Writes log to the 'server.log' and prints it into stdout"""
	logdata = '[{}] {}\n'.format(time.time(), data)
	print(logdata)
	with open('server.log','a') as logfile:
		logfile.write(logdata)
def loaddata():
	"""Loads data rows from 'server.data' file an returns them as dict"""
	data = {}
	with open('server.data','r') as datafile:
		for line in datafile:
			row = line.split('|')
			assert(len(row) == 2), 'Error in \'server.data\' file!'
			data.update({row[0] : int(row[1])})
	return data
def writedata(data):
	"""Writes data rows to 'server.data' file"""
	with open('server.data','w') as datafile:
		for kv in data.items():
			datafile.write('{}|{}\n'.format(kv[0],kv[1]))
		

try:
	s_s_d = loaddata()
	srv = socket.socket()
	assert (len(sys.argv) <= 2), 'Usage: server [port=9999]'
	port = 9999
	try:
		if (len(sys.argv) == 2):
			port = int(sys.argv[1])
	except ValueError as verr:
		print('Incorrect port value - should be integer. Using default')
	srv.bind(('localhost', port))
	srv.listen(0)
	log('Server started. Listening at {}'.format(port))
	cur_user = ''
	cur_level = -1
	while True:
		#log('Waiting for incoming connection...')
		res = srv.accept()
		#log('Connection established')
		buf = ''
		tmp = None
		while tmp is None or tmp != '':
			tmp = res[0].recv(100).decode()
			buf = ''.join([buf, tmp])
		log('Querry got: {}'.format(buf))
		if (buf == "exit"):
			res[0].close()
			break
		if ('login ' in buf and buf.find('login ') == 0):
			loginstr = buf.split()
			if (len(loginstr) != 3):
				continue
			(auth_res, cur_level) = auth(loginstr[1], loginstr[2])
			if ('successed' in auth_res):
				cur_user = auth_res.split()[0]
			else:
				cur_user = ''
			loginfo = '{}, current access level {}'.format(auth_res, cur_level)
			log(loginfo)
			res[0].sendall(loginfo.encode())
		elif ('adduser ' in buf and buf.find('adduser ') == 0):
			if (cur_user == ''):
				loginfo = 'Access error: You should log in to add new user!'
				log(loginfo)
				res[0].sendall(loginfo.encode())
				res[0].close()
				continue
			loginstr = buf.split()
			if (len(loginstr) != 4):
				loginfo = 'Error while adding user: incorect param count in {}'.format(loginstr)
				log(loginfo)
				res[0].sendall(loginfo.encode())
				res[0].close()
				continue
			level = cur_level
			if (level > int(loginstr[3])):
				level = int(loginstr[3])
			add_res = adduser(loginstr[1], loginstr[2], level)
			log(add_res)
			res[0].sendall(add_res.encode())
		elif ('read ' in buf and buf.find('read ') == 0):
			loginfo = 'Access level: {}'.format(cur_level)
			log(loginfo)
			res[0].sendall((loginfo+'\n').encode())
			for kv in s_s_d.items():
				if (kv[1] <= cur_level):
					loginfo = 'Data row read: {}'.format(kv)
					log(loginfo)
					res[0].sendall((loginfo+'\n').encode())
		elif ('edit ' in buf and buf.find('edit ') == 0 and len(buf.split()) == 3):
			et = buf.split()
			s_s_d_2 = {}
			modif = False
			for kv in s_s_d.items():
				if (kv[1] <= cur_level and kv[0] == et[1]):
					#tmp = kv[0] +  et[2]
					tmp = et[2]
					s_s_d_2.update({tmp : cur_level})
					res[0].sendall((tmp + ' : ' + str(cur_level) + '\n').encode())
					log('Data row modified: {0} -> {1}'.format(kv,{tmp : cur_level}))
					modif = True
				else:
					s_s_d_2.update({kv[0] : kv[1]})	
			if (not modif):
				loginfo = 'Error modifiing data row: \'{}\'. No such data row or your access level is too low'.format(et[1])
				log(loginfo)
				res[0].sendall(loginfo.encode())
			s_s_d = s_s_d_2
		elif ('add ' in buf and buf.find('add ') == 0):
			d_row = buf[len('add '):]
			if (not d_row in s_s_d.keys()):
				s_s_d.update({d_row : cur_level})
			else:
				loginfo = 'Error adding data row:{} > Such data row exists!'.format(d_row)
				log(loginfo)
				res[0].sendall(loginfo.encode())
		elif ('Done.' in buf):
			writedata(s_s_d)
			cur_user = ''
			cur_level = -1
			log('Client done. Saving data')
			res[0].sendall('Ok.'.encode())
		res[0].close()
	srv.close()
	writedata(s_s_d)
	
except AssertionError as err:
	log(err)
except socket.error as serr:
	log(serr)
except KeyboardInterrupt:
	log('Interrupted from keyboard...')
except IOError as ioerr:
	log(ioerr)
