import os
import sys
import pickle
import time
import threading
import itertools
from queue import Queue
import atexit

class ServiceMatcher:

	arrived_condition = threading.Condition()
	communication_queue = Queue()
	'''

	'''
	def main(self):
		self.listOfProcesses = []
		self.filename = '/tmp/ServicePipe'
		try:
			if not (os.path.exists(self.filename)):
				os.mkfifo(self.filename)
		except OSError:
			print('Could not create pipe')

		transfer_thread = threading.Thread(target=self.extract_from_pipe, daemon=True) #could set it to daemon
		transfer_thread.start()	
		self.receive()	

		return


	'''
	Getter method for getting the filename of Servicematcher
	'''
	def getFilename(self):
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

	"""
	def start(self):
		self.main()

	"""
	Sends the pid of service to the consumer
	"""
	def give(self, consumerpid, servicepid, *values):
		filename = '/tmp/pipe' + str(consumerpid)
		if not (os.path.isfile(filename)): # Make new pipe if pipe doesn't exist
			try:
				os.mkfifo(filename)
			except:
				pass
	
		# write to file
		pipe = open(filename, 'wb')
		pickle.dump(servicepid, pipe)
		pipe.close()

	"""
	Recieves message from a given process. Reads the from pipe names pipe(pid)
	"""	
	def receive(self): # read from file
		# Check if message from consumer of service	
		print('in recieve')
		while True:
			if not (self.communication_queue.qsize() == 0):
				input = self.communication_queue.get()
				if(input[0] == 'join'):
					tup = (input[1], input[2]); # order = name, pid
					self.listOfProcesses.append(tup)
					print(str(input[1]) + ' joined the service')
				if(input[0] == 'request'):
					for proc in self.listOfProcesses:
						name = proc[0]
						if(name == input[1]):
							self.give(input[2], proc[1])
				self.communication_queue.task_done()
			else:
				with self.arrived_condition:
					self.arrived_condition.wait(6) # wait until a new message
					if(self.communication_queue.qsize() == 0):
						print('server timed out')
						self.closePipe()
						return

	def closePipe(self):
		filename = self.filename
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

if __name__=='__main__':
	matcher = ServiceMatcher()
	matcher.start()