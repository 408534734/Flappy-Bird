import network
import game_controller
import shelve
import types
import time

def userSignup(username, password):
	if len(username) == 0:
		game_controller.signUpResult("Username is empty!")
		return
	if len(password) == 0:
		game_controller.signUpResult("Password is empty!")
		return
	sendData = {
		'sid' : network.serialID,
		'type' : "signUp",
		'username' : username,
		'password' : password
	}
	network.clientSend(sendData)

def userLogin(username, password):
	if len(username) == 0:
		game_controller.signUpResult("Username is empty!")
		return
	if len(password) == 0:
		game_controller.signUpResult("Password is empty!")
		return
	sendData = {
		'sid' : network.serialID,
		'type' : "login",
		'username' : username,
		'password' : password
	}
	network.clientSend(sendData)

def requestRank():
	sendData = {
		'sid' : network.serialID,
		'type' : "requestRank"
	}
	network.clientSend(sendData)


user = None
def userDataProcess(data):
	global user
	data = washData(data)
	if data['type'] == "notice":
		game_controller.showContent(data['content'])
	elif data['type'] == "signUpResult":
		if data['result'] == "success":
			user = User(data['username'], 0, data['rank'],[])
		game_controller.signUpResult(data['result'])
	elif data['type'] == "loginResult":
		if data['result'] == "success":
			user = User(data['username'], data['bestScore'], data['rank'], data['record'])
		game_controller.signUpResult(data['result'])
	elif data['type'] == "Update user info":
		userData = user.file[user.username]
		userData['bestScore'] = data['bestScore']
		userData['rank'] = data['rank']
		userData['record'] = data['record']
		user.file[user.username] = userData
		game_controller.showContent("Upload record success!")
	elif data['type'] == "Nothing":
		#print "Server has received data from", data['source']
		pass
	elif data['type'] == "Unknown message":
		game_controller.showContent("Server receive unknown message")
	elif data['type'] == "rank":
		game_controller.showRank(data['rank'])
	elif data['type'] == "error":
		game_controller.showContent(data['content'])
	else:
		game_controller.showContent("Client receive unknown message")


class User:
	def __init__(self, username, bestScore, rank, record):
		self.username = username
		self.sid = network.serialID
		try:
			self.file = shelve.open("user.dat")
			userData = {
				'bestScore' : bestScore,
				'rank' : rank,
				'record' : record
			}
			self.file[username] = userData
		except Exception:
			game_controller.showContent("No privilege to read or write data! :(")
			print(Exception)

	def recordRecentData(self, recentScore):
		try:
			userData = self.file[self.username]
			userData['recentScore'] = recentScore
			self.file[self.username] = userData
			sendData = {
				'sid' : self.sid,
				'type' : "recentScore",
				'username' : self.username,
				'score' : recentScore
				#'time' : int(time.time()-game_controller.startTime)
			}
			network.clientSend(sendData)
		except:
			game_controller.showContent("Record recent data Error! :(")

	def recordFinalData(self):
		try:
			sendData = {
				'sid' : self.sid,
				'type' : "finalScore",
				'username' : self.username,
				'score' : self.file[self.username]['recentScore'],
				'time' : int(time.time()-game_controller.startTime),
				'date' : time.strftime('%Y-%m-%d',time.localtime(time.time()))
			}
			network.clientSend(sendData)
			return max(self.file[self.username]['bestScore'], self.file[self.username]['recentScore'])
		except:
			game_controller.showContent("Record final data Error! :(")

	def __del__(self):
		try:
			self.file.close()
			del self.file
		except:
			pass

	def logout(self):
		try:
			self.file.close()
			del self.file
		except:
			pass

def washData(data):
	newData = {}
	for key in data:
		if type(data[key]) == types.UnicodeType:
			newData[key.encode("ascii")] = data[key].encode("ascii")
		else:
			newData[key.encode("ascii")] =data[key]
	return newData