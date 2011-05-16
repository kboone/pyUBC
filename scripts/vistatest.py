#!/usr/bin/python
import sys

# cd to right directory
sys.path += [".."]
from ubc import Vista

v = Vista()
v.printCourses()
v.courses[0].printGrades()
