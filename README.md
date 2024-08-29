# Data Smell Detection +
Repository of the project made for Software Engineering for Artificial Intelligence (SE4AI) and Software
Engineering, Management and Evolution (IGES), two master degree courses at [University of Salerno](https://www.unisa.it/).

<br/>
<p align="center" style="border-radius:10px;"><img src="web_application/argon-dashboard-django/core/static/assets/img/brand/tuk5.png" width = "350vw"></p>
<br/>

## Contributors

* [Francesco Paolo D'Antuono](https://github.com/CpDant)
* [Daniele Fabiano](https://github.com/Tensa53)
* [Adriano Emanuele Califano](https://github.com/adriano22jr)

## Introduction
DSD (Data Smell Detection) is based on the open-source data validation tool <b>Great Expectations</b> and it uses rule-based techniques for detecting smells by analyzing a dataset. <b>DSD+</b> aims to extend the existing smell detection suite, and it is also intended to improve the current dataset reporting mechanism by integrating the calculation of data quality dimensions metrics, along with additional measurements. In addition, it will be possible to visualize the results of the tool's execution, to track changes obtained over time as a result of new analyses and to form a basis for indications of quality improvement/deterioration of the modified dataset.

## Setup Server
It is assumed that all the following steps are executed inside the root directory of this project.
### Setup with Docker (Recommended if you only want to try the project)

 1. The **Dockerfile** and **docker-compose.yml** are located in the root directory.
 2. Build the docker image with `sudo docker-compose build`.
 3. Start the web application with `sudo docker-compose up -d`.
 4. The web application can be visited at `http://127.0.0.1:5005`.

### Dockerless Server Setup (Recommended if you want to contribute the improvement of the tool)
#### Setup Data Smell Detection Library
```bash

    # Virtualenv modules installation and activation (Unix based systems)
    sudo apt-get install python3-pip
    sudo pip3 install virtualenv 
    virtualenv env 
    source env/bin/activate

    # Install the requirements and the data smell detection library
    cd data_smell_detection
    pip install -r requirements-dev.in
    python3 setup.py install
     
```
#### Setup Web Application
```bash

    cd ../web_application/argon-dashboard-django/ # application root folder

    # Install modules
    pip3 install -r requirements.txt

    # Create tables
    python manage.py makemigrations
    python manage.py migrate

    # Start the application
    python manage.py runserver

    # Access the web app in browser http://127.0.0.1:8000/
      
```
## Goals

The main goals for this project are:
* <b>CR_01 - Extension of the data smell detection suite</b>: At least one new data smell detector should
be implemented to extend the detection suite that makes the tool available.
* <b>CR_02 - Mechanism for calculating data quality dimension metrics</b>: Related to creating a mechanism for calculating a subset of data quality dimensions referring to the results obtained
from the tool’s analysis done on the specific dataset.
* <b>CR_03 - Improved reporting system</b>: Add the ability to display on the screen the results obtained
from the analysis of a dataset and show over time the change in the dataset, related smells
identified, and metrics/measures calculated.

## Data Collection and System Testing
Datasets that were used for the real-world simulation and system testing, were put in <a href="https://drive.google.com/drive/folders/1zbLlQ9Lg6o-Smvg7BMawz6uSr5otr5U0?usp=sharing">this</a> shared folder.

