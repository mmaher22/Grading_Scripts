# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 12:56:24 2019
@author: s-moh
"""
import os
import json
import os.path
import textdistance
import numpy as np

class HomeworkTask: #Class for the Homework Task or Subtask
    def __init__(self, hw_no, task_no, grade, begin_flag, end_flag):
        self.hw_no = hw_no
        self.task_no = task_no
        self.task_grade = grade
        self.begin_flag = begin_flag
        self.end_flag = end_flag
        
        grading_dir = f'./output/Grading_HW{self.hw_no:02d}'
        #Create directory for the homework
        if not os.path.exists(grading_dir):
            os.makedirs(grading_dir)
        #Create a new ipynb file for the task
        self.task_path = os.path.join(grading_dir, f'/Task{self.task_no}.ipynb')
        
    #Create ipynb files for the tasks
    def create_task_ipynb(self):
        with open("./data/ipynb_tmp.ipynb") as f:
            lines = f.readlines()

        opt = 1            
        if os.path.isfile(self.task_path):
            opt = int(input('WARNING: ' + str(self.task_path) + "Exists. Input 1 to overwrite, 2 to Append. \n"))
        if opt == 1:
            with open(self.task_path, "w") as f:
                f.writelines(lines)
    
    #Append Solution to task ipynb file
    def append_solution(self, solution):
        with open(self.task_path, 'r') as f:
            data = json.load(f)
        data['cells'].extend(solution)
        
        with open(self.task_path, 'w') as f:
            json.dump(data, f)
            
    #Extract Results from the graded task notebook
    def extract_results(self):
        id_grade = {}
        id_comment = {}
        with open(self.task_path, 'r', encoding="utf8") as f:
            data = json.load(f)['cells']
            for cell in data:
                if len(cell['source']) != 0 and '# StudentID:' in cell['source'][0]:
                    student_id = cell['source'][0].split(':')[1][:-1] #Parse Student ID
                    comment_flag = False #flag the beginning of the comments
                    for row in cell['source']:
                        if 'Grade:' in row:
                            id_grade[student_id] = float(row.split(':')[1]) #Parse Grade Value
                        elif 'Comments:' in row: 
                            id_comment[student_id] = row
                            comment_flag = True
                        elif comment_flag and row != "\n":
                            id_comment[student_id] += row
                        elif comment_flag and row == "\n":
                            break
        return id_grade, id_comment
    
    #Calculate Similarity Measurement for all students
    def similarity_calculator(self, threshold = 2):
        #return suspects whose similarity > mean + threshold * standard deviation
        def get_suspects(mu, std, sim_matrix, ids):
            suspects = []
            for i in range(sim_matrix.shape[0]):
                for j in range(i+1, sim_matrix.shape[0]):
                    if sim_matrix[i,j] > mu + threshold * std:
                        suspects.append((ids[i], ids[j], sim_matrix[i,j]))
            return suspects
        #Compute similarity value matrix between all students
        students_solutions = {}
        student_ids = []
        with open(self.task_path, 'r', encoding="utf8") as f:
            data = json.load(f)['cells']
            cnt_solution = ''
            for cell in data:
                if len(cell['source']) != 0 and '# StudentID:' in cell['source'][0]:
                    grade = 1
                    student_id = cell['source'][0].split(':')[1][:-1] #Parse Student ID
                    for row in cell['source']:
                        if 'Grade:' in row:
                            grade = float(row.split(':')[1]) #Parse Grade Value
                            break
                    if grade == 0: #Wrong/empty solution - no need to check plagarism
                        continue
                    student_ids.append(student_id)
                    students_solutions[student_id] = cnt_solution
                    cnt_solution = ''
                elif len(cell['source']) != 0:
                    for row in cell['source']:
                        cnt_solution += row
        sim_matrix = np.zeros((len(student_ids), len(student_ids)))
        scores = []
        for i in range(len(student_ids)):
            for j in range(i+1, len(student_ids)):
                score = textdistance.jaccard.normalized_similarity(students_solutions[student_ids[i]], students_solutions[student_ids[j]])
                sim_matrix[i, j] = score
                scores.append(score)
                
        return get_suspects(np.mean(scores), np.std(scores), sim_matrix, student_ids)