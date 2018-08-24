# Must be run from same dir as terraform variables
# terraform binary must be callable from shell
import os
from MappingCommon import MappingCommon
import subprocess

def main():
    # sets up .terraform/
    mapc = MappingCommon()
    os.chdir(mapc.projectRoot + "/terraform")
    subprocess.Popen(mapc.projectRoot + "/terraform/terraform init", shell=True).wait()
    # starts cvml cluster and a single iteration
    subprocess.Popen(mapc.projectRoot + "/terraform/terraform apply -auto-approve", shell=True).wait()
    return True


if __name__ == "__main__":
    main()
