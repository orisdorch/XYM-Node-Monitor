PURPOSE
Scheduled script to monitor a Symbol(XYM) Node for outages or stalled height, send email alert on error.

DESCRIPTION
Checks node block height -- if no response from node OR no change in height since last check, send alert.

SETUP
Provide relevant variables in the User Defined Variables section
Run on a recurring schedule (i.e. every 10 min)

Coded with Python v3.9