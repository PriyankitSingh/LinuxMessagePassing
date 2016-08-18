import os
import sys
import pickle
import time
import threading
import itertools
from queue import Queue
import atexit


ANY = 'any'
"""
Class for processing messaging between processes using named pipes.
"""
class MessageProc:
	filename = '/tmp/pipe'
	arrived_condition = threading.Condition()
	communication_queue = Queue()
	timeout = None
	anyFlag = False
	anyMessage = None
	childPid = None
	timeoutflag = False
	"""
	Creates a pipe names pipe(pid) and sets filename field
	"""
	def main(self):
		self.filename = '/tmp/pipe' + str(os.getpid())
		try:
			if not (os.path.exists(self.filename)):
				os.mkfifo(self.filename)
		except OSError:
			print ('Could not create pipe')
			pass
		transfer_thread = threading.Thread(target=self.extract_from_pipe, daemon=True) #could set it to daemon
		transfer_thread.start()		
		return
	
	"""
	Getter for filename
	"""
	def getfilename(self):
		return self.filename

	"""
	Code from Robert's lecture.
	"""
	def extract_from_pipe(self): # Gets messages and puts them in a queue
		''' '''
		with open(self.filename, 'rb') as pipe:
			while True:
				try:
					message = pickle.load(pipe)
					with self.arrived_condition:
						self.communication_queue.put(message)
						self.arrived_condition.notify() # notify anything waiting
				except EOFError:
					time.sleep(0.01)

	"""
	Sends message to the pipe. Opens the pipe and writes message to it
	"""
	def give(self, pid, label, *values):
		filename = '/tmp/pipe' + str(pid)
		if not (os.path.isfile(filename)): # Make new pipe if pipe doesn't exist
			try:
				os.mkfifo(filename)
			except:
				pass
	
		# write to file
		pipe = open(filename, 'wb')
		if(len(values) != 0):
			tup = (label, values);
			pickle.dump(tup,pipe)
		else:
			tup = (label,);
			pickle.dump(tup, pipe)
		pipe.close()
		

	"""
	Starts a new copy of current process and returns its pid.	
	"""
	def start(self, *values): 
		newpid = os.fork()
		if(newpid == 0):
			self.main()
			sys.exit()
			time.sleep(1)
			# return
		else :
			# return os.getpid()
			return newpid
	"""
	Recieves message from a given process. Reads the from pipe names pipe(pid)
	"""	
	def receive(self, *messages): # read from file
		# Set up messages
		messageList = []
		for msg in messages: # check if its a timeout of message
			if(type(msg).__name__ == 'Message'):
				messageList.append(msg)
				if(msg.getLabel() == 'any'):
					self.anyFlag = True
					self.anyMessage = msg
			if(type(msg).__name__ == 'Timeout') and not (self.timeout == None):
				self.timeout = msg
				self.timeoutflag = True

		if(self.timeout == None):
			self.timeout = TimeOut(100000, action=lambda: None)
			
		while True:
			if not (self.communication_queue.qsize() == 0):
				input = self.communication_queue.get()
				i = 1
				for msg in messageList:
					if(input[0] == msg.getLabel()):
						# do action for the msg if label matches input
						if(msg.getLabel() == 'stop'):
							# self.closePipe()
							return msg.doAction()
							break
						if(len(input) == 1):
							return msg.doAction()
							break
						else:
							return msg.doAction(*input[1])
							break

					if(len(messageList) <= i) and (self.anyFlag):
						self.anyMessage.doAction()
					i=i+1
				self.communication_queue.task_done()	
			else:
				with self.arrived_condition:
					self.arrived_condition.wait(self.timeout.getTime()) # wait until a new message
					if(self.communication_queue.qsize() == 0) and (timeoutflag) : # if queue is empty do timeout action
						self.timeout.doAction() # add args

		closePipe()

	def closePipe():
		filename = '/tmp/pipe'+str(os.getpid())
		try:
			os.remove(filename)			
		except FileNotFoundError:
			print('pipe not found in ' + str(os.getpid()))
		else:
			print ('closed pipe for ' + str(os.getpid()))
		try:
			os.remove('/tmp/pipeNone')
		except FileNotFoundError:
			pass
	
	atexit.register(closePipe)



class Message:
	def __init__(self, message, action=None, guard=None):
		self.message = message
		self.action = action
		self.argcount = action.__code__.co_argcount
		if(message == ANY):
			self.message = 'any'
		
		#action() # assuming no parameters for now, have to check for that later

	def getAction(self):
		return self.action
	
	def doAction(self, *args):
		return self.action(*args)

	def getLabel(self):
		return self.message

class TimeOut:
	def __init__(self, time, action=None):
		self.time = time
		self.action = action

	def getTime(self):
		return self.time

	def doAction(self, *args):
		self.action(*args)

	def main(self, main_proc):
		print('in timeout')

	
if __name__=='__main__':
	pid = os.getpid()
	msg = MessageProc()
	msg.main()	
	newpid = msg.start()
	msg.give(pid, 'sup')
	pid2 = os.getpid()