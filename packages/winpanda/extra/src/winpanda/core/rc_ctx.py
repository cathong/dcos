"""Panda package management for Windows.

Resource rendering context calculation stuff.
"""
import configparser as cfp
import json
import subprocess

from common import constants as cm_const
from common import logger
from common.storage import ISTOR_NODE, IStorNodes
from core.package.id import PackageId
from typing import Dict

LOG = logger.get_logger(__name__)

CMD_GET_IP = ('powershell', '-executionpolicy', 'Bypass', '-File',
              'C:\\d2iq\\dcos\\bin\\detect_ip.ps1')

class RCCONTEXT_ITEM:
    """Element of resource rendering context."""
    MASTER_LOCATION = 'master_location'
    MASTER_PRIV_IPADDR = 'master_priv_ipaddr'
    LOCAL_PRIV_IPADDR = 'local_priv_ipaddr'
    ZK_CLIENT_PORT = 'zk_client_port'

    DCOS_INST_DPATH = 'dcos_inst_dpath'
    DCOS_CFG_DPATH = 'dcos_cfg_dpath'
    DCOS_WORK_DPATH = 'dcos_work_dpath'
    DCOS_RUN_DPATH = 'dcos_run_dpath'
    DCOS_LOG_DPATH = 'dcos_log_dpath'
    DCOS_TMP_DPATH = 'dcos_tmp_dpath'
    DCOS_BIN_DPATH = 'dcos_bin_dpath'
    DCOS_LIB_DPATH = 'dcos_lib_dpath'

    PKG_INST_DPATH = 'pkg_inst_dpath'
    PKG_LOG_DPATH = 'pkg_log_dpath'
    PKG_RTD_DPATH = 'pkg_rtd_dpath'
    PKG_WORK_DPATH = 'pkg_work_dpath'
    PKG_SHRCFG_DPATH = 'pkg_shrcfg_dpath'


def _identity(s):
    return s


def _escape_json_string(s):
    result = json.dumps(s)
    if result.startswith('"'):
        result = result[1:-1]
    return result


