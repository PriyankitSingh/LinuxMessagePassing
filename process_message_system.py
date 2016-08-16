import os
import sys
import pickle
import time
import threading

"""
Class for processing messaging between processes using named pipes.
"""
class MessageProc:
	filename = '/tmp/pipe'
	"""
	Creates a pipe names pipe(pid) and sets filename field
	"""
	def main(self):
		self.pid = os.getpid()
		self.filename = '/tmp/pipe'
		try:
			if not (os.path.exists('/tmp/pipe')):
				os.mkfifo('/tmp/pipe')
		except OSError:
			print ('Could not create pipe')
			pass		
	
	"""
	Getter for filename
	"""
	def getfilename(self):
		return self.filename

	"""
	Sends message to the pipe. Opens the pipe and writes message to it
	might need to pickle the data before adding it to file.
	"""
	def give(self, pid, label, *values):
		filename = self.getfilename()
		if(os.path.isfile(filename)): # Make new pipe if pipe doesn't exist
			os.mkfifo(filename)
		# write to file
		pipe = open(filename, 'wb')
		if(len(values) != 0):
			tup = (label, values);
			pickle.dump(tup,pipe)
			# pipe.write(str(values[0]))  #pickle here
		else:
			tup = (label,);
			pickle.dump(tup, pipe)
		pipe.close()
		time.sleep(0.005)

	"""
	Starts a new copy of current process and returns its pid.	
	"""
	def start(self, *values): 
		newpid = os.fork()
		if(newpid == 0):
			self.main()
		else :
			return os.getpid()
		
	"""
	Recieves message from a given process. Reads the from pipe names pipe(pid)
	"""	
	def receive(self, *messages): # read from file
		# Set up messages
		messageList = []
		for msg in messages:
			messageList.append(msg)
		fifo = open(self.filename, 'rb')
				
		while 1: # Reads pickle file until the EOF 
			try:
				input = pickle.load(fifo)
				for msg in messageList:
					if(input[0] == msg.getLabel()):
						# do action for the msg here
						# print('doing action ' + str(msg.getAction()))
						msg.doAction(*input[1])
						break
			except:
				break
		

	def closePipe(self):
		filename = self.filename
		try:
			os.remove(filename)			
		except FileNotFoundError:
			print('pipe not found')
		else:
			print ('closed pipe')


class Message:
	def __init__(self, message, action=None):
		self.message = message
		self.action = action
		self.argcount = action.__code__.co_argcount
		#action() # assuming no parameters for now, have to check for that later

	def getAction(self):
		return self.action
	
	def doAction(self, *args):
		self.action(*args)

	def getLabel(self):
		return self.message

class Timeout:
	def __init__(self, time, action=None):
		self.time = time
		self.action = action

	def main(self, main_proc):
		print('in timeout')

	
if __name__=='__main__':
	pid = os.getpid()
	msg = MessageProc()
	msg.main()	
	newpid = msg.start()
	msg.give(pid, 'sup')
	pid2 = os.getpid()