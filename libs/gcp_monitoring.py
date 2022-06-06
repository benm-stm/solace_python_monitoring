from google.cloud import monitoring_v3
import time
import os


class GcpMonitoring:
    def __init__(self, config, logger):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config[
            "cloud_monitoring_credentials_path"
        ]
        self.project_name = config["cloud_monitoring_project"]
        self.series_metric_type = config["cloud_monitoring_series_metric_type"]
        self.logger = logger

    def construct_metrics(
        self,
        client_username,
        queue_name,
        msg_vpn_name,
        metric_name,
        metric_value,
        sia,
        irn,
        cluster_name,
        node_name,
        env,
    ):

        series = monitoring_v3.TimeSeries()
        series.metric.type = (
            "custom.googleapis.com/"
            + self.series_metric_type
            + "/"
            + metric_name
        )
        # global cause we need our identifier to be only project_id
        series.resource.type = "global"

        series.metric.labels["irn"] = irn
        series.metric.labels["sia"] = sia
        series.metric.labels["msg_vpn_name"] = msg_vpn_name
        series.metric.labels["cluster_name"] = cluster_name
        series.metric.labels["node_name"] = node_name
        series.metric.labels["client_user_name"] = client_username
        series.metric.labels["queue_name"] = queue_name
        series.metric.labels["env"] = env

        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        interval = monitoring_v3.TimeInterval(
            {"end_time": {"seconds": seconds, "nanos": nanos}}
        )
        point = monitoring_v3.Point(
            {
                "interval": interval,
                "value": {"double_value": float(metric_value)},
            }
        )
        series.points = [point]
        return series

    def construct_bridge_metrics(
        self,
        bridge_name,
        local_msg_vpn_name,
        remote_msg_vpn_name,
        metric_name,
        metric_value,
        cluster_name,
        node_name,
        env,
    ):

        series = monitoring_v3.TimeSeries()
        series.metric.type = (
            "custom.googleapis.com/"
            + self.series_metric_type
            + "/"
            + metric_name
        )
        # global cause we need our identifier to be only project_id
        series.resource.type = "global"

        series.metric.labels["bridge_name"] = bridge_name
        series.metric.labels["local_msg_vpn_name"] = local_msg_vpn_name
        series.metric.labels["remote_msg_vpn_name"] = remote_msg_vpn_name
        series.metric.labels["cluster_name"] = cluster_name
        series.metric.labels["node_name"] = node_name
        series.metric.labels["env"] = env

        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        interval = monitoring_v3.TimeInterval(
            {"end_time": {"seconds": seconds, "nanos": nanos}}
        )
        point = monitoring_v3.Point(
            {
                "interval": interval,
                "value": {"double_value": float(metric_value)},
            }
        )
        series.points = [point]
        return series

    def construct_cluster_metrics(
        self,
        metric_name,
        metric_value,
        cluster_name,
        node_name,
        env,
    ):

        series = monitoring_v3.TimeSeries()
        series.metric.type = (
            "custom.googleapis.com/"
            + self.series_metric_type
            + "/"
            + metric_name
        )
        # global cause we need our identifier to be only project_id
        series.resource.type = "global"

        series.metric.labels["cluster_name"] = cluster_name
        series.metric.labels["node_name"] = node_name
        series.metric.labels["env"] = env

        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        interval = monitoring_v3.TimeInterval(
            {"end_time": {"seconds": seconds, "nanos": nanos}}
        )
        point = monitoring_v3.Point(
            {
                "interval": interval,
                "value": {"double_value": float(metric_value)},
            }
        )
        series.points = [point]
        return series

    def send_metrics(self, series):
        project = self.project_name
        project_name = f"projects/{project}"
        client = monitoring_v3.MetricServiceClient()

        self.logger.info("%s Timeseries will be written" % len(series))
        # A maximum of 200 TimeSeries can be written in a single request.
        for first_two_h_series in self.chunks(series, 199):
            client.create_time_series(
                request={
                    "name": project_name,
                    "time_series": first_two_h_series,
                }
            )
            self.logger.info("Successfully wrote time series.")

    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i: i + n]
