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
        
        ################### TODO: Remove This after 2nd Homework (Replace Exception Statements)
        with open(self.submission_path, 'r', encoding="utf8") as f:
            data = json.dumps(json.load(f))
        data = data.replace("except NotImplementedError as e", "except Exception as e")
        with open(self.submission_path, 'w', encoding="utf8") as f:
            json.dump(json.loads(data), f, indent=4)
        ################### END TODO: Remove This after 2nd Homework
        
        with open(self.submission_path, 'r', encoding="utf8") as f:
            self.old_data = json.load(f)
            
        
        if self.rerun_flag == 1:
            self.rerun()
    
    def rerun(self):
        cmd = 'jupyter nbconvert --to notebook --inplace --ExecutePreprocessor.timeout=6000 --execute "' + self.submission_path + '"'
        out = subprocess.getoutput(cmd)
        if "Error:" in out:
            with open("FailedNBs.txt", "a") as f:
                f.write(str(self.id) + '\n')
        #os.system(cmd)
        
    # Method to Find specific task solution for that user
    def find_task(self, task_no, grade, taskFlag = '', nxtTaskFlag = ''):
        #print('Submission Path = ', self.submission_path)
        with open(self.submission_path, 'r', encoding="utf8") as f:
            cnt_data = json.load(f)
        #Create Alert Cell For Different Solutions after rerun
        alert_cell = {"cell_type": "markdown", "metadata": {},
                       "source": ["# ALERT: Solution After Rerun is different!!! (Old Solution is Next)"]}
        #Create Solution Footer Cells
        solution_footer = {"cell_type": "markdown", "metadata": {},
                       "source": ["# StudentID:" + str(self.id) + "\n",
                                  "\n",
                                  "TrialNO:" + str(self.trial) + "\n",
                                  "\n",
                                  "SubmissionURL:<a href = '" + self.submission_path + "'>HERE</a> \n",
                                  "\n",
                                  "Grade:" + str(grade) + "\n",
                                  "\n",
                                  "Comments:"]}
        # Flag to mark task needed
        if taskFlag == '':
            taskFlag = 'Task ' + str(task_no)
        # Flag to mark next task
        if nxtTaskFlag == '':
            nxtTaskFlag = 'Task ' + str(task_no + 1)
        
        def finder(data):
            solution = []
            # Search for the task in the user submission
            flag = False
            for cell in data['cells']:
                #Found the task
                try:
                    if taskFlag in cell['source'][0]:
                        flag = True
                    #Reached next task
                    if flag == True and nxtTaskFlag in cell['source'][0]:
                        break
                    elif flag == True:
                        solution.append(cell)
                except:
                    continue
            return solution
        
        solution = finder(cnt_data)
        old_solution = finder(self.old_data)
        
        add_alert = False #Alert for different solutions cells after rerun
        for s_cnt, s_old in zip(solution, old_solution):
            if s_cnt != s_old or len(solution) != len(old_solution):
                add_alert = True
                break
            
        if add_alert == True:
            solution.append(alert_cell)
            solution.extend(old_solution)
        
        solution.append(solution_footer)
        return solution