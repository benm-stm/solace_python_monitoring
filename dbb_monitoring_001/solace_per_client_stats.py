"""
Local cron Plugin for Solace client side monitoring
Author: Digital Backbone - Mohamed Rafik Ben Mansour
Maintaner: Digital BackBone - Mohamed Rafik Ben Mansour
Copyrights/Licensing: Digital Backbone.
"""

import os

from libs.core_client_stats import (
    CoreClientStats,
    CoreClientStatsListProcessor,
)
from libs.generic import Utils
from libs.solace_client import SolaceClient as solaceClient
from libs.gcp_monitoring import GcpMonitoring as gcpMonitoring


class SolacePerClientStats:

    PLUGIN_NAME = "dbb-monitoring-001"

    def __init__(
        self, common_conf_path, node_conf_path, metrics_list_file
    ) -> None:
        # Read .env config file
        self.utils = Utils()
        self.config = self.utils.get_conf(node_conf_path)
        self.config.update(self.utils.get_conf(common_conf_path))
        self.metrics_list = self.utils.file_lines_to_array(metrics_list_file)

        # Init logger
        instance_name = os.path.splitext(os.path.basename(node_conf_path))[0]
        self.logger = self.utils.set_logger(
            self.config["log_lvl"], self.PLUGIN_NAME + ":" + instance_name
        )

        self.solace_connector = solaceClient(
            self.config, self.metrics_list, self.logger
        )
        self.gcp_monitoring = gcpMonitoring(self.config, self.logger)

    def get_qslist(self) -> "list[dict]":
        result_q = self.solace_connector.get_qs_flows_data()
        if result_q:
            return result_q.get("queue")
        else:
            return None

    def get_core_client_stats(
        self, client, queue_name, msg_vpn_name
    ) -> "CoreClientStats":
        client_username = client.get("client-username")

        if client_username not in self.solace_connector.ignored_clients:
            client_stats = client.get("stats")
            flat_client_stats = self.utils.same_lvl_json(
                client_stats, dict(), "", ""
            )
            filtered_flat_client_stats = self.utils.json_fields_selector(
                flat_client_stats,
                dict(),
                self.solace_connector.metrics_selector,
            )
            core_client_stats = CoreClientStats(
                client_username, queue_name, msg_vpn_name
            )
            core_client_stats.update(filtered_flat_client_stats)
            return core_client_stats

    def clients_linked_to_q_processing(
        self, queue, client_name_list
    ) -> "list[CoreClientStats]":
        # i used the exception block cause sometimes the returned json
        # don't have the client block in it, so it spawns an error
        core_client_stats_list = []
        try:
            # 1st case : many clients on the Q
            if int(queue.get("info").get("clients").get("count")) > 1:
                clients = queue.get("info").get("clients").get("client")
                for client in clients:
                    client_name_list.append(client.get("name"))
                    client = self.solace_connector.get_per_client_raw_data(
                        client.get("name")
                    ).get("client")
                    core_client_stats = self.get_core_client_stats(
                        client,
                        queue.get("name"),
                        queue.get("info").get("message-vpn"),
                    )
                    if core_client_stats is not None:
                        core_client_stats_list.append(core_client_stats)
            # 2nd case : 1 client on the Q
            elif int(queue.get("info").get("clients").get("count")) == 1:
                # get client by name from solace.
                # this client contains the username
                client = self.solace_connector.get_per_client_raw_data(
                    queue.get("info").get("clients").get("client").get("name")
                ).get("client")
                core_client_stats = self.get_core_client_stats(
                    client,
                    queue.get("name"),
                    queue.get("info").get("message-vpn"),
                )

                if core_client_stats is not None:
                    core_client_stats_list.append(core_client_stats)
                    client_name_list.append(
                        queue.get("info")
                        .get("clients")
                        .get("client")
                        .get("name")
                    )
        except AttributeError as e:
            self.logger.debug(e)
        return core_client_stats_list

    def clients_non_linked_to_q_processing(
        self, clients, consumer_client_name_list
    ):
        core_client_stats_list = []
        if clients:
            clients = list(clients.get("client"))
            for client in clients:
                if client.get("name") not in consumer_client_name_list:
                    core_client_stats = self.get_core_client_stats(
                        client, "N/A", client.get("message-vpn")
                    )
                    if core_client_stats is not None:
                        core_client_stats_list.append(core_client_stats)
        return core_client_stats_list

    def send_metrics(self, core_client_stats_list):
        series = []
        for core_client_stats in core_client_stats_list:
            sia, irn = self.utils.get_sia_irn(
                core_client_stats.client_username
            )
            for stat in core_client_stats.get_stats_list():
                series.append(
                    self.gcp_monitoring.construct_metrics(
                        core_client_stats.client_username,
                        core_client_stats.queue_name,
                        core_client_stats.msg_vpn_name,
                        stat,
                        getattr(core_client_stats, stat),
                        sia,
                        irn,
                        self.solace_connector.cluster_name,
                        self.solace_connector.node_name,
                        self.solace_connector.env,
                    )
                )
        self.gcp_monitoring.send_metrics(series)

    def run(self, env):
        clients_arr = (
            []
        )  # list used to remove already processed clients linked to queue
        per_client_q_and_vpn_stats_summed = []

        qslist = self.get_qslist()
        if qslist:
            if type(qslist) != list:
                list(qslist)
            for q_stats in qslist:
                client_linked_to_q_stats = self.clients_linked_to_q_processing(
                    q_stats, clients_arr
                )

                if client_linked_to_q_stats:
                    per_client_q_and_vpn_stats_summed += client_linked_to_q_stats

            consumers_core_client_stats_list = CoreClientStatsListProcessor(
                per_client_q_and_vpn_stats_summed
            ).sum_core_client_stats_with_same_labels()

            consumer_client_name_list = [
                i
                for n, i in enumerate(clients_arr)
                if i not in clients_arr[n + 1:]
            ]

            self.send_metrics(consumers_core_client_stats_list)

            # Get all client stats
            clients = self.solace_connector.get_per_client_raw_data("*")
            # remove already processed clients who are linked to a queue
            publishers_core_client_stats_list = (
                self.clients_non_linked_to_q_processing(
                    clients, consumer_client_name_list
                )
            )

            publishers_core_client_stats_list = CoreClientStatsListProcessor(
                publishers_core_client_stats_list
            ).sum_core_client_stats_with_same_labels()

            self.send_metrics(publishers_core_client_stats_list)
        return env.split(".")[0] + " - complete"
