# Universal Robots

This documentation refers to the UR model UR3e, Polyscope v. 5.12
- manual: https://myurhelpresources.blob.core.windows.net/resources/PDF/SW_5_12/e-Series_SW_en_Global.pdf
- help forum: https://forum.universal-robots.com/

## Real Time Data Exchange (RTDE)
### Useful Links
- https://www.universal-robots.com/articles/ur/interface-communication/real-time-data-exchange-rtde-guide/
- link to pdf: https://s3-eu-west-1.amazonaws.com/ur-support-site/22229/Real_Time_Data_Exchange_(RTDE)_Guide.pdf
- video tutorial (series): https://www.youtube.com/playlist?list=PLnJ9fSRnDN3B1wEuxQY4thTWyGoT2N0yd
- Overview of Client Interfaces: https://www.universal-robots.com/articles/ur/interface-communication/overview-of-client-interfaces/
- Remote Control via TCP/IP: https://www.universal-robots.com/articles/ur/interface-communication/remote-control-via-tcpip/

### Client
- Download the client from github: https://github.com/UniversalRobots/RTDE_Python_Client_Library 
- input/output bits: https://s3-eu-west-1.amazonaws.com/ur-support-site/22229/IMMI_Euromap67_input_output_bits.pdf 

### Getting Started (Running the examples)
This explains how to run the examples inside the `RTDE_Python_Client_Library/examples`   

#### Connect robot/controller to external computer
1. Connect the ethernet cable from the robot control box to your computer
2. Get the IP adress from your ethernet connection (i.e. the robot in this case) using the terminal   
`$ ifconfig` (Linux)   
`$ ipconfig` (Win)
3. In the top right corner in PolyScope select `Burger button>Settings>System>Network>select static address`. Set the **IP adress** and **subnet mask** (the rest can be kept at **0.0.0.0**). Check it the green tick turns on to 'Network is connectet'
4. test if you can contact the robot from your computer with:   
`$ ping <ip>`

#### Load Script into PolyScope
If you have a file `.urp` you load it onto a usb stick and load it into PolyScope via `Run>Load Programm`. Press the `Play` button in the right bottom corner to run the program.

#### Python 
ROBOT_HOST = '\<IP number from above\>'   
Port = 30004   
config_filename = '\<config_file\>.xml'

#### Possible bugfixes
- Turn off Wifi and other network connections
- In the PolyScope enable Remote Control, check that
- **[Python] Input parameters already in use**: In PolyScope, go to `Installation>Fieldbus>EtherNet/IP>Disable` 

### Change Output Frequency
In the file `rtde/rtde.py` the function `send_output_setup(frequency=125)` the value can be changed to `frequency=500` to increase the output frequency

### Run example 


