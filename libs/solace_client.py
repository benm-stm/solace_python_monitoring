import requests
import xmltodict
import json


class SolaceClient:
    MSG_VPN_ENDPOINT = "/SEMP/v2/monitor/msgVpns?select=msgVpnName"
    MSG_VPN_STATS_RPC_BODY = '<rpc semp-version="soltr/9_2_0VMR"><show><message-vpn> \
        <vpn-name>toBeModified</vpn-name><stats></stats></message-vpn> \
        </show></rpc>'
    MSG_VPN_SPOOL_STATS_RPC_BODY = '<rpc semp-version="soltr/9_5VMR"><show><message-spool> \
        <vpn-name>toBeModified</vpn-name><stats></stats></message-spool> \
        </show></rpc>'
    BRIDGE_DETAILS_RPC_BODY = '<rpc semp-version="soltr/9_2_0VMR"><show><bridge> \
        <bridge-name-pattern>*</bridge-name-pattern><detail></detail> \
        </bridge></show></rpc>'

    """ BRIDGE_STATS_RPC_BODY = '<rpc semp-version="soltr/9_2_0VMR"><show>
     <bridge><bridge-name-pattern>toBeModified</bridge-name-pattern> \
     <stats></stats></bridge></show></rpc>'
    """
    """ BRIDGE_ENDPOINT = (
        "/SEMP/v2/monitor/msgVpns/{msgVpnName}/bridges?select=bridgeName"
     )"""
    """ BRIDGE_STATUS_ENDPOINT_TEMPLATE = \
     "/SEMP/v2/monitor/msgVpns/{msgVpnName}/bridges/{bridgeName},auto?select=inboundState,outboundState"
    """

    CLIENT_STATS_RPC_BODY = '<rpc semp-version="soltr/9_6VMR"><show><client><name>toBeModified</name> \
                            <stats></stats></client></show></rpc>'
    QUEUE_FLOW_STATS_RPC_BODY = '<rpc semp-version="soltr/9_2VMR"><show><queue><name>*</name> \
                                <flows></flows></queue></show></rpc>'
    QUEUE_INFOS_RPC_BODY = '<rpc semp-version="soltr/9_2VMR"><show><queue><name>toBeModified</name> \
                            </queue></show></rpc>'
    QUEUE_STATS_RPC_BODY = '<rpc semp-version="soltr/9_6VMR"><show><queue><name>*</name> \
                            <stats></stats></queue></show></rpc>'
    QUEUE_RATES_RPC_BODY = '<rpc semp-version="soltr/9_6VMR"><show><queue><name>*</name> \
                            <rates></rates></queue></show></rpc>'
    CLUSTER_STATS_RPC_BODY = '<rpc semp-version="soltr/9_9_0VMR"><show><stats><client></client> \
                            </stats></show></rpc>'

    def __init__(self, config, metrics_list, logger):
        if config["solace_api_port"]:
            self.url = config["solace_url"] + ":" + config["solace_api_port"]
        else:
            self.url = config["solace_url"]
        self.username = config["solace_username"]
        self.password = config["solace_password"]
        self.health_check_url = (
            config["solace_url"]
            + ":"
            + str(config["solace_health_check_port"])
        )
        self.ignored_msg_vpns = config["solace_ignored_msgvpns"].split(",")
        self.ignored_clients = config["solace_ignored_clients"]
        self.ignored_msg_vpns = config["solace_ignored_msgvpns"]
        self.cluster_name = config["solace_cluster_name"]
        self.node_name = config["solace_node_name"]
        self.env = config["solace_env"]
        self.metrics_selector = metrics_list
        self.logger = logger

    def get_per_client_raw_data(self, client):
        # replace client name
        endpoint = self.url + "/SEMP"
        body_template = SolaceClient.CLIENT_STATS_RPC_BODY
        body = body_template.replace("toBeModified", client)

        # issue an XMLRPC call to solace to get msgVpn stats
        response = requests.post(
            endpoint,
            verify=False,
            auth=(self.username, self.password),
            data=body,
            headers={"Content-Type": "application/xml"},
        )
        response = json.loads(
            json.dumps(
                xmltodict.parse(response.text)
                .get("rpc-reply")
                .get("rpc")
                .get("show")
                .get("client")
            )
        )
        if response:
            if response.get("primary-virtual-router") is not None:
                return response.get("primary-virtual-router")
            elif response.get("backup-virtual-router") is not None:
                return response.get("backup-virtual-router")
            elif response.get("internal-virtual-router") is not None:
                return response.get("internal-virtual-router")
        else:
            return None

    def get_qs_stats(self):
        endpoint = self.url + "/SEMP"
        body = SolaceClient.QUEUE_STATS_RPC_BODY

        try:
            response = requests.post(
                endpoint,
                verify=False,
                auth=(self.username, self.password),
                data=body,
                headers={"Content-Type": "application/xml"},
            )

            json_response = json.loads(
                json.dumps(
                    xmltodict.parse(response.text)
                    .get("rpc-reply")
                    .get("rpc")
                    .get("show")
                    .get("queue")
                    .get("queues")
                )
            )
            return json_response
        except BaseException as err:
            self.logger.error("%s, response content : %s" %
                              (err, response.text))
            return None

    def get_qs_rates(self):
        endpoint = self.url + "/SEMP"
        body = SolaceClient.QUEUE_RATES_RPC_BODY

        try:
            response = requests.post(
                endpoint,
                verify=False,
                auth=(self.username, self.password),
                data=body,
                headers={"Content-Type": "application/xml"},
            )

            json_response = json.loads(
                json.dumps(
                    xmltodict.parse(response.text)
                    .get("rpc-reply")
                    .get("rpc")
                    .get("show")
                    .get("queue")
                    .get("queues")
                )
            )
            return json_response
        except BaseException as err:
            self.logger.error("%s, response content : %s" %
                              (err, response.text))
            return None

    def get_qs_flows_data(self):
        endpoint = self.url + "/SEMP"
        body = SolaceClient.QUEUE_FLOW_STATS_RPC_BODY

        try:
            response = requests.post(
                endpoint,
                verify=False,
                auth=(self.username, self.password),
                data=body,
                headers={"Content-Type": "application/xml"},
            )

            json_response = json.loads(
                json.dumps(
                    xmltodict.parse(response.text)
                    .get("rpc-reply")
                    .get("rpc")
                    .get("show")
                    .get("queue")
                    .get("queues")
                )
            )
            return json_response
        except BaseException as err:
            self.logger.error("%s, response content : %s" %
                              (err, response.text))
            return None

    def get_q_info(self, msg_vpn_name, q_name, field):
        endpoint = (
            self.url
            + "/SEMP/v2/config/msgVpns/"
            + msg_vpn_name
            + "/queues/"
            + q_name
            + "?select="
            + field
        )
        response = requests.get(
            endpoint,
            verify=False,
            auth=(self.username, self.password),
            headers={"Content-Type": "application/xml"},
        )
        if json.loads(response.content.decode()).get("data"):
            return json.loads(response.content.decode()).get("data").get(field)

    def get_bridges_details(self):
        endpoint = self.url + "/SEMP"
        body = SolaceClient.BRIDGE_DETAILS_RPC_BODY

        try:
            response = requests.post(
                endpoint,
                verify=False,
                auth=(self.username, self.password),
                data=body,
                headers={"Content-Type": "application/xml"},
            )

            json_response = json.loads(
                json.dumps(
                    xmltodict.parse(response.text)
                    .get("rpc-reply")
                    .get("rpc")
                    .get("show")
                    .get("bridge")
                    .get("bridges")
                )
            )
            return json_response
        except BaseException as err:
            self.logger.error("%s, response content : %s" %
                              (err, response.text))
            return None

    def get_cluster_stats(self):
        endpoint = self.url + "/SEMP"
        body = SolaceClient.CLUSTER_STATS_RPC_BODY
        try:
            response = requests.post(
                endpoint,
                verify=False,
                auth=(self.username, self.password),
                data=body,
                headers={"Content-Type": "application/xml"},
            )

            json_response = json.loads(
                json.dumps(
                    xmltodict.parse(response.text)
                    .get("rpc-reply")
                    .get("rpc")
                    .get("show")
                    .get("stats")
                    .get("client")
                    .get("global")
                )
            )
            return json_response
        except BaseException as err:
            self.logger.error("%s" % err)
            return {}
