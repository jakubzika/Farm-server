#!/usr/bin/env python3.5
import downloadBuild
import os

def main():
    os.system('git pull')
    os.system('python3.5 -m pip install -r requirements.txt')
    os.system('chmod 771 server/main.py')
    downloadBuild.main()

if __name__ == '__main__':
    main()