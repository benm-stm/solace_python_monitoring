import os

from concurrent.futures import ThreadPoolExecutor, as_completed
from solace_monitoring_001.solace_per_client_stats import SolacePerClientStats

if __name__ == "__main__":
    # iterate on conf files to processe many solaces from the same machine
    conf_dir = "config"
    envs_dir = conf_dir + "/envs"
    common_conf_file = conf_dir + "/common.conf"
    metrics_list_file = conf_dir + "/metrics_list.conf"
    conf_extention = ".conf"

    threads = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for env_conf_file in os.listdir(envs_dir):
            if env_conf_file.endswith(conf_extention):
                solace_per_client_stats = SolacePerClientStats(
                    common_conf_file,
                    os.path.join(envs_dir, env_conf_file),
                    metrics_list_file,
                )
                threads.append(
                    executor.submit(solace_per_client_stats.run, env_conf_file)
                )
        for task in as_completed(threads):
            print(task.result())
