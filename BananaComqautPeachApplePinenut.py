#! /usr/bin/python2

"""
    Operating Systems
    Project 3

    Mason Cooper & John Drogo
    11/23/2015
"""

import sys
import copy

# Memory module provides tools necessary for contiguous memory management simulation
from memory import Memory

#Important constants
t_cs = 13 #Context switching time.
t_slice = 80
n = -1 #Max number of processes. Set to -1 to auto scale. Will be set to the number of processes loaded after input file is loaded.

# critical whitespace
class Process:
    id = 0
    bursttime = 0 #Time of a single burst.
    bursts = 0
    iotime = 0
    starttime = 0;
    #priority = 0
    timeremaining = 0 #Time remaining in the current burst.
    memsize = 0

    turnaround = 0 #Time spent in a CPU or the queue, context switch included.
    wait = 0 #Time spent in the ready queue.
    currentwait = 0 #Time in ready queue since last I/O completion. Count after preemption?
    status = "" #waiting, performingio, loadingcpu, cpu, terminated
    currentIOTime = 0
    executedBursts = 0

    def __init__(self, inputString):
        details = inputString.split("|")
        #There should only be five entries for every line.
        assert(len(details) == 6)
        self.id = details[0]
        self.starttime = int(details[1])
        self.bursttime = int(details[2])
        self.bursts = int(details[3])
        self.iotime = int(details[4])
        self.memsize = int(details[5])
        #self.priority = int(details[4])
        #Priority must be in a valid range.
        #assert(self.priority <= 5 and self.priority >= 0)
        self.timeremaining = self.bursttime
        self.status = "future"


class CPU:
    global t_cs, t_slice
    defaultContextTime = t_cs #Context switch time.
    sliceTime = t_slice
    
    contextTime = 0 #Time spent in the current context switch. When this == defaultContextTime we are good.
    currentProcess = None
    processQueue = [] #Does not include the process that is currently processing.
    contextSwitches = 0
    processTime = 0 #Time spent processing current process.
    algorithm = "fcfs"
    iosys = None
    mem = None
    memCooldown = 0 #How long it will take the memory to finish its current defragmentation. -1 indicates it is impossible to allocate the memory.
    status = "normal"

    def isReady(self):
        #If the cpu is ready for the next process.
        return (self.currentProcess == None)

    def loadNextProcess(self):
        #print "LOADING CPU"
        if (len(self.processQueue)):
            self.currentProcess = self.processQueue[0]
            self.currentProcess.status = "loadingcpu"
            self.currentProcess.currentwait = 0
            self.processTime = 0
                #I assume we keep the process in the queue even while we context switch.
            self.contextSwitches += 1


    def addProcessToQueue(self, finishedProcess):
    
        if (self.algorithm == "fcfs" or self.algorithm == "rr"):
            self.processQueue.append(finishedProcess)
        
        elif (self.algorithm == "srt"):
            #Add the new process to the queue and start loading it into the processor.
            self.processQueue.append(finishedProcess)
            self.processQueue.sort(key=lambda x: x.timeremaining)
            if (self.currentProcess != None):
                if (self.processQueue[0].timeremaining < self.currentProcess.timeremaining): #PREEMPTION
                    #Add the current process back into the processor queue.
                    self.currentProcess.status = "preempted"
                    
                    #Watch for if we are preempted durring a context switch.
                    if (self.currentProcess not in self.processQueue):
                        self.processQueue.append(self.currentProcess)
                        self.processQueue.sort(key=lambda x: x.timeremaining) #This will work since it is the only sort criteria.
                    else:
                        assert(self.contextTime < self.defaultContextTime)

                    self.currentProcess.preemptedByProcess = self.processQueue[0]

                    #If we haven't had a chance to record the next cpu tick do so now then flag the preempted process for preemption.
                    if (self.currentProcess.id > self.processQueue[0].id):
                        self.currentProcess.timeremaining -= 1
                        self.processQueue[0].turnaround += 1

                    if (self.processQueue[0] != finishedProcess):
                        printStatusMessage("EVERYTHING DIED", cpu.processQueue)
                        print finishedProcess.id, finishedProcess.timeremaining
                        print self.processQueue[0].id, self.processQueue[0].timeremaining
                        assert(0)

                    self.loadNextProcess()
                    self.contextTime = 0
                    finishedProcess.status = "preempting"
        
        elif (self.algorithm == "pwa"):
            self.processQueue.append(finishedProcess)
            self.processQueue.sort(key=lambda x: (x.priority, x.id))    #Break priority ties by process id? This complicates things a bit.
            #DEGBUG2 printStatusMessage("QUEUE UPDATED", cpu.processQueue)

            if (self.currentProcess != None):
                        
                #DEGBUG2 if (len(self.processQueue)):
                    #DEGBUG2 print self.processQueue[0].priority, self.currentProcess.priority
            
                if (self.processQueue[0].priority < self.currentProcess.priority):
                    #Preemption
                    #DEGBUG2 print "PREEMPTION"
                
                    #Add the current process back into the processor queue.
                    self.currentProcess.status = "preempted"
                    
                    #Watch for if we are preempted durring a context switch.
                    if (self.currentProcess not in self.processQueue):
                        self.processQueue.append(self.currentProcess)
                        self.processQueue.sort(key=lambda x: (x.priority, x.id))
                
                    else:
                        assert(self.contextTime < self.defaultContextTime)
                
                    
                    self.currentProcess.preemptedByProcess = self.processQueue[0]
                    self.processQueue.sort(key=lambda x: (x.priority, x.id))

                    #If we haven't had a chance to record the next cpu tick do so now then flag the preempted process for preemption.
                    if (self.currentProcess.id > self.processQueue[0].id):
                        self.currentProcess.timeremaining -= 1
                        finishedProcess.turnaround += 1

                    #We print the message once we processes the preempted process.
                    assert(self.processQueue[0] != self.currentProcess)
                    self.loadNextProcess()
                    self.contextTime = 0
                    finishedProcess.status = "preempting"
                  
                #Edge case when the current process is still in the queue and the preempting process has a smaller pid.
                #Leave the process loading as the first element in the queue.
                elif (self.processQueue[0].priority == self.currentProcess.priority and self.currentProcess != self.processQueue[0] and self.currentProcess in self.processQueue):
                    #Joy...
                    assert(self.contextTime < self.defaultContextTime)
                    cpu.processQueue.remove(self.currentProcess)
                    cpu.processQueue = [self.currentProcess] + cpu.processQueue

        if (self.isReady()):
            self.loadNextProcess()


