from decimal import Decimal
from event import *
from log import *
from domfunctions import connect
from crontab import CronTab

import data
import datetime
import os
import psutil


def get_host_stats():
    con = connect()
    memory_stats = con.getMemoryStats(0, 0)
    total_memory = memory_stats['total'] / 1024
    free_memory = memory_stats['free'] / 1024
    res = psutil.cpu_times_percent()
    cpu_system = float(res.system)
    cpu_user = float(res.user)
    cpu_guest = float(res.guest)
    io_wait = float(res.iowait)
    memory_used = total_memory - free_memory
    data.make_host_statistic(round(cpu_system, 5),
                             round(cpu_user, 5),
                             round(cpu_guest, 5),
                             int(memory_used),
                             int(total_memory),
                             round(io_wait, 5),
                             datetime.datetime.now())


def sync_status():
    conn = connect()
    real_status = conn.listDefinedDomains()

    servers = data.get_all_servers()

    message_sync = "Syncing real state with database states."
    create_log(message_sync, 1)

    for server in servers:
        try:
            if server['type'] == "do" or server['type'] == "linode":
                break
        except:
            pass
        real_id = "vm%s" % str(server['_id'])
        if server['state'] == 0 and real_id not in real_status:
            message = "Checked %s, DB says it should not be running, but it is running." % real_id
            create_log(message, 2)

            inconsistent_event(server['_id'])

            data.set_server_inconsistent(server['_id'], 1)
        elif server['state'] == 1 and real_id in real_status:
            message = "Checked %s, DB says it should be running, but is is not running." % real_id
            create_log(message, 2)

            inconsistent_event(server['_id'])

            data.set_server_inconsistent(server['_id'], 1)


def import_images():
    config = data.get_config()
    filesystem_images = [f for f in os.listdir(config['image_directory']) if
                         os.path.isfile(
                             os.path.join(config['image_directory'], f))]
    message = "Image sync initated."
    create_log(message, 1)
    for image in filesystem_images:
        images = data.get_all_images()
        state = 0
        for existing_image in images:
            if os.path.splitext(image)[0] == existing_image['name']:
                state = 1
        if state == 0:
            image_name = os.path.splitext(image)[0]
            image_path = "%s/%s" % (str(config['image_directory']), str(image))
            image_size = os.path.getsize(image_path) / (1024 * 1024)
            message2 = "Found new image at %s, adding to the DB" % str(
                image_path)
            create_log(message2, 1)
            data.make_image(image_name, image_path, image_size)


def add_crontab_entries():
    cron = CronTab(user=True)
    job1 = cron.new(command="/usr/bin/python /srv/space/cron_minute.py")
    job1.minute.every(1)
    job2 = cron.new(command="/usr/bin/python /srv/space/cron_15minute.py")
    job2.minute.every(15)
    job3 = cron.new(command="/usr/bin/python /srv/space/cron_daily.py")
    job3.hour.on(0)
    job3.minute.on(0)
    cron.write()
