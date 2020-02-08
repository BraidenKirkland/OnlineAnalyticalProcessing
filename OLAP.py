#!/usr/bin/env python3

import csv
import argparse
import sys
import os

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Takes one argument which is the csv file you want to read data from.")
    parser.add_argument("--top", nargs=2, help="Computes the top k most common values of the specified categorical field")
    parser.add_argument("--groupby", nargs=1, help="Groups the output by the specified categorical field")
    parser.add_argument("--count", action="store_true", help="Counts the number of records")
    parser.add_argument("--min", nargs='*', action='append', help="Computes the minimum value of the specified numeric field")
    parser.add_argument("--max", nargs='*', action='append', help="Computes the maximum value of the specified numeric field")
    parser.add_argument("--mean", nargs='*', action='append', help="Computes the mean value of the specified numeric field")
    parser.add_argument("--sum", nargs="*", action='append', help="Computes the sum value of the specified numeric field")
    args = parser.parse_args()

    # Initial command line input error checks

    if(args.min and (len(args.min) < 1 or [] in args.min)):

        print("Error: You must provide the aggregate min with one argument everytime it is called", end="", file=sys.stderr)
        exit(6)
    
    if(args.max and (len(args.max) < 1 or [] in args.max)):

        print("Error: You must provide the aggregate max with one argument everytime it is called", end="", file=sys.stderr)
        exit(6)
    
    if(args.mean and (len(args.mean) < 1 or [] in args.mean)):

        print("Error: You must provide the aggregate mean with one argument everytime it is called", end="", file=sys.stderr)
        exit(6)
    
    if(args.sum and (len(args.sum) < 1 or [] in args.sum)):

        print("Error: You must provide the aggregate sum with one argument everytime it is called", end="", file=sys.stderr)
        exit(6)

    if(args.input==None):

        print("Error: You must specify a file using the command --input <filename>", end="", file=sys.stderr)
        exit(6)


    inputs = sys.argv
    keywords = ["--min", "--mean", "--max", "--sum", "--top"]

    # inputs is a list of all commands entered minus any digits that may have been present in the arguments

    for input in inputs:

        if (input.isdigit()):

            inputs.remove(input)

    
    # populates the list of tuples called command_order where each tuple contains the command name followed by the field
    # there is an exception for 'count' which is just listed as an individual string (not part of a tuple)
    # command_order is used to help determine the order in which to compute arguments and display the names in the header

    command_order = []

    for i in range(len(inputs)):

        if(inputs[i] in keywords):

            command_order.append((inputs[i].strip("--"), inputs[i+1].lower()))

        elif(inputs[i] == '--count'):

            command_order.append('count')
    
    # Tries opening the input file, throws an error and exits if file does not exist or is not readable

    try:
        with open(args.input, 'r', encoding="utf-8-sig") as input_file:

            if(not args.input.endswith(".csv")):

                print("Error: The file you entered in not a csv file. This program only works for csv files.", file=sys.stderr)
                exit(6)

            csv_reader = csv.DictReader(input_file)

            header_line = csv_reader.fieldnames
            
            if(header_line == None):

                print("Error:{} is empty".format(args.input), file=sys.stderr)
                exit(6)

            header_line = [i.lower() for i in header_line]
  
            # look through the aggregate commands entered and see if 
            # - the user entered a field that does not exist

            for command in command_order:

                if(command != 'count' and command[0] != 'top'):

                    if(command[1] not in header_line):

                        print("Error: {}:no field with name \'{}\' found".format(args.input, command[1]), end="", file=sys.stderr)
                        exit(8)

            # if the user called top k
            # 1. check if k is an integer greater than 0
            # 2. check the specified field is a valid categorical field

            if(args.top):

                k = args.top[0]
                categorical_field = args.top[1].lower()
                args.top[1] =  categorical_field
                        
                if(k.isnumeric() == False or int(k) <= 0):
                    
                    print("Error: {} : The first argument for top must be an integer greater than 0.".format(args.input), end="", file=sys.stderr)
                    exit(6)
                    
                if(categorical_field not in header_line):
                    
                    print("Error: {}:no field with name \'{}\' found".format(args.input, args.top[1]), end="", file=sys.stderr)
                    exit(6)


            # if the user called group-by
            # - check that field they requested exists in the input file

            if(args.groupby):

                args.groupby[0] = args.groupby[0].lower()

                if (args.groupby[0] not in header_line):

                    print("Error: {}:no group-by argument with name \'{}\' found".format(args.input, args.groupby[0]), end="", file=sys.stderr)
                    exit(9)

            # Categories is the main dictionary that holds all of the information required to perform the necessary aggregate calculations
           
            categories = {}
            grand_total = {'count': 0}

            for field in header_line:

                grand_total[field] = []

                if((args.groupby and args.groupby[0] == field) or (args.top and args.top[1] == field)):

                    categories[field] = {}

           # total_lines tracks the number of lines read
           # current_line tracks where we are at the file. since the first line of the file is headers,
           # the actual data starts on line 2 of the file

            total_lines = 0
            current_line = 2

            # read in a line from the csv reader, represented as a dictionary
            for line in csv_reader:

                # new line is a dictionary that is the same as line, but all keys have been converted to lowercase
                new_line = {}

                for field in line:

                    new_line[field.lower()] = line[field]
                
                # now fill the dictionary grand_total which is used to perform calculations in the event the
                # user only enters --input <some_file> or --input <some_file> --count
                # grand_total stores field names and a list of the tuples (line_number, value)
                # the value portion of each tuple is converted to a float if possible

                for field in new_line:

                    if(field in grand_total):

                        try:

                            element = (current_line, float(new_line[field]))
                            grand_total[field].append(element)

                        except:

                            element = (current_line, new_line[field])
                            grand_total[field].append(element)

                # The following block of code fills the main dictionary categories
                # Data stored in categories is used to perform calculations based on the specified aggregates

                for field in header_line:

                    if field in categories:

                        if (new_line[field] not in categories[field]):

                            categories[field][new_line[field]] = {field: new_line[field], 'count': 1}

                            for other_field in header_line:

                                if(other_field != field):

                                    if((args.groupby and args.groupby[0] == other_field) or (args.top and args.top[1] ==other_field)):

                                        categories[field][new_line[field]][other_field] = [1, new_line[other_field]]

                                    else:

                                        try:

                                            categories[field][new_line[field]][other_field] = [(current_line, float(new_line[other_field]))]

                                        except:

                                            categories[field][new_line[field]][other_field] = [(current_line, new_line[other_field])]


                        else:

                            categories[field][new_line[field]]['count'] += 1

                            for other_field in header_line:

                                if(other_field != field):

                                    if((args.groupby and args.groupby[0] == other_field) or (args.top and args.top[1] ==other_field)):

                                        categories[field][new_line[field]][other_field].append(new_line[other_field])
                                        categories[field][new_line[field]][other_field][0] += 1

                                    else:    
                                       
                                        try:

                                            categories[field][new_line[field]][other_field].append((current_line, float(new_line[other_field])))

                                        except:

                                            categories[field][new_line[field]][other_field].append((current_line, new_line[other_field]))

                total_lines += 1
                current_line += 1

            grand_total['count'] = total_lines

    except FileNotFoundError:

        print("Error: File not found or cannot be read!", end="", file=sys.stderr)
        exit(6)

    # The following decision block decides what functions to call based off of the specified arguments
        
    if (args.groupby and args.top):    

        groupby(categories, command_order, args)
    
    elif (args.top):

        k = args.top[0]
        k = int(k)
        categorical_field = args.top[1].lower()
        cardinality = len(list(categories[args.top[1]].keys()))

        if(cardinality > 20 and k > 20):

            print("Error: {}: {} has been capped at 20 distinct values".format(args.input, categorical_field), end="", file=sys.stderr)
            print("top_" + categorical_field + "_capped")
            print(top(categories, 20, categorical_field))
      
        else:

            print("top_" + categorical_field)
            print(top(categories, k, categorical_field))
    
    elif(args.groupby):

        groupby(categories, command_order, args)
    
    else:

        if(len(command_order) == 0 or command_order == ['count']):

            print('count')
            print(total_lines)

        else:

            print_total(grand_total, command_order, total_lines, args)

