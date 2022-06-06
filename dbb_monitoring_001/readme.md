# Solace client instances monitoring Plugin

This plugin lets you gather :

-   Clients instances stats in solace :
     - Stats related to queues (clients instances consuming)
     - Stats not related to queues

# operations list
1. Get all queues stats
```
<rpc semp-version="soltr/9_6VMR"><show><queue><name>*</name><flows></flows></queue></show></rpc>
```

2. get all clients stats present in the queue's egress flow:

3. Get the rest of the clients and flag the queue label to **N/A**
