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
	
	# will return true / false for fail / success
	def add_process(self, process, size):
		# 
		start = 0
		self.partitions.append(Partition(process, start, size))
		self.partitions.sort(key=lambda p: p.start_unit)

	def defragment(self, time):
		time_elapsed = 0
		return time_elapsed

	# assumes partitions is sorted by start_unit, and start_unit is unique
	def representation(self):
		representation = []
		current_unit = 0
		for p in self.partitions:
			if p.start_unit > current_unit:
				representation.append("."*(p.start_unit-curent_unit))
				representation.append(p.process*p.size)
			else:
				representation.append(p.process*p.size)
			current_unit = p.start_unit+p.size+1
		if current_unit < self.size:
			representation.append("."*(self.size-current_unit))
		return "".join(representation)

	def __str__(self):
		rep = self.representation()
		out_rep = []
		for i in range(len(rep)/self.split):
			out_rep.append(rep[i*self.split:(i+1)*self.split])
		if self.size % 32 != 0:
			out_rep.append(rep[(i+1)*self.split:])
		return "="*self.split + "\n" + "\n".join(out_rep) + "\n" + "="*self.split + "\n"

	def __init__(self, type="ff", size=256, t_memmove=10):
		types = ["ff", "nf", "bf"]
		self.type = type
		self.size = size
		self.t_memmove = t_memmove

if __name__ == "__main__":
	test_mem = Memory()
	print test_mem