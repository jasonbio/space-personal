from utilities import *
from dofunctions import get_droplet_ipaddress
from services import check_services

get_host_stats()
sync_status()
get_droplet_ipaddress()
check_services()
