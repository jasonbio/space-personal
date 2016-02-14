from netaddr import *
import data


def ennumerate_iprange(id):
    iprange = data.get_iprange_id(id)
    ip_list = list(iter_iprange(iprange[0]['startip'], iprange[0]['endip']))
    for x in range(0, len(ip_list)):
        data.make_ipaddress(str(ip_list[x]), iprange[0]['netmask'], 0)