def get_numeric(tuple):

    """
    Takes in a tuple containing two elements and returns the second element which is the numeric element.

    """
    
    return tuple[1]

def top(data, k, category, key_list=None):

    """
    Computes the top k most common values in the categorical field name specified by the user

    Returns a string containing the name of each value followed by it's count

    Example: --top 3 ticker
             "ibm: 14059,dis: 12072,axp: 11556"

    If there are less values than the user requested, all of the values in that category are printed.
    If there are more than 20 distinct values and the user called for more than 20 values  (e.g. top 25 ticker),
    the output will only contain the counts of the top 20 values
    
    """

    field_plus_count = []

    if(key_list == None):

        for field in data[category]:

            field_plus_count.append((field, data[category][field]['count']))

    else:

        for field in data[category]:

            if(field in key_list):

                field_plus_count.append((field, data[category][field]['count']))

    if(k > len(field_plus_count)):

        k = len(field_plus_count)

    field_plus_count.sort(key=get_numeric, reverse=True)

    output_string  = ''
    output_string += '\"'

    for i in range(k):


        if( i < k-1):

            output_string += (str(field_plus_count[i][0]).strip() + ": " + str(field_plus_count[i][1]).strip() + ",")

        else:

            output_string += (str(field_plus_count[i][0]).strip() + ": " + str(field_plus_count[i][1]).strip())

    
    output_string += '\"'

    return output_string

