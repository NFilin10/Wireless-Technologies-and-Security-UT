# this module will be imported in the into your flowgraph
def generate_bits():
	current = [0,0,0,0,1,1,0,0,1,1,0,1,0,1,0,1,1,1,1,1,1,1,0,0,0]
	new_bits = []
	for bit in current:
		if bit == 1:
			new_bits += [1,1,1,0]
		else:
			new_bits += [1,0,0,0]
			
	new_bits += [0, 0, 0, 0] * 7
	
	return new_bits
