import boto3
import datetime

def getCloudWatchData(r,s,d):

    r = 'cn-northwest-1'
    global period
    global start_time
    global end_time

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.datetime.timedelta(minutes=5)
    period = 5*60
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = boto3.client('ec2', region_name=r)
        aws_metric = {
            "metric": "BytesUsedForCacheItems",
            "statistics": "Maximum"
        }
        cloud_watch_data = ''

        metric_name = aws_metric['metric']
        statistics = aws_metric['statistics']
        results = conn.get_metric_statistics(period, start_time, end_time, metric_name, statistics)
        print(results)

    except:
        print("YES")


if __name__ == "__main__":
    getCloudWatchData('cn-northwest-1', 'SQS', '')