def print_total(data, command_order, line_count, args):

    """
    print_total() prints handles printing all of the requested aggregates in the event that group-by was not called.

    The printed result is the computed values of each aggregates in the order they were entered on the command line.

    """

    header_string = ''
    value_string  = ''

    for command in command_order:

        if(command != 'count'):

            header_string += command[0] + "_" + command[1] + ","

        else:

            header_string += 'count' + ","

    if(header_string.endswith(",")):

        header_string = header_string[:-1]

    print(header_string)

    
    for command in command_order:

        if(command != 'count'):

            if (command[0] == 'max'):

                value_string += str(custom_max(data[command[1]], args, command[1])) + ","

            if(command[0] == 'min'):

                value_string += str(custom_min(data[command[1]], args, command[1])) + ","

            if(command[0] == 'mean'):

                value_string += str(mean(data[command[1]], args, command[1])) + ","

            if(command[0] == 'sum'):

                value_string += str(numeric_sum_count(data[command[1]], args, command[1])[0]) + ","

        else:

            value_string += str(line_count) + ","
    
    if value_string.endswith(","):

        value_string = value_string[:-1]

    print(value_string)


def non_numeric_error_check(data, command_order, fields, flag):

    non_nums_max = 0
    non_nums_min = 0
    non_nums_mean = 0
    non_nums_sum = 0

    for field in fields:

        for command in command_order:

            if(command[0] == 'max'):

               for element in  data[flag][field][command[1].lower()]:

                   try:
                       float(element[1])

                   except:

                       non_nums_max += 1

            if(command[0] == 'min'):

                for element in data[flag][field][command[1].lower()]:

                    try:
                        float(element[1])

                    except:

                        non_nums_min += 1

            if(command[0] == 'mean'):

                for element in data[flag][field][command[1].lower()]:

                    try:
                        float(element[1])

                    except:

                        non_nums_mean += 1

            if(command[0] == 'sum'):



                for element in data[flag][field][command[1].lower()]:

                    try:
                        float(element[1])

                    except:

                        non_nums_sum += 1

        if (max(non_nums_max, non_nums_min, non_nums_mean, non_nums_sum) > 100):
            
            return True

    return False
    


