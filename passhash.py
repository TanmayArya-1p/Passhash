import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sqlite3
import pyperclip
import hashlib
import random
import getpass
import sys
import time
import msvcrt
import pyfiglet
import colorama
from colorama import Fore
from quo import echo


def Generate_PBKDF_Fernet(password:str):
    password = password.encode()
    #salt = os.urandom(16) 
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,iterations=100000,salt=b"")
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return Fernet(key)

class PasswordManager:
    def __init__(self,Fernet:Fernet,db_path:str="pass.db"):
        self.fernet = Fernet
        self.con = sqlite3.connect(db_path)
        self.cursor = self.con.cursor()
        try:
            self.cursor.execute("CREATE TABLE passhash(name text PRIMARY KEY, pass text)")
        except:
            pass
    
    def insert_password(self,name:str,password:str):
        self.cursor.execute(f"INSERT OR IGNORE INTO passhash VALUES('{name}','{self.fernet.encrypt(password.encode()).decode()}')")
        self.con.commit()

    def update_password(self,name:str,new_pass:str):
        self.cursor.execute(f"UPDATE passhash SET pass='{self.fernet.encrypt(new_pass.encode()).decode()}' WHERE name = '{name}'")
        self.con.commit()

    def delete_password(self,name:str):
        self.cursor.execute(f"DELETE FROM passhash WHERE name ='{name}'")
        self.con.commit()
    
    def fetch_password(self,name:str,clipboard=False):
        self.cursor.execute(f"SELECT pass FROM passhash WHERE name ='{name}'")
        otpt = self.fernet.decrypt(self.cursor.fetchone()[0].encode()).decode()
        if(clipboard):
            pyperclip.copy(otpt)
        return otpt

    def fetch_all_passwords(self):
        self.cursor.execute("SELECT * FROM passhash")
        otpt = {}
        for i in self.cursor.fetchall():
            otpt[i[0]] = self.fernet.decrypt(i[1].encode()).decode()
        return otpt


def set_master_pass(password:str):
    with open("pass.env" , "w") as p:
        p.write(str(os.urandom(random.randint(10,50)).hex()) + ":" + str(hashlib.sha256(password.encode()).hexdigest()) + ":" + str(os.urandom(random.randint(10,50)).hex()))

def verify_master_pass(password:str):
    hash = str(hashlib.sha256(password.encode()).hexdigest())
    with open("pass.env" , "r") as p:
        if(p.read().split(":")[1] == hash):
            return True
        else:
            return False

os.system('mode 50,30')
os.system("title Passhash")
print(Fore.GREEN + pyfiglet.figlet_format("Passhash", font = "slant") + "--------------------------------------------------")
while True:
    inp = getpass.getpass("Enter Master Key:\n")
    if(verify_master_pass(inp)):
        m = PasswordManager(Generate_PBKDF_Fernet(inp))
        while True:
            time.sleep(1)
            print("""--------------------------------------------------
Enter Task Mode:
-Fetch Mode(f) - Fetch Passwords
-Set Mode(s) - Set Passwords
-List Passwords(l) - List All Passwords
-Delete Passwords(d)
-Change Masterpass(c)
-Quit(q)
--------------------------------------------------""")
            os.system("echo off")
            while True:
                inp = msvcrt.getch().decode().lower()
                print(inp)
                if(inp in ['s','f','l','d','q','c']):
                    task = inp
                    break
            os.system("echo on")
            if(task == "s"):
                name = input("Enter Password Name:\n").lower()
                password = getpass.getpass(f"Enter Password for '{name}':\n")
                
                if(name in list(m.fetch_all_passwords().keys())):
                    m.update_password(name,password)
                else:
                    m.insert_password(name,password)
            elif(task == "f"):
                name = input("Enter Password Name: ").lower()
                if(name in list(m.fetch_all_passwords().keys())):
                    print(name + " : " + m.fetch_password(name,True))
                    print("Password Copied to Clipboard.")
                else:
                    print(f"{name} is not a valid password.")
            elif(task == "l"):
                fa = m.fetch_all_passwords() 
                for i in fa:
                    print(i + " : " + fa.get(i))
            elif(task == "d"):
                name = input("Enter Password to Delete:\n")
                if(name.lower() in list(m.fetch_all_passwords().keys())):
                    m.delete_password(name.lower())
                else:
                    print(f"{name} is not a valid password.")
            elif(task == "c"):
                if(verify_master_pass(getpass.getpass("Re-verify Old Master Password:\n"))):
                    old_pass = m.fetch_all_passwords()
                    for i in old_pass:
                        m.delete_password(i)
                    inp = getpass.getpass("Enter New Master Pass:")
                    set_master_pass(inp)
                    m = PasswordManager(Generate_PBKDF_Fernet(inp))
                    for i in old_pass:
                        m.insert_password(i,old_pass[i])
                else:
                    print("Invalid password")
            elif(task == "q"):
                sys.exit()

    else:
        print("Incorrect Master Key.")
