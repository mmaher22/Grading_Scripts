# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 12:56:24 2019
@author: s-moh
"""
import os
import json
import os.path

class HomeworkTask: #Class for the Homework Task or Subtask
    def __init__(self, hw_no, task_no, grade, begin_flag, end_flag):
        self.hw_no = hw_no
        self.task_no = task_no
        self.task_grade = grade
        self.begin_flag = begin_flag
        self.end_flag = end_flag
        
        directory = 'Grading_HW' + str(self.hw_no)
        #Create directory for the homework
        if not os.path.exists(directory):
            os.makedirs(directory)
        #Create a new ipynb file for the task
        self.task_dir = directory + '//Task' + str(self.task_no) + '.ipynb'
        
    #Create ipynb files for the tasks
    def create_task_ipynb(self):
        with open("ipynbTmp.ipynb") as f1:
            lines = f1.readlines()

        opt = 1            
        if os.path.isfile(self.task_dir):
            opt = int(input('WARNING: ' + str(self.task_dir) + "Exists. Input 1 to overwrite, 2 to Append. \n"))
        if opt == 1:
            with open(self.task_dir, "w") as f2:
                f2.writelines(lines)
    
    #Append Solution to task ipynb file
    def append_solution(self, solution):
        with open(self.task_dir, 'r') as f:
            data = json.load(f)
        data['cells'].extend(solution)
        
        with open(self.task_dir, 'w') as f:
            json.dump(data, f)
            
    #Extract Results from the graded task notebook
    def extract_results(self):
        id_grade = {}
        id_comment = {}
        with open(self.task_dir, 'r', encoding="utf8") as f:
            data = json.load(f)['cells']
            for cell in data:
                if len(cell['source']) != 0 and '# StudentID:' in cell['source'][0]:
                    student_id = cell['source'][0].split(':')[1][:-1] #Parse Student ID
                    commentFlag = False #flag the beginning of the comments
                    for row in cell['source']:
                        if 'Grade:' in row:
                            id_grade[student_id] = float(row.split(':')[1]) #Parse Grade Value
                        elif 'Comments:' in row: 
                            id_comment[student_id] = row
                            commentFlag = True
                        elif commentFlag == True and row != "\n":
                            id_comment[student_id] += row
                        elif commentFlag == True and row == "\n":
                            break
        return id_grade, id_comment
