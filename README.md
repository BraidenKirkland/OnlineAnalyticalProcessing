# OnlineAnalyticalProcessing
An implementation of basic online analytical processing queries using Python. This program can be used to extract meaningful data from .csv files. The data returned by the query is sent to standard output in .csv format.
# Getting Started
1. Clone the repository using **git clone https://github.com/YOURUSERNAME/OnlineAnalyticalProcessing.git**
2. Run the program from the command line using the following format 
  **python OLAP.py --input <file-name> [aggregate arguments] [--groupby fieldname]**
    The **-h** flag can be used to view a description of the available command line arguments.
3. Since the data returned is sent to standard output in .csv format, the user can use stream redirection to create a new .csv file that 
 contains the results of the query. e.g. **python OLAP.py --input file-name --count > output-file-name.csv**

# Argument Descriptions

* **--input file-name**
  * **file-name** is the name of the input .csv file to process. It must contain a header line
* **aggregate arguments**
  * indicates which aggregate functions to use on the file. Any number of aggregate functions can be specified. If the user does not      specify any aggregate functions, --count will execute as the default.
* **--groupby name-of-categorical-field**
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
 
 # Examples
 Using the StudentPerformance.csv file provided in the repository.
 Note: When entering commands using the command line, header fields with spaces must be wrapped in quotes.
 
 **Example 1**
 
 $ python OLAP.py --input StudentsPerformance.csv --groupby lunch --mean 'math score' --mean 'reading score' --mean 'writing score'


lunch,mean_math score,mean_reading score,mean_writing score
free/reduced,58.92112676056338,64.65352112676057,63.02253521126761
standard,70.03410852713178,71.65426356589147,70.8232558139535

**Example 2**

$ python OLAP.py --input StudentsPerformance.csv --count --groupby 'parental level of education' --mean 'math score' --mean 'reading score' --mean 'writing score'


parental level of education,count,mean_math score,mean_reading score,mean_writing score
associate's degree,222,67.88288288288288,70.92792792792793,69.8963963963964
bachelor's degree,118,69.38983050847457,73.0,73.38135593220339
high school,196,62.13775510204081,64.70408163265306,62.44897959183673
master's degree,59,69.7457627118644,75.37288135593221,75.67796610169492
some college,226,67.1283185840708,69.46017699115045,68.84070796460178
some high school,179,63.497206703910614,66.93854748603351,64.88826815642459

**Example 3**

$ python OLAP.py --input StudentsPerformance.csv --top 3 'parental level of education'
top_parental level of education


"some college: 226,associate's degree: 222,high school: 196"

