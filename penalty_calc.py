import csv
course_slot = {}
with open('exams-timetbl.txt','r') as read_exam_slot:
    # data =list(csv.reader(read_exam_slot, delimiter=' '))
    for i in read_exam_slot:
        course,slot = i.strip().split(' ')
        course_slot[course]=slot
    # x=  [key for key,val in course_slot.items() if val=='24'] 
    # print(x)
with open('regist.in','r') as regis:
    student = list(csv.reader(regis, delimiter=' '))
# get_slot(course_slot,student)

def get_slot(course_slot,student):
    student_slot = []
    for s in student:
        each_student_slot = []
        for c in s:
            each_student_slot.append(int(course_slot.get(c,99)))
        student_slot.append(each_student_slot)
    return(student_slot)
# print(get_slot(course_slot,student))
