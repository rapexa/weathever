# weather

This advance project is done for school teaching classes as a project series.

## Todolist :
- [x] start project
- [x] make comment and introduction in both code sites
- [x] connect this function to the others and project :: readdata
- [x] make this variable jinja for .html template :: cityname
- [x] twins readdata solve for once
- [x] make latest read data and index page without timestamp
- [x] work on history page read data from mysql server and show it  
- [x] develop more ... 
- [x] write complete readme.md file + help and manufacturing
- [ ] add download xlsx file to history page continue coding
- [x] done 

## How to run

1. Install python3, pip3, virtualenv, MySQL in your system.

2. Clone the project `https://github.com/rezvanghd/weather.git` && cd sms_serial_verification

3. in the app folder, in `config.py` do proper changes.

4. run this comand in MYSQL database : `CREATE DATABASE weather;`

5. run this comand in MYSQL database : `CREATE USER 'weather'@'localhost' IDENTIFIED BY 'weather';`

6. run this comand in MYSQL database : `GRANT ALL PRIVILEGES ON weather.* TO 'weather'@'localhost';`

7. run this comand in MYSQL database : `DROP TABLE IF EXISTS works`

8. db configs are in config.py. Create the db and grant all access to the specified user with specified password, but you also need to add this table to the database manually: `CREATE TABLE works (tempmanualc VARCHAR(100),pressure VARCHAR(100),humidity VARCHAR(100),croodlon VARCHAR(100),croodlat VARCHAR(100),weathermain VARCHAR(100),weatherdescription VARCHAR(100),visibility VARCHAR(100),windspeed VARCHAR(100),winddeg VARCHAR(100),cloudsall VARCHAR(100),syscountry VARCHAR(100),syssunrise VARCHAR(100),syssunset VARCHAR(100),timezone TIMESTAMP,name VARCHAR(100),timestamp TIMESTAMP);`

9. you also need to add this table to the database manually: `CREATE TABLE messages (alltext VARCHAR(1024),time TIMESTAMP);`

10. Create a virtualenve named build using `virtualenv -p python3 venv`

11. Connect to virtualenv using `source venv/bin/activate`

12. From the project folder, install packages using `pip install -r ./requirements.txt`

13. Now environment is ready. Run it by `python app/main.py`

#### DONE