from celery import Celery

import data
import subprocess
import datetime

from log import create_log
from event import resize_event

app = Celery("jobs", broker="amqp://")


@app.task
def resize_disk(vmid, size):
    try:
        server = data.get_server_id(vmid)
        data.set_server_blocked(vmid, 1)

        resize_event_id = resize_event(str(server[0]['_id']))

        make_temp_disk(size)

        log1 = "Created temporary disk temp.img of size %sGB" % str(size)
        create_log(log1, 1)

        if int(server[0]['disk_size']) < int(size):
            log2 = "Starting resize process for vm%s to size %sGB" % (
                str(server[0]['_id']), str(size))
            create_log(log2, 1)

            try:
                do_resize(server, 1)
            except Exception as e:
                log3 = "Resize process failed for vm%s: %s" % (
                    str(server[0]['_id']), str(e.args))
                create_log(log3, 3)

            log4 = "Resize process for vm%s completed." % (
                str(server[0]['_id']))
            create_log(log4, 1)
        else:
            log5 = "Couldn't resize vm%s, chosen size is smaller than current size." % str(
                server[0]['_id'])
            create_log(log5, 3)
            return 0
        do_rename(server)
        data.set_server_disksize(vmid, size)
        data.set_event_status(resize_event_id, 1)
        data.set_server_blocked(vmid, 0)
        data.set_event_complete(resize_event_id, str(datetime.datetime.now()))
        return 1
    except Exception as e:
        log6 = "Resize process failed for vm%s: %s" % (
            str(server[0]['_id']), str(e.args))
        create_log(log6, 3)
        data.set_server_blocked(vmid, 0)
        data.set_event_status(resize_event_id, 99)
        data.set_event_complete(resize_event_id, str(datetime.datetime.now()))


def make_temp_disk(size):
    config = data.get_config()
    command = "qemu-img create %s/temp.img %sG" % (
        str(config['disk_directory']), str(size))
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)


def do_resize(server, direction):
    config = data.get_config()
    if direction == 1:
        # we are resizing up
        command = "virt-resize --expand /dev/sda2 %s %s/temp.img" % (
            str(server[0]['disk_path']), str(config['disk_directory']))
    elif direction == 0:
        # we are resizing down
        command = "virt-resize --shrink /dev/sda2 %s %s/temp.img" % (
            str(server[0]['disk_path']), str(config['disk_directory']))
    p = subprocess.call(command.split(), stdout=subprocess.PIPE)


def do_rename(server):
    config = data.get_config()
    command = "rm %s" % str(server[0]['disk_path'])
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    command2 = "mv %s/temp.img %s" % (
        str(config['disk_directory']), str(server[0]['disk_path']))
    d = subprocess.Popen(command2.split(), stdout=subprocess.PIPE)
