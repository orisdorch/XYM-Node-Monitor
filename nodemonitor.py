# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 22:00:46 2021 using python v3.9
@author: orisdorch
PURPOSE
Scheduled script to monitor a blockchain node for outages or stalled height, send email alert on error.

DESCRIPTION
Checks node block height -- if no response from node OR no change in height since last check, send alert.

SETUP
Provide relevant variables in the User Defined Variables section
Run on a recurring schedule (i.e. every 10 min)

Distributed under  Mozilla Public Licence 2.0
"""
import requests
import smtplib
from email.message import EmailMessage
import os
from dotenv import dotenv_values


### Global/Static Variables - do not edit ###
headers={'content-type':'application/json', 'Accept':'application/json'}  #parameters used in API calls

### API Query Functions ###
# For queries without responses (full contents are returned with a single query) #
def APICallNotPaged(APINodeURL,endPoint,dataKey):
    requestURL = APINodeURL+endPoint
    print('Collecting data from '+requestURL)
    try:   #Attempt the API Call
        r = requests.get(requestURL).json()
        data = r.get(dataKey)
        return data
    except requests.exceptions.RequestException as e:   #Catch any exception returned from the request
        print("###ERROR### Node could not be contacted via API call...")
        errorHandling("Alert: " + nodeChain + " Node Offline"," Node could not be contacted due to error: \n" + nodeAPIURL + "\n" + str(e))
        raise SystemExit(e)   #Exit

### Error Management ### - with error counter and email notifications
def errorHandling(subject,message):   #Takes the email alert contents, checks error count to see if alert should be supressed, sends alert if warranted.
    newErrorCount = str(int(errorCount) + 1)
    if newErrorCount == "1" or (int(newErrorCount)/int(realertEvery)).is_integer():  #For notifications -- check if lase run was successful, if no: check if due for a re-alert
        print ("Sending alert - error number " + newErrorCount)
        sendEmailAlert(subject,message)
    else: 
        print ("No Alert - error number " + newErrorCount + ", alerts sent every " + str(realertEvery))
    overwriteFile(errorFilePath,newErrorCount)   #Update the error counter file

### File management processes ### --very basic, for one line files only
def checkFile(path):
    try: # try to open the file at the specified path
        f = open(path, "r")
        content = f.read()
        f.close()
        if content.isdigit():   #Check if file contains  a valid integer
            return content
        else:   #If file contents are not integer, ignore file contents and return 0
            print("Invalid file contents in "+path+" - using 0...")
            return "0"
    except IOError:   #If file cannot be found, create a new empty one and return 0
        print("no previous output file has been found at " + path + ", creating a new file and using 0...")
        f = open(path, "w+")
        f.close()
        return "0"

def overwriteFile(path, data):
    with open(path, 'w') as f:
        f.write(data)
    f.close()


### Node Monitor Processes ###
def lastRunFileCheck():   #Checks for outputs from the last session and updates counters based on these
    global lastBlock
    global errorCount
    print('checking for outputs from last session...')
    lastBlock = checkFile(blockFilePath)
    print("Last known block height is: " + lastBlock)
    errorCount = checkFile(errorFilePath)
    print("Errors since last success: " + errorCount)

def checkNodeStatus(nodeAPIURL,endPoint,dataKey):   # primary function of this script
    height = str(APICallNotPaged(nodeAPIURL,endPoint,dataKey))
    print("Node's current block height is " + height)
    if height <= lastBlock:   #height reduced or unchanged
        print("###ERROR### Height has not increased since last check - sending alert...")
        errorHandling("Alert: " + nodeChain + " Node Stuck","Your node's block height " + height + " has not increased since last check: \n" + nodeAPIURL)
    else:   #Success -- Height increased since last check
        overwriteFile(blockFilePath,height)  #update tracking file with new height
        overwriteFile(errorFilePath,"0")   #set error count to 0


### Messaging Component for email alerts ###
def sendEmailAlert(subject,message): #Plain text messaging only
    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = subject
    msg['From'] = senderPass
    msg['To'] = recipientAddress

    # Send the message via speified SMTP server
    print("Sending |" + subject + "| to " + recipientAddress)
    #Create SMTP session for sending the mail
    session = smtplib.SMTP(smtpServer,smtpPort) #use gmail with port
    session.starttls() #enable security
    session.login(senderAddress, senderPass) #login with mail_id and password
    session.send_message(msg)
    session.quit()
    print("Message sent")

    
### Begin Script Execution ###
# Load .env files and cycle through them
env_dir = os.path.dirname(os.path.realpath(__file__))


# Find all .env files in the directory
env_files = [f for f in os.listdir(env_dir) if f.endswith('.env')]
print("found the following environment files: " + str(env_files))

# Loop through each .env file and feed it to lastRunFileCheck and checkNodeStatus - this isn't a defined function in order to simplify setting global variables.
for env_file in env_files:
    env_path = os.path.join(env_dir, env_file)
    print("Loading environment file " + env_path)
    lastBlock = "0"  # The last BLock Height retrieved from your node -- stored in blockFilePath
    errorCount = "0"  # Counts #  runs with errors since last success -- stored in errorFilePath

    ### Load User Defined Variables from .env file ###
    environment = dotenv_values(env_path)
    nodeAPIURL = environment['nodeAPIURL']
    endPoint = environment['endPoint']
    dataKey = environment['dataKey']
    blockFilePath = environment['blockFilePath']
    errorFilePath = environment['errorFilePath']
    senderAddress = environment['senderAddress']
    senderPass = environment['senderPass']
    smtpServer = environment['smtpServer']
    smtpPort = environment['smtpPort']
    recipientAddress = environment['recipientAddress']
    realertEvery = environment['realertEvery']
    nodeChain = environment['nodeChain']

    ### Check for output files from last run; create them if missing.
    lastRunFileCheck()

    ### Get node block height / notify on error
    checkNodeStatus(nodeAPIURL,endPoint,dataKey)
