# # File: main.py
# # Project: CS 422 Project 1
# # Authors: Ethan Hyde
# # Creation date: 4-20-2024
# # Description: This file contains the user interface for the ARA application using
# #               TKinter and the tkPDFViewer library. It will be what the users interact
# #               with while using our software

# # Modifications:
# # Date        Author       Change
# # ----------- ------------ -----------------------------------------------------
# # 04-20-2024  Ethan        Initial creation of the file
# # 04-21-2024  Ethan        Adding buttons/loading PDF into the UI
# # 04-21-2024  Ben          initial creation of logout system
# # 04-24-2024  Ethan        fixed login screen functionality, password can't be seen when typing
# # 04-25-2024  Ben          Added notesapp/section classes             
# # 04-26-2024  Ethan       Switched library to pymu
# # 04-26-2024  Ben         Added PDF selection
# # 04-26-2024  John H      Fixed TKinter window 
# # 04-26-2024  John H      Fixed PDF path 
# # 04-26-2024  Ben         Added section heading/title text box 
# # 04-26-2024  John O      PDF switch buttons 
# # 04-26-2024  Ben         Fixed user notes
# # 04-27-2024  John/Ethan  TKinter bug fixes
# # 04-27-2024  John O      Automatic notes save
# # 04-28-2024  John H      Offline functionality 
# # 04-28-2024  Ethan       Code Comments 
# # 04-28-2024  John O      Automatic save notes improvements 
# # 04-29-2024  Ben         SQ3R Prompts 
# # 04-29-2024  John O      Example prewritten notes
# # 04-29-2024  John O      More code comments
# # ==============================================================================

import tkinter as tk  # Used for creating interactive learning module's user interface  
from tkinter import Canvas, Frame, Label, Toplevel, Button, messagebox, scrolledtext, Entry, font, Scrollbar, ttk
import fitz  # PyMuPDF, used to handle and display PDF files within the application
import tempfile  # Used to create temporary files for PDF rendering
import os  # Used to handle file and directory operations
import sys  # Used to manipulate the Python runtime environment

main_dir = os.path.dirname(os.path.abspath(__file__)) # Directory of current script
code_dir = os.path.dirname(main_dir) # Parent directory
mongodb_dir = os.path.join(code_dir, 'MongoDB') # MongoDB's path
sys.path.insert(1, mongodb_dir) # Add MongoDB to system path

from datastructs import Database, notesDS, User # Our custom datastructures for handling operations

# Represents a section of notes in the ARA
class NoteSection:
    def __init__(self, master, username, pdfid, db, notes_app):
        self.frame = Frame(master) # main frame for holding the notes
        self.notes_app = notes_app  # Store the reference to the NotesApp instance (used for prompts)
        self.username = username # username of the user
        self.pdfid = pdfid # ID of the PDF 
        self.db = db # Database connection

        # Use an Entry widget instead of a Label for the section title
        self.title_entry = Entry(self.frame, fg='grey', bg='lightgrey', width=20)
        self.title_entry.insert(0, "Enter Section Title")
        self.title_entry.bind("<FocusIn>", self.on_title_entry_click)
        self.title_entry.bind("<FocusOut>", self.on_title_focusout)
        self.title_entry.pack(side='top', fill='x')


        # Toggle to collapse or expand notes section
        self.toggle_button = Button(self.frame, text="-", command=self.toggle)
        self.toggle_button.pack(side='top', fill='x')

        # Delete section button
        self.delete_button = Button(self.frame, text="Delete", command=self.on_delete_click)
        self.delete_button.pack(side='top', fill='x')

        # Creates text area for writing notes
        self.text_area = tk.Text(self.frame, height=5, width=50)
        self.text_area.pack(side='top', fill='x', expand=True)

        # Bind a key press event to the text area to detect when the user starts typing
        self.text_area.bind("<KeyPress>", self.on_text_entry)

        

    # when user starts taking notes, display prompt 'recite'
    def on_text_entry(self, event):
        # Call the update_prompt method on the NotesApp instance
        self.notes_app.update_prompt('Recite')

    def toggle(self):
        # Collapse or expand text area
        if self.text_area.winfo_viewable():
            self.text_area.pack_forget()
            self.toggle_button.configure(text="+")
        else:
            self.text_area.pack(side='top', fill='x', expand=True)
            self.toggle_button.configure(text="-")

    def on_title_entry_click(self, event):\
        # Clear the entry field when it gets modified
        if self.title_entry.get() == 'Enter Section Title':
            self.title_entry.delete(0, "end")
            self.title_entry.insert(0, '')
            self.title_entry.config(fg='black')

    def on_title_focusout(self, event):
        # Resets the title field if empty
        if not self.title_entry.get().strip():
            self.title_entry.insert(0, 'Enter Section Title')
            self.title_entry.config(fg='grey')

    @property
    def title(self):
        # Gets current title of the section, or default if there isn't one
        return self.title_entry.get().strip() or "Untitled Section"
    
    def delete_section(self, root):
        # Remove section from UI
        if self.db: # Check to see if DB is connected, if so deleteSection.
            self.db.deleteSection(self.username, self.pdfid, self.title_entry.get())
        self.frame.destroy()
        root.withdraw()
    
    def on_delete_click(self): 
        # Confirms deletion of a notes section
        popup = Toplevel() # Popup location
        label = Label(popup, text="Are you sure you want to delete your notes?") # Popup message
        label.pack(fill='x', padx=50, pady=5)

        # Functionality for 'yes'
        logout_button = Button(popup, text="Yes", command=lambda: self.delete_section(popup))
        logout_button.pack(side="left", fill='x', expand=True, padx=10, pady=10)

        # Functionaslity for 'no'
        quit_button = Button(popup, text="No", command=lambda: popup.withdraw())
        quit_button.pack(side="right", fill='x', expand=True, padx=10, pady=10)
    

