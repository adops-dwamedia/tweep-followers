import time

def pause_wrapper(x,n):
	def decorator(f):
		config = [x,time.time() + n + 3]
		def inner(*args,**kwargs):
			config[0] = config [0]-1
			if config[0] == 0:
				print "limit reached for %s, waiting %s seconds."%(f.__name__, round(config[1]-time.time()))
				time.sleep(config[1] - time.time())
				config[0] = x
				config[1] = time.time() + n + 3
			return f(*args,**kwargs)
		return inner
	return decorator
			
			
	




def decorator(f):
	calls_left = 2
	def inner(*args,**kwargs):
		if calls_left == 0:
			print "limit reached, reseting"
		calls_left -= 1
		return f(*args,**kwargs)
	return inner
		
		


@pause_wrapper(2,1)
def foo():
	print "Function called"


	
foo()
foo()
foo()
foo()
foo()
foo()


