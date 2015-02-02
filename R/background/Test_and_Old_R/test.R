# Input args
#args <- commandArgs(TRUE)
#kmlid <- args[1]  # ID of grid cell 
#assignmentid <- args[2]  # Job identifier
#print(kmlid)
#print(assignmentid)
initial.options <- commandArgs(trailingOnly = FALSE)
arg.name <- "--file="
script.name <- sub(arg.name, "", initial.options[grep(arg.name, initial.options)])
script.dir <- dirname(script.name)
print(script.dir)
