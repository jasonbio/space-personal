import libvirt
import datetime
import os
import subprocess
import create
import xml.etree.ElementTree as et
import data

from log import *
from event import *


def restart_dhcpd():
    config = data.get_config()
    command = "service %s restart" % str(config['dhcp_service'])
    ip = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    create_log("Restarted DHCPD.", 1)


def connect():
    config = data.get_config()
    conn = libvirt.open("%s:///system" % config['system_type'])
    message = "Connection established with server."
    create_log(message, 1)
    return conn


def list_vms():
    conn = connect()
    other_domains = conn.listDefinedDomains()
    running_domains = conn.listDomainsID()
    message = "Got a list of domains."
    create_log(message, 1)
    data = []
    for id in running_domains:
        data.append(conn.lookupByID(id))
    return data, other_domains


def shutdown_vm(name):
    conn = connect()
    message = "Sent shutdown to vm%s." % str(name)
    create_log(message, 1)
    vm = conn.lookupByName("vm%s" % str(name))
    try:
        vm.destroy()
    except:
        message2 = "Attempted to shutdown vm%s, but it wasn't running." % str(
            name)
        create_log(message2, 2)


def start_vm(name):
    conn = connect()
    message = "Sent startup to vm%s." % str(name)
    create_log(message, 1)
    vm = conn.lookupByName("vm%s" % str(name))
    try:
        vm.create()
    except:
        message = "Attempted to start vm%s but it was already running." % (
            str(name))
        create_log(message, 2)


def create_vm(name, ram, disk_size, image, vcpu, bootdev="hd"):
    config = data.get_config()
    create.make_config(name, "", ram, vcpu, image, bootdev=bootdev)
    message = "Created new configuration for vm%s at %s/vm%s.xml" % (
        str(name), str(config['config_directory']), str(name))

    create_log(message, 1)

    create.make_image(name, disk_size)
    message2 = "Created new disk image %s/vm%s.img of size %sGB." % (
        str(name), str(config['disk_directory']), str(disk_size))

    create_log(message2, 1)

    conn = connect()
    xmlpath = "%s/vm%s.xml" % (str(config['config_directory']), str(name))

    xml = ""

    with open(xmlpath, "r") as file:
        xml = file.read()

    conn.defineXML(xml)

    message3 = "Defined new domain vm%s." % str(name)
    create_log(message3, 1)

    newdom = conn.lookupByName("vm%s" % str(name))
    newdom.create()

    message4 = "Sent startup to vm%s." % str(name)
    create_log(message4, 1)


def update_config(vm, bootdev="hd"):
    config = data.get_config()
    path = "%s/vm%s.xml" % (str(config['config_directory']), str(vm[0]['_id']))
    try:
        os.remove(path)
    except:
        message2 = "Tried to delete config at %s but it wasn't there." % path
        create_log(message2, 2)
        pass

    message1 = "Deleted config for vm%s at %s/vm%s.xml" % (
        str(vm), str(config['config_directory']), str(vm[0]['_id']))
    create_log(message1, 1)

    create.make_config(
        vm[0]['_id'], "", str(vm[0]['ram']), str(vm[0]['vcpu']), vm[0]['disk_image'], bootdev=bootdev)

    message = "Created new configuration for vm%s at %s/vm%s.xml" % (
        str(vm[0]['_id']), str(config['config_directory']), str(vm[0]['_id']))
    create_log(message, 1)


def redefine_vm(vm):
    config = data.get_config()
    conn = connect()
    dom = conn.lookupByName("vm%s" % str(vm))
    try:
        dom.destroy()
    except:
        pass
    finally:
        dom.undefine()

    xmlpath = "%s/vm%s.xml" % (str(config['config_directory']), str(vm))

    xml = ""

    with open(xmlpath, "r") as file:
        xml = file.read()

    conn.defineXML(xml)

    message3 = "Redefined domain vm%s." % str(vm)
    create_log(message3, 1)


