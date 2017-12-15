import os, shelve, types


def processData(recvData):
	recvData = washData(recvData)
	#print "debug: receive", recvData
	try:
		file = shelve.open("user.dat")
		if recvData['type'] == "notice":
			sendData = {
				'type' : "notice",
				'content' : "Sever is connected"
			}
		elif recvData['type'] == "signUp":
			username = recvData['username']
			password = recvData['password']
			if username in file:
				sendData = {
					'type' : "signUpResult",
					'result' : "User already exist!"
				}
			else:
				userData = {
					'password' : password,
					'bestScore' : 0,
					'rank' : len(file),
					'record' : []
				}
				file[username] = userData
				sendData = {
					'type' : "signUpResult",
					'result' : "success",
					'username' : username,
					'rank' : file[username]['rank']
				}
		elif recvData['type'] == "login":
			username = recvData['username']
			password = recvData['password']
			if username in file:
				if password == file[username]['password']:
					sendData = {
						'type' : "loginResult",
						'result' : "success",
						'username' : username,
						'bestScore' : file[username]['bestScore'],
						'rank' : file[username]['rank'],
						'record' : file[username]['record']
					}
				else:
					sendData = {
						'type': "loginResult",
						'result': "Password error"
					}
			else:
				sendData = {
					'type' : "loginResult",
					'result' : "Unregistered username"
				}
		elif recvData['type'] == "recentScore":
			username = recvData['username']
			userData = file[username]
			userData['recentScore'] = recvData['score']
			file[username] = userData
			print "User", username, "recent Score is", file[username]['recentScore']
			sendData = {
				'type' : "Nothing",
				'source' : "recentScore"
			}
		elif recvData['type'] == "finalScore":
			username = recvData['username']
			userData = file[username]
			for i in range(len(userData['record'])+1):
				if i == len(userData['record']) or \
						userData['record'][i][0] < recvData['score']:
					userData['record'].insert(i, (recvData['score'],
												  recvData['time'],
												  recvData['date']))
					break
			if len(userData['record']) > 20:
				userData['record'].pop()
			if userData['bestScore'] < recvData['score']:
				userData['bestScore'] = recvData['score']
			file[username] = userData
			rank = 1
			for i in file:
				if i != username:
					if file[i]['bestScore'] > file[username]['bestScore']:
						rank += 1
			print "User", username, "final Score is", file[username]['recentScore'], ", rank is", rank
			sendData = {
				'type' : "Update user info",
				'bestScore' : file[username]['bestScore'],
				'rank' : rank,
				'record' : file[username]['record']
			}
		elif recvData['type'] == "requestRank":
			rank = []
			for i in file:
				for j in range(len(rank)+1):
					if j == len(rank) or rank[j]['bestScore'] < file[i]['bestScore']:
						rank.insert(j, {'username' : i,
										'bestScore' : file[i]['bestScore']})
						break
				if len(rank) > 20:
					rank.pop()
			sendData = {
				'type' : "rank",
				'rank' : rank
			}

		else:
			sendData = {
				'type' : "Unknown message"
			}
		file.close()
	except:
		sendData = {
			'type': "error",
			'content': "Server file I/O error",
		}
	#print "debug: send", sendData
	return sendData


def washData(data):
	newData = {}
	for key in data:
		if type(data[key]) == types.UnicodeType:
			newData[key.encode("ascii")] = data[key].encode("ascii")
		else:
			newData[key.encode("ascii")] =data[key]
	return newData

if __name__ == "__main__":
	print os.path.isfile(r"user/tmp")