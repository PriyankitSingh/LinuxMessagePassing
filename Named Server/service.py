from service_matcher import *
import os
import sys
import pickle
import time
import threading
import itertools
from queue import Queue
import atexit

class Service:
	name = None
	def main(self, name):
		self.name = name
		print('service main')
		self.pid = os.getpid()

	def start(self):
		print('service start')
		self.main()

	def sendJoinRequest(self):
		filename = '/tmp/ServicePipe'
		pid = os.getpid()
		if not (os.path.isfile(filename)):
			try:
				os.mkfifo(filename)
			except:
				pass

		# write to file
		pipe = open(filename, 'wb')
		tup = ('join', self.name, pid);
		pickle.dump(tup,pipe)
		pipe.close()
		print('request sent')


if __name__=='__main__':
	service = Service()
	service.main('SomeProcess')
	service.sendJoinRequest()