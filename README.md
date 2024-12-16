# Alwassit Dictionary Django API

## Overview

The **Alwassit Dictionary Django API** is a **Django-based REST API** that provides powerful dictionary lookup services. It allows users to interact with the Alwassit Dictionary programmatically, offering a range of advanced search functionalities. This API is designed to support linguistic research, language learning, and dictionary services.

### **Key Functionalities**
- **Exact Match**: Retrieve dictionary entries by exact word match, with or without diacritics.
- **No Match Suggestions**: Suggest alternative words when no exact match is found.
- **Homonyms**: Handle multiple meanings by linking entries with the same lexical ID.
- **Root-Based Search (جذر)**: Find conjugated or inflected forms of a word based on its root.
- **Spelling Variations**: Account for common spelling variations (e.g., همزة/ألف) using normalization.
- **Idioms and Compound Phrases**: Search for multi-word phrases or idioms within definitions and contexts.
- **Advanced Filtering**: Apply filters to results based on various fields, such as grammatical categories or context.

---

## Setup Instructions

### **1. Clone the Repository**
1. Open a terminal and navigate to the folder where you want to clone the repository.
2. Run the following commands:
   ```bash
   git clone https://github.com/Hind-Almerekhi/AlwassitDjango.git
   cd AlwassitDjango
   ```

---

### **2. Install Git LFS**
This project uses **Git LFS** to manage large files. Install it using one of the following methods:
- **Ubuntu/Debian**:
  ```bash
  sudo apt install git-lfs
  ```
- **macOS**:
  ```bash
  brew install git-lfs
  ```
- **Windows**:
  Download Git LFS from [Git LFS](https://git-lfs.github.com) or use a package manager like Chocolatey.

After installation, run:
```bash
git lfs install
git lfs pull
```

---

### **3. Create a Virtual Environment**
Set up a Python virtual environment for the project:
1. Create the virtual environment:
   ```bash
   python -m venv env
   ```
2. Activate it:
   - **Linux/macOS**:
     ```bash
     source env/bin/activate
     ```
   - **Windows**:
     ```bash
     env\Scripts\activate
     ```

---

### **4. Install Dependencies**
Install the required Python packages using:
```bash
pip install -r requirements.txt
```

---

### **5. Apply Database Migrations**
Set up the database schema:
```bash
python manage.py makemigrations dictionary
python manage.py migrate
```

---

### **6. Populate the Database**
Use the provided script to populate the database with dictionary data:
```bash
python manage.py shell
import populate_db as pdb
pdb.main()
```

---

### **7. Run the Development Server**
Start the Django development server:
```bash
python manage.py runserver
```

- Access the API in your browser or testing tools like Postman:
  - Main endpoint: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
  - API documentation : [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

---

## Note
- Ensure you have **Python 3.10 or later** installed before starting the setup. This is required for compatibility with Django 5.1.