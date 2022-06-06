class CoreBridgeStats:
    def __init__(
            self, bridge_name: str, local_msg_vpn_name: str,
            remote_msg_vpn_name: str) -> None:
        self.bridge_name = bridge_name
        self.local_msg_vpn_name = local_msg_vpn_name
        self.remote_msg_vpn_name = remote_msg_vpn_name
        # There are other attributes that will be set with the method update()
        # The added attributes are the diffrent stats of a client

    def update(self, stats: dict) -> None:
        for stat, value in stats.items():
            setattr(self, stat, value)

    def __hash__(self) -> int:
        return hash(self.bridge_name +
                    self.local_msg_vpn_name +
                    self.remote_msg_vpn_name)

    def __add__(self, core_bridge_stats) -> "CoreBridgeStats":
        core_bridge_stats_object = CoreBridgeStats(
            self.bridge_name, self.local_msg_vpn_name,
            self.remote_msg_vpn_name
        )
        for attribute_key, attribute_value in self.__dict__.items():
            if attribute_key not in [
                "bridge_name",
                "local_msg_vpn_name",
                "remote_msg_vpn_name"
            ]:
                setattr(
                    core_bridge_stats_object,
                    attribute_key,
                    int(attribute_value)
                    + int(getattr(core_bridge_stats, attribute_key)),
                )
            else:
                setattr(
                    core_bridge_stats_object, attribute_key, attribute_value
                )
        return core_bridge_stats_object

    def __eq__(self, other) -> bool:
        if (
            self.bridge_name == other.bridge_name
            and self.local_msg_vpn_name == other.local_msg_vpn_name
            and self.remote_msg_vpn_name == other.remote_msg_vpn_name
        ):
            return True
        else:
            return False

    def get_stats_list(self) -> "list[CoreBridgeStats]":
        stats_list = []
        for stat in self.__dict__.keys():
            if stat not in ["bridge_name",
                            "local_msg_vpn_name",
                            "remote_msg_vpn_name"]:
                stats_list.append(stat)
        return stats_list
