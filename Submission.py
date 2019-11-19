# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 12:57:13 2019
@author: s-moh
"""
import os
import json
import subprocess

#Class for the student submission of the Homework
class Submission:
    def __init__(self, student_id, submission_path, trial, rerun_flag):
        self.id = student_id
        self.submission_path = submission_path
        self.trial = trial
        self.rerun_flag = rerun_flag
        
        
        with open(self.submission_path, 'r', encoding="utf8") as f:
            self.old_data = json.load(f)
            
        
        if self.rerun_flag == 1:
            self.rerun()
    
    def rerun(self):
        cmd = 'jupyter nbconvert --to notebook --inplace --ExecutePreprocessor.timeout=6000 --execute "' + self.submission_path + '"'
        out = subprocess.getoutput(cmd)
        if "Error:" in out:
            with open("./logs/failed_nb.txt", "a") as f:
                f.write(str(self.id) + '\n')
        #os.system(cmd)
        
    # Method to Find specific task solution for that user
    def find_task(self, task_no, grade, task_flag='', next_task_flag='', task_dir=''):
        #print('Submission Path = ', self.submission_path)
        with open(self.submission_path, 'r', encoding="utf8") as f:
            cnt_data = json.load(f)
        #Create Alert Cell For Different Solutions after rerun
        alert_cell = {"cell_type": "markdown", "metadata": {},
                       "source": ["# ALERT: Solution After Rerun is different!!! (Old Solution is Next)"]}
        path_diff = str(os.path.relpath(self.submission_path, start=os.path.dirname(os.path.abspath(task_dir)))).replace('\\', '/')
        #Create Solution Footer Cells
        solution_footer = {"cell_type": "markdown", "metadata": {},
                       "source": ["# StudentID:" + str(self.id) + "\n",
                                  "\n",
                                  "TrialNO:" + str(self.trial) + "\n",
                                  "\n",
                                  "Submission:Link to [Notebook]("+ path_diff + ")\n",
                                  "\n",
                                  "Grade:" + str(grade) + "\n",
                                  "\n",
                                  "Comments:",
                                  "\n",
                                  "\n___\n<font size = '20' color='darkgreen'> END BLOCK </font>\n___"]}
        # Flag to mark task needed
        if task_flag == '':
            task_flag = 'Task ' + str(task_no)
        # Flag to mark next task
        if next_task_flag == '':
            next_task_flag = 'Task ' + str(task_no + 1)
        
        def finder(data):
            solution = []
            # Search for the task in the user submission
            flag = False
            finished_flag = False
            for cell in data['cells']:
                #Found the task
                try:
                    for row_in_cell in cell['source']:
                        if task_flag in row_in_cell:
                           flag = True
                           break
                    
                    #Check if Reached next task
                    if flag:
                        for row_in_cell in cell['source']:
                            if next_task_flag in row_in_cell:
                                finished_flag = True
                        if finished_flag:
                            break
                    
                    if flag:
                        solution.append(cell)
                except Exception as e:
                    print('Exception was raised:', e)
                    continue
            return solution
        
        solution = finder(cnt_data)
        old_solution = finder(self.old_data)
        
        add_alert = False #Alert for different solutions cells after rerun
        for s_cnt, s_old in zip(solution, old_solution):
            if s_cnt != s_old or len(solution) != len(old_solution):
                add_alert = True
                break
            
        if add_alert:
            solution.append(alert_cell)
            solution.extend(old_solution)
        
        solution.append(solution_footer)
        return solution
