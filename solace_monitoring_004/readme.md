# Solace cluster stats Plugin

This plugin lets you gather :

-   Clusters stats

# operations list
1. Get clusters stats
```
<rpc semp-version="soltr/9_9_0VMR"><show><stats><client></client></stats></show></rpc>
```
3.  example xml output

```
      <stats>
        <client>
          <global>
            <stats>
              <total-clients>474</total-clients>
              <total-clients-connected>405</total-clients-connected>
              <total-clients-connected-with-compression>10</total-clients-connected-with-compression>
              <total-clients-connected-with-ssl>394</total-clients-connected-with-ssl>
              <total-clients-connected-service-smf>405</total-clients-connected-service-smf>
              <total-clients-connected-service-web>0</total-clients-connected-service-web>
              <total-clients-connected-service-rest>0</total-clients-connected-service-rest>
              <total-clients-connected-service-mqtt>0</total-clients-connected-service-mqtt>
              <total-client-messages-received>392743499</total-client-messages-received>
              <total-client-messages-sent>406173598</total-client-messages-sent>
              <client-data-messages-received>164156807</client-data-messages-received>
              <client-data-messages-sent>187205609</client-data-messages-sent>
              <client-persistent-messages-received>70545708</client-persistent-messages-received>
              <client-persistent-messages-sent>140096433</client-persistent-messages-sent>
              <client-non-persistent-messages-received>93520112</client-non-persistent-messages-received>
              <client-non-persistent-messages-sent>47100864</client-non-persistent-messages-sent>
              <client-direct-messages-received>90987</client-direct-messages-received>
              <client-direct-messages-sent>8312</client-direct-messages-sent>
              <large-messages-received>0</large-messages-received>
              <dto-messages-received>0</dto-messages-received>
              <client-control-messages-received>228586692</client-control-messages-received>
              <client-control-messages-sent>218967989</client-control-messages-sent>
              <login-msgs-received>6100274</login-msgs-received>
              <login-msgs-sent>6100274</login-msgs-sent>
              <certificate-revocation-check-stats>
                <total>0</total>
                <allowed-valid>0</allowed-valid>
                <allowed-revoked>0</allowed-revoked>
                <allowed-unknown>0</allowed-unknown>
                <denied-unknown>0</denied-unknown>
                <denied-revoked>0</denied-revoked>
              </certificate-revocation-check-stats>
              <denied-duplicate-clients>0</denied-duplicate-clients>
              <denied-authorization-failed>2310489</denied-authorization-failed>
              <denied-client-connect-acl>0</denied-client-connect-acl>
              <update-msgs-received>0</update-msgs-received>
              <update-msgs-sent>0</update-msgs-sent>
              <keepalive-msgs-received>2348682</keepalive-msgs-received>
              <keepalive-msgs-sent>28047044</keepalive-msgs-sent>
              <assured-ctrl-msgs-received>216420225</assured-ctrl-msgs-received>
              <assured-ctrl-msgs-sent>181183823</assured-ctrl-msgs-sent>
              <add-subscription-msgs-received>138</add-subscription-msgs-received>
              <add-subscription-msgs-sent>111</add-subscription-msgs-sent>
              <add-subscription-manager-msgs-received>0</add-subscription-manager-msgs-received>
              <add-subscription-manager-msgs-sent>0</add-subscription-manager-msgs-sent>
              <already-exists-msgs-sent>0</already-exists-msgs-sent>
              <not-enough-space-msgs-sent>0</not-enough-space-msgs-sent>
              <max-exceeded-msgs-sent>0</max-exceeded-msgs-sent>
              <parse-error-on-add-msgs-sent>0</parse-error-on-add-msgs-sent>
              <denied-subscribe-topic-acl>0</denied-subscribe-topic-acl>
              <denied-subscribe-topic-reserved>0</denied-subscribe-topic-reserved>
              <denied-unsubscribe-topic-acl>0</denied-unsubscribe-topic-acl>
              <shared-subscription-permission-denied>0</shared-subscription-permission-denied>
              <denied-subscribe-permission>0</denied-subscribe-permission>
              <subscribe-client-not-found>0</subscribe-client-not-found>
              <subscription-manager-shared-subscription-permission-denied>0</subscription-manager-shared-subscription-permission-denied>
              <remove-subscription-msgs-received>18</remove-subscription-msgs-received>
              <remove-subscription-msgs-sent>18</remove-subscription-msgs-sent>
              <remove-subscription-manager-msgs-received>0</remove-subscription-manager-msgs-received>
              <remove-subscription-manager-msgs-sent>0</remove-subscription-manager-msgs-sent>
              <not-found-msgs-sent>18</not-found-msgs-sent>
              <parse-error-on-remove-msgs-sent>0</parse-error-on-remove-msgs-sent>
              <denied-unsubscribe-permission>0</denied-unsubscribe-permission>
              <unsubscribe-client-not-found>0</unsubscribe-client-not-found>
              <total-client-bytes-received>276970338540</total-client-bytes-received>
              <total-client-bytes-sent>262949191825</total-client-bytes-sent>
              <client-data-bytes-received>260697672043</client-data-bytes-received>
              <client-data-bytes-sent>251666434434</client-data-bytes-sent>
              <client-persistent-bytes-received>108243724853</client-persistent-bytes-received>
              <client-persistent-bytes-sent>175342087809</client-persistent-bytes-sent>
              <client-non-persistent-bytes-received>152305463363</client-non-persistent-bytes-received>
              <client-non-persistent-bytes-sent>76244952780</client-non-persistent-bytes-sent>
              <client-direct-bytes-received>148483827</client-direct-bytes-received>
              <client-direct-bytes-sent>79393845</client-direct-bytes-sent>
              <client-control-bytes-received>16272666497</client-control-bytes-received>
              <client-control-bytes-sent>11282757391</client-control-bytes-sent>
              <ingress-compressed-bytes>2351057335</ingress-compressed-bytes>
              <egress-compressed-bytes>1440519191</egress-compressed-bytes>
              <current-ingress-rate-per-second>52</current-ingress-rate-per-second>
              <current-egress-rate-per-second>51</current-egress-rate-per-second>
              <average-ingress-rate-per-minute>44</average-ingress-rate-per-minute>
              <average-egress-rate-per-minute>44</average-egress-rate-per-minute>
              <current-ingress-byte-rate-per-second>83641</current-ingress-byte-rate-per-second>
              <current-egress-byte-rate-per-second>83583</current-egress-byte-rate-per-second>
              <average-ingress-byte-rate-per-minute>69571</average-ingress-byte-rate-per-minute>
              <average-egress-byte-rate-per-minute>70393</average-egress-byte-rate-per-minute>
              <ingress-discards>
                <total-ingress-discards>14407074</total-ingress-discards>
                <no-subscription-match>0</no-subscription-match>
                <topic-parse-error>0</topic-parse-error>
                <parse-error>0</parse-error>
                <msg-too-big>0</msg-too-big>
                <ttl-exceeded>0</ttl-exceeded>
                <web-parse-error>0</web-parse-error>
                <publish-topic-acl>0</publish-topic-acl>
                <msg-spool-discards>14407074</msg-spool-discards>
                <message-promotion-congestion>0</message-promotion-congestion>
                <message-spool-congestion>0</message-spool-congestion>
              </ingress-discards>
              <egress-discards>
                <total-egress-discards>56941183</total-egress-discards>
                <transmit-congestion>893</transmit-congestion>
                <compression-congestion>0</compression-congestion>
                <message-elided>0</message-elided>
                <ttl-exceeded>0</ttl-exceeded>
                <payload-could-not-be-formatted>0</payload-could-not-be-formatted>
                <message-promotion-congestion>0</message-promotion-congestion>
                <message-spool-congestion>0</message-spool-congestion>
                <client-not-connected>5672</client-not-connected>
                <msg-spool-egress-discards>56934618</msg-spool-egress-discards>
              </egress-discards>
            </stats>
          </global>
        </client>
      </stats>
```

PS: because queues stats and cluster stats are alike in term of name, we chose to prefix cluster stats by <b>cluster-</b>