import sys
import csv

course_slot = {}
exam_table = sys.argv[1]
# regis_student = sys.argv[2]
exam_courses = set()
student_enrolled_courses = set()
conflicts = {}

with open(exam_table, "r") as read_exam_slot:
    for i in read_exam_slot:
        course, slot = i.strip().split(" ")
        course_slot[course] = int(slot)
        exam_courses.add(course)

with open("regist.in", "r") as regist:
    STUDENTS = list(csv.reader(regist, delimiter=" "))


with open("data/sched-1-63/courses.in", "r") as courses:
    for row in courses:
        student_enrolled_courses.add(row.split()[0])

COURSE_LIST = list(student_enrolled_courses.intersection(exam_courses))
COURSE_LIST.sort()

TOTAL_COURSES = len(COURSE_LIST)


def remove_no_slot(student):
    global COURSE_LIST
    return [slot for slot in student if slot in COURSE_LIST]


def get_slot(course_list, student):
    student_slot = []
    for s in student:  # s = all enroll course Ex. [001101, 001102]
        s_remove_noslot = remove_no_slot(s)
        # Remove student that don't have any exam
        student_slot.append(s_remove_noslot)
    return student_slot


def pen_overlap(s1, s2):  # 2 exams in 1 slot
    return 1 if abs(s1 - s2) == 0 else 0


def same_code_conflict(student, student_course):
    sc_sorted_rmdup = {}

    for i in range(len(student_course)):
        sc_sorted_rmdup[student_course[i]] = student[i]
    sc_sorted = sorted(student_course, key=lambda x: sc_sorted_rmdup[x])

    student.sort()

    mark = 0

    for i in range(len(student) - 1):
        count = pen_overlap(student[i], student[i + 1])
        if count == 1:
            if str(sc_sorted[i]) == str(sc_sorted[i + 1]):
                mark = 1
                with open("same-code-conflict.txt", "a") as ch:
                    ch.write(str(sc_sorted[i]) + "," + str(sc_sorted[i + 1]) + ",")
    return mark


STUDENT_CLEAN = get_slot(COURSE_LIST, STUDENTS)

for j in range(len(STUDENT_CLEAN)):
    student_slot = []
    # Convert course-code to exam-slot
    for key in STUDENT_CLEAN[j]:
        student_slot.append(course_slot[key])
    mark = same_code_conflict(student_slot, STUDENT_CLEAN[j])
    if mark == 1:
        with open("same-code-conflict.txt", "a") as ch:
            ch.write(str(j + 1) + "\n")
