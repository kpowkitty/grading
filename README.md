## SFSU Python Grading Pipeline

---------

### Multi-class grading scripts for SFSU CS courses.

---------

### Repository layout:

* `grader/` — shared, class-agnostic grading modules (extraction, compilation, design checks, regrade handling)
* `classes/<class>/scripts/` — per-class grader scripts (one per assignment)
* `classes/<class>/<N>_assignment_misc/` — per-assignment test files, reference code, etc.
* `classes/<class>/submissions_unzip/` — runtime: bulk submissions are unzipped here (gitignored)
* `run_grader.sh` — entry point, dispatches to the right class/script

### Active classes:

* `classes/csc340/` — Programming Methodology (4 assignments)
* `classes/csc641/` — Computer Performance (in progress)

### Usage:

```
./run_grader.sh <class> <script_name> <output_file>
```

Examples:
```
./run_grader.sh csc340 4_assignment_grader grading_output
./run_grader.sh csc641 milestone2_grader grading_output
```

### Project expectations:

* If there are `testing_files/`, put them in `classes/<class>/<N>_assignment_misc/testing_files/`
* `submissions.zip` goes into `classes/<class>/`
* `submissions.zip` will unzip into `classes/<class>/submissions_unzip/`

### Adding a new class:

1. `mkdir -p classes/<new_class>/scripts`
2. Drop assignment grader scripts into `classes/<new_class>/scripts/`. They can import from `grader.*` directly — repo-root resolution is handled at the top of each script.
