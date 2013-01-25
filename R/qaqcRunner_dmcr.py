import subprocess
#score = subprocess.Popen(["Rscript", "KMLAccuracyCheck.1.1.R", "27209", "1A2BC3456"], stdout=subprocess.PIPE).communicate()[0]
#score = subprocess.Popen(["Rscript", "KMLAccuracyCheck.1.1.R", "27209", "1A2BC3457"], stdout=subprocess.PIPE).communicate()[0]
#score = subprocess.Popen(["Rscript", "KMLAccuracyCheck.1.1.R", "3348", "1A2BC3458"], stdout=subprocess.PIPE).communicate()[0]
#score = subprocess.Popen(["Rscript", "KMLAccuracyCheck.1.1.R", "3348", "1A2BC3459"], stdout=subprocess.PIPE).communicate()[0]
#score = subprocess.Popen(["Rscript", "KMLAccuracyCheck.1.1.R", "27209", "1A2BC3460"], stdout=subprocess.PIPE).communicate()[0]
#score = subprocess.Popen(["Rscript", "KMLAccuracyCheck.1.1.R", "3348", "1A2BC3461"], stdout=subprocess.PIPE).communicate()[0]
#score = subprocess.Popen(["Rscript", "KMLAccuracyCheck.1.1.R", "3348", "1A2BC3463"], stdout=subprocess.PIPE).communicate()[0]
#score = subprocess.Popen(["Rscript", "KMLAccuracyCheck.R", "SA364154", "298KPEIB9BAWRHKC1FWV0UD3MH4X0F"], stdout=subprocess.PIPE).communicate()[0]
#score = subprocess.Popen(["Rscript", "KMLAccuracyCheck.R", "SA175522", "2TNCNHMVHVKCPPZGWRY4M79KQKI42Q"], stdout=subprocess.PIPE).communicate()[0]
score = subprocess.Popen(["Rscript", "KMLAccuracyCheck.R", "SA175418", "22CMT6YTWX4H9604NT49CGI6I8SW1E"], stdout=subprocess.PIPE).communicate()[0]
score = float(score)
print "score = %.2f\n" % score

#SA485793   2BG3W5XH0JPPY70ZA3GLVP75K92KE2 
#SA175522   2TNCNHMVHVKCPPZGWRY4M79KQKI42Q   
