import xml.etree.cElementTree as et
import uuid
import subprocess
import data


def make_config(name, disk_path, ram, vcpu, image, bootdev="hd"):
    config = data.get_config()

    domain = et.Element("domain")
    domain.set("type", "kvm")

    namexml = et.SubElement(domain, "name")
    namexml.text = "vm%s" % str(name)

    cpuxml = et.SubElement(domain, "cpu")
    cputopologyxml = et.SubElement(cpuxml, "topology")
    cputopologyxml.set("sockets", "1")
    cputopologyxml.set("cores", "4")
    cputopologyxml.set("threads", "4")

    uuidxml = et.SubElement(domain, "uuid")
    uuidxml.text = str(uuid.uuid1())

    memoryxml = et.SubElement(domain, "memory")
    memoryxml.set("unit", "MB")
    memoryxml.text = ram

    cmemoryxml = et.SubElement(domain, "currentMemory")
    cmemoryxml.set("unit", "MB")
    cmemoryxml.text = ram

    vcpuxml = et.SubElement(domain, "vcpu")
    vcpuxml.set("placement", "static")
    vcpuxml.text = vcpu

    osxml = et.SubElement(domain, "os")

    typexml = et.SubElement(osxml, "type")
    typexml.text = "hvm"

    bootdev1xml = et.SubElement(osxml, "boot")
    bootdev1xml.set("dev", bootdev)

    bootmenuxml = et.SubElement(osxml, "bootmenu")
    bootmenuxml.set("enabled", "true")

    featurexml = et.SubElement(domain, "features")
    acpixml = et.SubElement(featurexml, "acpi")
    apicxml = et.SubElement(featurexml, "apic")
    paexml = et.SubElement(featurexml, "pae")

    clockxml = et.SubElement(domain, "clock")
    clockxml.set("offset", "utc")

    onpoweroffxml = et.SubElement(domain, "on_poweroff")
    onpoweroffxml.text = "destroy"

    onrebootxml = et.SubElement(domain, "on_reboot")
    onrebootxml.text = "restart"

    oncrashxml = et.SubElement(domain, "on_crash")
    oncrashxml.text = "restart"

    devicesxml = et.SubElement(domain, "devices")

    emulatorxml = et.SubElement(devicesxml, "emulator")
    
    if config['distribution'] == "centos":
        emulatorxml.text = "/usr/libexec/qemu-kvm"
    else:
        emulatorxml.text = "/usr/bin/kvm"

    disk1xml = et.SubElement(devicesxml, "disk")
    disk1xml.set("type", "file")
    disk1xml.set("device", "disk")

    disk1driverxml = et.SubElement(disk1xml, "driver")
    disk1driverxml.set("name", "qemu")
    disk1driverxml.set("type", "raw")
    disk1driverxml.set("cache", "none")

    disk1sourcexml = et.SubElement(disk1xml, "source")
    disk1sourcexml.set("file", "%s/vm%s.img" %
                       (str(config['disk_directory']), str(name)))

    disk1targetxml = et.SubElement(disk1xml, "target")
    disk1targetxml.set("dev", "hda")

    disk1addressxml = et.SubElement(disk1xml, "address")
    disk1addressxml.set("type", "drive")
    disk1addressxml.set("controller", "0")
    disk1addressxml.set("bus", "0")
    disk1addressxml.set("target", "0")
    disk1addressxml.set("unit", "0")

    disk2xml = et.SubElement(devicesxml, "disk")
    disk2xml.set("type", "file")
    disk2xml.set("device", "cdrom")

    disk2sourcexml = et.SubElement(disk2xml, "source")
    disk2sourcexml.set("file", "%s/%s.iso" %
                       (str(config['image_directory']), str(image)))

    disk2driverxml = et.SubElement(disk2xml, "driver")
    disk2driverxml.set("name", "qemu")
    disk2driverxml.set("type", "raw")

    disk2targetxml = et.SubElement(disk2xml, "target")
    disk2targetxml.set("dev", "hdc")
    disk2targetxml.set("bus", "ide")

    disk2readonlyxml = et.SubElement(disk2xml, "readyonly")

    disk2addressxml = et.SubElement(disk2xml, "address")
    disk2addressxml.set("type", "drive")
    disk2addressxml.set("controller", "0")
    disk2addressxml.set("bus", "1")
    disk2addressxml.set("target", "0")
    disk2addressxml.set("unit", "0")

    networkxml = et.SubElement(devicesxml, "interface")
    networkxml.set("type", "network")

    networksourcexml = et.SubElement(networkxml, "source")
    networksourcexml.set("network", "default")

    graphicsxml = et.SubElement(devicesxml, "graphics")
    graphicsxml.set("type", "vnc")
    graphicsxml.set("port", "-1")
    graphicsxml.set("passwd", str(name))

    interfacexml = et.SubElement(domain, "interface")

    interfacesourcexml = et.SubElement(interfacexml, "source")
    interfacesourcexml.set("bridge", "virbr0")

    interfacemodelxml = et.SubElement(interfacexml, "model")
    interfacemodelxml.set("type", "virtio")

    tree = et.ElementTree(domain)
    path = "%s/vm%s.xml" % (str(config['config_directory']), str(name))
    tree.write(path)


def make_image(name, disk_size):
    config = data.get_config()
    command = "qemu-img create %s/vm%s.img %sG" % (
        str(config['disk_directory']), str(name), str(disk_size))
    subprocess.Popen(command.split())
