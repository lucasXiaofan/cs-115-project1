from collections import deque
from operator import truediv
import random
import math
import sys
#test open the cmd on the directory with the 
#~cs115/bin/submit
#-A 
#copy the schedule file and newCrewfile 
#run the command
#   ~./ ==homedirctoary 
# if len(sys.argv) ==4:
#     #-s fileSchedule filenewCrew
#     pass
# elif len(sys.argv) == 3:
#     # 10 le^6
#     pass

# class of train to store information like train number, crew class, etc that helpful for output and statistic, 
# also provide helper function for self generating simulation

class Train():
    def __init__(self,tnum,tEnterStation,cCnum,
                GivenArriveTime = 0,GivenUnloadTime =0,GivenReCrewHours =0,GivenNewCrewTravelTIme = 0) -> None:
        self.trainNum = tnum
        #statistic 
        self.trainEnterStationTime = tEnterStation
        self.trainExitStationTime = 0
        self.enterQueue = tEnterStation
        self.exitQueue = 0
        
        self.hourToUnload = random.uniform(3.5,4.5)
        self.cCrew = Crew(cCnum) # check cCrew == None to determine whether the rain is hogout or not
        self.nextCrewNum = None
        self.RemainTimeForNewCrewCome = float('inf')
        self.allCrew = []
        
    def UpdateNextCrewNumber(self,crewN):
        self.nextCrewNum = crewN
    
    def UpdateUnloadTime(self,time):
        self.hourToUnload = time
    
    def UpdateNewCrewComeTime(self,time):
        self.RemainTimeForNewCrewCome = time
    
    def GenerateNewCrewComeTime(self):
        if self.cCrew==None:
            self.UpdateNewCrewComeTime(random.uniform(2.5,3.5))
        elif self.cCrew!=None:
            self.UpdateNewCrewComeTime(float('inf'))
        
    def UpdateCrew(self,crew):
        self.cCrew = crew
        if crew != None:
            self.allCrew.append(crew)
    
    def CurCrewWorkHRemain(self):
        if self.cCrew!=None:
            return self.cCrew.hBeforeHog
        else:
            return float('inf')
    
    def ChangeCurCrewWorkHRemain(self,hours): 
        if self.cCrew!=None:
            self.cCrew.UpdateRemainWorkTime(hours)
    
    def TotalHogoutTime(self):
        if len(self.allCrew)>=1:
            return len(self.allCrew)-1
        else: return 0

#store information about crew like hours before hog and crew num, 
# and helper functions make edit information in crew easy
class Crew():
    def __init__(self,cnum) -> None:
        self.CrewNum = cnum
        self.hBeforeHog = random.uniform(6.0,11.0)
    
    def CrewNumber(self):
        return self.CrewNum
    
    def HoursBeforeHog(self):
        return self.hBeforeHog
    
    def UpdateRemainWorkTime(self,hour:float):
        self.hBeforeHog = hour
    
