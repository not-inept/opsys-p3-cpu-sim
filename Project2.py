#! /usr/bin/python2
#John Drogo
#10/4/2015

import sys
import copy
t_cs = 13 #Context switching time.
n = -1 #Max number of processes. Set to -1 to auto scale. Will be set to the number of processes loaded after input file is loaded.
class Process:
    id = 0
    bursttime = 0 #Time of a single burst.
    bursts = 0
    iotime = 0
    priority = 0
    timeremaining = 0 #Time remaining in the current burst.
    turnaround = 0 #Time spent in a CPU or the queue, context switch included.
    wait = 0 #Time spent in the ready queue.
    currentwait = 0 #Time in ready queue since last I/O completion. Count after preemption?
    status = "" #waiting, performingio, loadingcpu, cpu, terminated
    currentIOTime = 0
    executedBursts = 0
    def __init__(self, inputString):
        details = inputString.split("|")
        #There should only be five entries for every line.
        assert(len(details) == 5)
        self.id = int(details[0])
        self.bursttime = int(details[1])
        self.bursts = int(details[2])
        self.iotime = int(details[3])
        self.priority = int(details[4])
        assert(self.priority <= 5 and self.priority >= 0) #Priority must be in a valid range.
        self.timeremaining = self.bursttime
        self.status = "waiting"

class CPU:
    global t_cs
    defaultContextTime = t_cs #Context switch time.
    contextTime = 0 #Time spent in the current context switch. When this == defaultContextTime we are good.
    currentProcess = None
    processQueue = [] #Does not include the process that is currently processing.
    contextSwitches = 0
    algorithm = "fcfs"
    iosys = None
    def isReady(self): #If the cpu is ready for the next process.
        return (self.currentProcess == None)

    def loadNextProcess(self):
        if (len(self.processQueue)):
            self.currentProcess = self.processQueue[0]
            self.currentProcess.status = "loadingcpu"
            self.currentProcess.currentwait = 0 #I assume we keep the process in the queue even while we context switch.
            self.contextSwitches += 1

    def addProcessToQueue(self, finishedProcess):
        if (self.algorithm == "fcfs"):
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
            self.processQueue.sort(key=lambda x: (x.priority, x.id)) #Break priority ties by process id? This complicates things a bit.
            if (self.currentProcess != None):
                if (self.processQueue[0].priority < self.currentProcess.priority): #Preemption
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
                #Leave the process loading as the first element in the queue.
                elif (self.processQueue[0].priority == self.currentProcess.priority and self.currentProcess != self.processQueue[0] and self.currentProcess in self.processQueue):
                    assert(self.contextTime < self.defaultContextTime)
                    cpu.processQueue.remove(self.currentProcess)
                    cpu.processQueue = [self.currentProcess] + cpu.processQueue
        if (self.isReady()):
            self.loadNextProcess()

class IOSystem:
    def startedIO(self, process):
        if (process.iotime): #Only print I/O messages for processes that take I/O.
            process.status = "performingio"
            printStatusMessage("P"+str(process.id)+" performing I/O", cpu.processQueue)

def printStatusMessage(message, queue):
    global currentTime
    queueString = "[Q"
    for el in queue:
        queueString += (" "+str(el.id))
    queueString += "]"
    print "time {0}ms: {1} {2}".format(currentTime, message, queueString)

def calculateStats(processes, cpu, f):
    totalburst = 0
    totalwait = 0
    totalturnaround = 0
    totalbursts = 0
    for process in processes:
        totalburst += process.executedBursts*process.bursttime
        totalwait += process.wait
        totalturnaround += process.turnaround
        totalbursts += process.executedBursts
    f.write("Algorithm {0}".format(cpu.algorithm.upper())+"\n")
    f.write("-- average CPU burst time: {0:.2f} ms".format(totalburst/float(totalbursts))+"\n")
    f.write("-- average wait time: {0:.2f} ms".format(totalwait/float(totalbursts))+"\n")
    f.write("-- average turnaround time: {0:.2f} ms".format(totalturnaround/float(totalbursts))+"\n")
    f.write("-- total number of context switches: {0}".format(cpu.contextSwitches)+"\n")

origprocesses = []
#Load input file.
if (len(sys.argv) > 2):
    print "Usage: program inputFile.txt"
    quit()
