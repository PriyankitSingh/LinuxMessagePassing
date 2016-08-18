from service_matcher import *
import os
import sys
import pickle
import time
import threading
import itertools
from queue import Queue
import atexit

class Consumer:

	arrived_condition = threading.Condition()
	communication_queue = Queue()

	def main(self):
		print('service main')
		self.filename = '/tmp/pipe' + str(os.getpid())
		self.pid = os.getpid()
		try:
			if not (os.path.exists(self.filename)):
				os.mkfifo(self.filename)
		except OSError:
			print ('Could not create pipe')
			pass
		transfer_thread = threading.Thread(target=self.extract_from_pipe, daemon=True) #could set it to daemon
		transfer_thread.start()	

	def start(self):
		print('service start')
		self.main()

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

	def sendServiceRequest(self, name):
		filename = '/tmp/ServicePipe'
		pid = os.getpid()
		if not (os.path.isfile(filename)):
			try:
				os.mkfifo(filename)
			except:
				pass

		# write to file
		pipe = open(filename, 'wb')
		tup = ('request', name, pid);
		pickle.dump(tup,pipe)
		pipe.close()
		print('request sent')

	"""
	Recieves message from a given process. Reads the from pipe names pipe(pid)
	"""	
	def receive(self): # read from file
		# Check if message from consumer of service	
		print('in recieve')
		while True:
			if not (self.communication_queue.qsize() == 0):
				input = self.communication_queue.get()
				print('joined process ' + str(input))
				self.communication_queue.task_done()
			else:
				with self.arrived_condition:
					self.arrived_condition.wait(10) # wait until a new message
					if(self.communication_queue.qsize() == 0):
						print('consumer logged out')
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
	consumer = Consumer()
	consumer.start()
	consumer.sendServiceRequest('SomeProcess')
	consumer.receive()
	consumer.closePipe()