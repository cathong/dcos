Please follow the [`CHANGES.md` modification guidelines](https://github.com/dcos/dcos/wiki/CHANGES.md-guidelines). Thank you!


## DC/OS 2.1.0-beta2 (in development)


### What's new

* Upgrade coreOS AMIs (D2IQ-64271)
* Added a new configuration option `mesos_http_executors_domain_sockets`, which will cause the mesos-agent to use
  domain sockets when communicating with executors. While this change should not have any visible impact on users
  in itself, it does enable administrators to write firewall rules blocking unauthorized access to the agent port
  5051 since access to this will not be required anymore for executors to work.

* Switched from Oracle Java 8 to OpenJDK 8 (DCOS-54902)

* Updated DC/OS UI to [v5.0.0](https://github.com/dcos/dcos-ui/releases/tag/v5.0.0).

* The configuration option `MARATHON_ACCEPTED_RESOURCE_ROLES_DEFAULT_BEHAVIOR` replaces the config option `MARATHON_DEFAULT_ACCEPTED_RESOURCE_ROLES`. Please see the Marathon [command-line flag documentation](https://github.com/mesosphere/marathon/blob/master/docs/docs/command-line-flags.md) for a description of the flag.

* Updated to Mesos [1.10.0-dev](https://github.com/apache/mesos/blob/e6b15b1e968649c794d67bb97961e8f0216e2ed8/CHANGELOG)

* Mesos overlay networking: support dropping agents from the state. (DCOS_OSS-5536)

* Update CNI to 0.7.6

* Updated to Boost 1.65.0 (DCOS_OSS-5555)

* Admin Router: Accept nil task list from Marathon when updating cache. (DCOS_OSS-5541)

* Marathon pod instances are now included in the DC/OS diagnostic bundle (DCOS_OSS-5616)

* Replace [docker-gc](https://github.com/spotify/docker-gc) with `docker system prune`. (DCOS_OSS-5441)

* Port the Mesos Fluent Bit container logger module to Windows. (DCOS-58622)

* Port the Mesos open source metrics module to Windows. (DCOS-58008)

* Add etcd into DC/OS. (DCOS-59004)

* Add etcd metrics into the DC/OS Telegraf Pipeline. (D2IQ-61004)

* Update libpq to 9.6.15 (DCOS-59145)

* Enable proxing of gRPC requests through Admin Router (DCOS-59091)

* Calico in DC/OS: introduced Calico networking into DC/OS, and provided network policy support (DCOS-58413)

* The config option `calico_network_cidr` can be set to a valid IPv4 CIDR range for Calico networks to use (default 172.29.0.0/16) (DCOS-60734)

* Updated DC/OS UI to [master+v2.154.16](https://github.com/dcos/dcos-ui/releases/tag/master+v2.154.16).

* Calico network: When using the Universal Runtime Engine, the contents of the `DCOS_SPACE`  network label will be compressed to `<7-char hash>...<last 53 chars>` if it is longer than 63 characters. (D2IQ-62219)

#### Update Marathon to 1.10.6

* Adds support for Mesos Resource Limits (D2IQ-61131) (D2IQ-61130)
* Removes `revive_offers_for_new_apps` option.

### Breaking changes

* Remove the octarine package from DC/OS. It was originally used as a proxy for the CLI but is not used for this purpose, anymore.

* DC/OS Net: wait till agents become active before fanning out Mesos tasks. (DCOS_OSS-5463)

* Remove the avro-cpp package from DC/OS. It was originally used as part of the metrics-collection framework which now relies on a different infrastructure.

* Remove the spartan package from DC/OS. Is was deprecated in 1.11 and replaced by dcos-net.

* Remove the toybox package from DC/OS. Is was used only by Spartan.

* Remove the dcos-history-service from DC/OS. (DCOS-58529)

* New format for Admin Router access logs. (D2IQ-43957, DCOS-59598, D2IQ-62839)

* Update OpenResty to 1.15.8.3. (DCOS-61159, D2IQ-66506)

### Marathon

* Marathon no longer sanitizes the field `"acceptedResourceRoles"`. The field is an array of one or two values: `*` and the service role. Previously, when an invalid value was provided, Marathon would silently drop it. Now, it returns an error. If this causes a disruption, you can re-enable this feature by adding `MARATHON_DEPRECATED_FEATURES=sanitize_accepted_resource_roles` to the file `/var/lib/dcos/marathon/environment` on all masters. You must remove this line before upgrading to DC/OS 2.2.

### Fixed and improved

* Reserve all agent VTEP IPs upon recovering from replicated log. (DCOS_OSS-5626)

* Set network interfaces as unmanaged for networkd only on coreos. (DCOS-60956)
* Allow Admin Router to accept files up to 32GB, such as for uploading large packages to Package Registry. (DCOS-61233)
* Update Kazoo to version 2.6.1. (DCOS-63065)

* Updated dcos-config.yaml to support some Mesos Flags. (DCOS-59021)

* Fix Telegraf migration when no containers present. (D2IQ-64507)

* Update OpenSSL to 1.1.1f. (D2IQ-65604, D2IQ-66526)

#### Update Marathon to 1.10.6

* Marathon updated to 1.9.136

* /v2/tasks plaintext output in Marathon 1.5 returned container network endpoints in an unusable way (MARATHON-8721)

* Marathon launched too many tasks. (DCOS_OSS-5679)

* Marathon used to omit pod status report with tasks in `TASK_UNKOWN` state. (MARATHON-8710)

* With UnreachableStrategy, setting `expungeAfterSeconds` and `inactiveAfterSeconds` to the same value will cause the
instance to be expunged immediately; this helps with `GROUP_BY` or `UNIQUE` constraints. (MARATHON-8719)

* Marathon was checking authorization for unrelated apps when performing a kill-and-scale operations; this has been resolved. (MARATHON-8731)

* A race condition would cause Marathon to fail to start properly. (MARATHON-8741)

#### Update Metronome to 0.6.41

* There was a case where regex validation of project ids was ineffecient for certain inputs. The regex has been optimized. (MARATHON-8730)

* Metronome jobs networking is now configurable (MARATHON-8727)