class ResourceContext:
    """Resource rendering context manager."""

    def __init__(self, istor_nodes: IStorNodes=None, cluster_conf: dict=None,
                 pkg_id: PackageId=None, extra_values: dict=None):
        """Constructor.

        :param istor_nodes:  IStorNodes, DC/OS installation storage nodes (set
                             of pathlib.Path objects)
        :param cluster_conf: dict, configparser.ConfigParser.read_dict()
                             compatible data. DC/OS cluster setup parameters
        :param pkg_id:       PackageId, package ID
        :param extra_values: dict, extra 'key=value' data to be added to the
                             resource rendering context.
        """
        self._istor_nodes = istor_nodes
        self._cluster_conf = cluster_conf
        self._pkg_id = pkg_id
        self._extra_values = extra_values
        self._local_priv_ipaddr = None

    @property
    def local_priv_ipaddr(self):
        if self._local_priv_ipaddr is None:
            if self._extra_values:
                # TODO replace this hardcoded value 'privateipaddr' on constant
                local_priv_ipaddr = self._extra_values['privateipaddr']
            else:
                result = subprocess.run(CMD_GET_IP, stdout=subprocess.PIPE, check=True)
                local_priv_ipaddr = result.stdout.decode('ascii').strip()
            self._local_priv_ipaddr = local_priv_ipaddr

        return self._local_priv_ipaddr

    def get_items(self, json_ready=False) -> Dict:
        """Get resource rendering context items.

        :param json_ready: bool, get JSON-compatible context items, if True
        :return:           dict, set of resource rendering context items
        """
        retrievers = (self._get_istor_items,
                      self._get_cluster_conf_items,
                      self._get_pkg_items,
                      self._get_extra_items)
        items = {}

        if json_ready:
            escape = _escape_json_string
        else:
            escape = _identity

        for retriever in retrievers:
            items.update(retriever(escape))

        return items

    def _get_istor_items(self, escape):
        """Discover resource rendering context items from DC/OS installation
        storage configuration.

        :param escape:     Callable, escape string function
        :return:           dict, set of resource rendering context items
        """
        if self._istor_nodes is None:
            return {}

        items = {
            RCCONTEXT_ITEM.DCOS_INST_DPATH: escape(str(
                getattr(self._istor_nodes, ISTOR_NODE.ROOT)
            )),
            RCCONTEXT_ITEM.DCOS_CFG_DPATH: escape(str(
                getattr(self._istor_nodes, ISTOR_NODE.CFG)
            )),
            RCCONTEXT_ITEM.DCOS_WORK_DPATH: escape(str(
                getattr(self._istor_nodes, ISTOR_NODE.WORK)
            )),
            RCCONTEXT_ITEM.DCOS_RUN_DPATH: escape(str(
                getattr(self._istor_nodes, ISTOR_NODE.RUN)
            )),
            RCCONTEXT_ITEM.DCOS_LOG_DPATH: escape(str(
                getattr(self._istor_nodes, ISTOR_NODE.LOG)
            )),
            RCCONTEXT_ITEM.DCOS_TMP_DPATH: escape(str(
                getattr(self._istor_nodes, ISTOR_NODE.TMP)
            )),
            RCCONTEXT_ITEM.DCOS_BIN_DPATH: escape(str(
                getattr(self._istor_nodes, ISTOR_NODE.BIN)
            )),
            RCCONTEXT_ITEM.DCOS_LIB_DPATH: escape(str(
                getattr(self._istor_nodes, ISTOR_NODE.LIB)
            )),
        }

        return items

    def _get_cluster_conf_items(self, escape):
        """Extract resource rendering context items from cluster configuration.

        :param escape:     Callable, escape string function
        :return:           dict, set of resource rendering context items
        """
        if self._cluster_conf is None:
            return {}

        cluster_conf = cfp.ConfigParser()
        cluster_conf.read_dict(self._cluster_conf)

        mnode_cfg_items = [
            (cluster_conf.get(s, 'privateipaddr',
                              fallback='127.0.0.1'),
             cluster_conf.get(s, 'zookeeperclientport',
                              fallback=cm_const.ZK_CLIENTPORT_DFT))
            for s in cluster_conf.sections() if s.startswith('master-node')
        ]

        if mnode_cfg_items:
            master_priv_ipaddr = mnode_cfg_items[0][0]
            zk_client_port = mnode_cfg_items[0][1]
            dsc_type = self._cluster_conf.get('discovery', {}).get('type')
            if dsc_type == 'static':
                master_location = f'{master_priv_ipaddr}:{zk_client_port}'
            else:
                master_location = ",".join(
                    [escape(f'{v[0]}:{v[1]}') for v in mnode_cfg_items])
        else:
            master_priv_ipaddr = '127.0.0.1'
            zk_client_port = cm_const.ZK_CLIENTPORT_DFT

            master_location = f'{master_priv_ipaddr}:{zk_client_port}'

        items = {
            RCCONTEXT_ITEM.MASTER_LOCATION: escape(master_location),
            RCCONTEXT_ITEM.MASTER_PRIV_IPADDR: escape(master_priv_ipaddr),
            RCCONTEXT_ITEM.LOCAL_PRIV_IPADDR: escape(self.local_priv_ipaddr),
            RCCONTEXT_ITEM.ZK_CLIENT_PORT: escape(zk_client_port)
        }

        return items

    def _get_pkg_items(self, escape):
        """Calculate resource rendering context items specific to a particular
        DC/OS package.

        :param escape:     Callable, escape string function
        :return:           dict, set of resource rendering context items
        """
        if self._istor_nodes is None or self._pkg_id is None:
            return {}

        pkg_inst_dpath = (
            getattr(self._istor_nodes, ISTOR_NODE.PKGREPO).joinpath(
                self._pkg_id.pkg_id
            )
        )
        pkg_log_dpath = getattr(self._istor_nodes, ISTOR_NODE.LOG).joinpath(
            self._pkg_id.pkg_name
        )
        pkg_rtd_dpath = getattr(self._istor_nodes, ISTOR_NODE.RUN).joinpath(
            self._pkg_id.pkg_name
        )
        pkg_work_dpath = getattr(self._istor_nodes, ISTOR_NODE.WORK).joinpath(
            self._pkg_id.pkg_name
        )
        pkg_shrcfg_dpath = getattr(self._istor_nodes, ISTOR_NODE.CFG).joinpath(
            self._pkg_id.pkg_name
        )

        items = {
            RCCONTEXT_ITEM.PKG_INST_DPATH: escape(str(pkg_inst_dpath)),
            RCCONTEXT_ITEM.PKG_LOG_DPATH: escape(str(pkg_log_dpath)),
            RCCONTEXT_ITEM.PKG_RTD_DPATH: escape(str(pkg_rtd_dpath)),
            RCCONTEXT_ITEM.PKG_WORK_DPATH: escape(str(pkg_work_dpath)),
            RCCONTEXT_ITEM.PKG_SHRCFG_DPATH: escape(str(pkg_shrcfg_dpath)),
        }

        return items

    def _get_extra_items(self, escape):
        """Extract resource rendering context items from provided extra
        'key=value' map.

        :param escape:     Callable, escape string function
        :return:           dict, set of resource rendering context items
        """
        if self._extra_values is None:
            return {}

        items = {
            k: escape(str(v)) for k, v in self._extra_values.items()
        }

        return items

    def as_dict(self):
        """Construct the dict representation."""
        if self._istor_nodes is None:
            istor_nodes = None
        else:
            istor_nodes = {
                k: str(v) for k, v in self._istor_nodes._asdict().items()
            }

        return {
            'istor_nodes': istor_nodes,
            'cluster_conf': self._cluster_conf,
            'pkg_id': self._pkg_id.pkg_id,
            'extra_values': self._extra_values
        }

    def update(self, values: dict=None):
        """Update context data.

        :param values: dict, 'key=value' data to be added to / updated in the
                             resource rendering context.
        """

        self._extra_values.update(values)
