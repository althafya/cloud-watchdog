import os, sys
import boto3
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
'''
EC2 count       - ok
EC2 instance id - Done
EBS volume id   - Done
EC2 status      - Done
OwnerId         - Done
Snapshot        - Done
Snapshot age    - Done
Elastic IP      -
Network In      - Done
Newtork Out     - Done
        Benifits:
                EC2 Count info
                EC2 Idle count
                EC2 can be turned off
                Snapshot older info
                Snapshot can be deleted
                Elastic IPs count info
                Elastic IPs used for Idle
'''

class Cloudwatchdog(object):
    def __init__(self):
        self.aws_access_key_id='AKIAIWFAWR2QNXKI3S7Q'
        self.aws_secret_access_key='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'
        self.region='us-east-1'
        self.ownerid=self.getownerid()

    def boto3client(self, service):
        client = boto3.client(service,
                               self.region,
                               aws_access_key_id=self.aws_access_key_id,
                               aws_secret_access_key=self.aws_secret_access_key)
        return client

    def getownerid(self):
        client = self.boto3client('sts')
        OwnerId = client.get_caller_identity()['Account']
        return OwnerId

    def totalec2count(self):
        ec2_volume=None
        ec2List=[]
        client = self.boto3client('ec2')
        ec2_instances_detail = client.describe_instances()
        for respons in ec2_instances_detail['Reservations']:
            volumeId = self.volumeid(respons)
            ec2_volume="%s!%s!%s" % (respons['Instances'][0]['InstanceId'], respons['Instances'][0]['State']['Name'], volumeId)
            ec2List.append(ec2_volume)

        return ec2List

    def volumeid(self, respons):
        volinfo=None
        volList=[]
        for ids in respons['Instances'][0]['BlockDeviceMappings']:
            volinfo="%s" % ids['Ebs']['VolumeId']
            volList.append(volinfo)

        return "!".join(volList)

    def snapshot(self):
        snapStatus=None
        snapList=[]
        client = self.boto3client('ec2')
        snap_details = client.describe_snapshots(OwnerIds=[self.ownerid])
        for resSnap in snap_details['Snapshots']:
            a = dateutil.parser.parse(datetime.datetime.now().strftime('%Y-%m-%d'))
            b = dateutil.parser.parse(datetime.date.strftime(resSnap['StartTime'],'%Y-%m-%d'))
            diff = relativedelta(a, b)
            snapshot_age=diff.years*365+diff.months*30+diff.days
            snapStatus = "%s!%s" %  (resSnap['VolumeId'], snapshot_age)
            snapList.append(snapStatus)

        return snapList

    def cloudwatch(self, instanceid, metric):
        idleusageList=[]
        client = self.boto3client('cloudwatch')
        metricout = client.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName=metric,
                        Dimensions=[
                                {
                                        'Name': 'InstanceId',
                                        'Value': instanceid
                                },
                                ],
                        StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                        EndTime=datetime.datetime.utcnow(),
                        Period=3600,
                        Statistics=['Average']
                        )

        if len(metricout['Datapoints']) > 0:
           metricres = "%s!%s!%s!%s" % (instanceid,metricout['Datapoints'][0]['Timestamp'], metricout['Datapoints'][0]['Average'],metric)
           return metricres