class IOSystem:
    def startedIO(self, process):
        #Only print I/O messages for processes that take I/O.
        if (process.iotime):
            process.status = "performingio"
            printStatusMessage(
str(process.id)+" performing I/O", cpu.processQueue)



def printStatusMessage(message, queue=None):
    global currentTime
    if (queue != None):
        queueString = "[Q"
        for el in [ x for x in queue if x.status != "future"]:
            queueString += (" "+str(el.id))
        queueString += "]"
        print "time {0}ms: {1} {2}".format(currentTime, message, queueString)

    else:
        print "time {0}ms: {1}".format(currentTime, message)


def calculateStats(processes, cpu, f):
    totalburst = 0
    totalwait = 0
    totalturnaround = 0
    totalbursts = 0
    
    #DEBUG3 waittimes = {}
    for process in processes:
        totalburst += process.executedBursts*process.bursttime
        totalwait += process.wait
        totalturnaround += process.turnaround
        totalbursts += process.executedBursts
    
        #DEBUG3 waittimes[process.id] = process.wait

    f.write("Algorithm {0}".format(cpu.algorithm.upper())+"\n")
    f.write("-- average CPU burst time: {0:.2f} ms".format(totalburst/float(totalbursts))+"\n")
    f.write("-- average wait time: {0:.2f} ms".format(totalwait/float(totalbursts))+"\n")
    f.write("-- average turnaround time: {0:.2f} ms".format(totalturnaround/float(totalbursts))+"\n")
    f.write("-- total number of context switches: {0}".format(cpu.contextSwitches)+"\n")
    #DEBUG3 print waittimes



origprocesses = []

#Load input file.
if (len(sys.argv) > 2):
    print "Usage: program inputFile.txt"
    quit()

else:
    #What happens if file loading fails?
    filename = "processes.txt"
    if (len(sys.argv) == 2):
        filename = sys.argv[1]

    with open(filename, "r") as f:
        for line in f:
            if (line[0] != "#" and len(line.strip())):

                #Limit the number of processes to simulate.
                if (n != -1):
                   if (len(origprocesses) >= n):
                       break

                newprocess = Process(line)

                #Only count processes that do work (plus are not negative).
                if (newprocess.bursts > 0 and newprocess.bursttime > 0):
                    origprocesses.append(newprocess)

                else:
                    print "Error loading process id: {0}. Cannot have a burst count or burst time of zero or less. Ignoring process.".format(newprocess.id)


#Set n to the number of processes loaded.
n = len(origprocesses)
    
#Setup the output file.
outputfile = open("simout.txt", "w")
#waittimes = open("#waittimes.txt", "w")

mem_algorithms = {"nf": "Next Fit", "bf": "Best Fit", "ff": "First Fit"}


