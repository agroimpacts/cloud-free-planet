# Must be run from same dir as terraform variables
# terraform binary must be callable from shell
import os
from MappingCommon import MappingCommon
import subprocess

def main():
    # sets up .terraform/
    mapc = MappingCommon()
    os.chdir(mapc.projectRoot + "/terraform")
    tf_init = subprocess.Popen(mapc.projectRoot + "/terraform/terraform init", shell=True, cwd = mapc.projectRoot + "/terraform").wait()
    # starts cvml cluster and a single iteration
    os.chdir(mapc.projectRoot + "/terraform")
    tf_apply =  subprocess.Popen(mapc.projectRoot + "/terraform/terraform apply -auto-approve", shell=True, cwd = mapc.projectRoot + "/terraform").wait()
    if tf_init == 0 and tf_apply == 0:
        return True
    else:
        return False


if __name__ == "__main__":
    main()
