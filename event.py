import datetime
import data

'''
Event Types
1 = Create
2 = Destroy
3 = Boot
4 = Shutdown
5 = Inconsistency
'''


def insert_event(type, vmid, status=1):
    id = data.make_event(type, str(vmid), datetime.datetime.now(), status)
    return id


def shutdown_event(vmid):
    insert_event(4, vmid)


def startup_event(vmid):
    insert_event(3, vmid)


def create_event(vmid):
    insert_event(1, vmid)


def destroy_event(vmid):
    insert_event(2, vmid)


def inconsistent_event(vmid):
    insert_event(5, vmid)


def resize_event(vmid):
    id = insert_event(6, str(vmid), status=0)
    return id
