provider "aws" {
    region = "us-east-1"
    version = "~> 0.1"
}

# removed definition of security group because of duplicate error, see this 
# link for the definition and guide to setup 
# https://tsaprailis.com/2017/09/11/How-to-automate-creating-a-virtual-machine-for-data-science/

resource "aws_instance" "Node" {
    count = 1
    ami = "ami-3657fe4c"
    instance_type = "${var.instance_type}"
    key_name = "${var.test_key_name}"
    security_groups = ["jupyterhub"]
    tags {
        Name = "Jupyter Notebook Planet Download Test Env"
    }   

    provisioner "file" {
        source      = "configure.sh"
        destination = "/tmp/configure.sh"

        connection {
            type     = "ssh"
            user     = "ubuntu"
            private_key = "${file("${var.test_key_path}")}"
        }
    }

    provisioner "remote-exec" {
        inline = [
            "chmod +x /tmp/configure.sh",
            "bash /tmp/configure.sh",
        ]
        connection {
            type     = "ssh"
            user     = "ubuntu"
            private_key = "${file("${var.test_key_path}")}"
        }

    }

    provisioner "file" {
        source      = "~/cloud-free-planet"
        destination = "~/planet/"

        connection {
            type     = "ssh"
            user     = "ubuntu"
            private_key = "${file("${var.test_key_path}")}"
        }
    }

    provisioner "file" {
        source      = "configure_env_manually.sh"
        destination = "/tmp/configure_env_manually.sh"

        connection {
            type     = "ssh"
            user     = "ubuntu"
            private_key = "${file("${var.test_key_path}")}"
        }
    }

    provisioner "remote-exec" {
        inline = [
            "chmod +x /tmp/configure_env_manually.sh",
            "bash /tmp/configure_env_manually.sh",
        ]
        connection {
            type     = "ssh"
            user     = "ubuntu"
            private_key = "${file("${var.test_key_path}")}"
        }

    }


}

output "node_dns_name" {
    value = "${aws_instance.Node.public_dns}"
}
