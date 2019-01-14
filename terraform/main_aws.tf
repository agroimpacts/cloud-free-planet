provider "aws" {
    region = "us-east-1"
    version = "~> 0.1"
}

resource "aws_security_group" "downloader_jupyter_notebook_sg" {
    name = "downloader_jupyter_notebook_sg"
    # Open up incoming ssh port
    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    # Open up incoming traffic to port 8888 used by Jupyter Notebook
    ingress {
        from_port   = 8888
        to_port     = 8888
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    # Open up outbound internet access
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_instance" "Node" {
    count = 1
    ami = "ami-0f9cf087c1f27d9b1"
    instance_type = "${var.instance_type}"
    key_name = "${var.test_key_name}"
    tags {
        Name = "Jupyter Notebook Planet Download Test Env"
    }
    
    vpc_security_group_ids = ["${aws_security_group.downloader_jupyter_notebook_sg.id}"]    

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
            "/tmp/configure.sh",
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

}

output "node_dns_name" {
    value = "${aws_instance.Node.public_dns}"
}
