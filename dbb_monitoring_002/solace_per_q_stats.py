"""
Local cron Plugin for Solace client side monitoring
Author: Digital Backbone - Mohamed Rafik Ben Mansour
Maintaner: Digital BackBone - Mohamed Rafik Ben Mansour
Copyrights/Licensing: Digital Backbone.
"""

# to import utils module
import os

from libs.core_queue_stats import CoreQueueStats, CoreQueueStatsListProcessor
from libs.generic import Utils
from libs.solace_client import SolaceClient as SolaceClient
from libs.gcp_monitoring import GcpMonitoring as gcpMonitoring


class SolacePerQStats:
    PLUGIN_NAME = "dbb-monitoring-002"

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

    def qs_flows_processing(self, qs_flows):
        core_queue_stats_list = []
        for q_flows in qs_flows:
            if (
                q_flows.get("info").get("message-vpn")
                not in self.solace_connector.ignored_msg_vpns
            ):
                # remove unimportant elements from q stats
                q_flows_core = q_flows.get("info").copy()

                q_flows_core = self.utils.json_fields_selector(
                    q_flows_core,
                    dict(),
                    self.solace_connector.metrics_selector,
                )
                # sometimes qs don't have an owner
                if q_flows.get("info").get("owner"):
                    core_queue_stats = CoreQueueStats(
                        q_flows.get("info").get("owner"),
                        q_flows.get("name"),
                        q_flows.get("info").get("message-vpn"),
                    )

                    core_queue_stats.update(q_flows_core)
                    core_queue_stats_list.append(core_queue_stats)
                else:
                    core_queue_stats = CoreQueueStats(
                        "N/A",
                        q_flows.get("name"),
                        q_flows.get("info").get("message-vpn"),
                    )
                    core_queue_stats.update(q_flows_core)
                    core_queue_stats_list.append(core_queue_stats)
                    self.logger.debug(
                        "- for queueFlow %s In msg-vpn %s owned by %s:"
                        % (
                            q_flows.get("name"),
                            q_flows.get("info").get("message-vpn"),
                            q_flows.get("info").get("owner"),
                        )
                    )
        return core_queue_stats_list

    def qs_stats_processing(self, qs_stats, core_queue_stats_list):
        core_queue_stats_processed_list = []
        for q_stats in qs_stats:
            if (
                q_stats.get("info").get("message-vpn")
                not in self.solace_connector.ignored_msg_vpns
            ):
                q_stats_core = q_stats.get("stats").copy()
                # make a 1 lvl json
                q_stats_core = self.utils.same_lvl_json(
                    q_stats_core, dict(), "", ""
                )
                q_stats_core = self.utils.json_fields_selector(
                    q_stats_core,
                    dict(),
                    self.solace_connector.metrics_selector,
                )
                core_queue_stats_processor = CoreQueueStatsListProcessor(
                    core_queue_stats_list, self.logger
                )
                client_username = core_queue_stats_processor.get_queue_owner(
                    q_stats.get("name"), q_stats.get("info").get("message-vpn")
                )
                core_queue_stats = CoreQueueStats(
                    client_username,
                    q_stats.get("name"),
                    q_stats.get("info").get("message-vpn"),
                )
                core_queue_stats.update(q_stats_core)
                core_queue_stats_processed_list.append(core_queue_stats)
                self.logger.debug(
                    "- for queue stats %s In msg-vpn %s owned by %s:"
                    % (
                        q_stats.get("name"),
                        q_stats.get("info").get("message-vpn"),
                        q_stats.get("info").get("owner"),
                    )
                )
        return core_queue_stats_processed_list

    def qs_rates_processing(self, qs_rates, core_queue_rates_list):
        core_queue_rates_processed_list = []
        for q_rates in qs_rates:
            if (
                q_rates.get("info").get("message-vpn")
                not in self.solace_connector.ignored_msg_vpns
            ):
                q_rates_core = q_rates.get("rates").get(
                    "qendpt-data-rates").copy()
                # make a 1 lvl json with prefix queue_rates
                # cause we have the same metric in the client stats
                q_rates_core = self.utils.same_lvl_json(
                    q_rates_core, dict(), "", "queue-rates"
                )
                q_rates_core = self.utils.json_fields_selector(
                    q_rates_core,
                    dict(),
                    self.solace_connector.metrics_selector,
                )
                core_queue_rates_processor = CoreQueueStatsListProcessor(
                    core_queue_rates_list, self.logger
                )
                client_username = core_queue_rates_processor.get_queue_owner(
                    q_rates.get("name"), q_rates.get("info").get("message-vpn")
                )
                core_queue_rates = CoreQueueStats(
                    client_username,
                    q_rates.get("name"),
                    q_rates.get("info").get("message-vpn"),
                )
                core_queue_rates.update(q_rates_core)
                core_queue_rates_processed_list.append(core_queue_rates)
                self.logger.debug(
                    "- for queue rates %s In msg-vpn %s owned by %s:"
                    % (
                        q_rates.get("name"),
                        q_rates.get("info").get("message-vpn"),
                        client_username,
                    )
                )
        return core_queue_rates_processed_list

    def send_metrics(self, core_queue_stats_list):

        series = []
        for core_queue_stats in core_queue_stats_list:
            sia, irn = self.utils.get_sia_irn(core_queue_stats.client_username)
            for stat in core_queue_stats.get_stats_list():
                series.append(
                    self.gcp_monitoring.construct_metrics(
                        core_queue_stats.client_username,
                        core_queue_stats.queue_name,
                        core_queue_stats.msg_vpn_name,
                        stat,
                        getattr(core_queue_stats, stat),
                        sia,
                        irn,
                        self.solace_connector.cluster_name,
                        self.solace_connector.node_name,
                        self.solace_connector.env,
                    )
                )
        self.gcp_monitoring.send_metrics(series)

    def run(self, env):
        self.logger.info("Start")
        qs_flows = self.solace_connector.get_qs_flows_data()
        qs_stats = self.solace_connector.get_qs_stats()
        qs_rates = self.solace_connector.get_qs_rates()
        if qs_flows:
            qs_flows = qs_flows.get("queue")
            qs_stats = qs_stats.get("queue")
            qs_rates = qs_rates.get("queue")
            if type(qs_flows) != list:
                qs_flows = [qs_flows]
                qs_stats = [qs_stats]
                qs_rates = [qs_rates]
            core_queue_stats_list = self.qs_flows_processing(qs_flows)
            core_queue_stats_list_processor = CoreQueueStatsListProcessor(
                core_queue_stats_list, self.logger
            )
            self.send_metrics(
                core_queue_stats_list_processor.remove_duplicates()
            )
            core_queue_stats_list_processor = CoreQueueStatsListProcessor(
                self.qs_stats_processing(qs_stats, core_queue_stats_list),
                self.logger,
            )
            self.send_metrics(
                core_queue_stats_list_processor.remove_duplicates()
            )
            core_queue_stats_list_processor = CoreQueueStatsListProcessor(
                self.qs_rates_processing(qs_rates, core_queue_stats_list),
                self.logger,
            )
            self.send_metrics(
                core_queue_stats_list_processor.remove_duplicates()
            )
        return env.split(".")[0] + " - complete"
