# test error logging for KMLAccuracyCheck.R

initial.options <- commandArgs(trailingOnly = FALSE)
arg.name <- "--file="
script.name <- sub(arg.name, "", 
                   initial.options[grep(arg.name, initial.options)])
script.dir <- dirname(script.name)
arg <- commandArgs(TRUE)
val <- as.numeric(arg[1])
print(val)
#print(script.dir)
#print(arg)
source(paste(script.dir, "getDBName.R", sep="/"))

log.file.path <- paste(project.root, "/log/", sep="")
#print(log.file.path)

pid <- Sys.getpid()
pstart.string <- paste0("KMLgenerate invoked at ", format(Sys.time(), "%a %b %e %H:%M:%S %Z %Y"), 
                       " (pid ", pid, ")")

options(digit.secs = 4)  # Display milliseconds for time stamps 

# Initialize Rlog file to record daemon start time and which kml ids written
rlog.hdr <- rbind("Log of script start, KML ids written and times, from KML", 
                  "##########################################################",
                  "")
logfname <- paste0(log.file.path, "KML_accuracy_check_error.log")  # Log file name
#print(logfname)
if(!file.exists(logfname)) {
  write(rlog.hdr, file = logfname)
}
logf <- file(logfname, open = "at")
#write(rbind(pstart.string, ""), file = logfname, append = TRUE)
write(rbind("", pstart.string, ""), file = logfname, append = TRUE)
sink(logf, append = TRUE, type = "message")
a <- log(val)
suppressWarnings(sink())

