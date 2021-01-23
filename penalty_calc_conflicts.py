import sys
import csv
import ast

course_slot = {}
exam_table = sys.argv[1]
# regis_student = sys.argv[2]
exam_courses = set()
student_enrolled_courses = set()
conflicts = {}

with open(exam_table, 'r') as read_exam_slot:
    for i in read_exam_slot:
        course, slot = i.strip().split(' ')
        course_slot[course] = int(slot)
        exam_courses.add(course)

with open('regist.in', 'r') as regist:
    STUDENTS = list(csv.reader(regist, delimiter=' '))


with open('data/sched-1-63/courses.in', 'r') as courses:
    for row in courses:
        student_enrolled_courses.add(row.split()[0])

COURSE_LIST = list(student_enrolled_courses.intersection(exam_courses))
COURSE_LIST.sort()

TOTAL_COURSES = len(COURSE_LIST)

def remove_no_slot(student):
    ''' 
    Input: Individual student regist Ex. [261216,261497]
    Remove course with no exam slot from student
    '''
    global COURSE_LIST
    return [slot for slot in student if slot in COURSE_LIST]


def remove_no_exam(students):
    ''' 
    Input: Student regists Ex. [[261216,261497],[],[261498],...]
    Remove student who has no exam -> []
    '''
    return [courses for courses in students if courses]


def get_slot(course_list, student):
    ''' 
    Return students who has at least one exam slot
    '''
    student_slot = []
    for s in student:  # s = all enroll course Ex. [001101, 001102]
        s_remove_noslot = remove_no_slot(s)
        # Remove student that don't have any exam
        student_slot.append(s_remove_noslot)
    return (remove_no_exam(student_slot))

# 1 over seat 250
# 2 overlap 10000
# 3 consecutive_a (0800,1200) 78
# 4 consecutive_b (1200,1530) 78
# 5 consecutive_c (0800,1530) 38
# 6 consecutive_d (1530,0800) 29
# 7 wait3day 12
# 7 first_slot 12


def pen_first_slot(first_slot):
    return 1 if first_slot > 9 else 0  # No exam more than 3 days


def pen_wait3day(s1, s2):  # No exam more than 3 days
    return 1 if abs(s1//3 - s2//3) > 3 else 0


def pen_overlap(s1, s2):  # 2 exams in 1 slot
    return 1 if abs(s1 - s2) == 0 else 0


def pen_consecutive_a(s1, s2):
    if abs(s1 - s2) == 1:  # Consecutive exam
        return 1 if s1 % 3 == 0 else 0  # Exam 8.00 then 12.00 on the same day
    return 0


def pen_consecutive_b(s1, s2):
    if abs(s1 - s2) == 1:  # Consecutive exam
        return 1 if s1 % 3 == 1 else 0  # Exam 12.00 then 15.30 on the same day
    return 0


def pen_consecutive_c(s1, s2):
    if abs(s1 - s2) == 2:  # Consecutive exam
        return 1 if s1//3 == s2//3 else 0  # Exam 8.00 then 15.30 on the same day
    return 0


def pen_consecutive_d(s1, s2):
    if abs(s1 - s2) == 1:  # Consecutive exam
        return 1 if s1//3 != s2//3 else 0  # Exam 15.30 then 8.00 on next day
    return 0


def penalty_count(student,student_course):
    sc_sorted_rmdup = {}
    
    global conflicts

    for i in range(len(student_course)):
        sc_sorted_rmdup[student_course[i]] = student[i]
    sc_sorted = sorted(student_course, key=lambda x: sc_sorted_rmdup[x])
    sc_sorted_rmdup = sorted(sc_sorted_rmdup, key=lambda x: sc_sorted_rmdup[x])
    
    student.sort()
    
    pen_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

    count = pen_first_slot(student[0])
    pen_count[7] += count


    for i in range(len(student)-1):
        count = pen_overlap(student[i], student[i+1])
        if count==1:
            if str(sc_sorted[i])+","+str(sc_sorted[i+1]) in conflicts:
                conflicts[str(sc_sorted[i])+","+str(sc_sorted[i+1])] += 1
            else:
                conflicts[str(sc_sorted[i])+","+str(sc_sorted[i+1])] = 1
            
        pen_count[2] += count
        count = pen_consecutive_a(student[i], student[i+1])
        pen_count[3] += count
        count = pen_consecutive_b(student[i], student[i+1])
        pen_count[4] += count
        count = pen_consecutive_c(student[i], student[i+1])
        pen_count[5] += count
        count = pen_consecutive_d(student[i], student[i+1])
        pen_count[6] += count
        count = pen_wait3day(student[i], student[i+1])
        pen_count[7] += count
    return pen_count


def penalty_calc(pen_count):
    pen_value = {1: 250, 2: 10000, 3: 78, 4: 78, 5: 38, 6: 29, 7: 12}
    penalty = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

    for i in range(1, len(pen_value) + 1):
        penalty[i] = pen_value[i] * pen_count[i]
    return penalty


total_penalty = 0
penalties = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
penalties_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

STUDENT_CLEAN = get_slot(COURSE_LIST, STUDENTS)

for s in STUDENT_CLEAN:
    student_slot = []
    # Convert course-code to exam-slot
    for key in s:
        student_slot.append(course_slot[key])

    pen_count = penalty_count(student_slot, s)

    pen_calc = penalty_calc(pen_count)

    for i in range(1, len(pen_calc)+1):
        penalties[i] += pen_calc[i]
        penalties_count[i] += pen_count[i]

print('Total courses:',TOTAL_COURSES)
print("Total students:", len(STUDENTS))
print("Total students cleaned:", len(STUDENT_CLEAN))
print('Penalties:',penalties)
print('Penalties_count:',penalties_count)
print('Total Penalty = ', sum(penalties.values()))
print('Total Penalty Count = ', sum(penalties_count.values()))

with open('conflict-courses.txt', 'a') as cf:
    for k, v in conflicts.items():
        cf.write(str(k)+","+str(v)+"\n")
