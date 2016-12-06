import os, sys, re
import Cloudwatchdog
import datetime
'''
 --- main --
 check for ec2 count
 find idle EC2 instances
 check snapshot older than ...
 switch off EC2/delete snapshot
 ElasticIP count
 ElasticIP for idle resource
 ------------
 '''



class MonitorAWS(object):
    def __init__(self):
         pass


    def extractEc2info(self):
        ec2info=watchdogobj.totalec2count()
        return ec2info

    def extractSnapshot(self):
        snapinfo=watchdogobj.snapshot()
        return snapinfo

    def extractCloudwatchIn(self):
        for instanceid in reportList:
            instanceid = instanceid.split('!')
            if instanceid[1] == "running":
                netIninfo=watchdogobj.cloudwatch(instanceid[0], 'NetworkIn')
                NetmonInList.append(netIninfo)

        return NetmonInList

    def extractCloudwatchOut(self):
        for instanceid in reportList:
            instanceid = instanceid.split('!')
            if instanceid[1] == "running":
                netOutinfo=watchdogobj.cloudwatch(instanceid[0], 'NetworkOut')
                NetmonOutList.append(netOutinfo)

        return NetmonOutList

    def reportgenerate(self):
        #EC2 with snapshots
        report=[]
        for repEc2 in reportList:
            snapFlag=False
            repEc2 = repEc2.split('!')
            for snap in snapInfo:
                snap = snap.split('!')
                if repEc2[2] == snap[0]:
                    #print repEc2[0], repEc2[1], repEc2[2], snap[0], snap[1]
                    Ec2stats = "%s, %s, %s, %s, %s" % (repEc2[0], repEc2[1], repEc2[2], snap[0], snap[1])
                    report.append(Ec2stats)
                    snapFlag=True

            if not snapFlag:
                #print repEc2[0], repEc2[1], repEc2[2]
                Snapstats = "%s, %s, %s" % (repEc2[0], repEc2[1], repEc2[2])
                report.append(Snapstats)

        #snapshots without EC2 
        for snap in snapInfo:
            snapFlag=False
            snap = snap.split('!')
            for repEc2 in reportList:
                repEc2 = repEc2.split('!')
                if repEc2[2] == snap[0]:
                    snapFlag=True
            
            if not snapFlag:
                #print "-----\t", "-----\t", "-----\t\t", snap[0], snap[1]
                snapStats = "%s, %s, %s, %s, %s" % ("-----\t", "-----\t", "-----\t\t", snap[0], snap[1])
                report.append(snapStats)
        
        #print report
        for stats in report:
            print stats




if __name__ == '__main__':
    mainobj = MonitorAWS()
    watchdogobj = Cloudwatchdog.Cloudwatchdog()
    #declar list:
    reportList=[]
    snapList=[]
    NetmonInList=[]
    NetmonOutList=[]

    #mainobj.extractEc2info()
    ec2Info=mainobj.extractEc2info()
    snapInfo=mainobj.extractSnapshot()

    for ec2info in ec2Info:
        reportList.append(ec2info)

    #print reportList
    #print snapInfo

    netmonInfo=mainobj.extractCloudwatchIn() 
    netmonOutinfo=mainobj.extractCloudwatchOut()

    #print netmonInfo
    #print netmonOutinfo
   
    mainobj.reportgenerate()


