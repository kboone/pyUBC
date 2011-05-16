import functools


"""
Utility file with random fun stuff
"""


class cached(object):
	"""Decorator that caches a function's return value each time it is called. If called later with
	the same arguments, the cached value is returned, and not re-evaluated.
	
	Adapted from "memoized" at http://wiki.python.org/moin/PythonDecoratorLibrary
	"""
	def __init__(self, func):
		self.func = func
		self.__doc__ = func.__doc__
		self.cache = {}
	
	def __call__(self, *args, **kwargs):
		try:
			if kwargs["skipCache"] == True:
				return self.func(*args)
		except KeyError:
			pass
			
			
		try:
			return self.cache[args]
		except KeyError:
			value = self.func(*args)
			self.cache[args] = value
			return value
		except TypeError:
			# uncachable -- for instance, passing a list as an argument.
			# Better to not cache than to blow up entirely.
			return self.func(*args)
	
	def __repr__(self):
		"""Return the function's docstring."""
		return self.func.__doc__
		
	def __get__(self, obj, objtype):
		"""Support instance methods."""
		return functools.partial(self.__call__, obj)

