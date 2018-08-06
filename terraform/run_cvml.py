#Must be run from same dir as terraform variables 
# terraform binary must be callable from shell
import os
# sets up .terraform/  
os.system("terraform init")
# starts cvml cluster and a single iteration
os.system("terraform apply -auto-approve")



