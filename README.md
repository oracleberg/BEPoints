# BEPoints created by Andrew Rhoads
This repository holds an example Points API built in Python

Steps to run:
1. Install PyCharm community and Python 3.9, which will be the python interpreter for PyCharm
2. Open PyCharm and install the modules Flask and Connexion from Python Packages (bottom left in PyCharm)
3. Open the terminal in PyCharm and enter: py -m pip install "connexion[swagger-ui]" (this installs an ui that lets us use the API and look at documentation in browser)
4. Open server.py and click the green arrow beside line number 23 (this starts our web server which hosts the API)
5. Navigate to http://localhost:5000/api/ui in your preferred web browser (Chrome) and click on the greyed out "Expand Operations"
6. To test the API we'll use the Post operation to add a transaction, the Put Operation to spend points, and the Get operation to return the points balance
7. Under Post enter: { "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" } in the text box under Value and then click "Try it out!", you should receive a 201 response code
8. Under Put enter: { "points": 5000 } in the text  box under Value and then click "Try it out!", you should see a response object that lists the payer and amount of points spent from them
9. Under Get click "Try it out!", you should see a response object that lists the payer and the points in their account

