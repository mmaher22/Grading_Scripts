# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 12:55:55 2019
@author: s-moh
"""
import json
import xlsxwriter
from glob import glob

from HomeworkTask import HomeworkTask
from Submission import Submission
from pathlib import Path

############ Filtering Submissions to keep most recent one only #################            
def filter_submissions(path, rerun_flag):
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
            final_submissions.append(Submission(student_id, str(submissions[s]), trial_no, rerun_flag))
            ids.append(student_id)
    return final_submissions
############ END: Filtering Submissions to keep most recent one only #################


#### BEGIN: READ CONFIGURATION ########
try:
    with open('conf.json', 'r', encoding="utf8") as f:
        data = json.load(f)
    
    hw_no = data['HW_NO'] #Homework number
    path = Path(data['HW_Path']) #HW Submission Folder
    student_ids_path = Path(data['student_ids']) #path to student ids file
    rerun_flag = data['Rerun']
    #data['Rerun'] = 0
    task_begin_flag = ''
    task_end_flag = ''
    
    #with open('conf.json', 'w', encoding="utf8") as f:
    #    json.dump(data, f, indent=4)
        
except Exception as e:
    print('Error 0.1: Error Reading JSON Configuration File - ', e)
# Initialize Information for each task
hwTasks = []
for task in data['Tasks']:
    hwTasks.append(HomeworkTask(hw_no, task['Task_NO'], task['Grade'], task['Task_Begin_Flag'], task['Task_End_Flag']))
#### END: READ CONFIGURATION #########

opt = int(input("Enter:\n 1 to Collect Solutions of each task in a separate notebook\n 2 to Collect Grades to an excel sheet:\n"))
############ BEGIN: Collect Solutions of a specific task #################
if opt == 1:
    # Filter Submission to keep most recent only
    print('Filtering Submissions.Please Wait...')
    try:
        filtered_submissions = filter_submissions(path, rerun_flag)
    except Exception as e:
        print("Error 1.1: An exception occured during running notebooks ", e)
        
    print('Creating Tasks Notebooks. Please Wait...')
    try:
        for task in hwTasks:
            task.create_task_ipynb()
            print(task.task_dir)
            for sol in filtered_submissions:
                solution = sol.find_task(task.task_no, task.task_grade, task.begin_flag, task.end_flag)
                task.append_solution(solution)
    except Exception as e:
        print("Error 1.2: An exception occured during creating tasks notebooks ", e)
############ END: Collect Solutions of a specific task #################
    
    
############ BEGIN: Save to Excel Sheet #################
if opt == 2:
    #Read Student IDs from the grades excel sheet
    try:
        student_ids_file = open(student_ids_path,"r+")
        student_ids = student_ids_file.readlines()
        for i in range(len(student_ids)):
            if student_ids[i][-1] == '\n':
                student_ids[i] = student_ids[i][:-1]
    except Exception as e:
        print("Error 2.1: An exception occurred During Reading Students IDs... Make sure of its path!", e)
    
    #Create Excel Sheet for the grades
    try:
        workbook = xlsxwriter.Workbook('Grades_HW' + str(hw_no) + '.xlsx')
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
        taskLetter = 66 #B = 66 in ASCII (To start with Column B)
        for task in hwTasks:
            id_grade, id_comments = task.extract_results()
            present_ids = list(id_grade.keys()) #list of students who solved this task
            if taskLetter < 91:
                taskColHeader = str(chr(taskLetter))
            else:
                taskColHeader = str('A' + chr(taskLetter - 26))
            worksheet.write(taskColHeader + '1', str(task.task_no)) #read task number header
            i = 2
            for student_id in student_ids:
                if student_id not in present_ids: #student has not submitted the homework
                    id_grade[student_id] = 0
                    id_comments[student_id] = ''
                worksheet.write(taskColHeader + str(i), str(id_grade[student_id])) #write the grade
                if len(id_comments[student_id]) > 10: #there is a comment
                    worksheet.write_comment(taskColHeader + str(i), id_comments[student_id]) #write the comment
                i += 1
            taskLetter += 1 #Move to next column for the next task
            
        workbook.close()
        print('Done: Adding Grades to the Excel Sheet')
    except Exception as e:
        print("Error 2.3: Something went wrong when adding the tasks grades!", e)
############ END: Save to Excel Sheet #################
        
        
############ BEGIN: Calculate AVG Time #################
if opt == 3:
    #Read Student IDs from the grades excel sheet
    try:
        print("This feature will be added later.")
    except Exception as e:
        print("Error 3.1: An exception occurred During AVG Time Calculation ... Make sure of its path!", e)
############ END: Calculate AVG Time #################