def delete_vm(name, image_path):
    conn = connect()
    try:
        vm = conn.lookupByName("vm%s" % str(name))
    except:
        pass
    try:
        vm.destroy()
    except:
        vm.undefine()
    os.remove(image_path)
    message = "Deleted VM with name vm%s, image removed at %s." % (
        str(name), str(image_path))
    create_log(message, 1)


def make_console(name):
    try:
        port, endport = get_vnc_port(name)
        novncport = start_novnc(port, endport)
        return novncport
    except Exception as e:
        message = "Failed to create VNC console. Got message: %s" % str(e)
        create_log(message, 3)
        return "error"


def get_vnc_port(name):
    conn = connect()
    vm = conn.lookupByName("vm%s" % str(name))
    command = "virsh vncdisplay vm%s" % str(name)
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.communicate()[0]
    endport = output.split(":")[1]
    if int(endport) < 10:
        port = "590%s" % str(endport)
        eport = "0%s" % str(endport)
    else:
        port = "59%s" % str(endport)
        eport = endport
    message = "Got VNC port %s, output returned: %s" % (str(port), str(output))
    create_log(message, 1)
    return port, eport


def start_novnc(port, last):
    config = data.get_config()
    command = "python %s/utils/websockify --web %s 61%s localhost:%s -D --cert %s" % (
        str(config['novnc_directory']), str(config['novnc_directory']), str(last), str(port), str(config['pem_location']))
    command = command.replace('\n', '')
#    command = "/srv/noVNC/utils/websockify 127.0.0.1:60%s --vnc 127.0.0.1:%s --web /srv/noVNC/utils -D" % (str(last), str(port))
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.communicate()[0]
    message = "Opened noVNC on port 60%s" % str(last)
    create_log(message, 1)
    port = "61%s" % str(last)
    return port


def assign_ip(vmid):
    available_ips = data.get_ipaddress_free()
    if not available_ips:
        create_log(
            "Attempted to assign an IP address, but no IP addresses remained.", 2)
        return 0
    data.set_ipaddress_server(vmid, available_ips['ip'])
    data.set_ipaddress_serverid(available_ips['_id'], vmid)
    return available_ips['ip']


def append_dhcp_config(mac_address, ip, vmid):
    config = data.get_config()
    with open(config['dhcp_configuration'], "a") as config:
        config.write("host vm%s {\n hardware ethernet %s;\n fixed-address %s;\n}" %
                     (str(vmid), str(mac_address), str(ip)))
        config.close()
    restart_dhcpd()


def rebuild_dhcp_config():
    config = data.get_config()
    ips = data.get_ipaddress_allocated_all()
    ipranges = data.get_all_iprange()
    create_log("Rebuilding DHCPD configuration to unassign IP.", 1)
    with open(config['dhcp_configuration'], "w") as config:
        config.write("option domain-name-servers 8.8.8.8, 8.8.4.4;\n\n")
        for range in ipranges:
            line = "subnet %s netmask %s {\n range %s %s;\n option routers %s;\n}\n" % (str(range['subnet']), str(
                range['netmask']), str(range['startip']), str(range['endip']), str(range['gateway']))
            config.write(line)
        for ip in ips:
            vm = data.get_server_id(ip['server_id'])
            config.write("host vm%s {\n hardware ethernet %s;\n fixed-address %s;\n}\n" % (
                str(vm[0]['_id']), str(vm[0]['mac_address']), str(ip['ip'])))
        config.close()
    restart_dhcpd()


def get_guest_mac(name):
    conn = connect()
    vm = conn.lookupByName("vm%s" % str(name))
    vm_xml = vm.XMLDesc(0)
    tree = et.fromstring(vm_xml)
    mac_address = ""

    for child in tree:
        if child.tag == "devices":
            for sub in child:
                if sub.tag == "interface":
                    for ssub in sub:
                        if ssub.tag == "mac":
                            mac_address = ssub.attrib

    return mac_address['address']
