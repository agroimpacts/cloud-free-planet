# Must be run from same dir as terraform variables
# terraform binary must be callable from shell
import os
from MappingCommon import MappingCommon


def main():
    # sets up .terraform/
    mapc = MappingCommon()
    os.chdir(mapc.projectRoot + "/terraform")
    os.system(mapc.projectRoot + "/terraform/terraform init")
    # starts cvml cluster and a single iteration
    os.system(mapc.projectRoot + "/terraform/terraform apply -auto-approve")
    return True


if __name__ == "__main__":
    main()
