#!/usr/bin/python
import sys

# make sure that the right directory is in our path
sys.path += [".."]
from ubc import Vista

v = Vista()
v.printCourses()
v.courses[0].printGrades()
