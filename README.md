
## SECTION 1 : PROJECT TITLE
## TravelAI - Flight & Hotel Recommender for multi-country trips.

<img src="SystemCode/clips/static/hdb-bto.png"
     style="float: left; margin-right: 0px;" />

---

## SECTION 2 : EXECUTIVE SUMMARY / PAPER ABSTRACT
Travel is a US 2.9 trillion dollar industry. Existing web scrapers offer the best deals for flights for a single searched date, and best deals for hotels for a single date range. Traditional travel agencies offer a hassle-free multi-destination travel experience. However, there is no product that a free and easy, multi-destination traveller can use to find the sequence of travel that will give the lowest overall flight and hotel cost. A possible solution could be to manually look up the different flights and hotels on all his travel dates, total up the prices of each combination, and pick the lowest-priced one. An exhaustive search for a trip with n different destinations, and d number of days would amount to at least  (n! × d) searches. Solving for the combination that gives the lowest cost will be another hassle.

In this project, our group has proposed an end-to-end solution by automating the collection of relevant flights and hotels details by calling an API, solving for the combination of flight and hotels that balances between cost and time spent at each destination, and booking the optimized package with respective travel agencies. As an added bonus, our solution will also based on the travel destination and user profile, return a curated list of top places of interest in the destinations that users will be travelling to.

Therefore, we introduce TravelAI, a conversational agent that helps users book multi-stop travel journeys optimised for their cost and time priorities, and offers a curated list of places of interest tailored to user profile and his travel destinations.

---

## SECTION 3 : CREDITS / PROJECT CONTRIBUTION

| Official Full Name  | Student ID (MTech Applicable)  | Work Items (Who Did What) | Email (Optional) |
| :------------ |:---------------:| :-----| :-----|
| Mohamed Mikhail Kennerley | A0213546J | •OR-Tools Optimiser <br>•Video <br>•Survey Design & Data Extraction| e0508649@u.nus.edu |
| Loy Pei Xin Veronica | A0213524R | •Flight,Hotel,Tripadvisor API <br>•Rules Formulation <br>•Project Report| E0508647@u.nus.edu|
| Oh Chun How | A1234567C | •System architecture and intergration <br>•Dialog Flow System zzzzzzzzzz| Chunhow.oh@u.nus.edu |

---

## SECTION 4 : VIDEO OF SYSTEM MODELLING & USE CASE DEMO

[![Sudoku AI Solver](http://img.youtube.com/vi/-AiYLUjP6o8/0.jpg)](https://youtu.be/-AiYLUjP6o8 "Sudoku AI Solver")
---

## SECTION 5 : USER GUIDE

`Refer to appendix <Installation & User Guide> in project report at Github Folder: ProjectReport`

### [ 1 ] To run the system using iss-vm

> download pre-built virtual machine from http://bit.ly/iss-vm

> start iss-vm

> open terminal in iss-vm

> $ git clone https://github.com/telescopeuser/Workshop-Project-Submission-Template.git

> $ source activate iss-env-py2

> (iss-env-py2) $ cd Workshop-Project-Submission-Template/SystemCode/clips

> (iss-env-py2) $ python app.py

> **Go to URL using web browser** http://0.0.0.0:5000 or http://127.0.0.1:5000

### [ 2 ] To run the system in other/local machine:
### Install additional necessary libraries. This application works in python 2 only.

> $ sudo apt-get install python-clips clips build-essential libssl-dev libffi-dev python-dev python-pip

> $ pip install pyclips flask flask-socketio eventlet simplejson pandas

---
## SECTION 6 : PROJECT REPORT / PAPER

`Refer to project report at Github Folder: ProjectReport`

- Executive Summary
- Market Research
- Problem Description
- Project Objectives & Scope
- Project System Architecture
- Project Systen Design and Implementation
- Project Conclusions: Findings & Recommendation
- Appendix of report: Project Proposal
- Appendix of report: Mapped System Functionalities against knowledge, techniques and skills of modular courses: MR, RS, CGS
- Appendix of report: Installation and User Guide
- Appendix of report: Individual project report
- Appendix of report: References

---
## SECTION 7 : MISCELLANEOUS

`Refer to Github Folder: Miscellaneous`

### HDB_BTO_SURVEY.xlsx
* Results of survey
* Insights derived, which were subsequently used in our system

---

**This [Machine Reasoning (MR)](https://www.iss.nus.edu.sg/executive-education/course/detail/machine-reasoning "Machine Reasoning") course is part of the Analytics and Intelligent Systems and Graduate Certificate in [Intelligent Reasoning Systems (IRS)](https://www.iss.nus.edu.sg/stackable-certificate-programmes/intelligent-systems "Intelligent Reasoning Systems") series offered by [NUS-ISS](https://www.iss.nus.edu.sg "Institute of Systems Science, National University of Singapore").**

**Lecturer: [GU Zhan (Sam)](https://www.iss.nus.edu.sg/about-us/staff/detail/201/GU%20Zhan "GU Zhan (Sam)")**

[![alt text](https://www.iss.nus.edu.sg/images/default-source/About-Us/7.6.1-teaching-staff/sam-website.tmb-.png "Let's check Sam' profile page")](https://www.iss.nus.edu.sg/about-us/staff/detail/201/GU%20Zhan)

**zhan.gu@nus.edu.sg**
