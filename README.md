1. System Description
This directory includes the software requirement specification (SRS) and software design specification (SDS) documents for the Active-Reading assistant software project. The SRS outlines the specific requirements of this software and the SDS describes our specific software design choices and how they were implemented. The directory also includes a project plan document which gives an overview of the planning process for this project. The programmer documentation provides guidance on the implementation of the software and guides a programmer on how to effectively modify the source code. The user documentation explains to the user how to use the system by showing them how different specific tasks are accomplished within the software. 

2. Authors 
Ben Bushey, John Hooft-Toomey, Ethan Hyde, John O'Donnell 

3. Creation Date 
The project first begun on 04/04/24 and this document was written on 04/27/2024.

4. Assignment Description 
This software system was created for Project 1 of CS422, Software Methodologies at University of Oregon 

5. How to run the program 
To compile and run this program the user should first run these commands within the terminal. 
* brew services start mongodb-community@7.0
* brew services stop mongodb-community@7.0
The user then needs to run the python TKinter/main.py using the following terminal command or IDE to start the program. Note that the user must be in the directory CS422_Project1. 
* Python Code/TKinter/main.py

6. Additional Setup 
This program can run with or without being connected to the MongoDB database. 

7. Additional Software Dependencies 
This software requires Python 3.9.6 to run. 
In order to connect to the database, MongoDB will need to be installed. The instructions are linked here: https://www.mongodb.com/docs/manual/installation/
This software requires a library called PyMuPDF. In order to install this, run the command 'pip install pymupdf'

8. Subdirectories 
The top directory for this software contains 3 subdirectories: 
* Code
This subdirectory contains the code for the Active-Learning assistant including separate subdirectories for the TKinter interface, MongoDB database and required data structures.
* Documentation 
This subdirectory contains the software requirements specification and the software design specifications for this project. 
* Resources
This subdirectory contains the PDF files that are pre-loaded within the Active-Learning assistant. 

 
