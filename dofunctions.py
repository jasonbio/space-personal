import digitalocean
import data

from log import *


def get_token():
    config = data.get_config()
    return config['do_api_key']


def get_manager():
    token = get_token()
    try:
        manager = digitalocean.Manager(token=token)
    except Exception as e:
        message = "Failed to get manager, DO API responded: %s" % str(e.args)
        create_log(message, 3)
    return manager


def get_droplets():
    manager = get_manager()
    all_droplets = manager.get_all_droplets()
    return all_droplets


def get_droplet(id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        return droplet
    except Exception as e:
        message = "Failed to get droplet, DO API responded: %s" % str(e.args)
        create_log(message, 3)


def import_droplets():
    droplets = get_droplets()
    for droplet in droplets:
        droplet_id = str(droplet).split(" ")[0]
        server = data.get_server_provider_id(int(droplet_id))
        print server.count()
        if server.count() == 0:
            droplet_obj = get_droplet(droplet_id)
            if droplet.status == "active":
                state = 1
            elif droplet.status == "off":
                state = 0
            else:
                state = 2
            server_id = data.make_server(droplet.name, droplet.disk, droplet.image[
                                         'slug'], droplet.memory, droplet.vcpus, type="do", id=int(droplet.id), ip=droplet.ip_address, state=state)


def make_droplet(name, region, image, size, backups=0, ssh_key=0):
    token = get_token()
    key_list = []
    if backups == 0:
        backups = False
    elif backups == 1:
        backups = True
    else:
        backups == False
    if int(ssh_key) != 0:
        key_list.append(int(ssh_key))
    try:
        droplet = digitalocean.Droplet(token=token,
                                       name=name,
                                       region=region,
                                       image=image,
                                       size=size,
                                       backups=backups,
                                       ssh_keys=key_list)
        droplet.create()
        droplet = get_droplet(str(droplet).split(" ")[0])
        return droplet
    except Exception as e:
        message = "Failed to create droplet, DO API responded: %s" % str(
            e.args)
        create_log(message, 3)


def destroy_droplet(id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        stat = droplet.destroy()
        if stat:
            return 1
        else:
            return 0
    except Exception as e:
        message = "Failed to destroy droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def shutdown_droplet(id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.shutdown()
    except Exception as e:
        message = "Failed to shutdown droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def start_droplet(id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.power_on()
    except Exception as e:
        message = "Failed to start droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def reboot_droplet(id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.power_cycle()
    except Exception as e:
        message = "Failed to reboot droplet %s, DO API responded: %s" % (
            str(id), str(e.args))


def get_dist_images():
    manager = get_manager()
    dist_images = manager.get_data(
        "https://api.digitalocean.com/v2/images?page=1&per_page=1&type=distribution")
    for image in dist_images['images']:
        if image['slug']:
            data.make_do_image(image['slug'], image['id'])


def get_sizes():
    manager = get_manager()
    sizes = manager.get_data("https://api.digitalocean.com/v2/sizes")
    for size in sizes['sizes']:
        data.make_do_size(size['slug'], size['memory'], size['vcpus'], size[
                          'disk'], size['transfer'], size['price_monthly'], size['price_hourly'])


def get_regions():
    manager = get_manager()
    regions = manager.get_data("https://api.digitalocean.com/v2/regions")
    for region in regions['regions']:
        data.make_do_region(region['slug'], region['name'])


def get_snapshot(id):
    manager = get_manager()
    server = data.get_server_provider_id(id)
    droplet = manager.get_droplet(id)
    snapshots = droplet.get_data("https://api.digitalocean.com/v2/droplets/%s/snapshots?page=1&per_page=1" % str(id))
    for snapshot in snapshots['snapshots']:
        data.make_do_snapshot(str(server[0]['_id']), snapshot['id'], snapshot['name'], snapshot['min_disk_size'])


def get_snapshots():
    droplets = data.get_server_type("do")
    for droplet in droplets:
        get_snapshot(droplet['id'])


def get_do_kernels(id, server_id):
    manager = get_manager()
    url = "https://api.digitalocean.com/v2/droplets/%s/kernels?page=1&per_page=1" % str(id)
    kernels = manager.get_data(url)
    for kernel in kernels['kernels']:
        data.make_do_kernel(server_id, kernel['name'], kernel['id'])

def get_all_kernels():
    droplets = data.get_server_type("do")
    for droplet in droplets:
        get_do_kernels(droplet['id'], str(droplet['_id']))

def get_all_sshkeys():
    manager = get_manager()
    keys = manager.get_all_sshkeys()
    for key in keys:
        keyid = str(key).split(" ")[0]
        name = str(key).split(" ")[1]
        data.make_do_sshkey(keyid, name)

def sync_status():
    manager = get_manager()
    droplets = data.get_server_type("do")
    for droplet in droplets:
        try:
            d = manager.get_droplet(droplet['id'])
        except:
            pass
        if droplet['state'] == 0 and d.status == "active":
            data.set_server_state(droplet['_id'], 1)
        elif droplet['state'] == 1 and d.status == "off":
            data.set_server_state(droplet['_id'], 0)
        elif droplet['state'] < 3 and d.status == "archive":
            data.set_server_state(droplet['_id'], 3)

        if droplet['ram'] != d.memory:
            data.set_server_memory(droplet['_id'], d.memory)

        if droplet['vcpu'] != d.vcpus:
            data.set_server_vcpus(droplet['_id'], d.vcpus)

        if droplet['disk_size'] != d.disk:
            data.set_server_disk_size(droplet['_id'], d.disk)

        if droplet['state'] == 2 and d.status != "new":
            if d.status == "active":
                data.set_server_state(droplet['_id'], 1)
            elif d.status == "off":
                data.set_server_state(droplet['_id'], 0)


def get_droplet_ipaddress():
    manager = get_manager()
    droplets = data.get_server_type("do")
    for droplet in droplets:
        try:
            if not droplet['ip']:
                d = manager.get_droplet(droplet['id'])
                data.set_ipaddress_server(droplet['_id'], d.ip_address)
                if droplet['state'] == "2":
                    if d.status == "active":
                        data.set_server_state(droplet['_id'], 1)
                    elif d.status == "off":
                        data.set_server_state(droplet['_id'], 0)
        except:
            pass


def resize_droplet(id, size):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.resize(size)
    except Exception as e:
        message = "Failed to resize droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def rename_droplet(id, name):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.rename(name)
    except Exception as e:
        message = "Failed to rename droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def reset_root_password(id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.reset_root_password
    except Exception as e:
        message = "Failed to reset root password for droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def disable_backups(id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.disable_backups()
    except Exception as e:
        message = "Failed to disable backups for droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def enable_private_networking(id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.enable_private_networking()
    except Exception as e:
        message = "Failed to enable private networking for droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def enable_ipv6(id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.enable_ipv6()
    except Exception as e:
        message = "Failed to enable IPv6 for droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def snapshot_droplet(id, name):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.take_snapshot(name)
    except Exception as e:
        message = "Failed to take snapshot for droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def change_kernel(id, kernel_id):
    try:
        kernel = digitalocean.Kernel(id=int(kernel_id))
        manager = get_manager()
        droplet = manager.get_droplet(id)
        droplet.change_kernel(kernel)
    except Exception as e:
        message = "Failed to change kernel for droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def restore_snapshot(id, image_id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.restore(image_id)
    except Exception as e:
        message = "Failed to restore snapshot for droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)


def rebuild_droplet(id, image_id):
    manager = get_manager()
    try:
        droplet = manager.get_droplet(id)
        droplet.rebuild(image_id=image_id)
    except Exception as e:
        message = "Failed to rebuild droplet %s, DO API responded: %s" % (
            str(id), str(e.args))
        create_log(message, 3)
