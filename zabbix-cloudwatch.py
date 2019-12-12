import boto3
import datetime

def getCloudWatchData(r,s,d):

    r = 'cn-northwest-1'
    global period
    global start_time
    global end_time

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(minutes=5)
    # end_time = datetime.datetime(2019,11,29,15,5,0)
    # start_time = datetime.datetime(2019,11,29,15,0,0)
    period = 5*60
    # end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    # start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

    # try:
    conn = boto3.client('cloudwatch', region_name=r)
    aws_metric = {
            "metric":"CPUUtilization",
            "statistics": ["Average"]
    }

    cloud_watch_data = ''

    metric_name = aws_metric['metric']
    statistics = aws_metric['statistics']
    results = conn.get_metric_statistics(Namespace='AWS/EC',
                    MetricName=metric_name,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=period,
                    Statistics=statistics)
    print(results)

    # except:
    #     print("YES")


if __name__ == "__main__":
    getCloudWatchData('cn-northwest-1', 'SQS', '')