class NotesApp:
    def __init__(self, master, pdf_path, username, pdf_id, root, db):
        self.master = master # main app window
        self.root = root     # root window, used for other windows
        self.pdf_path = pdf_path # Path to PDF file
        self.pdf_document = fitz.open(pdf_path) # Opens the PDF using PyMuPDF library                   
        self.current_page = 0       # inits current page to the first one 
        self.username = username    # Stores the username of the current user
        self.sections = []          # List to store note sections
        self.pdf_id = pdf_id        # Store the ID of current PDF

        self.db = db # Variable to store Database object
        if self.db is None: # Checks to see if Database has been connected too
            messagebox.showwarning("Warning", "You are not connected to the database. Your work will not be saved.")
        
        self.create_notes_frame()   # Creates frame for the notes
        self.create_buttons()       # Add buttons
        self.create_pdf_viewer()    # Sets up PDF viewer
        self.create_prompts()       # Creates prompts for user
        # Create example sections for notes 
        self.example_notes = {"Software process models": "A software process model is a simplified representation of a software process", "Process activities": "Real software processes are interleaved sequences of technical, collaborative, and managerial activities with the overall goal of specifying, designing, implementing, and testing a software system", 
                              "Coping with change": "Change adds to the costs of software development because it usually means that work that has been completed has to be redone. This is called rework.",
                                "Proccess improvement": "Two quite different approaches to process improvement and change are used: The process maturity approach and The agile approach"}

        if self.pdf_id == "Example Chapter":
            #If the user is accessing Example PDF we load the prewritten example notes
            self.add_example_notes()

    def load_notes(self):
        user = User(self.username, None)  # Assuming password is not used for now
        notes_data = user.getNotes(self.username, self.pdf_id) # Fetches notes
        
        # Debugging
        # print("Loaded notes data: ", notes_data) 

        if notes_data:
            # If notes exist, populate sections
            self.chapter_title_entry.delete(0, "end")
            self.chapter_title_entry.insert(0, notes_data.chapterTitle)
            self.chapter_title_entry.config(fg='black')

            # For debugging
            # print("Chapter title:", notes_data.chapterTitle)
            # print("Sections", notes_data.sections)
        
            for section in notes_data.sections:
                self.add_section(section['sectionTitle'], section['sectionNotes'])
        else:
            print("No notes found for this PDF.") # Log when there's no notes

    def create_notes_frame(self):
        # Sets up notes frame with widgets for note taking
        self.notes_frame = Frame(self.master)
        self.notes_frame.pack(side='right', fill='both', expand=True)

        # Set the larger font
        self.entry_font = font.Font(size=14)

        # Add a heading for the chapter title entry
        heading_label = Label(self.notes_frame, text="Chapter Title:", font=self.entry_font)
        heading_label.pack(side='left', padx=(5, 10), pady=25, anchor='n')

        # Entry for the chapter title
        self.chapter_title_entry = Entry(self.notes_frame, font=self.entry_font, fg='grey', bg='lightgrey')
        self.chapter_title_entry.insert(0, "Enter Chapter Title")
        self.chapter_title_entry.bind("<FocusIn>", self.on_entry_click)
        self.chapter_title_entry.bind("<FocusOut>", self.on_focusout)
        self.chapter_title_entry.pack(side='top', fill='x', padx=5, pady=25)

        self.create_add_section_button()  # Call it here to make sure it's packed in the correct frame

        # Create a canvas to hold NoteSections
        self.notes_canvas = Canvas(self.notes_frame, bg="white")

        scrollbar = Scrollbar(self.notes_frame, orient='vertical', command=self.notes_canvas.yview)
        scrollbar.pack(side='right', fill='y')

        # Configure the inner notes frame to use the scrollbar
        #self.notes_canvas.config(yscrollcommand=scrollbar.set, scrollregion=self.notes_canvas.bbox("all"))
        self.notes_canvas.pack(side="left", fill="both", expand=True)

    def on_entry_click(self, event):
        if self.chapter_title_entry.get() == 'Enter Chapter Title':
            self.chapter_title_entry.delete(0, "end")  # Delete all the text in the entry
            self.chapter_title_entry.insert(0, '')     # Insert blank for user input
            self.chapter_title_entry.config(fg='black')
    
    def on_focusout(self, event):
        # Event handler for clicking out of the entry
        if self.chapter_title_entry.get() == '':
            self.chapter_title_entry.insert(0, 'Enter Chapter Title')
            self.chapter_title_entry.config(fg='grey')

    def create_pdf_viewer(self):
        # Creates PDF viewing environment
        self.canvas = Canvas(self.master, width=800, height=1000) # Initializes canvas
        self.canvas.pack(side='left', fill='both', expand=True)
        self.display_page(self.current_page)

    def display_page(self, page_number):
        page = self.pdf_document.load_page(page_number) # Loads specified page
        pix = page.get_pixmap()                         # Library function call
        # Create a temporary file for the pixmap
        temp_file_path = tempfile.mktemp(suffix=".png")
        pix.save(temp_file_path)  # Save pixmap to a PNG file

        # Load this image into a PhotoImage
        self.photo = tk.PhotoImage(file=temp_file_path)
        self.canvas.create_image(0, 50, image=self.photo, anchor='nw')

        # Clean up the temporary file
        os.remove(temp_file_path)

    def get_current_pdf_id(self):
        # Since the PDF ID is pre-assigned and stored in the instance, just return it
        return self.pdf_id
    
    def switch_pdf(self):
        # Handles switching of PDFs for a user
        popup = Toplevel() # Popup location
        popup.title("Exit")
        label = Label(popup, text="Are you sure you want to switch PDFs?") # Popup message
        label.pack(fill='x', padx=40, pady=5)

        # Yes and no button functionality
        yes_button = Button(popup, text="Yes", command=lambda: [user_pdf_selection(self.username, popup), popup.withdraw(), self.master.withdraw(), self.save_notes()]) #INCLUDE SAVE_NOTES LATER WHEN WORKING
        yes_button.pack(side="left", fill='x', expand=True, padx=10, pady=10)
        no_button = Button(popup, text="No", command=popup.withdraw)
        no_button.pack(side="right", fill='x', expand=True, padx=10, pady=10)


    def create_buttons(self):
        # Creates buttons for different applications in the ARA

        self.buttons_frame = Frame(self.master) # Assigns a frame to where buttons are located
        self.buttons_frame.pack(side='left', fill='y', padx=10, pady=10)

        # Next page button
        next_page_button = Button(self.buttons_frame, text="Next Page", command=self.next_page)
        next_page_button.pack(padx=5, pady=5, fill="x")

        # Previous page button
        prev_page_button = Button(self.buttons_frame, text="Previous Page", command=self.prev_page)
        prev_page_button.pack(padx=5, pady=5, fill="x")

        # Save button
        save_button = Button(self.buttons_frame, text="Save", command=self.save_notes)
        save_button.pack(padx=5, pady=5, fill="x")
        
        # Exit button
        exit_button = Button(self.buttons_frame, text="Exit", command=self.on_exit_button_click)
        exit_button.pack(padx=5, pady=5, fill="x")

        # Button to change PDFs
        pdf_switch_button = Button(self.buttons_frame, text="Change PDF", command=self.switch_pdf)
        pdf_switch_button.pack(padx=5, pady=5, fill="x")

        # Hide or show PDF button
        hide_show_PDF_button = Button(self.buttons_frame, text="Hide/Show PDF", command=self.hide_show_pdf)
        hide_show_PDF_button.pack(padx=5, pady=5, fill="x")

        #Hide or show Prompts
        toggle_prompts_button = Button(self.buttons_frame, text="Toggle Prompts", command=self.toggle_prompts)
        toggle_prompts_button.pack(padx=5, pady=5, fill="x")
    
    def toggle_prompts(self):
        # This method toggles the visibility of the prompts
        if self.sq3r_prompt_label.winfo_viewable():
            self.sq3r_prompt_label.place_forget()  # This hides the prompt label
        else:
            self.sq3r_prompt_label.place(relx=0.5, rely=0, anchor="n")  # This shows the prompt label

    def update_prompt(self, action):
        # This method updates the prompt based on the action taken.
        if action in self.sq3r_prompts:
            self.current_prompt_key = action
            self.sq3r_prompt_label.config(text=self.sq3r_prompts[self.current_prompt_key])
            self.sq3r_prompt_label.place(relx=0.5, rely=0, anchor='n')  # Show the updated prompt

    def create_prompts(self):
        self.sq3r_prompts = {
            'Survey': "Survey the chapter: Look at titles, headings, and any available summaries or key points.",
            'Question': "Create questions: What do you expect to learn from this section based on the headings?",
            'Read': "Read to answer your questions. Pay attention to the arguments and evidence presented.",
            'Recite': "Recite the main points: Without looking at the text, note down what you remember.",
            'Review': "Review your notes and the text. Did you capture the key points? What did you miss?"
        }
        self.current_prompt_key = 'Survey'  # Start with the 'Survey' prompt
        self.sq3r_prompt_label = Label(self.canvas, text=self.sq3r_prompts[self.current_prompt_key], bg="lightyellow", fg="black", wraplength=self.canvas.winfo_reqwidth())
        self.sq3r_prompt_label.place(relx=0.5, rely=0, anchor='n')
        

    def hide_show_pdf(self):
        # Hides or shows a PDF

        # Checking if it has an attribute
        if hasattr(self, 'pdf_visible'):
            if self.pdf_visible:
                # Hide the PDF viewer
                self.canvas.pack_forget()
                self.pdf_visible = False # hides
            else:
                # Show the PDF viewer
                self.canvas.pack(side='left', fill='both', expand=True)
                self.pdf_visible = True # shows
        else:
            # If the attribute doesn't exist yet, assume the PDF is initially visible
            self.pdf_visible = True
            self.hide_show_pdf()  # Call sets init state

    def next_page(self):
        # PDF next page gets displayed
        if self.current_page < self.pdf_document.page_count - 1:
            self.current_page += 1
            self.display_page(self.current_page)
        
        if self.current_page % 2 == 0:  # after looking through couple pages, promp 'Question'
            self.update_prompt('Question')
        else:   # Assuming the user has started 'Reading'
            self.update_prompt('Read')

    def prev_page(self):
        # PDF previous page gets displayed
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page(self.current_page)
        
        if self.current_page == 0:    # If it's the first page, remind them to 'Survey'
            self.update_prompt('Survey')
        elif self.current_page % 2 == 0:  # after looking through couple pages, promp 'Question'
            self.update_prompt('Question')
        else:   # Assuming the user has started 'Reading'
            self.update_prompt('Read')

    def create_add_section_button(self):
        # Button for adding a new section
        add_section_button = Button(self.notes_frame, text="Add Section", command=self.add_new_section)
        add_section_button.pack(side='bottom',pady=5)

    def add_example_notes(self):
        # Function to add notes sections for the example notes PDF 
        # Only called when the user is accessing the Example PDF 
        self.chapter_title_entry.delete(0, "end")
        self.chapter_title_entry.insert(0, "Software processes")
        for title, text in self.example_notes.items():
            #Loop through the dictionary of (section title: section notes) and fill the notes section classes
            new_section = NoteSection(self.notes_canvas, self.username, self.pdf_id, self.db, self)  # No title passed here
            new_section.frame.pack(fill='x', expand=False)
            self.sections.append(new_section)
            new_section.title_entry.delete(0, "end")
            new_section.title_entry.insert(0, title)
            new_section.title_entry.config(fg='black')
            new_section.text_area.insert("end", text)

    def add_new_section(self):
        # Functionality for adding a new section
        # Allocating memory in the DB
        new_section = NoteSection(self.notes_canvas, self.username, self.pdf_id, self.db, self)  # No title passed here
        new_section.frame.pack(fill='x', expand=False)
        self.sections.append(new_section)
        self.update_prompt('Recite') #when user goes to take notes, prompt changes to Recite
            
        
            

    def add_section(self, title, content):
        # User interface update function for adding a new section
        # Getting user's PDF and notes from the DB
        new_section = NoteSection(self.notes_canvas, self.username, self.pdf_id, self.db, self)
        new_section.title_entry.delete(0, "end")
        new_section.title_entry.insert(0, title)
        new_section.title_entry.config(fg='black')
        new_section.text_area.insert("1.0", content)
        new_section.frame.pack(fill='x', expand=False)
        self.sections.append(new_section)


    def save_notes(self):
        # Checks to see if DB is connected, warns user if not.
        if self.db is None:
            messagebox.showwarning("Warning", "You are not connected to the database. Your work will not be saved.")
            return  # Stop further execution
        #pdfID should be available for the PDF being annotated
        pdfID = self.get_current_pdf_id()  # Implement this method or get pdfID from your app's state
        chapterTitle = self.chapter_title_entry.get()

        notes_obj = notesDS(pdfID, chapterTitle)  # Create a new notesDS object
        
        ## Collect the notes from each section
        for section in self.sections:
            # Check if the section still exists before accessing it
            if section.title_entry.winfo_exists() and section.text_area.winfo_exists():
                # Get the title from the Entry widget in NoteSection
                title = section.title
                # Get text from Text widget
                content = section.text_area.get("1.0", "end-1c")
                # Add section to notesDS object
                notes_obj.addSection(title, content)
            else:
                print("Section doesn't exist. Skipping...")

        # Now update the notes in the database
        self.db.updateUserNotes(self.username, notes_obj)  # Pass the notesDS object to update notes

        print("Notes saved!")
        
    def on_exit_button_click(self):
        # Functionality for exit button
        popup = Toplevel() # Popup location
        popup.title("Exit")
        label = Label(popup, text="Do you want to log out or quit?") # Popup text
        label.pack(fill='x', padx=50, pady=5)
        logout_button = Button(popup, text="Logout", command=lambda: self.logout(popup))   # Logout button 
        logout_button.pack(side="left", fill='x', expand=True, padx=10, pady=10)
        quit_button = Button(popup, text="Quit", command=lambda: self.quit_program(popup)) # Quit button 
        quit_button.pack(side="right", fill='x', expand=True, padx=10, pady=10)
        popup.grab_set()

        # Before quitting, suggest the user to 'Review' their work
        self.update_prompt('Review')

    def logout(self, popup):
        # Logs out user
        self.save_notes()   # Notes are auto saved
        self.master.withdraw()
        popup.destroy()     # Destroys the confirmation window
        global login_screen # Global login screen variable to access the login screen after logging out
        if login_screen:
            login_screen.deiconify()
        print("Logged out")

    def quit_program(self, popup):
        if self.db: # Check to see if DB is connected too
            self.save_notes() # If connected, save notes
        # Destroy the popup window
        popup.destroy()
        # Terminate the entire program
        if self.master is not None:
            self.master.quit()
            self.master.destroy()  # This will close the main window
        print("Program terminated")


