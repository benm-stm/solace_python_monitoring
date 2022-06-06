class CoreClusterStats:
    def __init__(self, cluster_name: str) -> None:
        self.cluster_name = cluster_name
        # There are other attributes that will be set with the method update()
        # The added attributes are the diffrent stats of a client

    def update(self, stats: dict) -> None:
        for stat, value in stats.items():
            setattr(self, stat, value)

    def __add__(self, core_cluster_stats) -> "CoreClusterStats":
        core_cluster_stats_object = CoreClusterStats(self.cluster_name)
        for attribute_key, attribute_value in self.__dict__.items():
            setattr(
                core_cluster_stats_object,
                attribute_key,
                int(attribute_value)
            )
        return core_cluster_stats_object

    def get_stats_list(self) -> "list[CoreClusterStats]":
        stats_list = []
        for stat in self.__dict__.keys():
            if stat not in ["cluster_name"]:
                stats_list.append(stat)
        return stats_list
