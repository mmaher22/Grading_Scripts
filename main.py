# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 12:55:55 2019
@author: s-moh
"""
import re
import json
import xlsxwriter
import pandas as pd
from glob import glob
from HomeworkTask import HomeworkTask
from Submission import Submission
from pathlib import Path
import argparse

############ Filtering Submissions to keep most recent one only #################            
def filter_submissions(path, rerun_flag):
    with open("./logs/failed_nb.txt", "w") as f:
        f.write('')
    submissions = list(sorted(path.glob('*.ipynb')))
    #print(submissions)
    final_submissions = []
    ids = []
    for s in range(len(submissions)-1, -1, -1):
        fname, _ = submissions[s].name.split(".") # ID_TRIAL.ext
        student_id, trial_no = fname.split("_") #Split ID and TRIAL nr
        #print('Student ID:', student_id, ',Trial NO:', trial_no, ' -->', submissions[s])
        if student_id in ids:
            continue
        else:
            try:
                processed_submission = Submission(student_id, str(submissions[s]), trial_no, rerun_flag)
                final_submissions.append(processed_submission)
                ids.append(student_id)
            except Exception as e:
                with open("./logs/failed_nb.txt", "a") as f:
                    f.write(str(student_id) + '\n')
                print('Error 1.1: Error Reading Submission of Student ID ' + student_id + '-->', e)
    return final_submissions
############ END: Filtering Submissions to keep most recent one only #################


#### BEGIN: READ CONFIGURATION ########
def read_config(config_path='./conf.json'):
    try:
        with open(config_path, 'r', encoding="utf8") as f:
            data = json.load(f)

        hw_no = data['HW_NO'] #Homework number
        path = Path(data['HW_Path']) #HW Submission Folder
        # rerun_flag = data['Rerun']
        # if 'plag_threshold' in data.keys():
        #     plagiarsim_threshold = data['plag_threshold']
        # else:
        #     plagiarsim_threshold = 2
        # task_begin_flag = ''
        # task_end_flag = ''

    except Exception as e:
        print('Error 0.1: Error Reading JSON Configuration File - ', e)
        raise e


    # Initialize Information for each task
    hw_tasks = []
    for task in data['Tasks']:
        if task['Task_NO'] == "Timing":
            continue
        hw_tasks.append(HomeworkTask(hw_no, task['Task_NO'], task['Grade'], task['Task_Begin_Flag'], task['Task_End_Flag']))

    return data, hw_tasks, path
#### END: READ CONFIGURATION #########

def read_student_ids(student_ids_path):
    # TODO move student ids to config
    student_ids_path = Path(student_ids_path)  # path to student ids file
    try:
        student_ids_file = open(student_ids_path,"r+")
        student_ids = student_ids_file.readlines()
        for i in range(len(student_ids)):
            if student_ids[i][-1] == '\n':
                student_ids[i] = student_ids[i][:-1]
    except Exception as e:
        print("Error 2.1: An exception occurred During Reading Students IDs... Make sure of its path!", e)
        raise e
    return student_ids



############ BEGIN: Collect Solutions of a specific task #################
def collect_solutions(hw_tasks, path, rerun_flag):
    # Filter Submission to keep most recent only
    print('Filtering submissions...')
    try:
        filtered_submissions = filter_submissions(path, rerun_flag)
    except Exception as e:
        print("Error 1.2: An exception occured during running notebooks ", e)
        
    print('Creating tasks notebooks. Please wait...')
    try:
        for task in hw_tasks:
            task.create_task_ipynb()
            print(task.task_path)
            for sol in filtered_submissions:
                solution = sol.find_task(task.task_no, task.task_grade, task.begin_flag, task.end_flag, task.task_path)
                task.append_solution(solution)
    except Exception as e:
        print("Error 1.3: An exception occured during creating tasks notebooks ", e)
############ END: Collect Solutions of a specific task #################
    
    
############ BEGIN: Save to Excel Sheet #################
def collect_grades(hw_no, student_ids, hw_tasks):
    #Read Student IDs from the grades excel sheet
    # try:
    #     student_ids_file = open(student_ids_path,"r+")
    #     student_ids = student_ids_file.readlines()
    #     for i in range(len(student_ids)):
    #         if student_ids[i][-1] == '\n':
    #             student_ids[i] = student_ids[i][:-1]
    # except Exception as e:
    #     print("Error 2.1: An exception occurred During Reading Students IDs... Make sure of its path!", e)
    
    #Create Excel Sheet for the grades
    try:
        workbook = xlsxwriter.Workbook(f'./output/Grades_HW{hw_no:02d}.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', 'ID')
        i = 2
        for student_id in student_ids:
            worksheet.write('A' + str(i), student_id)
            i += 1
    except Exception as e:
        print("Error 2.2: Failed to create an Excel Sheet for the grades!", e)
    
    #Add Tasks Grades to the grades excel sheet
    try:
        task_letter = 66 #B = 66 in ASCII (To start with Column B)
        for task in hw_tasks:
            id_grade, id_comments = task.extract_results()
            present_ids = list(id_grade.keys()) #list of students who solved this task
            if task_letter < 91:
                task_col_header = str(chr(task_letter))
            else:
                task_col_header = str('A' + chr(task_letter - 26))
            worksheet.write(task_col_header + '1', str(task.task_no)) #read task number header
            i = 2
            for student_id in student_ids:
                if student_id not in present_ids: #student has not submitted the homework
                    id_grade[student_id] = 0
                    id_comments[student_id] = ''
                worksheet.write(task_col_header + str(i), str(id_grade[student_id])) #write the grade
                if len(id_comments[student_id]) > 10: #there is a comment
                    worksheet.write_comment(task_col_header + str(i), id_comments[student_id]) #write the comment
                i += 1
            task_letter += 1 #Move to next column for the next task
            
        workbook.close()
        print('Done: Adding Grades to the Excel Sheet')
    except Exception as e:
        print("Error 2.3: Something went wrong when adding the tasks grades!", e)
############ END: Save to Excel Sheet #################
        
        
############ BEGIN: Calculate AVG Time #################
def collect_timings(data, path, student_ids, hw_no):
    #Read Student IDs from the grades excel sheet
    # try:
    task_beg = None
    task_end = None
    for task in data['Tasks']:
        if task['Task_NO'] == "Timing":
            task_beg, task_end = task['Task_Begin_Flag'], task['Task_End_Flag']
            # used as a sanity check of the number of fields expected for the timing
            if 'TASK_NR_FIELDS' in task:
                task_nr_fields = int(task['TASK_NR_FIELDS'])
            else:
                task_nr_fields = int(input("How many fields timing has for this homework (enter an integer):"))
    # print("This feature will be added later.")
    print("Timing extraction setting review: ")
    print("  Beg tag: ", task_beg)
    print("  End tag: ", task_end)
    print("  path: ", path)
    print('Filtering Submissions.Please Wait...')
    filtered_submissions = filter_submissions(path, 0)
    p1 = re.compile("Task \w+|TOTAL", flags=re.IGNORECASE) # pattern 1 for task #
    p2 = re.compile("\d+[.\d+]* hours", flags=re.IGNORECASE) # pattern 2 for task hours 
    timings = {}
    nr_tasks = None
    cols = None
    for j, sol in enumerate(filtered_submissions):
        # print(j) # for debugging purposes
        timing = []
        columns = []
        solution = sol.find_task(task['Task_NO'], "1", task_beg, task_end)
        next_is_hour = False 
        for s in solution:
            # print(s['source'][0])
            if next_is_hour:
                next_is_hour=False
                if not s['source']:
                    continue
                result = p2.search(s['source'][0])
                if result is not None:
                    result = re.sub('[+#$%^&*(<>-]', '', result.group(0)) # remove symbols like plus in "5+ hours"
                    timing.append(float(result.split(' hours')[0].replace(',', '.')))
                else:
                    timing.append(0)
                continue
            #
            result = p1.search(s['source'][0])
            if result is not None:
                str_task = result.group(0).split('Task ')[-1]
                if str_task == 'TOTAL':
                    columns.append('TT')
                else:
                    columns.append("T%s" % str_task)
                # print("%s%s",(str_task[0],str_task[-1]))
                next_is_hour = True
                # print(rslt.group(0))
            # print(s['source'][0].split('Task '))
            # print(s.split('Task'))
        p3 = re.compile("\w*\d+")
        result = p3.search(s['source'][0])
        std_id = result.group(0)
        if task_nr_fields == len(timing):
            timings[std_id]=timing
        else:
            print("ignore timing from %s, expected %i fields in timing but found %i " % (std_id,
                task_nr_fields, len(timing)))
        # break
    # TODO: Following 2 lines could be done in a better! (I assume student would not change the
    # titles, and places that they are not supposed to change!)
    nr_tasks = len(timing) # from the last student's
    cols = columns # from the last student's columns
    # print(len(timings.keys()))
    # print(cols)
    # 
    #Read Student IDs from the grades excel sheet
    # try:
    #     student_ids_file = open(student_ids_path,"r+")
    #     student_ids = student_ids_file.readlines()
    #     for i in range(len(student_ids)):
    #         if student_ids[i][-1] == '\n':
    #             student_ids[i] = student_ids[i][:-1]
    # except Exception as e:
    #     print("Error 2.1: An exception occurred During Reading Students IDs... Make sure of its path!", e)

    # for student who were not present replace timing with zeros
    print("Matching students..")
    failed_extractions = []
    for id in student_ids:
        if id not in timings.keys():
            failed_extractions.append(id)
            timings[id] = [0]*nr_tasks

    if failed_extractions:
        print("Failed to extract timings for %i students: " % len(failed_extractions), failed_extractions)
    # remove students that are not part of this group!
    # TODO: perhaps these two loops could be handled better!
    keys_to_delete = []
    for k in timings.keys():
        if k not in student_ids:
            keys_to_delete.append(k)
    # remove studetns not in the list
    for k in keys_to_delete:
        del timings[k] 

    # to keep the order as in the student_ids.txt (FIXME: this is a hack!)
    timings_aranged = {}
    for id in student_ids:
        timings_aranged[id] = timings[id]

    # print(student_ids)
    # save as excel file
    df = pd.DataFrame.from_dict(timings_aranged, orient='index', columns=cols)
    # print(df)
    # df.sort_index(inplace=True)
    filename = f'./output/Timings_HW{hw_no:02d}.xlsx'
    df.to_excel(filename)
    print("Number of (current) submissions: ", len(filtered_submissions))
    print("Number of records for timings to store (whole class): ", len(df))
    print("Successfully wrote to file: ", filename)

    # except Exception as e:
        # print("Error 3.1: An exception occurred During AVG Time Calculation ... Make sure of its path!", e)
############ END: Calculate AVG Time #################


############ BEGIN: Similarity Checker #################
def check_plagiarism(hw_tasks, plagiarism_threshold):
    #Calculate Similarity for each task
    #try:
    suspects_freq = {}
    fname = "./logs/plagiarism_suspects.txt"
    with open(fname, "w") as f:
        f.write('SUSPECTS PER TASK\nStudent1,Student2,Similarity_Score,Task\n')
    suspects_total = 0
    for task in hw_tasks:
        with open(fname, "a") as f:
            suspects = task.similarity_calculator(plagiarism_threshold)
            for s in suspects:
                suspects_key = str(s[0]) + ',' + str(s[1])
                f.write(suspects_key + ',' + str(s[2] * 100) + ',' + str(task.task_no) + '\n')
                if suspects_key in suspects_freq.keys():
                    suspects_freq[suspects_key] += 1
                else:
                    suspects_freq[suspects_key] = 1
                    
        suspects_total += len(suspects)
        
    with open(fname, "a") as f:
        f.write('#########################################\nFREQUENCY OF SAME SUSPECTS\nStudent1,Student2,Frequency\n')
        for k in suspects_freq.keys():
            f.write(k + ',' + str(suspects_freq[k]) + '\n')
    print('Done: checking for plagiarism --> ', suspects_total, ' suspects found!')
    #except Exception as e:
    #    print("Error 4.2: Something went wrong when checking similarity!", e)
############ END: Similarity Checker #################

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    # Select homework
    parser.add_argument('homework',
                        help='homework id to work with',
                        type=int,
                        choices=[1,2,3,4,5,6])
    # Select mode
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('-s', '--solutions',
                       help='collect solutions of each task in a separate notebook',
                       action='store_true')
    modes.add_argument('-g', '--grades',
                       help='collect grades to an excel sheet',
                       action='store_true')
    modes.add_argument('-t', '--timings',
                       help='collect timings',
                       action='store_true')
    modes.add_argument('-p', '--plagiarism',
                       help='check plagiarism',
                       action='store_true')

    # Path to config file
    parser.add_argument('-c', '--config',
                        help='path to config json',
                        type=str,
                        default='./config/conf.json')

    parser.add_argument('-i', '--students',
                        help='path to config json',
                        type=str,
                        default='./data/student_ids.txt')

    # Others
    parser.add_argument('-r', '--rerun',
                        help='rerun all the submissions',
                        action='store_true')

    parser.add_argument('--threshold',
                        help='plagiarism warning threshold',
                        type=int,
                        default=2)

    args = parser.parse_args()

    # Read config files
    # TODO move student ids to config
    data, hw_tasks, path = read_config(config_path=args.config)
    student_ids = read_student_ids(args.students)

    if args.solutions:
        print(f'Collecting solutions for Homework {args.homework:02d}...')
        collect_solutions(hw_tasks=hw_tasks, path=path, rerun_flag=args.rerun)
        pass
    elif args.grades:
        print(f'Collecting grades for Homework {args.homework:02d}...')
        collect_grades(hw_no=args.homework, student_ids=student_ids, hw_tasks=hw_tasks)
        pass
    elif args.timings:
        print(f'Collecting timings for Homework {args.homework:02d}...')
        collect_timings(data=data, path=path, student_ids=student_ids, hw_no=args.homework)
        pass
    elif args.plagiarism:
        print(f'Checking plagiarism for Homework {args.homework:02d}...')
        check_plagiarism(hw_tasks=hw_tasks, plagiarism_threshold=args.threshold)
        pass

    return


if __name__ == '__main__':
    main()