for algorithm in ["srt", "rr"]:
    for mem_algorithm in ["ff", "bf", "nf"]:

        #Generate a new cpu and io subsystem.
        cpu = CPU()
        iosys = IOSystem()
        mem = Memory(mem_algorithm)

        cpu.iosys = iosys
        cpu.mem = mem
        iosys.cpu = cpu
        cpu.algorithm = algorithm


        #Start the simulation.
        currentTime = 0
        print "time 0ms: Simulator started for "+cpu.algorithm.upper() +\
            (" (t_slice {0})".format(t_slice) if algorithm == "rr" else "")  +" and "+mem_algorithms[mem_algorithm]


        #Consider the processes in order, only after we added them to the queues. So we don't mess up fcfs.
        processes = copy.deepcopy(origprocesses)
        for process in processes:
            if (process.starttime == 0):
                process.status = "waiting"
                if (not mem.allocate(process.id, process.memsize)):
                    printStatusMessage("{0} unable to be added; lack of memory".format(process.id), cpu.processQueue)
                    printStatusMessage("Starting defragmentation (suspending all processes)", cpu.processQueue)
                    printStatusMessage("Simulated Memory:\n"+mem)
                    cpu.memCooldown = mem.defragment
                    cpu.status = "defragging"
                    assert(0) #This probably shouldn't happen before we actualy run items.
                
                else:
                    cpu.processQueue.append(process) #Append instead of cpu.addProcessToQueue to avoid unnecessary preemption at time 0.
                    printStatusMessage("Process {0} added to system".format(process.id), cpu.processQueue)
                    print "time "+str(currentTime)+"ms: Simulated Memory:\n"+str(mem)

        #Initial sort.
        if (algorithm == "srt"):
            cpu.processQueue.sort(key=lambda x: x.timeremaining)

        elif (algorithm == "pwa"):
            cpu.processQueue.sort(key=lambda x: (x.priority, x.id))

        #Initial load.
        cpu.loadNextProcess() #DEGBUG2 print "BEGINNING WITH PROCESS: {0}".format(cpu.currentProcess.id)

        #Consider the processes in order.
        processes.sort(key=lambda x: x.id) #waittimes.write("Wait times for: {0}\n".format(cpu.algorithm.upper()))

        #Process main loop.
        while True:
            currentTime += 1
            terminatedProcesses = 0
            
            #Add process to queue if it is time.
            if (cpu.status != "defragging"):
                for process in processes:
                    if (process.starttime == currentTime):
                        process.status = "waiting"
                        if (not mem.allocate(process.id, process.memsize)):
                            printStatusMessage("{0} unable to be added; lack of memory".format(process.id), cpu.processQueue)
                            printStatusMessage("Starting defragmentation (suspending all processes)", cpu.processQueue)
                            cpu.memCooldown = mem.defragment
                            cpu.status = "defragging"
                            assert(0) #Not implemented.
                        
                        else:
                            cpu.addProcessToQueue(process)
                            printStatusMessage("Process {0} added to system".format(process.id), cpu.processQueue)

                        print "time "+str(currentTime)+"ms: Simulated Memory:\n"+str(mem)

            #Main tick for all processes.
            for process in processes:
                if (process.status == "terminated"):
                    terminatedProcesses += 1
            
                elif (process.status == "performingio"):
                    process.currentIOTime += 1
                    if (process.currentIOTime >= process.iotime):
                        process.currentIOTime = 0
                        #Only print I/O messages for processes that take I/O.
                        if (process.iotime):
                            if (process.status == "preempting"):
                                #The process should "skip" the queue if it is preempting or was preempted.
                                filteredCPUQueue = [ x for x in cpu.processQueue if x.status not in ["preempting", "preempted"] ]
                                printStatusMessage(str(process.id)+" completed I/O", filteredCPUQueue)
                            
                            else: #Processes can only terminate on a CPU burst, never straight out of I/O.
                                printStatusMessage(str(process.id)+" completed I/O", cpu.processQueue)

                        #Reset the process for the next burst.
                        process.status = "waiting"
                        process.currentwait = 0
                        process.timeremaining = process.bursttime
                        cpu.addProcessToQueue(process)

                elif (process.status == "waiting"): #Wait time.
                    process.wait += 1
                    process.currentwait += 1
                    if (cpu.algorithm == "pwa"):
                        if (process.currentwait > process.bursttime*3):
                            process.priority = max(0, process.priority-1)
                            
                            if (process not in cpu.processQueue):
                                printStatusMessage("DEAD AGAIN", cpu.processQueue)
                                print process.id, process.priority, process.status
                                assert(0)
                            
                            cpu.processQueue.remove(process)
                            cpu.addProcessToQueue(process)
                            process.currentwait = 0
                    #Since the process can't be both waiting and in the cpu this shouldn't double count the turnaround time.
                    process.turnaround += 1


                #if (cpu.status != "defragging"):
                #We are the process in the cpu, should only happen with a status of loadingcpu or cpu.
                elif (process.status == "loadingcpu" or process.status == "cpu"):
                    if (process != cpu.currentProcess):
                        print process.id, process.status
                        print cpu.currentProcess.id, cpu.currentProcess.status
                        assert(0)
                    
                    process.turnaround += 1

                    #Preform the context switch.
                    if (cpu.contextTime < cpu.defaultContextTime):
                        cpu.contextTime += 1

                        #If we are done with the context switch display that we have started using the CPU.
                        if (cpu.contextTime == cpu.defaultContextTime):
                            #Remove the process from the queue and load it into the CPU.
                            #cpu.processQueue.pop(0)
                            if (cpu.currentProcess != cpu.processQueue[0]):
                                printStatusMessage("MORE DEAD THINGS", cpu.processQueue)
                                print cpu.currentProcess.id, cpu.currentProcess.status
                                print cpu.processQueue[0].id, cpu.processQueue[0].status
                                assert(0)
                            
                            cpu.processQueue.remove(cpu.currentProcess)
                            cpu.currentProcess.status = "cpu"
                            printStatusMessage(str(cpu.currentProcess.id)+" started using the CPU", cpu.processQueue)

                    #Actually perform the burst for a time step.
                    else:
                        cpu.currentProcess.timeremaining -= 1
                        cpu.processTime += 1

                        #The process is done, kick it over to the IO queue.
                        if (cpu.currentProcess.timeremaining <= 0):
                        
                            cpu.currentProcess.bursts -= 1
                            cpu.currentProcess.executedBursts += 1

                            #Only report burst completions if the process isn't about to terminate.
                            if (cpu.currentProcess.bursts):
                                printStatusMessage(str(cpu.currentProcess.id)+" completed its CPU burst", cpu.processQueue)
                                iosys.startedIO(process)

                            else:
                                #Process is done.
                                cpu.currentProcess.status = "terminated"
                                mem.deallocate(cpu.currentProcess.id)
                                printStatusMessage(str(cpu.currentProcess.id)+" terminated", cpu.processQueue)
                                terminatedProcesses += 1

                            cpu.currentProcess = None
                            cpu.contextTime = 0


                        #For round robin detect when time slice expires.
                        elif (cpu.algorithm == "rr" and cpu.processTime >= cpu.sliceTime):
                            #PREMPTION TIME SLICE EXPIRED!
                            assert(cpu.processTime)

                            #Outputting for the srt preemption is different from the round robin queue output. (First process is included.
                            printStatusMessage(str(process.id)+" preempted due to time slice expiration", cpu.processQueue)

                            #Load the next process if we have one, otherwise ignore the context switch.
                            if (len([x for x in cpu.processQueue if x.status != "future"])):

                                #Add the current process back into the processor queue.
                                cpu.currentProcess.status = "preempted"
                                cpu.processQueue.append(cpu.currentProcess)
                                cpu.currentProcess.preemptedByProcess = cpu.processQueue[0]

                                cpu.loadNextProcess()
                                cpu.processQueue[0].status = "preempting"
                                cpu.contextTime = 0
                                
                            else:
                                cpu.processTime = 0;


            #Clear the preemption flags.
            #waittimes.write("Tick {0: 5}:     ".format(currentTime))
            for process in processes:
                #waittimes.write("P{0} {1: 5}          ".format(process.id, process.wait))
                if (process.status == "preempting"):
                    process.status = "loadingcpu"

                elif (process.status == "preempted"):
                    #Ignore preempting process when printing the cpu queue.
                        #We should be able to just ignore the start of the queue. (Context switch.)
                    if (cpu.algorithm != "rr"):
                        printStatusMessage(str(process.id)+" preempted by P" + str(process.preemptedByProcess.id), cpu.processQueue[1:])
                    process.status = "waiting"

            if (cpu.status == "defragging"):
                if (cpu.memCooldown > 0):
                    cpu.memCooldown -= 1
                else:
                    assert(cpu.memCooldown == 0)
                    cpu.status = "normal"

            #When all processes have finished.
            if (terminatedProcesses == n):
                print "time {0}ms: Simulator for {1} ended [Q]".format(currentTime, cpu.algorithm.upper())
                break

            if (cpu.isReady()):
                cpu.loadNextProcess()

        calculateStats(processes, cpu, outputfile)
        
        #Don't print the three lines if we are done with output.
        if not (cpu.algorithm == "rr" and mem_algorithm == "nf"):
            print "\n"
            #waittimes.write("\n\n\n")

outputfile.close()