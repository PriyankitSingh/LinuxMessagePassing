import os
import sys
import pickle
import time

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
		pipe = open(filename, 'w')
		if(len(values) != 0):
			#pickle.dump(label,pipe)
			pipe.write(str(values[0]))  #pickle here
		# else:
		# 	if(label == 'stop'):
		# 		pipe.write('stop')
		pipe.close()
		time.sleep(0.01)

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
		# for msg in messages:
		# 	print(msg.getMessage())
		fifo = open(self.filename, 'r')
		for line in fifo:
			if(line == 'stop'): # Change this, not going in here
				print('stop message')
				fifo.close()
				return
			else:
				print(line) # unpickle here
				
		# while 1: # Reads pickle file until the EOF 
		# 	try:
		# 		lists.append(pickle.load(fifo))
		# 	except (EOFError, UnpicklingError):
		# 		break
		


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
		#action() # assuming no parameters for now, have to check for that later

	def getAction(self):
		return self.action

	def getMessage(self):
		return self.message

class Timeout:
	def main(self, main_proc):
		print('in timeout')

	
if __name__=='__main__':
	pid = os.getpid()
	msg = MessageProc()
	msg.main()	
	newpid = msg.start()
	msg.give(pid, 'sup')
	pid2 = os.getpid()