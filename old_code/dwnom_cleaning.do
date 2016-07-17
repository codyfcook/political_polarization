#delimit ;
clear all; 
set more off;

cd "/Users/Cody/Documents/School/1 Fourth Year /Third Quarter/ECON_407/Primary Elections/DWNOM";

use house_dwnom.dta, clear; 
	keep if cong==112; 
	keep statenm party name dwnom1 dwnom2; 
	gen chamber="house"; 

export delimited using "house_dwnom_clean.csv", replace; 

use senate_dwnom.dta, clear; 
	keep if cong==112; 
	keep statenm party name dwnom1 dwnom2; 
	gen chamber = "senate";

export delimited using "senate_dwnom_clean.csv"; 
