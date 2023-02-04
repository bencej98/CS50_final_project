# CS50_final_project 

## Project name: Financial Tracker  
  
# Description:  

This project was created for the final lesson of Harvard University's CS50 course. Throughout my aim was to create a webapp that tracks the change of savings in a persons life. The webapp is hosted on pythonanywhere and you can reach it via this link: https://financetracker.pythonanywhere.com/

# App Structure:

├── CS50_final_project  
│   ├── app.py  
│   ├── helpers.py  
│   ├── README.md  
│   ├── requirements.txt  
│   ├── static  
│   │   ├── highlight_current.js  
│   │   ├── picture.ico  
│   ├── templates  
│   │   ├── admin.html  
│   │   ├── layout.html  
│   │   ├── login.html  
│   │   ├── main_page.html  
│   │   ├── registers.html  
│   │   ├── reports.html  
│   │   ├── transactions.html  


# Tech Stack:

Python  
Flask Framework  
Javascript  
HTML  
CSS  
SQLite  

# Usage

### Registering:  

To use this app one should register using a username and a password. There are prerequisites for both the username and the password and in case they are not met the webapp displays and error message to the user. For the username one should only use numbers or letters meanwhile the password must containt at least 8 characters in which at least there is one uppercase letter and a number.

The webapp currently consists of 4 pages which are the homepage, transactions, reports and admin

### Homepage:  

After logging in you are redirect to the homepage where you can see your current balance of the different kind of assets. These are updated as you deposit or withdraw from your account.

### Transactions:  

On the transactions tab you can perfrom two kind of transactions which are depositing or withdrawing from your account. After choosing the transaction type you also have to choose a possession type that you want to modify. 

NOTE that currently the webapp only supports USD currency!

### Reports:  

On this tab you can see all of the transactions that the currently logged in user made in the past.

### Admin:  

This is a special tab where you can delete from all of the users that have registered before. You can only access this tab if you have admin rights. There is a preregistered admin user for the webapp.
The credentials for this user are the following:
Username: admin
Password: admin

The user can log out from the webapp with the Log Out button situated in the right corner.


# Structure of the webapp  

Financie Tracker is written mainly in Python using Flask framework. It also contains a little bit of Javascript as well.

For the database it uses SQLite3 which is a relational database.

To use the app you need specific tables that the webapp handles.

The app.py contains the main functions that the webapp operates with. All of the functions that are called using the navbar are located in this file.

The helpers.py contains smaller function that are called in the app.py file.

The highlight_current.js contains a javascript function to highlight the current tab on the navbar.

There are other supporting files as well such as the html files.

# Future Development  

Currently there is a plan to make a new tab called "Budget" and a currency selector. The home page dashboard could be improved with some diagrams.

# Struggles / Summary 

Given the fact the the Flask framework, Javascript and SQLite is completely new to me most of the time I had to use the documentations to connect the dots. 
I believe that I learnt a lot of new technologies and solutions throughout this project. Before starting CS50 I could have never imagined that I will be able to create something like this from scratch. I am eager to learn new technologies and continue my path to be a full-time developer one day.


