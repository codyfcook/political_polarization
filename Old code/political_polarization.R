library(Matrix)
library(parallel)
library(textir)
setwd("~/Documents/School/1 Fourth Year /Third Quarter/ECON_407/Primary Elections/R")

#main_data <- readMM("cong2012.mtx", header=False)
cong2012counts <- read.csv("cong2012counts.csv", header=TRUE)
covars_raw <- read.csv("covars.csv", header=TRUE)

covars <- data.frame(gop=covars_raw$party, dwnom1=covars_raw$dwnom1)
#covars$cscore <- covars$dwnom1 - tapply(covars$dwnom1,covars$gop,mean)[covars$gop+1]
congcounts = data.matrix(cong2012counts)
congcounts <- as(congcounts, "dgCMatrix")

cl <- NULL
cl <- makeCluster(detectCores(), type="FORK")
fitCS <- mnlm(cl, covars, congcounts, bins=5,gamma=1)
stopCluster(cl)

# Plot fits
par(mfrow=c(1,2))
for(j in c("death.tax","produc.own")){
  plot(fitCS[[j]], col=c("red","green"))
  mtext(j,line=2) }
legend("topright",bty="n",fill=c("red","green"),legend=names(covars))

# coefs
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
png("srproj.png", width=6, height=4, units="in", res=700)
plot(Z, pch=21, bg=covars$color, col=covars$color,main="SR projections", ylab='dw-nominate')
dev.off()
## two pols
Z[c(68,388),]


## Forward regression
x <- Z
summary(fwd <- lm(covars$dwnom1 ~ x))
par(mfrow=c(1,1))
png("fittedvals.png", width=5, height=5, units="in", res=300)
plot(fwd$fitted ~ covars$dwnom1, col="lightslategrey", ylab='fitted value', xlab='dw-nominate')
title(main="DW-NOMINATE Fitted Values")
dev.off()

x <- Z
summary(fwd <- lm(covars$gop ~ x))
par(mfrow=c(1,1))
png("gop_fittedvals.png", width=5, height=5, units="in", res=300)
boxplot(fwd$fitted ~ covars$gop, col="lightslategrey", ylab='fitted value', xlab='party affiliation')
title(main="Party Affiliation Fitted Values")
dev.off()

## plot fits for a few individual terms
terms <- c("month.afghanistan", "unborn.child",
           "manipul.currenc", "advantag.plan",
           "stafford.student","complianc.cost")
png("few_fits.png", width=6, height=8, units="in", res=700)
par(mfrow=c(3,2))
for(j in terms)
{ plot(fitCS[[j]]); mtext(j,font=2,line=2) }
legend(-6.9,-5.1,fill=c('red', 'black'),c('gop', 'dw-nominate'), xpd=NA, ncol=2)
dev.off()


# --------------------
# TESTING PREDICTIONS 
# --------------------
## Forward regression
x <- Z
#summary(fwd <- glm(y ~ x, family = binomial))
summary(fwd <- lm(covars$cscore ~ x))
cong_preds <- srproj(B,congcounts)
x <- cong_preds
cong_preds <- predict(fwd, data.frame(x), se.fit=TRUE, level=.95, interval="confidence", type="response")

corr(cong_preds[,2], covars[,2])
plot(cong_preds[,2]~covars[,2])





# ---------------
# CANDIDATES 
# --------------- 
library(plyr)
cand_counts_raw <- read.csv("pres_cand_counts.csv", header=TRUE)
cand_counts = data.matrix(cand_counts_raw)
cand_counts <- as(cand_counts, "dgCMatrix")
predinv=predict(fitCS,cand_counts_raw,type="response")


## Forward regression: DWNOMINATE
x <- Z
summary(fwd <- lm(covars$dwnom1 ~ x))
predinve <- srproj(B,cand_counts)
x <- predinve
fwd_preds <- predict(fwd, data.frame(x), se.fit=TRUE, level=.95, interval="confidence", type="response")

cand_labels <- read.csv("cand_date_labels.csv", header=FALSE)
cand_results <- cbind(cand_labels,fwd_preds)
#cand_results <- cbind(cand_labels,predinve)
cand_results <- rename(cand_results, c("V1"="candidate", "V2"="date"))

write.csv(cand_results, file="cand_results_2.csv")



## Forward regression: GOP 
x <- Z
y <- factor(covars$gop) 
summary(fwd <- glm(y ~ x, family = binomial))
#summary(fwd <- lm(covars$gop ~ x))
predinve <- srproj(B,cand_counts)
x <- predinve
fwd_preds <- predict(fwd, data.frame(x), se.fit=TRUE, level=.95, interval="confidence", type="response")

cand_labels <- read.csv("cand_date_labels.csv", header=FALSE)
cand_results_gop <- cbind(cand_labels,fwd_preds)
#cand_results <- cbind(cand_labels,predinve)
cand_results_gop <- rename(cand_results_gop, c("V1"="candidate", "V2"="date", "fit.fit"="pred_gop"))

write.csv(cand_results_gop, file="cand_results_gop_2.csv")

# ---------------
# PRIMARY VS GENERAL 
# --------------- 
pre_post_counts_raw <- read.csv("pre_post_counts.csv", header=TRUE)
pre_post_counts = data.matrix(pre_post_counts_raw)
pre_post_counts <- as(pre_post_counts, "dgCMatrix")

## Forward regression
x <- Z
summary(fwd <- lm(covars$dwnom ~ x))
predinve <- srproj(B,pre_post_counts)
x <- predinve
fudge = 1500
x[1,3]=fudge
x[2,3]=fudge
x[3,3]=fudge
x[4,3]=fudge

fwd_preds <- predict(fwd, data.frame(x), se.fit=TRUE, level=.95, interval="confidence", type="response")

pre_post_labels <- read.csv("pre_post_labels.csv", header=FALSE)
pre_post_results <- cbind(pre_post_labels,fwd_preds)
#pre_post_results <- rename(pre_post_results, c("V1"="candidate", "V2"="date"))

write.csv(pre_post_results, file="pre_post_results_dw_2.csv")

## GOP ## 
pre_post_counts_raw <- read.csv("pre_post_counts_2.csv", header=TRUE)
pre_post_counts = data.matrix(pre_post_counts_raw)
pre_post_counts <- as(pre_post_counts, "dgCMatrix")

## Forward regression
x <- Z
y <- factor(covars$gop) 
summary(fwd <- glm(y ~ x, family = binomial))
predinve <- srproj(B,pre_post_counts)
x <- predinve
fudge = 2000
x[1,3]=fudge
x[2,3]=fudge
x[3,3]=fudge
x[4,3]=fudge

fwd_preds <- predict(fwd, data.frame(x), se.fit=TRUE, level=.95, interval="confidence", type="response")

pre_post_labels <- read.csv("pre_post_labels.csv", header=FALSE)
pre_post_results <- cbind(pre_post_labels,fwd_preds)
#pre_post_results <- rename(pre_post_results, c("V1"="candidate", "V2"="date"))

write.csv(pre_post_results, file="pre_post_results_gop_2.csv")




