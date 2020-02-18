# OnlineAnalyticalProcessing
An implementation of basic online analytical processing queries using Python. This program can be used to extract meaningful data from .csv files
# Getting Started
1. Clone the repository using **git clone https://github.com/YOURUSERNAME/OnlineAnalyticalProcessing.git**
2. Run the program from the command line using the following format 
  **python OLAP.py --input <file-name> [aggregate arguments] [--groupby <fieldname>]**

# Argument Descriptions

* **--input file-name**
  * **file-name** is the name of the input .csv file to process. It must contain a header line
* **aggregate arguments**
  * indicates which aggregate functions to use on the file. Any number of aggregate functions can be specified. If the user does not      specify any aggregate functions, --count will execute as the default.
* **--group_by name-of-categorical-field**
  * the program will compute the requested aggregates for each categorical field
  
 # Aggregates
 
 |Argument|Description|Output Format|
 |------------|-----------|-------------|
 |--count|counts the number of records|an integer value|
 |--sum name-of-numeric-field|calcuates the sum of the specified numeric field|a floating point number|
 |--min name-of-numeric-field|calculates mean value of the specified numeric field|a floating point number|
 |--max name-of-numeric-field|calculates the maximum value of the specified numeric field| a floating point number|
 |--mean name-of-numeric-field|calculates the mean value of the specified numeric field| a floating point number|
 |--top k name-of-categorical-field|calculates the top k most common occuring categorical fields in the file (each row contributes 1)|a string listing the names of the top fields and their counts e.g. "Led Zeppelin: 327, ACDC: 245, Lynyrd Skynyrd: 197"|
 
