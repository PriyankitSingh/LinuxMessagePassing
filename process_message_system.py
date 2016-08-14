import os
import sys
import pickle

class MessageProc:
	filename = None

	"""
	Creates a pipe names pipe(pid) and sets filename field
	"""
	def main(self):
		print('main' + str(os.getpid()))
		self.pid = os.getpid()
		try:
			os.mkfifo('/tmp/pipe'+ str(self.pid))
		except OSError:
			print ('Could not create pipe')
			pass
		self.filename = '/tmp/pipe'+ str(self.pid)
		print('created pipe ' + self.filename)
		try:
			pipe = open(self.filename, 'r')
			pipe.close()
		except:
			print ('could not open file')		
	
	"""
	Getter for filename
	"""
	def getfilename(self):
		return self.filename

	"""
	Sends message to the pipe. Opens the pipe and writes message to it
	might need to pickle the data before adding it to file.
	"""
	def give(self, pid, label, *values): #sends message to given process
		print('give for '+ str(pid))
		filename = self.getfilename()
		# write to file
		print ('Opening file ' + filename)
		pipe = open(filename, 'w')
		pipe.write(str(label))
		pipe.close()
		print ('Successfully opened file ', filename)

	"""
	Starts a new copy of current process and returns its pid.	
	"""
	def start(self, *values): 
		print('starting new child process')
		newpid = os.fork()
		if(newpid == 0):
			self.main()
			print ('printed from child')
			return newpid
		else :
			print('printed from parent')
		
	"""
	Recieves message from a given process. Reads the from pipe names pipe(pid)
	"""	
	def receive(self, *messages): # read from file
		# open pipe
		print ('recieve')
		with open(self.filename) as fifo:
			while True:
				line = fifo.read()
				print (line)
		pid = self.pid
		print(str(pid))
		#for message in messages:
			# process messages here
			#print(message)


	def closePipe(self, pid):
		
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
	print('parent pid: ' + str(os.getpid()))
	pid = os.getpid()
	msg = MessageProc()
	msg.main()
	msg.give(pid, 'sup')
	newpid = msg.start()
	pid2 = os.getpid()
	msg.closePipe(newpid)


