import scipy 
import csv

dwnom = [] 
with open("dwnom_final.csv", 'rU') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader: 
    	dwnom.append(row)

reps = [l for l in dwnom if l[1]=='200']
dems = [l for l in dwnom if l[1]=='100']
stats.percentileofscore([float(l[3]) for l in reps], .363)
stats.percentileofscore([float(l[3]) for l in reps], .279)