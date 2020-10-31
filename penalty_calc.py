import sys
import csv

course_slot = {}
exam_table = sys.argv[1]
# regis_student = sys.argv[2]

with open(exam_table, 'r') as read_exam_slot:
    for i in read_exam_slot:
        course, slot = i.strip().split(' ')
        course_slot[course] = slot

with open('regist.in', 'r') as regis:
    student = list(csv.reader(regis, delimiter=' '))


def remove_noslot(each_student_slot):
    return [slot for slot in each_student_slot if slot != 99]


def remove_nocourse(student_slot):
    return [slot for slot in student_slot if slot]


def get_slot(course_slot, student):
    student_slot = []
    for s in student:
        each_student_slot = []
        for c in s:
            each_student_slot.append(int(course_slot.get(c, 99)))
        student_slot.append(remove_noslot(each_student_slot))
        # student_slot.append(each_student_slot)
    return(remove_nocourse(student_slot))

# 1 over seat 250
# 2 overlap 200
# 3 consecutive_a 50
# 4 consecutive_b 40
# 5 consecutive_c 30
# 6 consecutive_d 20
# 7 wait3day 10
# 7 first_slot 10


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
        return 1 if s2 % 3 == 1 else 0  # Exam 12.00 then 15.30 on the same day
    return 0


def pen_consecutive_c(s1, s2):
    if abs(s1 - s2) == 2:  # Consecutive exam
        return 1 if s1//3 == s2//3 else 0  # Exam 8.00 then 15.30 on the same day
    return 0


def pen_consecutive_d(s1, s2):
    if abs(s1 - s2) == 1:  # Consecutive exam
        return 1 if s1//3 != s2//3 else 0  # Exam 15.30 then 8.00 on next day
    return 0


def penalty_count(student):

    student.sort()

    pen_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

    count = pen_first_slot(student[0])
    pen_count[7] += count

    for i in range(len(student)-1):
        count = pen_overlap(student[i], student[i+1])
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
    pen_value = {1: 250, 2: 200, 3: 50, 4: 40, 5: 30, 6: 20, 7: 10}
    penalty = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

    for i in range(1, len(pen_value)+1):
        penalty[i] = pen_value[i]*pen_count[i]
    return penalty


total_penalty = 0
penalties = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
penalties_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

student_slot = get_slot(course_slot, student)

for s in student_slot:

    pen_count = penalty_count(s)
    pen_calc = penalty_calc(pen_count)
    for i in range(1, len(pen_calc)+1):
        penalties[i] += pen_calc[i]
        penalties_count[i] += pen_count[i]
print(penalties)
print(penalties_count)
print('Total Penalty = ', sum(penalties.values()))
print('Total Penalty Count = ', sum(penalties_count.values()))
