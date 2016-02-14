import dofunctions
import linodefunctions
import data

data.delete_linode_items()
linodefunctions.get_datacenters()
linodefunctions.get_plans()
linodefunctions.get_kernels()
linodefunctions.get_distributions()

data.delete_do_items()
dofunctions.get_sizes()
dofunctions.get_regions()
dofunctions.get_dist_images()
dofunctions.get_all_kernels()
dofunctions.get_all_sshkeys()
dofunctions.get_snapshots()
