# Must be run from same dir as terraform variables
# terraform binary must be callable from shell
import os
from MappingCommon import MappingCommon
import subprocess


def main():
    # sets up .terraform/
    mapc = MappingCommon()
    os.chdir(mapc.projectRoot + "/terraform")
    rf_init = subprocess.Popen(mapc.projectRoot + "/terraform/terraform init", shell=True,
                               cwd=mapc.projectRoot + "/terraform").wait()
    # starts cvml cluster and a single iteration
    os.chdir(mapc.projectRoot + "/terraform")
    id_cluster = subprocess.Popen("source " + mapc.projectRoot + "/common/bashrc_mapper.sh ; " +
                                mapc.projectRoot + "/terraform/terraform apply -auto-approve",
                                cwd=mapc.projectRoot + "/terraform", shell=True, stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT).communicate()[0]
    if rf_init == 0 and (not not id_cluster):
        return str.split(str.split(id_cluster, "\n")[-3], " = ")[1]
    else:
        return False


if __name__ == "__main__":
    main()
