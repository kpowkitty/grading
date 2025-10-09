## SFSU CSC340 Python Grading Scripts

---------

### Contains all my Python grading scripts for CSC340.

---------

### Repository Breakdown:

Project expectations:
* if there are `testing_files`, put them in `testing_files/`
* `submissions.zip` goes into root
* `submissions.zip` will unzip into `submissions_unzip/`

Project structure:
* `grader/` contains all of the grading modules.
  * `grader/controller.py` has control methods for running all files or a single
file
  * `grader/core.py` is the main class to run the assignment grader
  * `grader/utils.py` are various utils to help assignment grading

* `scripts/` is where each grader script is put
  * `scripts/grade_all.py` runs the general grading script for all students
  * `scripts/grade_one.py` runs the general grading script for a single student
  * the rest of the scripts are per assignment, and organized as such
