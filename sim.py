#!/usr/bin/python2
# by Mason Cooper (coopem4)

from sys import argv

class Process:
  def __init__(self, num, cpu, bursts, io, priority):
    self.num = int(num)
    self.cpu = int(cpu)
    self.bursts = int(bursts)
    self.io = int(io) 
    self.duration = int(cpu)
    self.queue = "NONE"
    self.priority = int(priority)
    self.entered_at = -1
    self.is_preempting = False
    self.acted = False
    self.been_waiting = 0
    self.bumped = False
    self.turnaround_ticker = 0
    self.secondary_wait_time = 0

class Stats:
  def __init__(self, method):
    self.method = method
    self.bursts = []
    self.avg_burst = -1
    self.wait_times = []
    self.avg_wait_time = -1
    self.avg_turnaround_time = -1
    self.context_switches = 0
    self.turnarounds = []
    self.secondary_wait_times = []
  def output(self):
    self.avg_burst = sum(self.bursts)/(len(self.bursts)*1.0)
    actual_wait_times = []
    for i in self.wait_times:
      if i[0] >= 12:
        actual_wait_times.append(i[0]-12)
    self.avg_wait_time = (sum(self.secondary_wait_times)+3)/(len(self.secondary_wait_times)*1.0)
    self.avg_turnaround_time = (sum(self.turnarounds))/(len(self.turnarounds)*1.0)
    fout = open('simout.txt','a')
    lines = []
    lines.append("Algorithm %s\n" % self.method)
    lines.append("-- average CPU burst time: %.2f ms\n" % self.avg_burst)
    lines.append("-- average wait time: %.2f ms\n" % self.avg_wait_time)
    lines.append("-- average turnaround time: %.2f\n" % self.avg_turnaround_time)
    lines.append("-- total number of context switches: %d\n" % self.context_switches)
    fout.writelines(lines)

def event(title, cpu_queue, time_elapsed):
  p_string = ""
  # if not title == "Simulator ended":
  p_string = " [Q"
  for process in cpu_queue:
    p_string += " %d" % process
  p_string += "]"
  title = title+p_string
  print "time %dms:" % time_elapsed, title

def parse_input(file_name):
  f = open(file_name, "r")
  processes = []
  for line in f:
    line = line.strip()
    if line and not line[0] == "#":
      line = line.split('|')
      if len(line) == 5:
        processes.append(Process(*line))
  return processes

def find_active(processes): 
  for process in processes:
    if process.queue == "ACTIVE":
      return process
  return None 
  # find active

def add_process(cpu_queue, processes, process, method, active, time_elapsed, waited, preempt, acted, stats):
  if method == "FCFS":
    process.been_waiting = 0
    cpu_queue.append(process.num) # add the process to the cpu queue
  elif method == "SRT":
    temp_processes = processes[:]
    temp_processes.sort(key=lambda x: x.duration)
    cpu_queue = []
    first = None
    for temp_process in temp_processes:
      if temp_process.is_preempting:
        waited -= t_cs
      temp_process.is_preempting = False
      if temp_process.queue == "CPU":
        cpu_queue.append(temp_process.num)
        if not first:
          first = temp_process
    cpu_active = find_active(processes)
    if cpu_active and first and cpu_active.duration > first.duration:
      first.queue = "CPU"
      cpu_queue[0] = cpu_active.num
      cpu_queue = [first.num] + cpu_queue
      active = -1
      if not acted: # no idea why this is useful, but it is!
        cpu_active.duration -= 1
      waited = 0
      cpu_active.been_waiting = 0
      process.been_waiting = 0
      cpu_active.queue = "CPU" # change project state
      preempt = cpu_queue[0]
      process.is_preempting = True
      process.secondary_wait_time = 0
      event("P%d" % process.num + " completed I/O", cpu_queue[2:], time_elapsed)
      event("P%d preempted by P%d" % (cpu_active.num, first.num), cpu_queue[1:], time_elapsed)
      acted = True
  elif method == "PWA":
    if not process.bumped:
      process.entered_at = time_elapsed
    temp_processes = processes[:]
    temp_processes.sort(key=lambda x: (x.priority, x.entered_at))
    cpu_queue = []
    first = None
    for temp_process in temp_processes:
      if temp_process.is_preempting:
        waited -= t_cs
      temp_process.is_preempting = False
      if temp_process.queue == "CPU":
        cpu_queue.append(temp_process.num)
        if not first:
          first = temp_process
    cpu_active = find_active(processes)
    if cpu_active and first and cpu_active.priority > first.priority:
      cpu_queue[0] = cpu_active.num
      cpu_queue = [first.num] + cpu_queue
      active = -1
      if not acted: # no idea why this is useful, but it is!
        cpu_active.duration -= 1
      waited = 0
      cpu_active.been_waiting = 0
      cpu_active.queue = "CPU" # change project state
      preempt = cpu_queue[0]
      first.is_preempting = True
      if not process.bumped:
        event("P%d" % first.num + " completed I/O", cpu_queue[2:], time_elapsed)        
      first.queue = "CPU"
      first.entered_at = time_elapsed
      cpu_active.entered_at = time_elapsed
      event("P%d preempted by P%d" % (cpu_active.num, first.num), cpu_queue[1:], time_elapsed)
      acted = True
  process.bumped = False
  return (waited, processes, process, cpu_queue, active, preempt, acted, stats)

