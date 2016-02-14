import data
import subprocess
import log


def check_services():
    services = data.get_all_service()
    command = "ps aux"
    ps = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    for service in services:
        if service['_id'] == "isc-dhcp-server":
            if "dhcpd" in output and service['status'] == 0:
                data.set_service_status(service['_id'], 1)
            elif "dhcpd" not in output and service['status'] == 1:
                data.set_service_status(service['_id'], 0)
        else:
            if service['_id'] in output and service['status'] == 0:
                data.set_service_status(service['_id'], 1)
            elif service['_id'] not in output and service['status'] == 1:
                data.set_service_status(service['_id'], 0)


def make_services():
    config = data.get_config()
    data.make_service(config['dhcp_service'], 0)
    data.make_service("celery", 0)
    data.make_service("gunicorn", 0)
    data.make_service("rabbitmq-server", 0)
    data.make_service("mongod", 0)
    check_services()


def manipulate_service(service_name, action):
    check = data.get_service_id(service_name)
    if check.count() == 0 or service_name == "celery" or service_name == "gunicorn" or service_name == "mongod":
        # We want to make sure you can only restart services
        # that are defined in the database. If not, return 0
        # Also don't shut down things we need to function
        return 0
    action_perf = ""
    if action == 1:
        action_perf = "start"
    elif action == 2:
        action_perf = "restart"
    elif action == 0:
        action_perf = "stop"
    command = "service %s %s" % (str(service_name), str(action_perf))
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.stdout.read()
    message = "Attempted to %s %s, received output: %s" % (
        str(action_perf), str(service_name), str(output))
    log.create_log(message, 1)
