# Memory Module
class Partition:
	process = "A"
	start_unit = 0
	size = 2
	def __init__(self, process, start, size):
		self.process = process
		self.start_unit = start
		self.size = size

class Memory:
	# the number of memory units
	size = 256
	# as per instructions, a list containing process identifier, 
	# starting unit, and size of allocation
	partitions = []	
	def __str__(self):

		return "="*32 + "\n" + representation + "="*32 + "\n"

	def __init__(self):
		p = Partition("A", 3, 2)
		done = False

if __name__ == "__main__":
	test_mem = Memory()
	print test_mem