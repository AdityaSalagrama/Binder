# Binder
Create Payload msfvenom -p windows/x64/messagebox TEXT="Loader Test" TITLE="Success" -f exe -o payload.exe 2>/dev/null 
Download image (eg: innocent.jpeg) Run python3 binder.py bind innocent.jpeg payload.exe malicious.jpg
