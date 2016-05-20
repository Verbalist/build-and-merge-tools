#!/usr/bin/python3
import sys
import os
import subprocess
import colorama
from colorama import Fore, Style
import re

themes = ['goantifraud', 'corporate', 'pakistan', 'solution', 'topex', 'univarse']
BUILD_FILES = ['themes/univarse/css/main-study-center.css', 'themes/univarse/js/main-study-center.js'] + \
              ['themes/%s/js/app.min.js' % theme for theme in themes] + \
              ['themes/%s/css/main.css' % theme for theme in themes]

colorama.init(autoreset=True)
local_dir = os.getcwd()
number = sys.argv[1]
if number == 'build':
    subprocess.call('gulp study', shell=True)
    print('successful rebuild')
    exit()
try:
    command = sys.argv[2]
except Exception:
    command = None

subprocess.call('git fetch', shell=True)
remotes = os.listdir('.git/refs/remotes/origin/')
branch = ''
for name in remotes:
    if name.startswith(number + '-'):
        branch = name
        break
if branch:
    if command == 'push':
        subprocess.call('git add .', shell=True)
        subprocess.call("git commit -m 'Merge branch \'%s\''" % branch, shell=True)
        subprocess.call('git push origin HEAD', shell=True)
        print('successful push')
        exit()
    elif command == 'build':
        subprocess.call('gulp study', shell=True)
        print('successful rebuild')
        exit()

    try:
        output = subprocess.check_output('git merge origin/%s' % branch, shell=True)
        if output.decode()[:-1] == 'Already up-to-date.':
            print(output.decode()[:-1])
        else:
            output = output.decode()[:-1]
            print('successful merge:' + output.replace('+', Fore.GREEN + '+' + Style.RESET_ALL).
                  replace('-', Fore.RED + '-' + Style.RESET_ALL))
            is_push = input('PUSH IT?(y/n): ')
            if is_push.lower() != 'n':
                subprocess.call('git push origin HEAD', shell=True)
                print('successful push')

    except subprocess.CalledProcessError as e:
        output = e.output.decode()
        print(output)

        conflicts = [x for x in output.split('\n') if x.startswith('CONFLICT')]
        build_conflict = [x for x in conflicts if re.fullmatch('.*(%s)$' % '|'.join(BUILD_FILES), x) is not None]
        if conflicts == build_conflict:
            subprocess.call('gulp study', shell=True)
            print('successful rebuild')
            subprocess.call('git add .', shell=True)
            subprocess.call("git commit -m 'Merge branch \'%s\''" % branch, shell=True)
            is_push = input('PUSH IT?(y/n): ')
            if is_push.lower() != 'n':
                subprocess.call('git push origin HEAD', shell=True)
                print('successful push')
        else:
            scss = [x for x in conflicts if x.endswith('.scss')]
            if build_conflict and not scss:
                subprocess.call('gulp study', shell=True)
                print('successful rebuild')

            print(Fore.RED + 'FAIL MERGE:' + Style.RESET_ALL)
            for x in conflicts:
                if x not in build_conflict:
                    print(x)
            if scss:
                print(Fore.RED + 'FAIL MERGE BUILD:' + Style.RESET_ALL)
                for x in build_conflict:
                    print(x)

else:
    print('not found branch')