def groupby(data, command_order, args):

    """
    Computes all requested aggregates for each distinct value in the categorical field passed to group-by
    up to a maximum of 20.

    If there are more than 20 distinct values in the specified categorical field, a message gets printed to stderr and
    another function, group_by_overflow, gets called to handle printing the remaining records.
    """

    top_info = args.top
    flag = args.groupby[0]
    file_name = args.input

    fields = list(data[flag].keys()) 
    
    error_present = non_numeric_error_check(data, command_order, fields, flag)

    num_fields = len(fields)
    fields.sort()
    cap = 20
    num_out = 0
    
    if(top_info):

        k = int(top_info[0])
    
    header_string = flag.lower() + ","

    for command in command_order:

        if(command[1] == flag):

            print("Error: {} : can't compute aggregate {} on group-by field \'{}\'".format(args.input, command[0], command[1]), end="", file=sys.stderr)
            exit(6)

        if (command[0] =='top' and k > 20 and num_fields > 20):

            header_string += command[0] + "_" + command[1] + "_capped,"
            print("Error: {}: {} has been capped at 20 distinct values".format(args.input, args.top[1].lower()), end="", file=sys.stderr)
        
        elif(command != 'count'):

            header_string += command[0] + "_" + command[1] + ","

        else:

            header_string += 'count' + ","
    
    if(header_string.endswith(",")):

        header_string = header_string[:-1]
    
    if(not error_present):

        print(header_string)

    for field in fields:

        value_string  = ''

        if(num_out < cap):

            value_string += field + ","

            for command in command_order:

                if(command != 'count'):

                    if(command[0] == 'max'):

                        value_string += str(custom_max(data[flag][field][command[1].lower()], args, command[1])) + ","

                    if(command[0] == 'min'):

                        value_string += str(custom_min(data[flag][field][command[1].lower()], args, command[1])) + ","

                    if(command[0] == 'mean'):

                        value_string += str(mean(data[flag][field][command[1].lower()], args, command[1])) + ","

                    if(command[0] == 'sum'):

                        value_string += str(numeric_sum_count(data[flag][field][command[1].lower()], args, command[1])[0]) + ","

                    if(command[0] == 'top'):

                        if(len(data[flag][field][command[1].lower()]) > 1):

                            value_string += top(data, k, command[1], key_list=data[flag][field][command[1].lower()]) + ","

                        else:

                            value_string += top(data, k, command[1], None) + ","
                else:

                    value_string += str(data[flag][field]['count']) + ","

            if(value_string.endswith(",")):

                value_string = value_string[:-1]
               
            if(not error_present):

                print(value_string)

        num_out += 1

    # The code below handles the case when group-by has been called on a category with more than 20 values

    if (num_fields > cap):

        print("Error: {}:{} has been capped at 20 distinct values".format(file_name, flag), file=sys.stderr)
        print("Error: {}:group-by argument {} has high cardinality".format(file_name, flag), file=sys.stderr)

        group_by_overflow(data, command_order, fields[20:], args)
        

def numeric_sum_count(tuple_list, args, field_name):

    """
    Takes a list of two-element tuples as a parameter where the first element represents the line number
    and the second element represents the value of the numerical field at that line number
    
    Returns: a tuple containing 
             1. the total sum of all numeric elements in the tuple_list
             2. the total count of all numeric elements in the tuple_list

    Throws an error and exits with code 7 if there are more than 100 non-numeric elements in the tuple_list
    """

    total_sum = 0
    numeric_count = 0
    non_numeric_count = 0

    for element in tuple_list:

        try:

            if(type(element) == tuple):
                
                total_sum += float(element[1])
                numeric_count += 1

        except:

            non_numeric_count += 1
            print("Error:{}:{} can't compute mean or sum on non-numeric value \'{}\'".format(args.input, element[0], element[1]), file=sys.stderr)

        if(non_numeric_count > 100):

            print("Error:{}:more than 100 non-numeric values found in aggregate column \'{}\'".format(args.input, field_name), file=sys.stderr)
            exit(7)

    if(numeric_count == 0):
        
        return ("NaN", "NaN")

    return (total_sum, numeric_count)


def custom_max(tuple_list, args, field_name):

    """
    Takes a list of two-element tuples as a parameter where the first element represents the line number
    and the second element represents the value of the numerical field at that line number
    
    Returns: the maximum value of the numerical field in the tuple list

    Throws an error and exits if there are more than 100 non-numeric elements in the tuple_list
    """

    maximum = -100000000000.0
    non_numeric_count = 0
    total_numeric_count = 0

    for element in tuple_list:

        try:

            if (type(element) == tuple and maximum < float(element[1])):

                maximum = float(element[1])

                total_numeric_count += 1

        except:

            non_numeric_count += 1
            print("Error:{}:{} can't compute max on non-numeric value \'{}\'".format(args.input, element[0], element[1]), file=sys.stderr)

        if(non_numeric_count > 100):

            print("Error:{}:more than 100 non-numeric values found in aggregate column \'{}\'".format(args.input, field_name), file=sys.stderr)
            exit(7)

    if(total_numeric_count == 0):
            
        return "NaN"
    
    return maximum

