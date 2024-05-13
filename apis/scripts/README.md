# Automation Script README
This repository contains a Python script for automation. 

Take one user input at a time from an Excel sheet, pass it to the chatbot to get a response, save the response, and then move on to the next input. Finally, store all the chatbot responses in another Excel sheet.


### Add secrets
Run the following command

```bash
cp example.env .env
```

### Navigate to the project directory:
cd scripts/

### Install the required dependencies by running the following command:
```bash
pip install -r requirements.txt
```

### Automation Script - To read user query from excel and ask it to our bot
```bash
python3 automation.py
```



