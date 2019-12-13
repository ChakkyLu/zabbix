import boto3
import datetime
import pytz
import sys


utc_tz = pytz.timezone('UTC')


def getCloudWatchData(r,s,m,st,clid,caid):

    r = 'cn-northwest-1'
    global period
    global start_time
    global end_time

    end_time = datetime.datetime.now(tz=utc_tz)
    start_time = end_time - datetime.timedelta(minutes=5)
    period = 5*60

    # try:
    conn = boto3.client('cloudwatch', region_name=r)
    aws_metric = {
            "metric": m,
            "statistics": st
    }

    cloud_watch_data = ''

    metric_name = aws_metric['metric']
    statistics = aws_metric['statistics']
    results = conn.get_metric_statistics(Namespace='AWS/ElastiCache',
                    MetricName=metric_name,
                    Dimensions=[
                        {
                            "Name": 'CacheClusterId',
                            "Value": clid
                        },
                        {
                            "Name": "CacheNodeId",
                            "Value": caid
                        }
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=period,
                    Statistics=statistics)
    datapoints = results['Datapoints']
    print(datapoints)

    # except:
    #     print("Exception on collecting data")


if __name__ == "__main__":
    args = sys.argv
    metric = args[1]
    clid = args[2]
    caid = '0001'
    getCloudWatchData('cn-northwest-1', 'ElastiCache', metric, ['Average'], clid, caid)
