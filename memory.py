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
	# size of split for output, default 32
	split = 32
	# mem_move time
	t_memmove = 10
	# as per instructions, a list containing process identifier, 
	# starting unit, and size of allocation
	partitions = []
	alloc_start = 0
	# will return true / false for fail / success
	def allocate(self, process, size):
		start = 0
		if self.type == "nf":	# handle next fit
			print "not implemented"
		elif self.type == "bf": # handle best fit
			print "not implemented"
		else: # handle first fit/default
			for i in range(len(self.partitions)):
				p = self.partitions[i]
				# handle if on first partition
				if p == self.partitions[0]: # compare remaining space
					if p.start_unit >= size:
						start = 0
						break
				# handle case if on last partition
				if p == self.partitions[-1]: # compare remaining space
					if self.size-(p.start_unit + p.size) >= size:
						start = p.start_unit+p.size
						break
					else:
						return False
				else: 
					p_next = self.partitions[i+1]
					# handle all other case where there are two partitions
					if p_next.start_unit - (p.start_unit + p.size) >= size:
						start = p.start_unit + p.size
						break
		self.partitions.append(Partition(process, start, size))
		self.partitions.sort(key=lambda p: p.start_unit)
		return True

	# assumes process has one associated memory block
	def deallocate(self, process):
		for p in self.partitions:
			if p.process == process:
				self.partitions.remove(p)
				return True
		return False

	def defragment(self, time):
		time_elapsed = 0
		return time_elapsed

	# assumes partitions is sorted by start_unit, and start_unit is unique
	def representation(self):
		representation = []
		current_unit = 0
		for p in self.partitions:
			if p.start_unit > current_unit:
				representation.append("."*(p.start_unit-current_unit))
				representation.append(p.process*p.size)
			else:
				representation.append(p.process*p.size)
			current_unit = p.start_unit+p.size
		if current_unit < self.size:
			representation.append("."*(self.size-current_unit))
		return "".join(representation)

	def __str__(self):
		# output memory visualization
		rep = self.representation() # get string of memory
		out_rep = []
		for i in range(len(rep)/self.split):
			out_rep.append(rep[i*self.split:(i+1)*self.split]) # split into nice looking chunks
		if self.size % 32 != 0:
			out_rep.append(rep[(i+1)*self.split:]) #ensure even printing
		return "="*self.split + "\n" + "\n".join(out_rep) + "\n" + "="*self.split + "\n"

	def __init__(self, type="ff", size=256, t_memmove=10):
		types = ["ff", "nf", "bf"]
		self.type = type
		self.size = size
		self.t_memmove = t_memmove

if __name__ == "__main__":
	test_mem = Memory()
	test_mem.allocate("A", 22)
	test_mem.allocate("B", 15)
	test_mem.allocate("C", 15)
	print test_mem