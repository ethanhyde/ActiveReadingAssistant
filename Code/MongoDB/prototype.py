 # File: main.py
 # Project: CS 422 Project 1
 # Authors: Ethan Hyde, John Hooft
 # Creation date: 4-16-2024
 # Description: This file contains a command line user interface prototype for the ARA application using
 #               TKinter and the tkPDFViewer library. 

 # Modifications:
 # Date        Author       Change
 # ----------- ------------ -----------------------------------------------------
 # 04-16-2024  Ethan        Initial creation of the file
 # 04-18-2024  John Hooft   Added print notes option
 # 4-20-2024   Ethan        Created User/notesDS classes, add sections in notes
 # 4-20-2024   Ethan        Changed MongoDB storage structure, fixed print function
 # 04-21-2024  John Hooft   Added User class getNotes() function, and server logic.
 # 04-22-2024  John Hooft   Moved classes / objects to datastructs.py file.
 # 04-22-2024  John Hooft   Update printNotes() to work with updated getNotes()
 # ==============================================================================

from datastructs import notesDS, User, Database

# Prompts user to enter notes
def promptNotes(user):
    print("Enter your notes. Type 'done' to finish.")
    pdfID = input("Enter PDF ID: ")
    chapterTitle = input("Enter chapter title: ")
    notesOBJ = notesDS(pdfID, chapterTitle)

    while True:
        command = input("Enter a command (section/done/print/del): ")

        if command.lower() == 'done':
            break

        if command.lower() == 'del':
            sectionTitle = input("Enter section title you want to delete: ")
            db = Database("mongodb://localhost:27017/", "active_reading_assistant", "schema.json")
            db.deleteSection(user.userName, pdfID, sectionTitle)

        elif command.lower() == 'section':
            sectionTitle = input("Enter section title: ")
            sectionNotes = input("Enter section notes: ")
            notesOBJ.addSection(sectionTitle, sectionNotes)

        elif command.lower() == 'print':
            printNotes(user, pdfID)

        else:
            print("Unknown command.")

    return notesOBJ

def printNotes(userclass, pdfID):
    db = Database("mongodb://localhost:27017/", "active_reading_assistant", "schema.json")
    usersCollection = db.getCollection("users")
    username = userclass.userName

    user = usersCollection.find_one({"username": username})

    if user:
        notedata = userclass.getNotes(username, pdfID)
        print(f"Notes for user {username} on PDF ID {pdfID}:")

        print(f"Chapter Title: {notedata.chapterTitle}")

        for section in notedata.sections:
            print(f"  Section Title: {section['sectionTitle']}")
            print(f"  Section Notes: {section['sectionNotes']}")
            print()  # For better readability
    else:
        print(f"User {username} not found.")


 # Saves notes to DB after user types 'done'
def saveNotes(username, notesOBJ):

    # Connecting to DB on 27017
    # URL will change when hosted with IX-dev
    db = Database("mongodb://localhost:27017/", "active_reading_assistant", "schema.json")
    db.updateUserNotes(username, notesOBJ)


def main():
    # Prompt the user for their username
    username = input("Enter your username: ")

    # Create user class for session, password is not implemented yet
    user = User(username, password="temp")

    while True:
        # Prompt user to enter notes
        notes = promptNotes(user)

        # Save notes to the database
        saveNotes(username, notes)

        exit = input("Do you want to exit? (y/n)")

        if exit == 'y':
            break

    # Clean up memory by deleting data structs.
    del(notes)
    del(user)

if __name__ == "__main__":
    main()