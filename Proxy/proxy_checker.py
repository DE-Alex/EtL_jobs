#!/usr/bin/env python
import Queue
import threading
import urllib2
import time
import os
import Proxy_DB_MGR

#TEST HTTP PROXY ONLY????  line 34!!!
#TODO read about HTTPS and SOCKS proxy


def main(path_to_proxy_DB, path_to_new_proxy):

	queue = Queue.Queue()
	output = []
	#===================================================
	class ThreadUrl(threading.Thread):
		"""Threaded Url Grab"""
		def __init__(self, queue):
			threading.Thread.__init__(self)
			self.queue = queue

		def run(self):
			while True:
				#grabs host from queue
				proxy_info = self.queue.get()
				N_rating = proxy_info[0] #N_rating = N_alive/N_total
				ip_port = proxy_info[1] #ip:port
				N_alive = proxy_info[2] #proxy alive N times
				N_total = proxy_info[3] #total requests to proxy
				
				try:
					N_total = N_total + 1
					proxy_handler = urllib2.ProxyHandler({'http':ip_port}) #!!!!! HTTP proxy only?
					opener = urllib2.build_opener(proxy_handler)
					opener.addheaders = [('User-agent','Mozilla/5.0')]
					urllib2.install_opener(opener)
					req = urllib2.Request("http://www.google.com")
					sock=urllib2.urlopen(req, timeout= 7)
					rs = sock.read(1000)
					if '<title>Google</title>' in rs:
					#if True: #uncomment to test in local mode
						N_alive = N_alive + 1
						N_rating  = N_alive*100/N_total
						output.append([N_rating, ip_port, N_alive, N_total])
						print '+',ip_port
					else:
						raise "Not Google"
				except:
					N_rating  = N_alive*100/N_total
					#check if proxy is older 100 and alive less than 10% - delete from DB
					if N_total >= 100 and N_rating <= 10: pass
					else: output.append([N_rating, ip_port, N_alive, N_total])
				#signals to queue job is done
				self.queue.task_done()
	#========================================================================		
			
			
	#spawn a pool of threads, and pass them queue instance 
	for i in range(50): #Number of threads!!
		t = ThreadUrl(queue)
		t.setDaemon(True)
		t.start()
	
	#Load Proxy_DB
	#import Proxy_DB_MGR
	Proxy_DB = Proxy_DB_MGR.Load_DB(path_to_proxy_DB, path_to_new_proxy)
	print '%d proxy to check:' %(len(Proxy_DB))
	
	#populate queue with data   
	for proxy_info in Proxy_DB:
		queue.put(proxy_info)

	queue.join() #wait on the queue until everything has been processed   

	output.sort(reverse = True)
	
	Proxy_DB_MGR.Write(output, path_to_proxy_DB)
	

if __name__ == '__main__':
	
	
	path_to_proxy_DB = os.path.dirname(__file__) + '\DB_proxy.txt'
	path_to_new_proxy = os.path.dirname(__file__) + '\proxy.txt'
	print path_to_proxy_DB
	print path_to_new_proxy
	
	for i in range (100): #times to check proxy
		start = time.time()
		print '== Check %d ==' %(i)
		main(path_to_proxy_DB, path_to_new_proxy)
		print "Elapsed Time: %s" % (time.time() - start)
		Sleep = 0 ##delay between check, minutes
		print 'Sleeping %d min' %(Sleep)
		time.sleep(Sleep*60) 