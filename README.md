
# Table of Contents
1. [Description of the solution implemented](#description-of-the-solution-implemented) 
    1. [Flask & Jinja](#flask-&-jinja)
    2. [Fernet (encryption)](#Fernet-(encryption))   
    3. [Flask-Login](#Flask-Login)
    4. [WTForms](#WTForms)
    5. [werkzeug](#werkzeug)
    6. [SQLalchemy & mySQL](#SQLalchemy-&-mySQL)
    7. [E-Mail validator](#E-Mail-validator)
    8. [Key storage](#Key-storage)
2. [Instructions on how to execute the code](#Instructions-on-how-to-execute-the-code)
    1. [Prerequisites](#Prerequisites)
        1. [Python libraries](#Python-libraries)
        2. [mySQL backend](#mySQL-backend)
    2. [Run the app](#Run-the-app)
    3. [Encryption-key-creation](#Encryption-key-creation)


# Description of the solution implemented
`app.py` is the monolithic code base of the app. The app lets you upload and share files securely.
It does have user registration & user roles. Additionally  the app also does have the following functions 
* **C**reate: Upload a file
* **R**ead: See what files are for download and download files
* **U**pdate: Update metadata to a file
* **D**elete: Uploaded files can be deleted 

The aforementioned  functions are only accessible if you are authenticated and if your role has the appropriate privileges. 
All files are encrypted on the server and will be decrypted if a properly authenticated user with sufficient privileges request to download the file.
The allowed file types are 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'. The allowed file types can be set within `app.py`.

`app.py` also holds the various classes necessary to run the app:

![UML class diagram of the app](https://raw.githubusercontent.com/janKuefner/eportfolio/main/images/class_diagramm.png)

## Flask & Jinja2
Flask & Jinja was used for this app, since it is a very powerful way of coding websites with Python. 
Jinja2 also automatically escapes all input, which prevents many cross site scripting (XSS) attacks
https://flask.palletsprojects.com/en/2.0.x/  https://pypi.org/project/Jinja2/ 

## Fernet (encryption)
Fernet  is used for encrypting the files for storage. Fernet uses 128-bit AES in CBC mode and PKCS7 padding, with HMAC using SHA256 for authentication, which is a very secure cipher suite. Fernet was also chosen since it is symmetric  encryption which is fast. Asymmetric encryption was not utilized, since no two communication parties are interacting in this scenario. Encryption and decryption is fully done server side.
https://cryptography.io/en/latest/fernet/

## Flask-Login
Flask login was chosen for many reasons. The main reasons for using it here are the following:
It easily stores user sessions in cookies and also keeps track of users on the server side. With Flask Login you can also easily restrict access to certain pages to authenticated users only. 
https://flask-login.readthedocs.io/en/latest/ 

## WTForms
WTForms was used to also implement additional security. WTForms for example comes with CSRF tokens natively.
https://github.com/wtforms/wtforms

## Werkzeug
The library Werkzeug is used to salt hash the password with SHA-256. SHA-256 was chosen, since it provides the highest security.
https://pypi.org/project/Werkzeug/  

## SQLalchemy & mySQL
SQLalchemy is used to store objects in the database without using dedicated database commands. SQLalchemy as the Object Relational Mapper is connected to a mySQL database. MySQL was not chosen for any particular reason. Any other database would also likely be fine.
SQLalchemy provides SQL injection attack prevention, if raw SQL is not utilized. This app does not have any raw SQL queries.
https://flask-sqlalchemy.palletsprojects.com/en/2.x/ 

## E-Mail validator
This library is used to validate, if the given input by the user for his/hers E-Mail address is a correct E-Mail address
https://pypi.org/project/email-validator/

## Key storage
`secrets_lcl.py` & `key.py` are outside the main source code. This is done to avoid hard coding. For best security the credentials should however better be stored in a hardware secure module

# Instructions on how to execute the code
## Prerequisites
### Python libraries
You need to install the following elements, prior using the app.


| Element           | Installing (using pip)                  | 
| ----------------- | --------------------------------------- | 
| Flask             | `(venv) $ pip install flask`            |           
| WTForms           | `(venv) $ pip install WTForms`          |                       
| Werkzeug          | `(venv) $ pip install Werkzeug`         |                     
| Jinja2            | `(venv) $ pip install Jinja2`           |                        
| Flask-SQLAlchemy  | `(venv) $ pip install flask-sqlalchemy` |     
| Flask-Login       | `(venv) $ pip install flask-login`      |          
| cryptography      | `(venv) $ pip install cryptography`     |                      
| E-Mail validator  | `(venv) $ pip install email-validator`  |                      


### mySQL backend
You need to have a properly configures mySQL backend server running. To do so follow these steps

1. Create a local mySQL instance & install mySQL workbench to run queries and troubleshoot the database. Note down mySQL username and password for later
2. Run the following script script in your MySQL workbench to have dummy data as well as a proper table layout for the app to work
```javascript
CREATE DATABASE IF NOT EXISTS iss_database_2 DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE iss_database_2;

CREATE TABLE IF NOT EXISTS `user` (
`id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('0','1','2','3','Admin') NOT NULL DEFAULT '0',
  `email` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

INSERT INTO `user` (`id`, `name`, `password`, `role`, `email`) VALUES
(1, 'keyser', 'sha256$kHBZbaJmReaEHBMA$0d4d3797f3906d5c9e352bde9da3e704011cc77715237cd860272952abfece46', 'Admin','keyser@soze.com' ),
(2, 'steven', 'sha256$kJCtq3B6Wbsq9YtK$a1dffc4ba12a6a60b9b5155cfb82121d8d9bb8029be3d4d4269b3b66e504b39a', '0','steven@iss.org' ),
(3, 'lisa', 'sha256$f6NXQWM1zW2PFrT7$fccc71d37f1bfc55809868ac64a5ce3e1420a1cc5631eac2ba845a9f10376288', '2','lisa@iss.org' );


CREATE TABLE IF NOT EXISTS `data` (
`id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `confidential` TINYINT(1) NOT NULL,
  `uploader` int(11) NOT NULL,
  `storage_name` varchar(255) NOT NULL,
  `short_description_of_file` varchar(255),

  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
```
3. To verify if the mySQL backend is correctly set, you might find this link useful https://stackoverflow.com/questions/18644812/how-to-view-table-contents-in-mysql-workbench-gui
4. Enter your database details in `secrets.py`
5. Verify the above steps with the following script `mySQL_test.py`. The script should provide you with the username of user one and two.

## Run the app
to run the app type
`$ python app.py`
Use the following case sensitive credentials to login and test the app
| Username    | password  | Clearance Level    |
| ----------- | --------- | ------------------ |
| keyser      | yolo      | Administrator      |    
| lisa        | yolo      | 2                  |    
| steven      | yolo      | 0                  |    


## Encryption key creation
`$python create_key.py` will create a new symmetric key for file encryption / decryption for you, if you need one. Store the current key prior to using the script elsewhere.



# References
the code is loosely inspired by the following tutorials
- https://medium.com/swlh/building-your-first-flask-app-753638ef9d7
- https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
- https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#a-minimal-application
- https://www.youtube.com/watch?v=aWN1CqMtzIE&t=192s 
- https://flask-login.readthedocs.io/en/latest/
- https://www.thepythoncode.com/article/encrypt-decrypt-files-symmetric-python 
- https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
- https://pythonprogramming.net/flask-send-file-tutorial/
- https://stackoverflow.com/questions/8858008/how-to-move-a-file-in-python
- https://stackoverflow.com/questions/15974730/how-do-i-get-the-different-parts-of-a-flask-requests-url
- https://stackoverflow.com/questions/27158573/how-to-delete-a-record-by-id-in-flask-sqlalchemy
- https://stackoverflow.com/questions/8551952/how-to-get-last-record
- https://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information
- https://techmonger.github.io/4/secure-passwords-werkzeug/
- https://stackoverflow.com/questions/31949733/is-a-sqlalchemy-query-vulnerable-to-injection-attacks
- https://flask.palletsprojects.com/en/2.0.x/security/