#!/usr/bin/python
import sys

# make sure that the right directory is in our path
sys.path += ["."]
sys.path += [".."]
from ubc import Vista

v = Vista()
v.printCourses()
print("Select a course to rip")
courseNum = int(raw_input())
v.courses[courseNum].getBaseFolder().download()