def open_login_screen(root):
    global login_screen
    def valid_login(username):
        # Retrieve the entered username and password
        if username == "Admin":
            adminwindow = tk.Toplevel(root)
            adminwindow.title("Setup Instructions")
            
            # Create a scrolled text widget to display the file contents
            text_area = scrolledtext.ScrolledText(adminwindow, wrap=tk.WORD, width=80, height=20)
            text_area.pack(expand=True, fill='both')
            
            try:
                # Open the file named "output.txt" and read its contents
                with open("../MongoDB/commands.txt", 'r') as file:
                    file_contents = file.read()
                
                # Display the contents in the text area
                text_area.insert(tk.END, file_contents)
            except FileNotFoundError:
                messagebox.showinfo("Info", "File not found.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            
            # Function to handle closing the setup instructions window
            def close_setup_instructions():
                # Show the root login screen
                # Close the setup instructions window
                adminwindow.destroy()
            
            # Bind the close event of the setup instructions window to the close_setup_instructions function
            adminwindow.protocol("WM_DELETE_WINDOW", close_setup_instructions)
            # Start the tkinter event loop
        else:
            login_screen.withdraw()  # Hide the login_screen window (Toplevel)
            user_pdf_selection(username, root)  # Pass the root window
            print("Login Successful, User: ", username)
        
    try:
        login_screen.destroy()
    except:
        pass  # If it doesn't exist yet, no need to destroy

    login_screen = tk.Toplevel(root)
    login_screen.title("Login")

    users = ["User1", "User2", "User3", "Admin"]
    for i, title in enumerate(users):
        # Create a label for the title
        label = tk.Label(login_screen, text=title)
        label.grid(row=0, column=i, padx=10, pady=5)
        
        # Create a button
        button = tk.Button(login_screen, text="Login", command=lambda t=title: valid_login(t))
        button.grid(row=1, column=i, padx=10, pady=5)
    login_screen.protocol("WM_DELETE_WINDOW", lambda: root.destroy())

def user_pdf_selection(username, root):
    # Create the PDF selection window as a Toplevel window
    selection_window = tk.Toplevel(root)
    selection_window.title("Select PDF")
    selection_window.geometry("300x200")
    
    # Display message
    message_label = tk.Label(selection_window, text=f"Hello, {username}. Please select a PDF to begin:")
    message_label.pack(pady=10)

    def on_pdf_selection(pdf_id):
        # You may want to pass the pdf_id (if different from chapter_title) to main_window
        selection_window.destroy()  # Close the PDF selection window
        main_window(username, pdf_id, root)  # Open the main window with the selected PDF
    
    # Dictionary of PDF chapter titles and corresponding IDs
    pdf_options = {
        "Chapter 6": 1,
        "Chapter 3": 2,
        "Chapter 2": 3,
        "Example Chapter": 4
    }

    # Create a button for each PDF chapter title
    for chapter_title, _ in pdf_options.items():
        button = tk.Button(selection_window, text=chapter_title, command=lambda title=chapter_title: on_pdf_selection(title))
        button.pack(fill='x', padx=50, pady=5)

    # Make the selection window modal
    selection_window.grab_set()

def main_window(username, pdf_id, root):
    # Main UI function

    # ARA window initializastion
    main_app_window = tk.Toplevel(root)
    main_app_window.geometry("1200x700")

    # Paths to selectable PDFs to be used with the ARA
    pdf_paths = {
        "Chapter 6": "../../Resources/Sommerville_Chapter_6_Survey_Highlighted.pdf",
        "Chapter 3": "../../Resources/Chapter3.pdf",
        "Chapter 2": "../../Resources/Sommerville-Chapter-2.pdf",
        "Example Chapter": "../../Resources/Sommerville-Chapter-2.pdf",

    }

    # Create Databse object and check to see if it connected properly
    db = Database("mongodb://localhost:27017/", "active_reading_assistant", "schema.json")
    if db.connected == False:
        db = None # DB set to None if unable to connect.

    # Retrieve the path using the pdf_id (which is the same as the chapter title in your case)
    pdf_path = pdf_paths[pdf_id]  # No need for the default path since the ID is guaranteed to be valid
    notes_app = NotesApp(main_app_window, pdf_path, username, pdf_id, root, db)  # The chapter title is used as the pdf_id
    if db:
        notes_app.load_notes()  # Load notes for the selected PDF
    main_app_window.protocol("WM_DELETE_WINDOW", lambda: notes_app.quit_program(main_app_window))

def main():
    global login_screen # To be accessed by logout function
    login_screen = None # Initialize as None

    root = tk.Tk()      # Using TKinter library
    root.withdraw()
    open_login_screen(root) # Calls login screen first
    root.mainloop()

if __name__ == "__main__":
    main()