class TrainStation():
    def __init__(self,seed,simulationLimit,GivenRatio):
        self.totalNumOFArrivedTrain = 0
        self.totalNumOfCrew = 0
        self.ratio = GivenRatio
        
        #special event:
        self.dockHogOut = False
        self.StopServe = False
        self.simulationEnd = False
        
        #for statistic 
        self.HogoutCountPerTrain = {}
        self.TimeEachTrainInqueue = []
        self.TimeEachTrainInSystem = []
        self.dockBusyTime = 0 #not counting the hogout
        self.maxiTimeInSystem = 0
        self.maxNumberTrainInqueue = 0
        self.hogoutTime = 0
        self.totalTime = 0
        self.simulationL = simulationLimit
        
        self.tQueue = deque()
        self.cUnloadTrain = None
        random.seed = seed
    
        # the core of this simulation is how to update total time and each component's time, 
        # and that depends on the compare of all their time
        self.compareAllTime= {"NextArrivalTime":float('inf'),"WorkRemainInQueue":float('inf')
                            ,"UnloadRemainTime":float('inf'),"NewCrewArrivalQueue":float('inf')
                            ,"CrewWorkRemainInUnload":float('inf'),"NewCrewArriveInUnload":float('inf')}
        self.TrainQueue = {"cCrewRemainHours":[],"NewCrewComingRemain":[]}
    
    def UpdateTQueCompareAllTime(self): #base on current data update compareAlltime dictionary
        if len(self.TrainQueue["cCrewRemainHours"])>0:
            self.compareAllTime["WorkRemainInQueue"] = min(self.TrainQueue["cCrewRemainHours"],key = lambda x:x[1])[1]
        else:
            self.compareAllTime["WorkRemainInQueue"] = float('inf')
        if len(self.TrainQueue["NewCrewComingRemain"])>0:
            self.compareAllTime["NewCrewArrivalQueue"] = min(self.TrainQueue["NewCrewComingRemain"],key = lambda x:x[1])[1]
        else:
            self.compareAllTime["NewCrewArrivalQueue"] =float('inf')
    
    def UpdateEachEventsTime(self,hours):
        command = ["NextArrivalTime","WorkRemainInQueue","NewCrewArrivalQueue"
                ,"UnloadRemainTime","CrewWorkRemainInUnload","NewCrewArriveInUnload"]
        for c in command:
            if ((c == "UnloadRemainTime" and self.dockHogOut) or 
            (c=="NextArrivalTime" and self.StopServe)):
                continue
            self.compareAllTime[c]-=hours
        for t in self.tQueue: # changing crew's working hours and newcrewcome hours
            if t.cCrew!=None:
                t.ChangeCurCrewWorkHRemain(t.CurCrewWorkHRemain()-hours)
            t.UpdateNewCrewComeTime(t.RemainTimeForNewCrewCome - hours)
            self.UpdateTrainInTrainQueue(t)
        if self.cUnloadTrain!=None:
            if self.dockHogOut ==False:
                self.cUnloadTrain.UpdateUnloadTime(self.cUnloadTrain.hourToUnload - hours)
            self.cUnloadTrain.ChangeCurCrewWorkHRemain(self.cUnloadTrain.CurCrewWorkHRemain()-hours)
            self.cUnloadTrain.UpdateNewCrewComeTime(self.cUnloadTrain.RemainTimeForNewCrewCome - hours)
        self.UpdateTQueCompareAllTime()
        
    def UpdateTrainInTrainQueue(self,train):
        if train.cCrew ==None:
            for i in range(len(self.TrainQueue["cCrewRemainHours"])):
                if self.TrainQueue["cCrewRemainHours"][i][0] == train.trainNum:
                    self.TrainQueue["cCrewRemainHours"].pop(i)
                    break
            for i in range(len(self.TrainQueue["NewCrewComingRemain"])):
                if self.TrainQueue["NewCrewComingRemain"][i][0] == train.trainNum:
                    self.TrainQueue["NewCrewComingRemain"].pop(i)
                    break
            self.TrainQueue["NewCrewComingRemain"].append((train.trainNum,train.RemainTimeForNewCrewCome))
        elif train.cCrew != None:
            for i in range(len(self.TrainQueue["NewCrewComingRemain"])):
                if self.TrainQueue["NewCrewComingRemain"][i][0] == train.trainNum:
                    self.TrainQueue["NewCrewComingRemain"].pop(i)
                    break
            for i in range(len(self.TrainQueue["cCrewRemainHours"])):
                if self.TrainQueue["cCrewRemainHours"][i][0] == train.trainNum:
                    self.TrainQueue["cCrewRemainHours"].pop(i)
                    break
            self.TrainQueue["cCrewRemainHours"].append((train.trainNum,train.cCrew.hBeforeHog))
        
    def NewTrainArrive(self,train):
        t = train 
        self.totalNumOFArrivedTrain+=1
        self.totalNumOfCrew+=1
        self.UpdateNextArriveTime()
        print(f"Time {round(self.totalTime,2)}: train {t.trainNum} arrival for {round(t.hourToUnload,2)}h of unloading, crew {t.cCrew.CrewNum} with {round(t.cCrew.hBeforeHog,2)}h before hogout (Q={len(self.tQueue)})")
        if len(self.tQueue)==0 and self.cUnloadTrain ==None:
            self.TrainEnter(t) # has bug
        else:
            self.tQueue.append(t)
            self.UpdateTrainInTrainQueue(t)
            self.UpdateTQueCompareAllTime()
            
    def TrainEnter(self,train): #prerequisite is that current unload train == None
        train.exitQueue = self.totalTime
        if train.cCrew != None and self.cUnloadTrain ==None:
            self.cUnloadTrain = train
            self.dockBusyTime +=train.hourToUnload
            self.compareAllTime["UnloadRemainTime"] = train.hourToUnload
            self.compareAllTime["CrewWorkRemainInUnload"] = train.cCrew.hBeforeHog
            print(f"Time {round(self.totalTime,2)}: train {train.trainNum} entering dock for {round(train.hourToUnload,2)}h of unloading, crew {train.cCrew.CrewNum} with {round(train.cCrew.hBeforeHog,2)}h before hogout")

        elif train.cCrew == None:
            self.dockHogOut = True
    
    #when a train departured, collect all the data generate by that train
    def TrainDeparture(self):
        self.cUnloadTrain.trainExitStationTime = self.totalTime
        self.compareAllTime["UnloadRemainTime"] = float('inf')
        self.compareAllTime["NewCrewArriveInUnload"] = float('inf')
        self.compareAllTime["CrewWorkRemainInUnload"] = float('inf')
        if self.cUnloadTrain !=None:
            if self.cUnloadTrain.TotalHogoutTime() not in self.HogoutCountPerTrain:
                self.HogoutCountPerTrain[self.cUnloadTrain.TotalHogoutTime()] = 1
            elif self.cUnloadTrain.TotalHogoutTime() in self.HogoutCountPerTrain:
                self.HogoutCountPerTrain[self.cUnloadTrain.TotalHogoutTime()]+=1
            self.TimeEachTrainInqueue.append(self.cUnloadTrain.exitQueue -self.cUnloadTrain.enterQueue)
            totalTimeSpendInSystem = self.cUnloadTrain.trainExitStationTime-self.cUnloadTrain.trainEnterStationTime
            self.TimeEachTrainInSystem.append(totalTimeSpendInSystem)
            self.maxNumberTrainInqueue = max(self.maxNumberTrainInqueue,len(self.tQueue))
            if totalTimeSpendInSystem>self.maxiTimeInSystem:
                self.maxiTimeInSystem = totalTimeSpendInSystem
            self.cUnloadTrain = None
    
    def UpdateNextArriveTime(self):
        time = -(self.ratio)*math.log((1-random.uniform(0,1)),math.e)
        self.compareAllTime["NextArrivalTime"] = time
    
    #when a train is poped from queue, also need to remove its record in queue list
    def RemoveTrainFromList(self,tnum):
        for i in range(len(self.TrainQueue["cCrewRemainHours"])):
            if self.TrainQueue["cCrewRemainHours"][i][0] ==tnum:
                self.TrainQueue["cCrewRemainHours"].pop(i)
                break
        for i in range(len(self.TrainQueue["NewCrewComingRemain"])):
            if self.TrainQueue["NewCrewComingRemain"][i][0] ==tnum:
                self.TrainQueue["NewCrewComingRemain"].pop(i)
                break
        
    def UpdateTotalTime(self): #update time for 6 different events & print out outcome for each events
        # if dock lock out stop compareing the unloadremaintime
        #current unloading train need change time too
    
        if self.totalTime>=self.simulationL:
            self.StopServe = True
            
        if self.StopServe and len(self.tQueue) == 0 and self.cUnloadTrain ==None:
            self.simulationEnd = True
            print(f"Time {round(self.totalTime,2)}: simulation ended")
            
        else:
            taskWithMinimumTime = ""
            mih = float('inf')
            if self.dockHogOut:
                for n,h in self.compareAllTime.items():
                    if n!= "UnloadRemainTime":
                        if self.compareAllTime[n]<mih:
                            taskWithMinimumTime = n
                            mih = h
            else:
                taskWithMinimumTime= min(self.compareAllTime,key=lambda x: self.compareAllTime[x])
            self.totalTime += self.compareAllTime[taskWithMinimumTime]
            self.UpdateEachEventsTime(self.compareAllTime[taskWithMinimumTime])
            
            if  taskWithMinimumTime =="WorkRemainInQueue":   
                for t in self.tQueue:
                    if t.trainNum == min(self.TrainQueue["cCrewRemainHours"],key = lambda x:x[1])[0]:
                        print(f"Time {round(self.totalTime,2)}: train {t.trainNum} crew {t.cCrew.CrewNum} hogged out during service (Q = {len(self.tQueue)})")
                        self.totalNumOfCrew+=1
                        t.UpdateNextCrewNumber(self.totalNumOfCrew)
                        t.cCrew = None
                        t.GenerateNewCrewComeTime()
                        self.UpdateTrainInTrainQueue(t)
                        self.UpdateTQueCompareAllTime()
                        break
            
            elif taskWithMinimumTime =="NextArrivalTime":
                if self.StopServe:
                    self.compareAllTime["NextArrivalTime"] = float('inf')
                else:
                    newTrain = Train(self.totalNumOFArrivedTrain,self.totalTime,self.totalNumOfCrew)
                    self.NewTrainArrive(newTrain)
            
            elif taskWithMinimumTime =="UnloadRemainTime":
                print(f"Time {round(self.totalTime,2)}: train {self.cUnloadTrain.trainNum} departing (Q={len(self.tQueue)})")
                if len(self.tQueue) == 0:
                    self.TrainDeparture()
                    self.UpdateNextArriveTime()
                else:
                    enterTrain = self.tQueue[0]
                    self.TrainDeparture()
                    if enterTrain.cCrew ==None:
                        if enterTrain.nextCrewNum ==None:
                            self.totalNumOfCrew+=1
                            enterTrain.UpdateNextCrewNumber(self.totalNumOfCrew)
                        self.hogoutTime+=enterTrain.RemainTimeForNewCrewCome
                        self.dockHogOut = True
                        print(f"Time {round(self.totalTime,2)}: train {enterTrain.trainNum} crew {enterTrain.nextCrewNum} hasn't arrived yet, cannot enter dock (SERVER HOGGED)")
                    else:
                        self.TrainEnter(enterTrain)
                        self.RemoveTrainFromList(enterTrain.trainNum)
                        self.UpdateTQueCompareAllTime()
                        self.tQueue.popleft()
                    
            elif taskWithMinimumTime =="NewCrewArrivalQueue":
                train = None
                if min(self.TrainQueue["NewCrewComingRemain"],key = lambda x:x[1])[0] == self.tQueue[0].trainNum and self.cUnloadTrain==None:
                    self.dockHogOut = False
                    train = self.tQueue[0]
                    newCrew = Crew(train.nextCrewNum)
                    train.UpdateCrew(newCrew)
                    print(f"Time {round(self.totalTime,2)}: train {train.trainNum} replacement crew {train.cCrew.CrewNum} arrives (SERVER UNHOGGED)")
                    self.TrainEnter(train)
                    self.RemoveTrainFromList(train.trainNum)
                    self.UpdateTQueCompareAllTime()
                    self.tQueue.popleft()
                for t in self.tQueue:
                    if len(self.TrainQueue["NewCrewComingRemain"]) >0 and t.trainNum ==min(self.TrainQueue["NewCrewComingRemain"],key = lambda x:x[1])[0]:
                        train = t
                        newCrew = Crew(train.nextCrewNum)
                        train.UpdateCrew(newCrew)
                        train.RemainTimeForNewCrewCome = float('inf')
                        self.UpdateTrainInTrainQueue(train)
                        self.UpdateTQueCompareAllTime()
                        print(f"Time {round(self.totalTime,2)}: train {train.trainNum} replacement crew {train.cCrew.CrewNum} arrives (Q = {len(self.tQueue)})")
                        break
                
            elif taskWithMinimumTime =="CrewWorkRemainInUnload":
                print(f"Time {round(self.totalTime,2)}: train {self.cUnloadTrain.trainNum} crew {self.cUnloadTrain.cCrew.CrewNum} hogged out during service (SERVER HOGGED)")
                self.cUnloadTrain.cCrew =None
                self.dockHogOut = True
                self.totalNumOfCrew+=1
                self.cUnloadTrain.UpdateNextCrewNumber(self.totalNumOfCrew)
                self.cUnloadTrain.GenerateNewCrewComeTime()
                self.hogoutTime+=self.cUnloadTrain.RemainTimeForNewCrewCome
                self.compareAllTime["CrewWorkRemainInUnload"] = float('inf')
                self.compareAllTime["NewCrewArriveInUnload"] = self.cUnloadTrain.RemainTimeForNewCrewCome
                
            elif taskWithMinimumTime =="NewCrewArriveInUnload":
                self.dockHogOut = False
                newCrew = Crew(self.cUnloadTrain.nextCrewNum)
                self.cUnloadTrain.UpdateCrew(newCrew)
                self.compareAllTime["CrewWorkRemainInUnload"] = self.cUnloadTrain.CurCrewWorkHRemain()
                self.compareAllTime["NewCrewArriveInUnload"] = float('inf')
                print(f"Time {round(self.totalTime,2)}: train {self.cUnloadTrain.trainNum} replacement crew {self.cUnloadTrain.nextCrewNum} arrives (SERVER UNHOGGED)")

    def RunSimulation(self):
        self.UpdateNextArriveTime()
        t = Train(self.totalNumOFArrivedTrain,self.compareAllTime["NextArrivalTime"],self.totalNumOfCrew)
        self.totalTime+=self.compareAllTime["NextArrivalTime"]
        self.NewTrainArrive(t)

        while self.simulationEnd==False:
            self.UpdateTotalTime()
        print()
        print("Statistics")
        print(f'Total number of trains served: {self.totalNumOFArrivedTrain}')
        print(f"Average time-in-system per train: {round(sum(self.TimeEachTrainInSystem)/self.totalNumOFArrivedTrain,2)}h")
        print(f"Maximum time-in-system per train: {round(self.maxiTimeInSystem,2)}h")
        print(f"Dock idle percentage: {round((1-self.dockBusyTime/self.totalTime)*100,2)}%")
        print(f"Dock busy percentage: {round((self.dockBusyTime/self.totalTime)*100,2)}%")
        print(f"Dock hogged-out percentage: {round((self.hogoutTime/self.totalTime)*100,2)}%")
        print(f"Time average of trains in queue: {round(sum(self.TimeEachTrainInqueue)/self.totalNumOFArrivedTrain,2)}")
        print(f"Maximum number of trains in queue: {self.maxNumberTrainInqueue}")
        print("Histogram of hogout count per train:")
        for key,val in self.HogoutCountPerTrain.items():
            print(f"[{key}]: {val}")
        
        
            
t = TrainStation(1,10000,10)
t.RunSimulation()
