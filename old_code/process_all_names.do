#delimit ;
clear all; 
set more off;

cd "/Users/Cody/Documents/School/1 Fourth Year /Third Quarter/ECON_407/Primary Elections/ThomasLOC";

use all_dwnom.dta, clear; 
keep if cong==112; 
keep statenm party name; 
