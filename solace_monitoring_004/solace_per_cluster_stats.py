"""
Local cron Plugin for Solace client side monitoring (clusters statistics)
Author: Digital Backbone - Mohamed Rafik Ben Mansour
Maintaner: Digital BackBone - Mohamed Rafik Ben Mansour
Copyrights/Licensing: Digital Backbone.
"""

# to import utils module
import os

from libs.core_cluster_stats import CoreClusterStats
from libs.generic import Utils
from libs.solace_client import SolaceClient as SolaceClient
from libs.gcp_monitoring import GcpMonitoring as gcpMonitoring


class SolacePerClusterStats:
    PLUGIN_NAME = "dbb-monitoring-004"

    def __init__(self, common_conf_file, env_conf_file, metrics_list_file):
        # Read config file
        self.utils = Utils()
        self.config = self.utils.get_conf(env_conf_file)
        self.config.update(self.utils.get_conf(common_conf_file))
        self.metrics_list = self.utils.file_lines_to_array(metrics_list_file)

        # Init logger
        instance_name = os.path.splitext(os.path.basename(env_conf_file))[0]
        self.logger = self.utils.set_logger(
            self.config["log_lvl"], self.PLUGIN_NAME + ":" + instance_name
        )

        self.solace_connector = SolaceClient(
            self.config, self.metrics_list, self.logger
        )
        self.gcp_monitoring = gcpMonitoring(self.config, self.logger)

    def cluster_stats_processing(self, cluster_stats):
        # make a 1 lvl json
        cluster_stats_core = self.utils.same_lvl_json(
            cluster_stats, dict(), "", "cluster"
        )
        cluster_stats = self.utils.json_fields_selector(
            cluster_stats_core,
            dict(),
            self.solace_connector.metrics_selector,
        )
        core_cluster_stats = CoreClusterStats(
            self.solace_connector.cluster_name
        )
        core_cluster_stats.update(cluster_stats)
        return core_cluster_stats

    def send_metrics(self, core_cluster_stats):
        series = []
        for stat in core_cluster_stats.get_stats_list():
            series.append(
                self.gcp_monitoring.construct_cluster_metrics(
                    stat,
                    getattr(core_cluster_stats, stat),
                    self.solace_connector.cluster_name,
                    self.solace_connector.node_name,
                    self.solace_connector.env
                )
            )
        self.gcp_monitoring.send_metrics(series)

    def run(self, env):
        self.logger.info("Start")
        cluster_stats = self.solace_connector.get_cluster_stats()
        if cluster_stats:
            cluster_stats = cluster_stats.get("stats")
            cluster_stats['health'] = '1'
            core_cluster_stats = self.cluster_stats_processing(
                                        cluster_stats)
        else:
            core_cluster_stats = CoreClusterStats(
                self.solace_connector.cluster_name
            )
            cluster_stats['cluster-health'] = '0'
            core_cluster_stats.update(cluster_stats)

        self.logger.debug(
            "- for cluster stats %s %s : %s"
            % (
                self.solace_connector.cluster_name,
                self.solace_connector.env,
                core_cluster_stats.__dict__
            )
        )
        self.send_metrics(
            core_cluster_stats
        )
        return env.split(".")[0] + " - complete"
