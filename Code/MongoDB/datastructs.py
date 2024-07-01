# File: datastructs.py
# Project: CS 422 Project 1
# Authors: John Hooft
# Creation date: 4-22-2024
# Description: This file contains the implementation of our classes (datastructs), which
#              are used in the main.py file.

# Modifications:
# Date        Author       Change
# ----------- ------------ -----------------------------------------------------
# 04-22-2024  Ethan Hyed   Adjusted GetNotes function to work as intended.
# 04-22-2024  John Hooft   Created file and added Database, User, and notesDS class.
# 04-22-2024  John Hooft   Updated getNotes() to work with new structure that notes are saved in.
# 04-22-2024  John Hooft   Implemented the logic for the updateUserNotes function in the Database class.
# 04-24-2024  John Hooft   Added deleteSection() function to Database class.
# 04-27-2024  Ethan Hyde   Fixed getNotes function to pull correctly from the DB
# ==============================================================================

import os
import json
from pymongo import MongoClient

# Manages database connections, can be checked with json schema file
class Database:
    def __init__(self, uri, dbname, schema_file):
        # Connection to MongoDB instance
        self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        self.connected = False # Variable that stores whether or not DB is connected too
        try:
            # Attempt to list the available databases, if succesfull set connected to True.
            db_names = self.client.list_database_names()
            print("MongoDB server is running.")
            self.connected = True
        except Exception as e: # If unable to query Database, print error.
            print("Error:", e)
            print("MongoDB server is not running.")
        # Database name
        self.db = self.client[dbname]
        # Find the full path to the schema file
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Directory where this script resides
        schema_file_path = os.path.join(current_dir, 'schema.json')
        # Not used really, can check schema against JSON
        self.loadSchema(schema_file_path)

    def loadSchema(self, schema_file_path):
        # For validation with JSON schema
        with open(schema_file_path, 'r') as f:
            self.schema = json.load(f)

    def getCollection(self, collectionName):
        # Returns a collection from DB with a given name
        return self.db[collectionName]
    
    def deleteSection(self, username, pdfID, targetTitle):
        usersCollection = self.getCollection("users")

        # Use update_one to directly remove the section
        result = usersCollection.update_one(
            {"username": username, "notes.pdf_id": pdfID},
            {"$pull": {"notes.$.chapter.sections": {"sectionTitle": targetTitle}}}
        )

        if result.modified_count > 0:
            print("Section deleted")
        else:
            print("Section not found or deletion unsuccessful")


    def updateUserNotes(self, username, notedata):
        pdfID = notedata.pdfID
        usersCollection = self.getCollection("users")

        # Check if user exists and get user data
        user = usersCollection.find_one({"username": username})

        if user:
            # Check if this PDF already has notes
            notes_exist = False
            for note in user['notes']:
                if note['pdf_id'] == pdfID:
                    notes_exist = True
                    #Update chapter title
                    usersCollection.update_one(
                        {"username": username, "notes.pdf_id": pdfID},
                        {"$set": {"notes.$.chapter.chapter_title": notedata.chapterTitle}}
                    )

                    # Clear existing sections to replace them
                    usersCollection.update_one(
                        {"username": username, "notes.pdf_id": pdfID},
                        {"$set": {"notes.$.chapter.sections": []}}
                    )

                    # Add sections
                    for section in notedata.sections:
                        usersCollection.update_one(
                            {"username": username, "notes.pdf_id": pdfID},
                            {"$push": {"notes.$.chapter.sections": {
                                "sectionTitle": section["sectionTitle"],
                                "sectionNotes": section["sectionNotes"]
                            }}}
                        )
                    break

            if not notes_exist:
                # If PDF does not have notes, create new note entry
                new_note = {
                    "pdf_id": pdfID,
                    "chapter": {
                        "chapter_title": notedata.chapterTitle,
                        "sections": notedata.sections
                    }
                }
                usersCollection.update_one(
                    {"username": username},
                    {"$push": {"notes": new_note}}
                )
            print("Notes updated or added successfully.")

        else:
            # If user does not exist, create a new user entry
            new_user = {
                "username": username,
                "notes": [{
                    "pdf_id": pdfID,
                    "chapter": {
                        "chapter_title": notedata.chapterTitle,
                        "sections": notedata.sections
                    }
                }]
            }
            usersCollection.insert_one(new_user)
            print("New user created and notes saved successfully.")



# Represents a user in our system
class User:
    def __init__(self, username, password):
        # Username
        self.userName = username 
        # Password, not used currently
        self.password = password 
    
    def getNotes(self, username, pdfID):
        db = Database("mongodb://localhost:27017/", "active_reading_assistant", "schema.json")
        usersCollection = db.getCollection("users")

        # Find the user by username, assumes unique username, i.e. no checking for duplicates
        user = usersCollection.find_one({"username": username})
        if not user:
            print(f"User {username} not found in the database.")
            return None

        for note in user.get('notes', []):  # Default to empty list if no notes
            if note.get('pdf_id') == pdfID:
                try:
                    chapter_title = note['chapter']['chapter_title']
                    usernotes = notesDS(pdfID, chapter_title)

                    sections = note['chapter'].get('sections', [])
                    for section in sections:
                        section_title = section['sectionTitle']
                        section_notes = section['sectionNotes']
                        usernotes.addSection(section_title, section_notes)
                    return usernotes
                except KeyError as e:
                    print(f"Error processing notes for user {username} and PDF {pdfID}: {e}")
                    return None

        print(f"No notes available for user {username} and PDF ID {pdfID}")
        return None

# Represents notes for a given PDF and chapter
class notesDS:
    def __init__(self, pdfID, chapterTitle):
        # PDF identifier
        self.pdfID = pdfID
        # Title of the chapter
        self.chapterTitle = chapterTitle
        # List to hold sections that the user creates
        self.sections = []

    def addSection(self, sectionTitle, sectionNotes):
        # Adds a section with a title and prompts for notes
        self.sections.append({
            "sectionTitle": sectionTitle,
            "sectionNotes": sectionNotes
        })