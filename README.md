# Grading Scripts

### [UPDATE]: Plagiarism Detection Option:
I added fourth option now to the scripts for plagiarism detection, and updated code on Github.
- The output of this option execution will be Plagiarism_Suspects.txt including 2 sections. The first contains suspects per task and the second is the frequency of same two students being suspects at different tasks.

- Plagiarism Suspection case is added when the similarity score between two students > mean + T x Std of the scores of all students  (T = 2 by default but can be updated from the conf.json)

- I used Jaccard Similarity measurement imported from this Repo with 30+implementations for text distance algorithms  https://github.com/life4/textdistance . So, we can change the distance measurement with any of those algorithms by just replacing 'jaccard' with the name of the new algorithm on Line 106 in HomeworkTask.py file and it should work the same.
I went quickly through the different similarity measurements. I think token based methods are the most suitable ones in our case even complexity wise. However, we may need to read more about other methods and choose a better one or even a hybrid method if jaccard doesn't work well.

- The script runs over the notebooks of subtasks after splitting. So, if we want to check plagarism over all students then we need to run option 1 first over all students submission OR one of us collects all graded notebooks at the end and merge them together before checking for plagarism (I prefer this option as we can avoid getting suspects who didn't solve the subtask at all --> (similarity = 100%) by skipping the solutions with grade = 0)
<hr>
## In Order to use the code, you need to modify each of the following:
### 1. conf.json:
- "HW_NO" --> is the homework number
- "student_ids" --> path to a txt file of student ids in the same order as the grades sheet to keep the order while collecting grades and importing to GDrive
- "HW_Path" --> path to the submissions folder
- "Rerun": --> 0 if you don't want to rerun the whole notebook before grading and 1 if you want to rerun the notebook
- "Tasks": --> list of dictionaries of the properties of the tasks
- "Task_NO" --> string to name the task / subtask
- "Grade": --> full mark of this task / subtask
- "Task_Begin_Flag" --> flag to mark the beginning of the task
- "Task_End_Flag" --> flag to mark the end of the task / beginning of the next task

For the timing section:
- "Task_NO": ---> "Timing"
- "Task_Begin_Flag": --> flag to mark the beginning of the timing section i.e. "How long did it take you to solve the homework?"
- "Task_End_Flag": --> flag to mark the end of the timing section i.e. "THANK YOU FOR YOUR EFFORT!"

##### NOTE: 
- In case of different output from the jupyter after rurunning from the original one, we are going to put both outputs with an alert cell between them
to tell you that the solution had a different output after rerunning.
- Please don't forget to add extra files needed during running notebooks in the submission folder (eg: data.csv)

### 2.student_ids.txt: contains the student ids in the same order as they are in the grades sheet in google drive. Each ID in a separate line.

### 3. Run main.py:
- You have to wait for some time in case of rurn was chosen to be 1.
- FailedNBs.txt will contain id of students that we failed to rerun their notebooks and need manual checking.
- After that, you have two options: Enter 1 to split the tasks into separate jupyter notebooks which you can find in folder called "Grading_HW#"
- Finish the grading process + add the comments.
- Run main.py again: Enter 2 to collect the grades from the notebook and save the results to "Grades_HW#.xlsx" where you can find the first column is the student id followed by each task in a column with the grade and comment.
- Import the excel file into a new sheet in GDrive to import the grades with comments
- Copy the data to your original excel sheet of the grades.


<hr>

## Code is divided into three files:
### 1. main.py
Contains the main logic of the code which basically does the following in the same order.
- read the configuration from conf.json 
- create objects for each student submission and keep most recent only for multiple submissions from the same id.
- ask user to enter either 1 for splitting the submissions into notebooks for each task/subtask alone and add cell for grades and comments after each solution.
- OR 2 for collecting the grades from the notebooks and export them to an excel sheet.
- OR 3 for collecting the timing (time spent, filled by students) from the notebooks and export them to another excel sheet.

### 2.HomeworkTask.py 
Class for homework task/subtask objects and it has three methods:
- create_task_ipynb: create a new notebook for this task to write all the submissions into it. 
- append_solution: to append a new solution to the notebook created by the previous method.
- extract_results: extract the grades and comments from the notebook into two dictionaries with keys as student ids and values as grades and comments.

### 3.Submission.py
Class for student submission objects and it has two methods:
- rerun: to rerun the jupyter notebook if specified in the conf.json.
- find_task: find a specific task in the student submission file based on the flags of the task start and end.
