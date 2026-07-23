# MyVault - A Simple & Secure Password Manager

Welcome to MyVault! This is a personal, offline password manager built with Python. 

Instead of trusting your passwords to a cloud server, MyVault saves everything safely on your own computer. It features a beautiful dark-mode interface and uses strong encryption to make sure nobody but you can see your saved accounts.

## Features

* **Beautiful Interface:** A modern, easy-to-use dashboard built with CustomTkinter.
* **Built-in Password Generator:** Need a strong password? Click one button to generate a highly secure, random password.
* **Instant Search:** Find your accounts quickly by typing in the search bar.
* **Click to Copy:** Copy your passwords directly to your clipboard so you don't have to type them out.
* **Data Portability:** Easily import existing passwords or export your vault using CSV files.
* **Fully Offline:** Doesn't connect to the internet, keeping your data safe from online hackers.

## How it Keeps You Safe

Even though this app is easy to use, it has serious security under the hood:

* **Your Master Password is a Secret:** The app never saves your Master Password anywhere. 
* **Data Scrambling:** When you save your passwords, the app scrambles them into unreadable gibberish (using industry-standard AES encryption). Without your Master Password, the saved file is completely useless to anyone who tries to open it.
* **Auto-Locking:** When you click "Lock Vault", the app instantly forgets your data until you log in again.
* **Export Warning:** If you choose to export your vault to a CSV, that file is saved in plain text. Please securely delete exported CSV files immediately after migrating your data!

## How to Run It

To run this app from the source code, you will need **Python 3** installed on your computer.

1. **Download the code:**
```bash
   git clone [https://github.com/YOUR_USERNAME/password_manager.git](https://github.com/YOUR_USERNAME/password_manager.git)
   cd password_manager

```

2. **Set up a virtual environment (optional but recommended):**
```bash
python -m venv venv
source venv/bin/activate

```


*(Note: If you are on Windows, use `venv\Scripts\activate` instead)*


3. **Install the required tools:**
```bash
pip install -r requirements.txt

```


4. **Launch the app:**
```bash
python main.py

```



## Important Note

*Because this app is completely private, there is no "Forgot Password" button. Please make sure you remember your Master Password, or you will not be able to unlock your vault!*

