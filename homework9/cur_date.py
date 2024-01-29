#!/usr/bin/env python3

'''
Wireless Technologies and Security (LTAT.04.009) Lab 9
Get current time
https://www.w3schools.com/python/python_datetime.asp
https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
Execution: python3 cur_date.py
'''

import datetime

x = datetime.datetime.now()

print(f"Current year: {x.year}")
print(f"Current month: {x.month}")
print(f"Current day: {x.day}")

print(f'Year: {x.strftime("%Y")} Month: {x.strftime("%m")} Day: {x.strftime("%d")}')
print(f'{x.strftime("%Y")}-{x.strftime("%b")}-{x.strftime("%d")}')
print(f'{x.strftime("%H")}:{x.strftime("%M")}:{x.strftime("%S")}')

print(f'Date: {x.strftime("%d/%m/%Y")}')
print(f'Time: {x.strftime("%H:%M:%S")}')
