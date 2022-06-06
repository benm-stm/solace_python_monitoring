# Solace queues stats Plugin

This plugin lets you gather :

-   Queues infos and stats

# operations list
1. Get all queues stats
```
<rpc semp-version="soltr/9_6VMR"><show><queue><name>*</name><flows></flows></queue></show></rpc>
```
2.  get queue owners and link them to spool stats
