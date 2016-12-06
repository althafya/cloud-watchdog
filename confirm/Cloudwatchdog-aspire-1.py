import boto3
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
import json
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
        self.region='us-west-2'
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
        client = self.boto3client('ec2')
        ec2_instances_detail = client.describe_instances()
        for respons in ec2_instances_detail['Reservations']:
            print respons['Instances'][0]['InstanceId'], respons['Instances'][0]['State']['Name']
            self.volumeid(respons)

    def volumeid(self, respons):
        for ids in respons['Instances'][0]['BlockDeviceMappings']:
            print ids['Ebs']['VolumeId'], self.ownerid

    def snapshot(self):
        client = self.boto3client('ec2')
        snap_details = client.describe_snapshots(OwnerIds=[self.ownerid])
        for resSnap in snap_details['Snapshots']:
            a = dateutil.parser.parse(datetime.datetime.now().strftime('%Y-%m-%d'))
            b = dateutil.parser.parse(datetime.date.strftime(resSnap['StartTime'],'%Y-%m-%d'))
            diff = relativedelta(a, b)
            snapshot_age=diff.years*365+diff.months*30+diff.days
            snapStatus = "%s!%s" %  (resSnap['VolumeId'], snapshot_age)
            print snapStatus

    def cloudwatch(self, instanceid, metric):
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
        
        metricres = "%s!%s!%s!%s" % (instanceid,metricout['Datapoints'][0]['Timestamp'], metricout['Datapoints'][0]['Average'],metric)
        print metricres

if __name__ == '__main__':
    object=Cloudwatchdog()
    object.totalec2count()
    #object.cloudwatch()
    object.snapshot()
    object.cloudwatch('i-755a7d6d','NetworkIn')
    object.cloudwatch('i-755a7d6d','NetworkOut')



