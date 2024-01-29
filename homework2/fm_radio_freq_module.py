# this module will be imported in the into your flowgraph

def set_center_frequency(arg):

	if 88e6 <= arg <= 92.9e6:
		return 90.5e6
		
	elif 93e6 <= arg <= 97.9e6:
		return 95.5e6
		
	elif 98e6 <= arg <= 103e6:
		return 100.5e6
		
	elif 103e6 <= arg <= 108e6:
		return 105.5e6
		
