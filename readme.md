# DBB Client Monitoring
These plugins lets you gather metrics from solace event broker and export them to gcp cloud monitoring

## Plugin Names explanation
| Plugin code  | plugin name  |
|---|---|
|  dbb-monitoring-001  |  client instances metrics |
|  dbb-monitoring-002  |  queues metrics |
## Development Requirements
install python 3
install gcc-c++ python3-devel
## Get and Test the monitoring plugins locally
You need a solace install on your local machine to test the monitoring plugins.
```
docker run -e TZ=Europe/Paris -d -p 8080:8080 -p 5550:5550 -p 1883:1883 -p 5672:5672 -p 55555:55555 --shm-size=2g --env username_admin_globalaccesslevel=admin --env username_admin_password=admin --name=solace solace/solace-pubsub-standard
```
## Install pip modules
- Install required python modules for both plugins (1 requirements file cause they share the same libs)
```
pip3 install -r requirements.txt
```

## Configuration
### Common config
Rename config/common.example into config/common.conf and change the parameters suited to your need
```
mv config/common.example config/common.conf
$ cat config/common.conf
# Solace filters
solace_ignored_msgvpns: "default,#config-sync"
solace_ignored_clients: "#client-username,#config-sync"

# logging conf
log_lvl: info

# Gcp monitoring exporter
cloud_monitoring_project: ********
cloud_monitoring_credentials_path: ../service-account-file.json
# monitoring series type must contain {env} so it will be replaced by the corresponding env
cloud_monitoring_series_metric_type: dbb/monitoring/int
```
PS: don't forget to create a service account in gcp which have the write privileges on the specified project
### Metrics list config
Rename config/metrics_list.example into config/metrics_list.conf and change the metrics suited to your need
```
$ cat config/metrics_list.conf
# client and queues stats
# empty lines and comments lines starting by '#' are permitted
total-egress-discards
total-ingress-discards
client-data-messages-received
```
### Environments
Rename config/envs/env.example into {env-name}.conf and change the parameters suited with your env

ps: {env-name} will be used like a logging source so choose wisely
```
$ mv envs/env.example envs/gcp-int.conf
$ cat envs/gcp-int.conf

```

## Run your solace plugins
Run your python scripts locally
```
$ cd dbb-monitoring-001 && python solace_per_client_stats.py
$ cd dbb-monitoring-002 && python solace_per_q_stats.py
```

