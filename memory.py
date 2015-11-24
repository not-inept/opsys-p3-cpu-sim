import re

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
	def allocate(self, process, size):
		start = self.alloc_start
		if self.type == "nf":	# handle next fit
			rep = self.representation()			
			i = self.alloc_start
			found = -1
			while (i+size < self.size and found == -1):
				if rep[i:i+size] == "."*size:
					found=i
				i += 1
			i = 0
			while (i+size < self.alloc_start and found == -1):
				if rep[i:i+size] == "."*size:
					found=i
				i += 1		
			if found == -1:
				return False
			start = found
			self.alloc_start = start+size
		elif self.type == "bf": # handle best fit
			m = self.representation()
			found = False
			for i in range(size, m.count(".")+1):
				rg = "^[.]{"+str(i)+"}$|[A-Z][.]{"+str(i)+"}[A-Z]|^[.]{"+str(i)+"}[A-Z]|[A-Z][.]{"+str(i)+"}$"
				place = re.search(rg, m)
				#Wohoo we have a match! :D
				if (place):
					found = True
					start = place.start()
					break
			if (not found):
				return False
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

	def defragment(self):
		units_moved = 0
		current_unit = 0
		for p in self.partitions:
			if p.start_unit != current_unit:
				p.start_unit = current_unit
				current_unit = current_unit+p.start_unit
				units_moved += p.size
		time_elapsed = units_moved*self.t_memmove
		return time_elapsed, units_moved # return time elapsed

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
		if len("".join(representation)) < self.size:
			representation.append("."*(self.size-len("".join(representation))))
		return "".join(representation)

	def __str__(self):
		# output memory visualization
		rep = self.representation() # get string of memory
		out_rep = []
		for i in range(len(rep)/self.split):
			out_rep.append(rep[i*self.split:(i+1)*self.split]) # split into nice looking chunks
		if self.size % self.split != 0:
			out_rep.append(rep[(i+1)*self.split:]) #ensure even printing
		return "="*self.split + "\n" + "\n".join(out_rep) + "\n" + "="*self.split

	def __init__(self, type="ff", size=256, t_memmove=10, split=32):
		# the type of allocation ("ff", "nf", "bf")
		self.type = type
		# the number of memory units
		self.size = size
		# size of split for output, default 32
		self.split = split
		# mem_move time
		self.t_memmove = t_memmove
		# as per instructions, a list containing process identifier, 
		# starting unit, and size of allocation
		self.partitions = []
		# where the next allocation should begin
		self.alloc_start = 0
		# will return true / false for fail / success
		self.partitions = []
		self.t_memmove = t_memmove

if __name__ == "__main__":
	# # first fit tests
	# print("Testing first fit:\n")
	# test_mem = Memory("ff")
	# test_mem.allocate("A", 22)
	# test_mem.allocate("B", 15)
	# test_mem.allocate("C", 15)
	# print test_mem
	# test_mem.deallocate("B")
	# test_mem.allocate("D", 15)
	# print test_mem

	# print("\nTesting next fit:\n")
	# 	test_mem2 = Memory("nf", 32)
 	# 	print test_mem2.alloc_start

	# test_mem2.allocate("A", 22)
	# print test_mem2.alloc_start

	# print test_mem2.allocate("B", 2)
	# print test_mem2.allocate("C", 15)
	# print test_mem2.alloc_start
	# print test_mem2
	# print test_mem2.allocate("D", 15)
	# test_mem2.deallocate("A")
	# print test_mem2.alloc_start
	# test_mem2.allocate("E", 2)
	# print test_mem2.alloc_start
	# print test_mem2

	# test defrag, following example 3
	print("\nDefragmentation test:\n")
	test_def = Memory("ff")
	# allocate nodes
	test_def.allocate("H", 16)
	test_def.allocate("X", 14)
	test_def.allocate("J", 59)
	test_def.allocate("Y", 2)
	test_def.allocate("K", 35)
	test_def.allocate("L", 24)
	test_def.allocate("N", 8)
	test_def.allocate("Z", 2)
	test_def.allocate("M", 17)
	test_def.allocate("W", 20)
	test_def.allocate("S", 24)
	# remove dummy nodes
	test_def.deallocate("W")
	test_def.deallocate("X")
	test_def.deallocate("Y")
	test_def.deallocate("Z")
	# defragulate
	print("starting defrag\n")
	print(test_def)
	time_elapsed, units_moved = test_def.defragment()
	print "defrag done, time elapsed: ", time_elapsed, " and units moved: ", units_moved
	print(test_def)