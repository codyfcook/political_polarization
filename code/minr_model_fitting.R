library(Matrix)
library(parallel)
library(textir)
setwd("~/GitHub/political_polarization/code")



# --------- ---------------------------
# Fit model with congressional counts 
# -------------------------------------

# Read in data
cong2016_counts <- read.csv("../final_data/cong2016_counts.csv", header=TRUE)
cong2016_covars <- read.csv("../final_data/cong2016_covars.csv", header=TRUE)

# Standardize. Need congcounts as a dgCMatrix for the model (sparce matrix)
covars <- data.frame(gop=cong2016_covars$party, dwnom=cong2016_covars$dwnom)
congcounts = data.matrix(cong2016_counts)
congcounts <- as(congcounts, "dgCMatrix")

# Fire up a cluster
cl <- NULL
cl <- makeCluster(detectCores()) #type="FORK" if on a Mac
# Fit the model using covars and congcounts
fitCS <- mnlm(cl, covars, congcounts, bins=5,gamma=1)
stopCluster(cl)




