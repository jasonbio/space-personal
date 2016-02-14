from flask import *

from domfunctions import *
from event import *
from utilities import *
from log import *
from data import *
from functools import update_wrapper, wraps
from dofunctions import *
from linodefunctions import *
from services import *

import libvirt
import subprocess
import datetime
import json
import networking
import jobs

app = Flask(__name__)

app.secret_key = "ENTER_SECRET_KEY_HERE"


def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            session['logged_in']
        except:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorator

@app.errorhandler(404)
def notfound_error_page(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error_page(e):
    return render_template("500.html"), 500

@app.route('/service/<service_name>/start')
@login_required
def service_start_endpoint(service_name):
    manipulate_service(service_name, 1)
    check_services()
    return redirect('/settings?message=3')


@app.route('/service/<service_name>/restart')
@login_required
def service_restart_endpoint(service_name):
    manipulate_service(service_name, 2)
    check_services()
    return redirect('/settings?message=3')


@app.route('/service/<service_name>/stop')
@login_required
def service_stop_endpoint(service_name):
    manipulate_service(service_name, 0)
    check_services()
    return redirect('/settings?message=3')


@app.route('/utils/import_droplets')
@login_required
def import_droplets_endpoint():
    import_droplets()
    return redirect('/server?message=3')


@app.route('/utils/import_linodes')
@login_required
def import_linodes_endpoint():
    import_linodes()
    return redirect('/server?message=3')


@app.route('/server/edit/<vmid>/droplet/resize', methods=['POST'])
@login_required
def droplet_resize(vmid):
    server = get_server_id(vmid)
    droplet = get_droplet(server[0]['id'])
    if server[0]['state'] == 1:
        return redirect('/server/edit/%s/droplet?error=2' % str(vmid))
    resize_droplet(server[0]['id'], request.form['size'])
    size = get_do_size(request.form['size'])
    set_server_do_specs(
        server[0]['_id'], size[0]['disk'], size[0]['memory'], size[0]['vcpus'])
    return redirect('/server/edit/%s/droplet?message=4' % str(vmid))


@app.route('/server/edit/<vmid>/droplet/snapshot', methods=['POST'])
@login_required
def droplet_snapshopt(vmid):
    server = get_server_id(vmid)
    droplet = get_droplet(server[0]['id'])
    name = request.form['snapshot_name']
    if server[0]['state'] == 1:
        return redirect('/server/edit/%s/droplet?error=2' % str(vmid))
    snapshot_droplet(server[0]['id'], name)
    return redirect('/server/edit/%s/droplet?message=4' % str(vmid))


@app.route('/server/edit/<vmid>/droplet/private', methods=['GET'])
@login_required
def droplet_private_networking(vmid):
    server = get_server_id(vmid)
    droplet = get_droplet(server[0]['id'])
    if server[0]['state'] == 1:
        return redirect('/server/edit/%s/droplet?error=2' % str(vmid))
    enable_private_networking(server[0]['id'])
    return redirect('/server/edit/%s/droplet?message=4' % str(vmid))


@app.route('/server/edit/<vmid>/droplet/ipv6', methods=['GET'])
@login_required
def droplet_ipv6(vmid):
    server = get_server_id(vmid)
    droplet = get_droplet(server[0]['id'])
    if server[0]['state'] == 1:
        return redirect('/server/edit/%s/droplet?error=2' % str(vmid))
    enable_ipv6(server[0]['id'])
    return redirect('/server/edit/%s/droplet?message=4' % str(vmid))


@app.route('/server/edit/<vmid>/droplet/disablebackups', methods=['GET'])
@login_required
def disable_backups_endpoint(vmid):
    server = get_server_id(vmid)
    droplet = get_droplet(server[0]['id'])
    if server[0]['state'] == 1:
        return redirect('/server/edit/%s/droplet?error=2' % str(vmid))
    disable_backups(server[0]['id'])
    return redirect('/server/edit/%s/droplet?message=4' % str(vmid))


@app.route('/server/edit/<vmid>/droplet/rename', methods=['POST'])
@login_required
def droplet_rename(vmid):
    server = get_server_id(vmid)
    rename_droplet(server[0]['id'], request.form['name'])
    set_server_name(server[0]['_id'], request.form['name'])
    return redirect('/server/edit/%s/droplet?message=3' % str(vmid))


@app.route('/server/edit/<vmid>/droplet/reset', methods=['GET'])
@login_required
def droplet_reset(vmid):
    server = get_server_id(vmid)
    reset_root_password(server[0]['id'])
    return redirect('/server/edit/%s/droplet?message=3' % str(vmid))


@app.route('/server/edit/<vmid>/droplet/kernel', methods=['POST'])
@login_required
def droplet_change_kernel(vmid):
    server = get_server_id(vmid)
    change_kernel(server[0]['id'], request.form['new_kernel'])
    return redirect('/server/edit/%s/droplet?message=4' % str(vmid))


@app.route('/server/edit/<vmid>/droplet/restoresnapshot', methods=['POST'])
@login_required
def droplet_restore_snapshot(vmid):
    server = get_server_id(vmid)
    restore_snapshot(server[0]['id'], request.form['restore_snapshot_name'])
    return redirect('/server/edit/%s/droplet?message=4' % str(vmid))


@app.route('/server/edit/<vmid>/droplet/rebuild', methods=['POST'])
@login_required
def droplet_rebuild(vmid):
    server = get_server_id(vmid)
    rebuild_droplet(server[0]['id'], request.form['rebuild_image_id'])
    return redirect('/server/edit/%s/droplet?message=4' % str(vmid))

@app.route('/server/edit/<vmid>/droplet')
@login_required
def edit_server_droplet(vmid):
    server = get_server_id(vmid)
    if server[0]['type'] == "do":
        droplet = get_droplet(server[0]['id'])
        do_sizes = get_do_sizes()
        kernels = get_do_kernel_droplet(str(server[0]['_id']))
        snapshots = get_do_snapshots(str(server[0]['_id']))
        do_images = get_do_images()
    else:
        return redirect('/server/edit/%s/local?error=3' % str(vmid))
    return render_template("view_droplet.html", server=server, droplet=droplet, do_sizes=do_sizes, kernels=kernels, do_snapshots=snapshots, do_images=do_images)


@app.route('/server/edit/<vmid>/linode')
@login_required
def edit_server_linode(vmid):
    server = get_server_id(vmid)
    if server[0]['type'] == "linode":
        linode = get_linode(server[0]['id'])
        linode_plans = get_linode_plan()
        linode_facilities = get_linode_facility()
    else:
        return redirect('/server/edit/%s/local?error=3' % str(vmid))
    return render_template("view_linode.html", server=server, linode=linode, linode_plans=linode_plans, linode_facilities=linode_facilities)


@app.route('/server/edit/<vmid>/linode/resize', methods=['POST'])
@login_required
def linode_resize(vmid):
    server = get_server_id(vmid)
    resize_linode(server[0]['id'], request.form['size'])
    return redirect('/server/edit/%s/linode?message=4' % str(vmid))


@app.route('/server/edit/<vmid>/linode/rename', methods=['POST'])
@login_required
def linode_rename(vmid):
    server = get_server_id(vmid)
    rename_linode(server[0]['id'], request.form['linode_name'])
    set_server_name(server[0]['_id'], request.form['linode_name'])
    return redirect('/server/edit/%s/linode?message=4' % str(vmid))


@app.route('/server/edit/<vmid>/linode/ptr', methods=['POST'])
@login_required
def linode_ptr(vmid):
    server = get_server_id(vmid)
    set_linode_rdns(server[0]['id'], request.form['linode_ptr'])
    return redirect('/server/edit/%s/linode?message=4' % str(vmid))


@app.route('/server/new', methods=['POST', 'GET'])
@login_required
def new_server():
    if request.method == "GET":
        images = get_all_images()
        do_images = get_do_images()
        do_sizes = get_do_sizes()
        do_regions = get_do_regions()
        do_sshkeys = get_do_sshkeys()
        linode_plans = get_linode_plan()
        linode_dists = get_linode_distribution()
        linode_facilities = get_linode_facility()
        linode_kernels = get_linode_kernel()
        return render_template("server_create.html", images=images, do_sshkeys=do_sshkeys, do_images=do_images, do_regions=do_regions, do_sizes=do_sizes, linode_plans=linode_plans, linode_dists=linode_dists, linode_facilities=linode_facilities, linode_kernels=linode_kernels)
    elif request.method == "POST":
        type = request.form['provider']
        if type == "do":
            name = request.form['server_name']
            region = request.form['do_region']
            image = request.form['do_image']
            size = request.form['do_plan']
            ssh_key = request.form['ssh_key']
            if "backups" in request.form:
                if ssh_key == 0:
                    droplet = make_droplet(name, region, image, size, backups=1)
                else:
                    droplet = make_droplet(name, region, image, size, backups=1, ssh_key=ssh_key)
            else:
                if ssh_key == 0:
                    droplet = make_droplet(name, region, image, size)   
                else:
                    droplet = make_droplet(name, region, image, size, ssh_key=ssh_key)
                if not droplet.ip_address:
                    new_vm = make_server(name, droplet.disk, droplet.image[
                                         'slug'], droplet.memory, droplet.vcpus, type="do", id=droplet.id, ip=droplet.ip_address, state=2)
                else:
                    new_vm = make_server(name, droplet.disk, droplet.image[
                                         'slug'], droplet.memory, droplet.vcpus, type="do", id=droplet.id, ip=droplet.ip_address)
            get_do_kernels(droplet.id, str(new_vm))
            get_snapshot(droplet.id)
            return redirect('/server/edit/%s/droplet?message=5' % str(new_vm))
        elif type == "linode":
            name = request.form['server_name']
            facility = request.form['linode_facility']
            plan = request.form['linode_plan']
            kernel = request.form['linode_kernel']
            dist = request.form['linode_distribution']
            rootPass = request.form['linode_root']
            plan_record = get_linode_plan_id(plan)
            linodeID = make_linode(facility, plan)
            diskID = make_disk(
                linodeID, dist, name, plan_record[0]['disk'] * 1024, rootPass)
            make_config(linodeID, kernel, name, diskID)
            linode_ip = get_linode_ip(linodeID)
            rename_linode(linodeID, name)
            new_vm = make_server(name, plan_record[0]['disk'], dist, plan_record[0][
                                 'ram'], plan_record[0]['cores'], type="linode", id=linodeID, ip=linode_ip['IPADDRESS']) 
            resp = boot_linode(linodeID)
            if resp == 0:
                return redirect('/server/edit/%s/linode?error=1' % str(new_vm))
            return redirect('/server/edit/%s/linode?message=5' % str(new_vm))
        else:
            name = request.form['server_name']
            ram = request.form['ram']
            disk_size = request.form['disk_size']
            image = request.form['disk_image']
            vcpu = request.form['vcpu']
            type = request.form['provider']

            image_obj = get_image_id(image)

            new_vm = make_server(
                name, disk_size, image_obj[0]['name'], ram, vcpu, type=type, bootdev="cdrom")
            new_vm = str(new_vm)

            result = assign_ip(new_vm)

            if result == 0:
                return redirect('/server/edit/%s/local?error=4' % str(vmid))

            create_event(new_vm)
            startup_event(new_vm)
            create_vm(new_vm, ram, disk_size, image_obj[0]['name'], vcpu, bootdev="cdrom")

            mac_address = get_guest_mac(new_vm)

            set_server_mac(new_vm, mac_address)

            append_dhcp_config(mac_address, result, new_vm)

            message = "Created a new VM with ID %s, name of %s, %sMB of RAM, %sGB disk image." % (
                str(new_vm), str(name), str(ram), str(disk_size))
            create_log(message, 1)

            return redirect('/server/edit/%s/local?message=5' % str(new_vm))


@app.route('/settings/providers/linode', methods=['POST'])
@login_required
def update_linode_api():
    set_config_linode(request.form['linode_api'])
    delete_linode_items()
    get_datacenters()
    get_plans()
    get_kernels()
    get_distributions()
    return redirect('/settings?message=1')


@app.route('/settings/providers/do', methods=['POST'])
@login_required
def update_do_api():
    set_config_do(request.form['do_api'])
    delete_do_items()
    get_dist_images()
    get_sizes()
    get_regions()
    get_all_kernels()
    get_all_sshkeys()
    return redirect('/settings?message=1')


@app.route('/login/reset', methods=['POST'])
@login_required
def login_reset():
    update_admin(session['username'], request.form['password1'])
    return redirect('/settings?message=2')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        try:
            admin = get_admin(request.form['username'])
            if request.form['username'] == admin[0]['username'] and encrypt_password(request.form['password']) == admin[0]['password']:
                session['logged_in'] = True
                session['username'] = request.form['username']
                if 'first_time' in request.form:
                    return redirect('/?first_time=1')
                else:
                    return redirect('/')
            else:
                return redirect('/login?error=1')
        except Exception, e:
            print e[0]
            return redirect('/login?error=1')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')


@app.route('/ajax/get_host_stats')
@login_required
def ajax_memory_stats():
    stats = get_host_statistic_specific(60)
    memory_stats = []
    cpu_user = []
    cpu_system = []
    cpu_guest = []
    iowait_stats = []
    dates = []
    max_memory = []
    for stat in stats:
        memory_stats.append(stat['memory_used'])
        cpu_user.append(stat['cpu_user'])
        cpu_system.append(stat['cpu_system'])
        cpu_guest.append(stat['cpu_guest'])
        iowait_stats.append(stat['iowait'])
        dates.append(stat['date'])
        max_memory.append(stat['total_memory'])
    dict = {"memory": list(reversed(memory_stats)), "cpu_user": list(reversed(cpu_user)), "iowait": list(
        reversed(iowait_stats)), "dates": list(reversed(dates)), "max_memory": list(reversed(max_memory)), "cpu_system":list(reversed(cpu_system)), "cpu_guest":list(reversed(cpu_guest))}
    return jsonify(dict)


@app.route('/utils/sync_status')
@login_required
def syncstatus():
    sync_status()
    return redirect('/?message=3')


@app.route('/utils/import_images')
@login_required
def importimages():
    import_images()
    return redirect('/images?message=3')


@app.route('/utils/sync_host_stats')
@login_required
def updatehoststats():
    get_host_stats()
    message = "Synced host data."
    create_log(message, 1)
    return redirect('/?message=3')


@app.route('/iprange', methods=['POST'])
@login_required
def iprange():
    range_id = make_iprange(request.form['startip'], request.form[
                            'endip'], request.form['subnet'], request.form['netmask'], request.form['gateway'])
    networking.ennumerate_iprange(range_id)
    rebuild_dhcp_config()
    return redirect('/networking?message=6')


@app.route('/iprange/delete/<iprangeid>', methods=['GET'])
@login_required
def iprange_delete(iprangeid):
    rebuild_dhcp_config()
    delete_iprange(iprangeid)
    return redirect('/networking?message=7')


@app.route('/iprange/edit/<iprangeid>', methods=['GET', 'POST'])
@login_required
def iprange_edit(iprangeid):
    if request.method == "GET":
        range = get_iprange_id(iprangeid)
        return render_template("edit_iprange.html", range=range[0])
    elif request.method == "POST":
        set_iprange_all(iprangeid, request.form['startip'], request.form[
                        'endip'], request.form['subnet'], request.form['netmask'], request.form['gateway'])
        rebuild_dhcp_config()
        return redirect('/networking?message=2')


@app.route('/console/<vmid>')
@login_required
def console(vmid):
    config = get_config()
    vm = get_server_id(vmid)
    vncport = make_console(str(vmid))
    return render_template("vnc_auto.html", port=vncport, server_name=vm[0]['name'], domain=config['domain'], server_id=vm[0]["_id"])


@app.route('/ip', methods=['POST', 'GET'])
@app.route('/networking', methods=['POST', 'GET'])
@login_required
def ips():
    if request.method == "GET":
        ips = get_all_ipaddress()
        ranges = get_all_iprange()
        return render_template("networking.html", ips=ips, ranges=ranges)
    else:
        address = request.form['address']
        netmask = request.form['netmask']
        new_ip = make_ipaddress(address, netmask, 0)
        message = "Added new IP %s/%s" % (str(address), str(netmask))
        create_log(message, 1)
        return redirect('/networking?message=6')


@app.route('/ip/edit/<ipid>', methods=['POST', 'GET'])
@login_required
def ip_edit(ipid):
    if request.method == "GET":
        ip = get_ipaddress(ipid)
        return render_template("edit_ip.html", ip=ip)
    elif request.method == "POST":
        set_ipaddress_all(ipid, request.form['address'], request.form[
                          'netmask'], request.form['server_id'])
        return redirect('/ip/edit/%s?message=2' % str(ipid))


@app.route('/ip/unassign/<ipid>', methods=['GET'])
@login_required
def ip_unassign(ipid):
    set_ipaddress_serverid(ipid, 0)
    rebuild_dhcp_config()
    return redirect('/networking?message=2')


@app.route('/ip/assign/<vmid>', methods=['POST'])
@login_required
def ip_assign(vmid):
    ip_id = request.form['ip']
    set_ipaddress_serverid(ip_id, vmid)
    rebuild_dhcp_config()
    return redirect('/server/edit/%s/local?message=2' % str(vmid))


@app.route('/ip/delete/<ipid>', methods=['GET'])
@login_required
def ip_delete(ipid):
    set_ipaddress_serverid(ipid, 0)
    rebuild_dhcp_config()
    delete_ipaddress(ipid)
    return redirect('/networking?message=7')


@app.route('/logs')
@login_required
def logs():
    try:
        page = int(request.args.get('page'))
    except: 
        page = 1
    date = ""
    level = ""
    try:
        date = request.args.get('date')
        level = request.args.get('level')
    except:
        pass
    if date != None and level != None:
        log = get_log_datelevel(date=date, level=int(level))
    elif date != None and level == None:
        log = get_log_datelevel(date=date)
    elif date == None and level != None:
        log = get_log_datelevel(level=int(level))
    else:
        log = get_all_logs()
    return render_template("logs.html", logs=log)


@app.route('/ajax/logs')
@login_required
def ajax_logs():
    log = get_all_logs()
    data = []
    for l in log:
        d = {
            "date":l['date'],
            "level":l['level'],
            "message":l['message']
        }
        data.append(d)
    return jsonify(data=data)


@app.route('/')
@login_required
def index():
    servers = get_all_servers(not_state=3)
    log = get_log_datelevel(date="day", level=3)
    images = get_all_images()
    stats = get_host_statistic_specific(1)
    services = get_all_service()
    all_good = 1
    for service in services:
        if service['status'] == 0:
            all_good = 0
    services = get_all_service()
    try:
        servers[0]
    except:
        servers = None

    try:
        stats[0]
    except:
        stats = None

    return render_template("index.html", servers=servers, images=images, log=log, stats=stats, services=services, all_good=all_good)


@app.route('/destroy/<vmid>')
@login_required
def destroy(vmid):
    vm = get_server_id(vmid)
    if vm[0]['type'] == "do":
        destroy_droplet(vm[0]['id'])
        set_server_state(vmid, 3)
        return redirect('/server/active?message=8')
    elif vm[0]['type'] == "linode":
        delete_linode(vm[0]['id'])
        set_server_state(vmid, 3)
        return redirect('/server/active?message=8')
    else:
        ip = get_ipaddress_server(vmid)

        try:
            set_ipaddress_serverid(ip[0]['_id'], 0)
        except:
            pass

        rebuild_dhcp_config()

        set_server_state(vmid, 3)
        destroy_event(vmid)
        delete_vm(vmid, vm[0]['disk_path'])

        message = "Deleted vm%s." % str(vmid)
        create_log(message, 1)

        return redirect('/server/active?message=8')


@app.route('/reboot/<vmid>')
@login_required
def reboot(vmid):
    server = get_server_id(vmid)
    if server[0]['type'] == "do":
        set_server_state(vmid, 0)
        reboot_droplet(server[0]['id'])
        set_server_state(vmid, 1)
        return redirect('/server/edit/%s/droplet?message=3' % str(vmid))
    elif server[0]['type'] == "linode":
        set_server_state(vmid, 0)
        reboot_linode(server[0]['id'])
        set_server_state(vmid, 1)
        return redirect('/server/edit/%s/linode?message=3' % str(vmid))
    else:
        if server[0]['blocked'] == 1:
            return redirect('/')

        set_server_state(vmid, 0)
        set_server_inconsistent(vmid, 0)

        shutdown_event(vmid)
        shutdown_vm(vmid)

        set_server_state(vmid, 1)

        startup_event(vmid)
        start_vm(vmid)

        return redirect('/server/edit/%s/local?message=3' % str(vmid))


@app.route('/shutdown/<vmid>')
@login_required
def shutdown(vmid):
    server = get_server_id(vmid)
    if server[0]['type'] == "do":
        set_server_state(vmid, 0)
        shutdown_droplet(server[0]['id'])

        return redirect('/server/edit/%s/droplet?message=3' % str(vmid))
    elif server[0]['type'] == "linode":
        set_server_state(vmid, 0)
        shutdown_linode(server[0]['id'])

        return redirect('/server/edit/%s/linode?message=3' % str(vmid))
    else:
        set_server_state(vmid, 0)
        set_server_inconsistent(vmid, 0)

        shutdown_event(vmid)
        shutdown_vm(vmid)

        return redirect('/server/edit/%s/local?message=3' % str(vmid))


@app.route('/server/type/droplet')
@login_required
def server_droplet():
    domains = get_server_type("do")
    return render_template("view.html", domains=domains, type="droplet")


@app.route('/server/type/linode')
@login_required
def server_linode():
    domains = get_server_type("linode")
    return render_template("view.html", domains=domains, type="linode")


@app.route('/server/type/local')
@login_required
def server_local():
    domains = get_server_type("local")
    return render_template("view.html", domains=domains, type="local")


@app.route('/start/<vmid>')
@login_required
def start(vmid):
    server = get_server_id(vmid)
    if server[0]['type'] == "do":
        set_server_state(vmid, 1)
        start_droplet(server[0]['id'])

        return redirect('/server/edit/%s/droplet?message=3' % str(vmid))
    if server[0]['type'] == "linode":
        set_server_state(vmid, 1)
        boot_linode(server[0]['id'])

        return redirect('/server/edit/%s/linode?message=3' % str(vmid))
    else:
        if server[0]['blocked'] == 1:
            return redirect('/')

        set_server_state(vmid, 1)
        set_server_inconsistent(vmid, 0)

        startup_event(vmid)
        start_vm(vmid)

        return redirect('/server/edit/%s/local?message=3' % str(vmid))


@app.route('/server/all')
@login_required
def view_all():
    domains = get_all_servers()
    try:
        domains[0]
    except:
        domains = None
    return render_template("view.html", domains=domains, type="all")


@app.route('/server/active')
@app.route('/server')
@login_required
def view_active():
    domains = get_all_servers(not_state=3)
    try:
        domains[0]
    except:
        domains = None
    return render_template("view.html", domains=domains, type="active")


@app.route('/server/deleted')
@login_required
def view_deleted():
    domains = get_server_state(3)
    try:
        domains[0]
    except:
        domains = None
    return render_template("view.html", domains=domains, type="deleted")


@app.route('/settings', methods=['POST', 'GET'])
@login_required
def settings():
    if request.method == "GET":
        config = get_config()
        try:
            config['disk_directory']
        except:
            return redirect('/setup')
        stats = get_host_statistic_specific(1)
        services = get_service_all()
        return render_template("settings.html", config=config, stat=stats, services=services)
    elif request.method == "POST":
        set_configuration_all(request.form['system'], request.form['domain'], request.form['disk_directory'], request.form['image_directory'], request.form[
                              'config_directory'], request.form['dhcp_configuration'], request.form['dhcp_service'], request.form['novnc_directory'], request.form['pem_location'], request.form['distribution'])
        return redirect('/settings?message=2')


@app.route('/setup', methods=['POST', 'GET'])
def setup():
    if request.method == "GET":
        config = get_config()
        try:
            print config['disk_directory']
        except:
            return render_template("setup.html")
        return "You can only complete setup once."
    elif request.method == "POST":
        make_configuration(request.form['image_directory'], request.form['disk_directory'], request.form['config_directory'], request.form['system_type'], request.form[
                           'domain'], request.form['dhcp_configuration'], request.form['dhcp_service'], request.form['novnc_directory'], request.form['pem_location'], request.form['distribution'])
        make_admin(request.form['username'], request.form['password1'])
        make_host("default")
        get_host_stats()
        make_services()
        add_crontab_entries()
        import_images()
        return redirect('/login?first_time=1')


@app.route('/utils/rebuild_dhcp_config')
@login_required
def rebuild_dhcpconfig():
    rebuild_dhcp_config()
    return redirect('/networking?message=3')


@app.route('/redefine/<vmid>/bootdev/cdrom', methods=['GET'])
@login_required
def setbootdev_cdrom(vmid):
    vm = get_server_id(vmid)
    set_server_bootdev(vmid, "cdrom")
    update_config(vm, bootdev="cdrom")
    try:
        shutdown_event(vm[0]['_id'])
        shutdown_vm(vm[0]['_id'])
    except:
        pass
    redefine_vm(vm[0]['_id'])
    if vm[0]['state'] == 1:
        start_vm(vm[0]['_id'])
        startup_event(vm[0]['_id'])
    return redirect('/server/edit/%s/local?message=3' % str(vmid)) 

@app.route('/redefine/<vmid>/bootdev/hd', methods=['GET'])
@login_required
def setbootdev_hd(vmid):
    vm = get_server_id(vmid)
    set_server_bootdev(vmid, "hd")
    update_config(vm, bootdev="hd")
    try:
        shutdown_event(vm[0]['_id'])
        shutdown_vm(vm[0]['_id'])
    except:
        pass
    redefine_vm(vm[0]['_id'])
    if vm[0]['state'] == 1:
        start_vm(vm[0]['_id'])
        startup_event(vm[0]['_id'])
    return redirect('/server/edit/%s/local?message=3' % str(vmid))


@app.route('/redefine/<vmid>', methods=['GET'])
@login_required
def redefine(vmid):
    vm = get_server_id(vmid)
    update_config(vm)
    try:
        shutdown_event(vm[0]['_id'])
        shutdown_vm(vm[0]['_id'])
    except:
        pass
    redefine_vm(vm[0]['_id'])
    if vm[0]['state'] == 1:
        start_vm(vm[0]['_id'])
        startup_event(vm[0]['_id'])
    return redirect('/server/edit/%s/local?message=3' % str(vmid))


@app.route('/edit/<vmid>/resize', methods=['POST'])
@login_required
def resize_disk(vmid):
    server = get_server_id(vmid)
    if server[0]['state'] == 1:
        set_server_state(vmid, 0)
        set_server_inconsistent(vmid, 0)
        shutdown_event(server[0]['_id'])
        shutdown_vm(server[0]['_id'])
    jobs.resize_disk.delay(vmid, request.form['new_size'])
    return redirect('/server/edit/%s/local?message=9' % str(vmid))


@app.route('/server/edit/<vmid>/local', methods=['POST', 'GET'])
@login_required
def edit(vmid):
    if request.method == "GET":
        server = get_server_id(vmid)
        events = get_events_server(vmid)
        my_ip = get_ipaddress_server(vmid)
        ips = get_all_ipaddress()
        images = get_all_images()
        try:
            print my_ip[0]
        except:
            my_ip = None
        return render_template("view_local.html", server=server, events=events, my_ip=my_ip, ips=ips, images=images)
    elif request.method == "POST":
        set_server_all(vmid, request.form['name'], request.form['disk_size'], request.form['disk_path'],
                       request.form['ram'], int(request.form['state']), request.form[
            'image'], request.form['vcpu'],
            request.form['mac_address'])

        if "push" in request.form:
            # We're going to actually update the config
            vm = get_server_id(vmid)
            update_config(vm)
            try:
                shutdown_event(vm[0]['_id'])
                shutdown_vm(vm[0]['_id'])
            except:
                pass
            redefine_vm(vm[0]['_id'])
            if vm[0]['state'] == 1:
                start_vm(vm[0]['_id'])
                startup_event(vm[0]['_id'])
        return redirect('/server/edit/%s/local?message=2' % str(vmid))


@app.route('/images', methods=['POST', 'GET'])
@login_required
def images():
    if request.method == "GET":
        images = get_all_images()
        return render_template("images.html", images=images)
    else:
        new_image = make_image(
            request.form['name'], request.form['path'], request.form['size'])
        message = "Created new image %s" % str(new_image)
        create_log(message, 1)
        return redirect('/images?message=6')


@app.route('/image/edit/<imageid>', methods=['POST', 'GET'])
@login_required
def edit_image(imageid):
    if request.method == "GET":
        image = get_image(imageid)
        return render_template("edit_image.html", image=image)
    else:
        image = Image.query.filter_by(id=imageid).first()
        name = request.form['name']
        size = request.form['size']
        path = request.form['path']
        set_image_all(imageid, name, path, size)
        return redirect('/image/edit/%s?message=2' % str(imageid))


@app.route('/image/delete/<imageid>')
@login_required
def delete_image_route(imageid):
    delete_image(imageid)
    return redirect('/images?message=7')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10050, debug="true")
