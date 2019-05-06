# tt4ScriptOpen
This is a script for RPI Python that can control and read Parade TT41701 touch driver
# First Case : tt4P
usage 
Case1 to print the coordinate data
python tt4Main.py --tt4P --filename.txt (print the result to file)
python tt4Main.py --tt4P (do not print to file)

Case 2

Case 3

# Case 4 : tt4R
Case 4 to get the Cm and Cp self test data
python tt4Main.py --tt4R --filename.txt

# Case 5 : tt4S
Case 5 to get the mutual/self data
python tt4Main.py --tt4S --xx --test.txt
xx
0: mutual/self Raw  : self raw data still has issue
1: mutual/self baseline
2: mutual/self diffcount
test.txt : raw data file name 

Known issue
1. case 5 : mutual/self raw and base line self has the issue.
2. ctrl+C : has the issue of unable to turn off the LDO power.
