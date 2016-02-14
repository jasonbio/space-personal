import data
import linode
import time
import log


def get_api():
    config = data.get_config()
    try:
        api = linode.Api(config['linode_api_key'])
        return api
    except:
        pass


def get_linode(linodeID):
    api = get_api()
    try:
        linode = api.linode.list(LinodeID=linodeID)
        return linode[0]
    except:
        pass


def get_linodes():
    api = get_api()
    try:
        linodes = api.linode.list()
        return linodes
    except:
        pass


def import_linodes():
    linodes = get_linodes()
    try:
        for linode in linodes:
            linode_id = linode['LINODEID']
            server = data.get_server_provider_id(int(linode_id))
            if server.count() == 0:
                if linode['STATUS'] == 1:
                    state = 1
                elif linode['STATUS'] == 2:
                    state = 0
                else:
                    state = 2
                linode_ip = get_linode_ip(int(linode['LINODEID']))
                plan = data.get_linode_plan_id(linode['PLANID'])
                server_id = data.make_server(linode['LABEL'], plan[0]['disk'], linode['DISTRIBUTIONVENDOR'], linode[
                                             'TOTALRAM'], plan[0]['cores'], type="linode", id=int(linode['LINODEID']), ip=linode_ip['IPADDRESS'], state=state)
    except:
        pass


def get_linode_ip(linodeID):
    api = get_api()
    try:
        linode_ip = api.linode.ip.list(LinodeID=linodeID)
        return linode_ip[0]
    except:
        pass


def get_datacenters():
    api = get_api()
    try:
        facilities = api.avail.datacenters()
        for facility in facilities:
            data.make_linode_facility(
                facility['DATACENTERID'], facility['LOCATION'])
    except:
        pass


def get_plans():
    api = get_api()
    try:
        plans = api.avail.linodeplans()
        for plan in plans:
            data.make_linode_plan(plan['PLANID'], plan['RAM'], plan['DISK'], plan[
                                  'CORES'], plan['XFER'], plan['LABEL'], plan['PRICE'], plan['HOURLY'])
    except:
        pass


def get_kernels():
    api = get_api()
    try:
        kernels = api.avail.kernels()
        for kernel in kernels:
            data.make_linode_kernel(kernel['KERNELID'], kernel['LABEL'])
    except:
        pass


def get_distributions():
    api = get_api()
    try:
        distributions = api.avail.distributions()
        for dist in distributions:
            if dist['IS64BIT'] == 1:
                data.make_linode_distribution(dist['DISTRIBUTIONID'], dist['LABEL'])
    except:
        pass


def make_linode(datacenterID, planID):
    api = get_api()
    try:
        linode = api.linode.create(DatacenterID=datacenterID, PlanID=planID)
        return linode['LinodeID']
    except:
        pass

def make_config(linodeID, kernelID, label, diskID):
    api = get_api()
    try:
        config = api.linode.config.create(
            LinodeID=linodeID, KernelID=kernelID, Label=label, DiskList="%s" % str(diskID))
    except:
        pass


def make_disk(linodeID, distributionID, label, size, rootPass):
    api = get_api()
    try:
        disk = api.linode.disk.createfromdistribution(
            LinodeID=linodeID, DistributionID=distributionID, Label=label, Size=size, rootPass=rootPass)
        return disk['DiskID']
    except:
        pass


def boot_linode(LinodeID):
    api = get_api()
    try:
        api.linode.boot(LinodeID=LinodeID)
    except linode.api.LinodeException as e:
        message = "Tried to boot Linode %s but failed, API returned: %s" % (str(LinodeID), str(e))
        log.create_log(message, 3)
        return 0


def shutdown_linode(linodeID):
    api = get_api()
    try:
        api.linode.shutdown(LinodeID=linodeID)
    except:
        pass


def reboot_linode(linodeID):
    api = get_api()
    try:
        api.linode.reboot(LinodeID=linodeID)
    except:
        pass


def delete_linode(LinodeID):
    api = get_api()
    try:
        api.linode.delete(LinodeID=LinodeID, skipChecks="True")
    except:
        pass


def resize_linode(LinodeID, PlanID):
    api = get_api()
    try:
        api.linode.resize(LinodeID=LinodeID, PlanID=PlanID)
    except:
        pass


def rename_linode(LinodeID, Label):
    api = get_api()
    try:
        api.linode.update(LinodeID=LinodeID, Label=Label)
    except:
        pass


def set_linode_rdns(LinodeID, Hostname, IPAddressID=0):
    api = get_api()
    ip_obj = api.linode.ip.list(LinodeID=LinodeID)
    try:
        api.linode.ip.setrdns(IPAddressID=ip_obj[0]['IPADDRESSID'], Hostname=Hostname)
    except:
        message = "Attempted to set rDNS for Linode %s, couldn't do so because a forward lookup record doesn't exist for that hostname." % str(LinodeID)
        log.create_log(message, 3)
