# Database Normalization Guide
## Contents
- [Purpose](#purpose)
- [Authors](#authors)
- [Required Inputs](#required-inputs)
- [Generated Outputs](#generated-outputs)
- [Main Components](#main-components)
- [Presumptions](#presumptions)
- [Contact Information](#contact-information)

## Purpose:
The goal is to create a program that takes a dataset (relation) and functional dependencies as input, normalizes the relations based on these dependencies, generates SQL queries to create the normalized database tables, and optionally identifies the highest normal form of the input table.</br>

## Authors:
Jayanth Veeramachaneni (jvp9d@umsystem.edu)

## Required Inputs
1) The input relation data should be provided in the _**'exampleInputTable.csv'**_ file.
2) Functional dependencies should be specified in the _**'dependencies.txt'**_ file (e.g., _'StudentID -> FirstName, LastName'_).
3) Multi-valued dependencies, if any, should be mentioned in the _**'mvd_dependencies.txt'**_ file (e.g., _'Course ->> Professor'_).
4) The _**'primary key (key)'**_ is user input and must be comma-separated for composite keys (e.g., '_StudentID, Course_').
5) The **'Choice of the highest normal form to reach (1: 1NF, 2: 2NF, 3: 3NF, B: BCNF, 4: 4NF, 5: 5NF)'** is a user input (e.g., 4).
6) **'Find the highest normal form of the input table? (1: Yes, 2: No)'** is a user input (e.g., 1).
7) For 5NF, each relation requires _candidate keys_ (user input) in the format _'(A, B), (C, D)'_.</br>
NOTE: Ensure all keys are entered as specified above for the code to function correctly.

## Generated Outputs
1) The input relation will undergo normalization processes until it reaches the specified highest normal form.
2) At each stage, the program will verify if the relation meets the normalization form and output the normalized tables with data if it does not.
3) Upon reaching the desired highest normal form, the program will exit and output the _**'CREATE TABLE <table-name> ...'**_ queries for the normalized tables.
4) At the end, depending on user input, the highest normal form of the input table will be displayed or not.
5) The SQL CREATE TABLE <table-name> queries for the normalized tables are saved in the _**'output.txt'**_ file.

## Main Components
1) [main.py](/main.py): The _**main script to be executed**_. It handles all input redirections.
2) [input_parser.py](/input_parser.py): Parses inputs from the CSV file, text files, and user inputs for use in the program.
3) [normalizations.py](/normalizations.py): Contains the logic for all normalizations from 1NF to 5NF.
4) [output_generator.py](/output_generator.py): Generates the required SQL queries based on the normalized tables.

## Presumptions
1) The user has Python >= 3.9 installed and an environment set up to run this program.
2) The required libraries (pandas, numpy, etc.) are pre-installed.
3) The user will provide the necessary inputs in the specified format.</br>
NOTE: Run the default example with the provided key (StudentID, Course) and highest normal form (4) to understand the program's workings.

## Contact Information
For any questions about the program and its functionality, contact [jvp9d@umsystem.edu](mailto:jvp9d@umsystem.edu).