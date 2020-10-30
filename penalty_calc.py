import csv
course_slot = {}
with open('exams-timetbl.txt','r') as read_exam_slot:
    # data =list(csv.reader(read_exam_slot, delimiter=' '))
    for i in read_exam_slot:
        course,slot = i.strip().split(' ')
        course_slot[course]=slot
    x=  [key for key,val in course_slot.items() if val=='24'] 
    print(x)
      # mydict.keys()[mydict.values().index(16)]