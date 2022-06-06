# {'client-username'+':'+'queue-name'+':'+'msg-vpn-name':resultClient.get('client').get("client-username")+':'+qName+':'+msgVpnName}


class CoreClientStats:
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

    def __add__(self, core_client_stats) -> "CoreClientStats":
        core_client_stats_object = CoreClientStats(
            self.client_username, self.queue_name, self.msg_vpn_name
        )
        for attribute_key, attribute_value in self.__dict__.items():
            if attribute_key not in [
                "client_username",
                "queue_name",
                "msg_vpn_name",
            ]:
                setattr(
                    core_client_stats_object,
                    attribute_key,
                    int(attribute_value)
                    + int(getattr(core_client_stats, attribute_key)),
                )
            else:
                setattr(
                    core_client_stats_object, attribute_key, attribute_value
                )
        return core_client_stats_object

    def get_stats_list(self) -> "list[CoreClientStats]":
        stats_list = []
        for stat in self.__dict__.keys():
            if stat not in ["client_username", "queue_name", "msg_vpn_name"]:
                stats_list.append(stat)
        return stats_list


class CoreClientStatsListProcessor:
    def __init__(self, core_client_stats_list) -> None:
        self.core_client_stats_list = core_client_stats_list

    # labels are: username, msg_vpn_name, queue_name
    def group_by_labels(self) -> "dict[list[CoreClientStats]]":
        grouped_core_client_stats_dict = {}
        for core_client_stats in self.core_client_stats_list:
            key = hash(core_client_stats)

            if key not in grouped_core_client_stats_dict:
                grouped_core_client_stats_dict[key] = []
            if core_client_stats is not None:
                grouped_core_client_stats_dict[key].append(core_client_stats)

        return grouped_core_client_stats_dict

    def sum_core_client_stats_with_same_labels(
        self,
    ) -> "list[CoreClientStats]":
        summed_core_client_stats_list = []
        grouped_core_client_stats_dict = self.group_by_labels()

        for core_client_stats_list in grouped_core_client_stats_dict.values():
            core_client_stats_list
            summed_core_client_stats = {}
            client_instances_count = 0
            for core_client_stats in core_client_stats_list:
                if summed_core_client_stats:
                    summed_core_client_stats = (
                        summed_core_client_stats + core_client_stats
                    )
                else:
                    summed_core_client_stats = core_client_stats
                client_instances_count += 1
            setattr(
                summed_core_client_stats,
                "client-instances-count",
                client_instances_count)
            summed_core_client_stats_list.append(summed_core_client_stats)

        return summed_core_client_stats_list
