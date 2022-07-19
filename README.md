PURPOSE
Scheduled script to monitor an API-capable Node for outages or stalled chain height, sends email alert on error. Initially written for Symbol(XYM) nodes, but refactored for flexibility.

DESCRIPTION
Checks node block height -- if no response from node OR no change in height since last check, send alert.

SETUP
Provide relevant user defined variables in the .env file (examples provided)
Run on a recurring schedule (i.e. every 10 min)

Written for Python v3.9
