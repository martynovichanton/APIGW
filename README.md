# APIGW

## 2 projects - Django and Flask
## 2 apps in each projects - 1 for the GUI dashboard and 1 for the APIGW

## Traffic flow
Client -> nginx -> uwsgi -> api -> device  
Client -> nginx -> uwsgi -> app  
Can be used withoug nginx  

## Features
1. Run multiple commands on multiple devices
2. Seperation by set of commands per main directory - Each main folder can hold multiple devices and their respective commands
3. Flexible and supports multiple devices and commands based on the required set
4. Log all commands and output to the file per device
5. General log to track the process
6. Support for multithreading for all commands per device
7. Playing with in memory ecryption of username, password and token
8. API for F5 and Fortimanager
9. Can be easily extended to use with other APIs


## Django
### Running the server
1 project with 2 apps  
python manage.py runserver  


## Flask
### Running the server
2 projects  
cd API  
python apigw.py  
cd APP  
python app.py  





