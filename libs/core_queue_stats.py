# {'client-username'+':'+'queue-name'+':'+'msg-vpn-name':resultClient.get('client').get("client-username")+':'+qName+':'+msgVpnName}


class CoreQueueStats:
    def __init__(
        self, client_username: str, queue_name: str, msg_vpn_name: str
    ) -> None:
        self.client_username = client_username
        self.queue_name = queue_name
        self.msg_vpn_name = msg_vpn_name
        # There are other attributes that will be set with the method update()
        # The added attributes are the diffrent stats of a client

    def update(self, stats: dict) -> None:
        for stat, value in stats.items():
            setattr(self, stat, value)

    def __hash__(self) -> int:
        return hash(self.client_username + self.queue_name + self.msg_vpn_name)

    def __add__(self, core_queue_stats) -> "CoreQueueStats":
        core_queue_stats_object = CoreQueueStats(
            self.client_username, self.queue_name, self.msg_vpn_name
        )
        for attribute_key, attribute_value in self.__dict__.items():
            if attribute_key not in [
                "client_username",
                "queue_name",
                "msg_vpn_name",
            ]:
                setattr(
                    core_queue_stats_object,
                    attribute_key,
                    int(attribute_value)
                    + int(getattr(core_queue_stats, attribute_key)),
                )
            else:
                setattr(
                    core_queue_stats_object, attribute_key, attribute_value
                )
        return core_queue_stats_object

    def __eq__(self, other) -> bool:
        if (
            self.client_username == other.client_username
            and self.queue_name == other.queue_name
            and self.msg_vpn_name == other.msg_vpn_name
        ):
            return True
        else:
            return False

    def get_stats_list(self) -> "list[CoreQueueStats]":
        stats_list = []
        for stat in self.__dict__.keys():
            if stat not in ["client_username", "queue_name", "msg_vpn_name"]:
                stats_list.append(stat)
        return stats_list


class CoreQueueStatsListProcessor:
    def __init__(self, core_queue_stats_list, logger) -> None:
        self.core_queue_stats_list = core_queue_stats_list
        self.logger = logger

    # labels are: username, msg_vpn_name, queue_name
    def group_by_labels(self) -> "dict[list[CoreQueueStats]]":
        grouped_core_queue_stats_dict = {}
        for core_queue_stats in self.core_queue_stats_list:
            key = hash(core_queue_stats)
            if key not in grouped_core_queue_stats_dict:
                grouped_core_queue_stats_dict[key] = []
            if core_queue_stats is not None:
                grouped_core_queue_stats_dict[key].append(core_queue_stats)

        return grouped_core_queue_stats_dict

    def sum_core_queue_stats_with_same_labels(self) -> "list[CoreQueueStats]":
        summed_core_queue_stats_list = []
        summed_core_queue_stats = {}
        grouped_core_queue_stats_dict = self.group_by_labels()

        for core_queue_stats_list in grouped_core_queue_stats_dict.values():
            for core_queue_stats in core_queue_stats_list:
                if summed_core_queue_stats:
                    summed_core_queue_stats += core_queue_stats
                else:
                    summed_core_queue_stats = core_queue_stats
            summed_core_queue_stats_list.append(summed_core_queue_stats)
        return summed_core_queue_stats_list

    def get_queue_owner(self, queue_name, msg_vpn_name) -> str:
        for core_queue_stats in self.core_queue_stats_list:
            if (
                core_queue_stats.queue_name == queue_name
                and core_queue_stats.msg_vpn_name == msg_vpn_name
            ):
                return core_queue_stats.client_username

    def remove_duplicates(self):
        # if two CoreQueueStats objects have the same queue_name
        # (This a solace bug)
        # Client creates queue when consuming
        # This queue gets same name as an existing one
        # if It has a white space at the end
        core_queue_stats_set = set(self.core_queue_stats_list)
        if len(self.core_queue_stats_list) != len(core_queue_stats_set):
            self.logger.warn("There are queues with same name")
        return core_queue_stats_set