else:
    filename = "processes.txt" #What happens if file loading fails?
    if (len(sys.argv) == 2):
        filename = sys.argv[1]
    with open(filename, "r") as f:
        for line in f:
            if (line[0] != "#" and len(line.strip())):
                if (n != -1): #Limit the number of processes to simulate.
                   if (len(origprocesses) >= n):
                       break
                newprocess = Process(line)
                #Only count processes that do work (plus are not negative).
                if (newprocess.bursts > 0 and newprocess.bursttime > 0):
                    origprocesses.append(newprocess)
                else:
                    print "Error loading process id: {0}. Cannot have a burst count or burst time of zero or less. Ignoring process.".format(newprocess.id)

n = len(origprocesses) #Set n to the number of processes loaded.
outputfile = open("simout.txt", "w")
for algorithm in ["fcfs", "srt", "pwa"]:
    #Generate a new cpu and io subsystem.
    cpu = CPU()
    iosys = IOSystem()
    cpu.iosys = iosys
    iosys.cpu = cpu
    cpu.algorithm = algorithm
    processes = copy.deepcopy(origprocesses) #Consider the processes in order, only after we added them to the queues.
    for process in processes:
        cpu.processQueue.append(process)
    if (algorithm == "srt"): #Initial sort.
        cpu.processQueue.sort(key=lambda x: x.timeremaining)
    elif (algorithm == "pwa"):
        cpu.processQueue.sort(key=lambda x: (x.priority, x.id))
    #Initial load.
    cpu.loadNextProcess()
    #Consider the processes in order.
    processes.sort(key=lambda x: x.id)
    #Start the simulation.
    currentTime = 0
    printStatusMessage("Simulator started for "+cpu.algorithm.upper(), cpu.processQueue)
    while True:
        currentTime += 1
        terminatedProcesses = 0
        for process in processes:
            if (process.status == "terminated"):
                terminatedProcesses += 1
            elif (process.status == "performingio"):
                process.currentIOTime += 1
                if (process.currentIOTime >= process.iotime):
                    process.currentIOTime = 0
                    process.status = "waiting" #Reset the process for the next burst.
                    process.currentwait = 0
                    process.timeremaining = process.bursttime
                    cpu.addProcessToQueue(process)
                    if (process.iotime): #Only print I/O messages for processes that take I/O.
                        if (process.status == "preempting"):
                            #The process should "skip" the queue if it is preempting or was preempted.
                            filteredCPUQueue = [ x for x in cpu.processQueue if x.status not in ["preempting", "preempted"] ]
                            printStatusMessage("P" + str(process.id)+" completed I/O", filteredCPUQueue)
                        else:
                            printStatusMessage("P" + str(process.id)+" completed I/O", cpu.processQueue)
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
                        if (cpu.currentProcess != cpu.processQueue[0]):
                            printStatusMessage("MORE DEAD THINGS", cpu.processQueue)
                            print cpu.currentProcess.id, cpu.currentProcess.status
                            print cpu.processQueue[0].id, cpu.processQueue[0].status
                            assert(0)
                        cpu.processQueue.remove(cpu.currentProcess)
                        cpu.currentProcess.status = "cpu"
                        printStatusMessage("P"+str(cpu.currentProcess.id)+" started using the CPU", cpu.processQueue)
                else: #Actually perform the burst for a time step.
                    cpu.currentProcess.timeremaining -= 1
                    #The process is done, kick it over to the IO queue.
                    if (cpu.currentProcess.timeremaining <= 0):
                        cpu.currentProcess.bursts -= 1
                        cpu.currentProcess.executedBursts += 1
                        #Only report burst completions if the process isn't about to terminate.
                        if (cpu.currentProcess.bursts):
                            printStatusMessage("P"+str(cpu.currentProcess.id)+" completed its CPU burst", cpu.processQueue)
                            iosys.startedIO(process)
                        else: #Process is done.
                            cpu.currentProcess.status = "terminated"
                            printStatusMessage("P"+str(cpu.currentProcess.id)+" terminated", cpu.processQueue)
                            terminatedProcesses += 1
                        cpu.currentProcess = None
                        cpu.contextTime = 0
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
                process.turnaround += 1
        for process in processes: #Clear the preemption flags.
            if (process.status == "preempting"):
                process.status = "loadingcpu"
            elif (process.status == "preempted"): #Ignore preempting process when printing the cpu queue.
                printStatusMessage("P" + str(process.id)+" preempted by P" + str(process.preemptedByProcess.id), cpu.processQueue[1:])
                process.status = "waiting"
        if (cpu.isReady()):
            cpu.loadNextProcess()
        if (terminatedProcesses == n): #When all processes have finished.
            print "time {0}ms: Simulator for {1} ended [Q]".format(currentTime, cpu.algorithm.upper())
            break
    calculateStats(processes, cpu, outputfile)
    if cpu.algorithm != "pwa": #Don't print the three lines if we are done with output.
        print "\n"
outputfile.close()