import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_verify_conf_file(File):
    c_file = File('/etc/aerospike/aerospike.conf')
    assert c_file.exists
    assert c_file.user == 'root'
    assert c_file.group == 'root'


def test_verify_log_file(File):
    l_file = File('/var/log/aerospike/aerospike.log')
    assert l_file.exists


def test_aerospike_service(Service):
    c_service = Service("aerospike")
    assert c_service.is_running
    assert c_service.is_enabled


def test_aerospike_cluster_size(Command):
    if 'aerospike-clust' in Command("hostname").stdout:
        cluster_size = Command("asinfo --no-config-file -v statistics").stdout
        assert 'cluster_size=3' in cluster_size
    elif 'localhost.localdomain' in Command("hostname").stdout:
        cluster_size = Command("asinfo --no-config-file -v statistics").stdout
        assert 'cluster_size=3' in cluster_size
    else:
        cluster_size = Command("asinfo --no-config-file -v statistics").stdout
        assert 'cluster_size=1' in cluster_size


@pytest.mark.parametrize("nodename,local_address", [
    ("aerospike", "0.0.0.0:3000"),
    ("aerospike", "0.0.0.0:3001"),
    ("aerospike", "0.0.0.0:3003"),
    ("aerospike-clust", "0.0.0.0:3002"),
])
def test_aerospike_listening_ports(Command, nodename, local_address):
    listener = Command("netstat -ant").stdout
    if nodename in Command("hostname").stdout:
        assert local_address in listener


@pytest.mark.parametrize("nodename,teststring", [
    ("aerospike", "file /var/log/aerospike/aerospike.log"),
    ("aerospike", "service-threads 4"),
    ("aerospike", "transaction-queues 4"),
    ("aerospike", "transaction-threads-per-queue 4"),
    ("aerospike", "proto-fd-max 15000"),
    ("aerospike", "proto-fd-idle-ms 60000"),
    ("aerospike", "high-water-memory-pct 60"),
    ("aerospike", "high-water-disk-pct 50"),
    ("aerospike", "default-ttl 4d"),
    ("aerospike", "replication-factor 2"),
    ("aerospike", "interval 250"),
    ("aerospike", "timeout 10"),
    ("aerospike", "paxos-single-replica-limit 1"),
    ("aerospike", "storage-engine memory"),
    ("aerospike-multi", "file /opt/aerospike/data/file1"),
    ("aerospike-multi", "file /opt/aerospike/data/file2"),
    ("aerospike-multi", "data-in-memory true"),
    ("aerospike-multi", "data-in-memory false"),
    ("aerospike-multi", "scheduler-mode noop"),
    ("aerospike-multi", "write-block-size 128K"),
    ("aerospike-multi", "mode multicast"),
    ("aerospike-multi", "port 9917"),
    ("aerospike-multi", "filesize 2G"),
    ("aerospike-multi", "default-ttl 30d"),
    ("aerospike-multi", "multicast-group 239.1.99.2"),
    ("aerospike-clust", "mode mesh"),
    ("aerospike-clust", "port 3002 # Heartbeat port for this node."),
    ("aerospike-clust", "address any"),
    ("aerospike-clust", "mesh-seed-address-port "),
])
def test_aerospike_config(File, Command, teststring, nodename):
    c_file = File('/etc/aerospike/aerospike.conf')
    if nodename in Command("hostname").stdout:
        assert c_file.contains(teststring)


def test_aerospike_access_port(File, Command):
    ip_address = Command("hostname -I").stdout
    c_file = File('/etc/aerospike/aerospike.conf')
    assert c_file.contains("access-address " + ip_address)
