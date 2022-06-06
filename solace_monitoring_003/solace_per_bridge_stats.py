"""
Local cron Plugin for Solace client side monitoring (bridges statistics)
Author: Digital Backbone - Mohamed Rafik Ben Mansour
Maintaner: Digital BackBone - Mohamed Rafik Ben Mansour
Copyrights/Licensing: Digital Backbone.
"""

# to import utils module
import os

from libs.core_bridge_stats import CoreBridgeStats
from libs.generic import Utils
from libs.solace_client import SolaceClient as SolaceClient
from libs.gcp_monitoring import GcpMonitoring as gcpMonitoring


class SolacePerBridgeStats:
    PLUGIN_NAME = "dbb-monitoring-003"

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

    def bridges_stats_processing(self, bridges_stats):
        core_bridge_stats_processed_list = []
        for bridge_stats in bridges_stats:
            if (
                bridge_stats.get("local-vpn-name")
                not in self.solace_connector.ignored_msg_vpns
            ):
                bridge_stats_core = bridge_stats.copy()
                # make a 1 lvl json
                bridge_stats_core = self.utils.same_lvl_json(
                    bridge_stats_core, dict(), "", ""
                )
                bridge_stats_core = self.utils.json_fields_selector(
                    bridge_stats_core,
                    dict(),
                    self.solace_connector.metrics_selector,
                )
                self.transformPositiveResultToBool(bridge_stats_core)

                core_bridge_stats = CoreBridgeStats(
                    bridge_stats.get("bridge-name"),
                    bridge_stats.get("local-vpn-name"),
                    bridge_stats.get("connected-remote-vpn-name")
                )
                core_bridge_stats.update(bridge_stats_core)
                core_bridge_stats_processed_list.append(core_bridge_stats)
                self.logger.debug(
                    "- for bridge stats %s In msg-vpn %s owned by %s:"
                    % (
                        bridge_stats.get("bridge-name"),
                        bridge_stats.get("local-vpn-name"),
                        bridge_stats.get("connected-remote-vpn-name"),
                    )
                )
        return core_bridge_stats_processed_list

    def transformPositiveResultToBool(self, data):
        for key, value in data.items():
            try:
                float(value)
            except ValueError:
                if data[key].lower() in ["ready-insync", "ready", "up"]:
                    data[key] = 1
                else:
                    data[key] = 0
        return data

    def send_metrics(self, core_bridge_stats_list):

        series = []
        for core_bridge_stats in core_bridge_stats_list:
            for stat in core_bridge_stats.get_stats_list():
                series.append(
                    self.gcp_monitoring.construct_bridge_metrics(
                        core_bridge_stats.bridge_name,
                        core_bridge_stats.local_msg_vpn_name,
                        core_bridge_stats.remote_msg_vpn_name,
                        stat,
                        getattr(core_bridge_stats, stat),
                        self.solace_connector.cluster_name,
                        self.solace_connector.node_name,
                        self.solace_connector.env
                    )
                )
        self.gcp_monitoring.send_metrics(series)

    def run(self, env):
        self.logger.info("Start")
        br_stats = self.solace_connector.get_bridges_details()
        if br_stats:
            br_stats = br_stats.get("bridge")
            if type(br_stats) != list:
                br_stats = [br_stats]
            core_bridge_stats_list = self.bridges_stats_processing(br_stats)
            self.send_metrics(
                core_bridge_stats_list
            )
        return env.split(".")[0] + " - complete"
