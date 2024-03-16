# MirrorMe
Welcome to MirrorMe! MirrorMe is a tool designed to help effectively enhance the virtual learning experience of physical actions. This interactive application allows users to join live sessions under either the role of student or teacher. Teachers are able to track and record specific movements, which they can then send live to multiple students. Students can then learn the movement with personalized, guided feedback in the form of both on-screen tracking and haptic feedback from a device worn on the wrist.  
## User Guide
https://docs.google.com/document/d/19Ljv2DmeATat1j7PWR03KJ3raVAts24WCoCltPWTh4Q/edit?usp=sharing
## Requirements
All required python packages are below in requirements.txt
# Repository organization
```
    .streamlit/ --> Contains the theme for the application.
    archive/ --> Contains no longer required, but relevant files.
    BerryIMU/ --> Contains relevant code for supporting the BerryIMU
    gui/ --> Contains all the pages of the application.
    node_modules/ --> Contains styling for the application.
    pi_files/ --> Contains the libraries and packages that will run on the MirrorModule Rapsberry Pi.
    testing_and_data/ --> Includes the programs for and the data of testing networking latency
    model_utils.py --> Utils file for Stick Pose Estimation ML model.
    movement.py --> Library for storing and displaying movement data
    package-lock.json --> Json file related to styling the application front-end
    package.json --> Json file related to styling the application front-end
    pi.py --> Application that runs on the MirrorModule
    point.py --> Enum file used by the application
    requirements.txt --> List of required python packages.
```