def simulate(processes, time_elapsed, t_cs, method):
  stats = Stats(method)
  cpu_queue = [] # init the cpu queue
  active = -1 # set the cpu active state to -1 (not active)
  preempt = -1
  waited = 0 # set the context switch / idle counter to 0 for start
  acted = False
  for process in processes: # put all processes in the cpu queue to start
    for i in range(process.bursts):
      stats.bursts.append(process.cpu)
    stats.wait_times.append((process.been_waiting, process.num))
    process.been_waiting = 0
    process.queue = "CPU"
    waited, processes, process, cpu_queue, active, preempt, acted, stats = add_process(cpu_queue, processes, process, method, active, time_elapsed, waited, preempt, acted, stats) # add the process to the cpu queue
  event("Simulator started for " + method, cpu_queue, time_elapsed) # begin booting
  while processes: # loop until there's nothing more to do (system terminates when no processes exist)
    time_elapsed += 1 # increment time as it passes
    if active == -1 and len(cpu_queue) > 0:
      waited += 1 # increases time waited if idling/waiting for context switch
    temp_processes = processes[:]
    temp_processes.sort(key=lambda x: x.num) # sort by process number for tie dealing
    acted = False
    for process in temp_processes:
      if process.queue == "IO":
        process.duration -= 1 # reduce the duration remaining for the current IO burst
        if process.duration <= 0:
          if len(cpu_queue) == 0: # allows for variable handling of idling based on architecture
            waited = 0
          process.duration = process.cpu # set the process remaining duration to the time of its cpu burst
          process.been_waiting = 0
          process.queue = "CPU" # mark what the process is doing
          waited, processes, process, cpu_queue, active, preempt, acted, stats = add_process(cpu_queue, processes, process, method, active, time_elapsed, waited, preempt, acted, stats) # add the process to the cpu queue
          if not process.is_preempting:
            event("P%d" % process.num + " completed I/O", cpu_queue, time_elapsed)
      elif active == -1: # if nothing is happening
        if waited >= t_cs and len(cpu_queue) > 0 and cpu_queue[0] == process.num:
          # if there is a process waiting and it is this process, make it active!
          if cpu_queue[0] == preempt:
            preempt = -1
          if process.is_preempting:
            process.is_preempting = False
            process.been_waiting = 0
          active = process.num
          waited = 0
          process.queue = "ACTIVE" # change project state
          cpu_queue.pop(0)
          stats.wait_times.append((process.been_waiting, process.num))
          process.been_waiting = 0
          stats.context_switches += 1
          event("P%d" % process.num + " started using the CPU", cpu_queue, time_elapsed)
        elif process.queue == "CPU":
          process.been_waiting += 1
          if process.been_waiting > process.cpu*3 and process.priority > 0 and method == "PWA":
            process.priority -= 1
            stats.wait_times.append((process.been_waiting, process.num))
            process.been_waiting = 0
            process.bumped = True
            waited, processes, process, cpu_queue, active, preempt, acted, stats = add_process(cpu_queue, processes, process, method, active, time_elapsed, waited, preempt, acted, stats) # add the process to the cpu queue
      elif process.queue == "ACTIVE":
        # if the process is active and there has yet to be a cpu event this tick
        # then tick this processes cpu duration down one (execute it)
        if not acted:
          acted = True
          process.duration -= 1
        if process.duration <= 0:
          process.bursts -= 1
          if process.bursts <= 0:
            stats.turnarounds.append(process.turnaround_ticker+1)
            process.turnaround_ticker = 0
            stats.secondary_wait_times.append(process.secondary_wait_time)
            process.secondary_wait_time = 0
            event("P%d" % process.num + " terminated", cpu_queue, time_elapsed)
            processes.remove(process)
            active = -1
            waited = 0
          else:
            process.queue = "IO"
            stats.turnarounds.append(process.turnaround_ticker)
            process.turnaround_ticker = 0
            stats.secondary_wait_times.append(process.secondary_wait_time)
            process.secondary_wait_time = 0
            process.duration = process.io
            event("P%d" % process.num + " completed its CPU burst", cpu_queue, time_elapsed)
            event("P%d" % process.num + " performing I/O", cpu_queue, time_elapsed)
            active = -1
            waited = 0
      elif process.queue == "CPU":
        process.been_waiting += 1
        if process.been_waiting > process.cpu*3 and process.priority > 0 and method == "PWA":
          process.priority -= 1
          stats.wait_times.append((process.been_waiting, process.num))
          process.been_waiting = 0
          process.bumped = True
          waited, processes, process, cpu_queue, active, preempt, acted, stats = add_process(cpu_queue, processes, process, method, active, time_elapsed, waited, preempt, acted, stats) # add the process to the cpu queue
    for process in temp_processes:
      if process.queue != "IO":
        process.turnaround_ticker += 1 
      if process.queue == "CPU" and not (active == -1 and process.num == cpu_queue[0]) and not process.is_preempting:
        process.secondary_wait_time += 1
  event("Simulator for " + method + " ended", cpu_queue, time_elapsed)
  stats.output()

if __name__ == "__main__":
  if len(argv) == 2:
    script, file_name = argv
  else:
    file_name = "processes.txt"
  # define tunable constants requested
  # number of processes to simulate: 
  n = None # will be set by input file
  # time (in ms) to perform a context switch
  t_cs = 13 # defined as specified in the assignment 
  # parse file input
  processes = parse_input(file_name)
  n = len(processes)
  fout = open('simout.txt','w')
  fout.close() # clear the file if it exists D:
  simulate(processes, 0, t_cs, "FCFS")
  print "\n"
  time_elapsed = 0
  processes = parse_input(file_name)
  n = len(processes)
  simulate(processes[:], 0, t_cs, "SRT")
  print "\n"
  time_elapsed = 0
  processes = parse_input(file_name)
  n = len(processes)
  simulate(processes[:], 0, t_cs, "PWA")