def custom_min(tuple_list, args, field_name):

    """
    Takes a list of two-element tuples as a parameter where the first element represents the line number
    and the second element represents the value of the numerical field at that line number
    
    Returns: the minimum value of the numerical field in the tuple list

    Throws an error and exits if there are more than 100 non-numeric elements in the tuple_list
    """

    minimum = 100000000000.0
    non_numeric_count = 0
    total_numeric_count = 0

    for element in tuple_list:

        try:

            if (type(element) == tuple and minimum > float(element[1])):

                minimum = float(element[1])
                
                total_numeric_count += 1
        except:

            non_numeric_count += 1
            print("Error:{}:{} can't compute max on non-numeric value \'{}\'".format(args.input, element[0], element[1]), file=sys.stderr)

        if(non_numeric_count > 100):

            print("Error:{}:more than 100 non-numeric values found in aggregate column \'{}\'".format(args.input, field_name), file=sys.stderr)
            exit(7)

    if(total_numeric_count == 0):
        
        return "NaN"
    
    return minimum


def mean(data, args, field_name):

    """
    Calculates and returns the mean value of a numerical field.
    Makes use of the helper function numeric_sum_count.
    """
    info = numeric_sum_count(data, args, field_name)

    if(info[0] == "NaN" or info[1] == "NaN"):
        
        return "NaN"

    return info[0]/info[1]




def group_by_overflow(data, command_order, fields, args):

    """
    In the event the cardinality of the group-by field is greater than 20,
    this function prints a summary of the results for the remaining elements in the specified field.
    The output format is: _OTHER value1, value2, ...., 
    """

    flag = args.groupby[0]

    value_string = '_OTHER' + ","

    for command in command_order:

        total_sum = 0
        total_count = 0
        
        if(command == 'count'):

            count = 0

            for field in fields:

               try:
                   count += len(data[flag][field]['count'])

               except:

                  count += data[flag][field]['count']

            value_string += str(count) + ","
        
        else:

            if(command[0] == 'max'):

                maximum = 0

                try:

                    for field in fields:

                        current_max = custom_max(data[flag][field][command[1].lower()], args, command[1])

                        if(current_max > maximum):

                            maximum = current_max

                    value_string += str(maximum) + ","

                except:
                    
                    value_string += "NaN"


            if(command[0] == 'min'):

                minimum = sys.maxsize

                try:

                    for field in fields:

                        current_min = custom_min(data[flag][field][command[1].lower()], args, command[1])

                        if(current_min < minimum):

                            minimum = current_min

                    value_string += str(minimum) + ","

                except:
                    
                    value_string += "NaN"


            if(command[0] == 'sum'):

                total_sum = 0

                try:

                    for field in fields:

                        total_sum += numeric_sum_count(data[flag][field][command[1].lower()], args, command[1])[0]

                    value_string += str(total_sum) + ","

                except:

                    value_string += "NaN"

            
            if(command[0] == 'mean'):

                total_sum = 0
                total_count = 0

                for field in fields:

                    sum_and_count = numeric_sum_count(data[flag][field][command[1].lower()], args, command[1])
                    total_sum += sum_and_count[0]
                    total_count += sum_and_count[1]

                average = total_sum/total_count
                value_string += str(average) + ","

            if(command[0] == 'top'):

                field_plus_count = []

                for field in fields:

                    field_plus_count.append((field, data[flag][field]['count']))

                field_plus_count.sort(key=get_numeric, reverse=True)

                k = int(args.top[0])

                if(k > 20):

                    k = 20

                if(k > len(field_plus_count)):

                    k = len(field_plus_count)

                for i in range(k):

                    value_string += ('\"' + str(field_plus_count[i][0]).strip() + ": " + str(field_plus_count[i][1]).strip() + '\"' + ",")


    if(value_string.endswith(",")):

        value_string = value_string[:-1]

    print(value_string)


if __name__ == "__main__":
    main()

