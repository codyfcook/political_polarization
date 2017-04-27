library(Matrix)
library(parallel)
library(textir)
setwd("~/GitHub/political_polarization/2008_election/code")


# --------- ---------------------------
# Fit model with congressional counts 
# -------------------------------------

# Read in data
cong2008_counts <- read.csv("../final_data/cong2008_counts.csv", header=TRUE)
cong2008_covars <- read.csv("../final_data/cong2008_covars.csv", header=TRUE)

# Standardize. Need congcounts as a dgCMatrix for the model (sparce matrix)
covars <- data.frame(gop=cong2008_covars$party, dwnom=cong2008_covars$dwnom)
congcounts = data.matrix(cong2008_counts)
congcounts <- as(congcounts, "dgCMatrix")

# Fire up a cluster
cl <- NULL
cl <- makeCluster(detectCores()) #type="FORK" if on a Mac
# Fit the model using covars and congcounts
fitCS <- mnlm(cl, covars, congcounts, bins=5,gamma=1)
stopCluster(cl)


# Plot fits
par(mfrow=c(1,2))
for(j in c("lose.job","issu.urg")){
  plot(fitCS[[j]], col=c("red","green"))
  mtext(j,line=2) }
legend("topright",bty="n",fill=c("red","green"),legend=names(covars))

# Save coefficients to a csv as loadings in case we later want to check most loaded phrases
B <- coef(fitCS)
library(reshape)
B2 <- data.frame(t(as(B, 'matrix')))
write.csv(B2, "loadings.csv")
mean(B[2,]==0) # sparsity in loadings
## some big loadings in IR
B[1,order(B[2,])[1:30]]
B[1,order(-B[2,])[1:30]]


## plot the IR sufficient reduction space
Z <- srproj(fitCS, congcounts)
par(mfrow=c(1,1))
covars$color[covars$gop==1]='red'
covars$color[covars$gop==0]='blue'
png("../graphs/srproj.png", width=6, height=4, units="in", res=700)
plot(Z, pch=21, bg=covars$color, col=covars$color,main="SR projections", ylab='dw-nominate')
dev.off()

## Forward regression DWNOMINATE with plot for fitted vals
x <- Z
summary(fwd <- lm(covars$dwnom ~ x))
par(mfrow=c(1,1))
png("../graphs/dwnom_fittedvals.png", width=5, height=5, units="in", res=300)
plot(fwd$fitted ~ covars$dwnom, col="lightslategrey", ylab='fitted value', xlab='dw-nominate', xlim=c(-1,1), ylim=c(-1,1))
title(main="DW-NOMINATE Fitted Values")
dev.off()

## Forward regression GOP with plot for fitted vals
x <- Z
summary(fwd <- lm(covars$gop ~ x))
par(mfrow=c(1,1))
png("../graphs/gop_fittedvals.png", width=5, height=5, units="in", res=300)
boxplot(fwd$fitted ~ covars$gop, col="lightslategrey", ylab='fitted value', xlab='party affiliation')
title(main="Party Affiliation Fitted Values")
dev.off()

# Compare to true values
x <- Z
summary(fwd <- lm(covars$dwnom ~ x))
cong_preds <- srproj(B,congcounts)
x <- cong_preds
cong_preds <- predict(fwd, data.frame(x), se.fit=TRUE, level=.95, interval="confidence", type="response")

corr(cong_preds$fit[,1], covars[,2])
plot(cong_preds$fit[,1]~covars[,2], ylim=c(-1,1), xlim=c(-1,1))


# ---------------
# CANDIDATES 
# --------------- 
library(plyr)
cand_counts_raw <- read.csv("../final_data/pres_cand_counts.csv", header=TRUE)
cand_counts = data.matrix(cand_counts_raw)
cand_counts <- as(cand_counts, "dgCMatrix")

## Forward regression: DWNOMINATE
x <- Z
summary(fwd <- lm(covars$dwnom ~ x))
predinve <- srproj(B,cand_counts)
x <- predinve
fwd_preds <- predict(fwd, data.frame(x), se.fit=TRUE, level=.95, interval="confidence", type="response")

cand_labels <- read.csv("../final_data/cand_date_labels.csv", header=FALSE)
cand_results <- cbind(cand_labels,fwd_preds)
#cand_results <- cbind(cand_labels,predinve)
cand_results <- rename(cand_results, c("V1"="candidate", "V2"="date"))

write.csv(cand_results, file="../final_data/candidate_fitted_values.csv")


## ALL SPEECH ##
library(plyr)
cand_counts_raw <- read.csv("../final_data/candidates_all_speech.csv", header=TRUE)
cand_counts = data.matrix(cand_counts_raw)
cand_counts <- as(cand_counts, "dgCMatrix")
x <- Z
summary(fwd <- lm(covars$dwnom ~ x))
predinve <- srproj(B,cand_counts)
x <- predinve
fwd_preds <- predict(fwd, data.frame(x), se.fit=TRUE, level=.95, interval="confidence", type="response")

cand_labels <- read.csv("../final_data/candidates_all_speech_labels.csv", header=FALSE)
cand_results <- cbind(cand_labels,fwd_preds)
cand_results <- rename(cand_results, c("V1"="candidate"))

write.csv(cand_results, file="../final_data/candidates_all_speech_fitted_values.csv")



