import sys
import csv

course_slot = {}
exam_table = sys.argv[1]

with open(exam_table, 'r') as read_exam_slot:
    for i in read_exam_slot:
        course, slot = i.strip().split(' ')
        course_slot[course] = slot

output_name = 'exams-timetbl-opt-swap-0800-1530.txt'

# swap 0800 and 1530
file = open(output_name,'a')
for key, val in course_slot.items():
    if int(val) % 3 == 0:
        file.write(key+' '+str(int(val)+2)+'\n')
    elif int(val) % 3 == 2:
        file.write(key+' '+str(int(val)-2)+'\n')
    else:
        file.write(key+' '+val+'\n')
file.close()