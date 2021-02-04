import sys
import csv
import ast
import os
import math

course_slot = {}
exam_table = sys.argv[1]
# regis_student = sys.argv[2]
exam_courses = set()
student_enrolled_courses = set()
course_total_enroll = {}
max_capacity = {
    "01": math.inf,
    "02": math.inf,
    "03": math.inf,
    "04": math.inf,
    "05": math.inf,
    "06": math.inf,
    "07": math.inf,
    "08": math.inf,
    "09": math.inf,
    "10": math.inf,
    "11": math.inf,
    "12": math.inf,
    "13": math.inf,
    "14": math.inf,
    "15": math.inf,
    "16": math.inf,
    "17": math.inf,
    "18": math.inf,
    "19": math.inf,
    "20": math.inf,
    "21": math.inf,
    "RB": math.inf,
    "99": math.inf,
}
course_group = {}

with open(exam_table, "r") as read_exam_slot:
    for i in read_exam_slot:
        course, slot = i.strip().split(" ")
        course_slot[course] = int(slot)
        exam_courses.add(course)

with open("regist-mod.in", "r") as regist:
    STUDENTS = list(csv.reader(regist, delimiter=" "))


with open("data/sched-1-63/courses-mod.in", "r") as courses:
    for row in courses:
        student_enrolled_courses.add(row.split()[0])
        course_total_enroll[row.split()[0]] = int(row.split()[1])

# Read capacity
# for file in os.listdir('data/used-capacity/capa-reg'):
with open("data/capacity/sum-capa-reg.in", "r") as courses:
    for row in courses:
        max_capacity[row.split()[0]] = int(row.split()[1])

for file in os.listdir("data/exam-courses"):
    with open(os.path.join("data/exam-courses", file), "r") as courses:
        for row in courses:
            course_group[row.rstrip("\n").replace("๏ปฟ", "")] = file.replace(".in", "")

to_remove = set()
for c in student_enrolled_courses:
    if c[3]=="7":
        to_remove.add(c)
    elif c[3]=="8":
        to_remove.add(c)
    elif c[3]=="9":
        to_remove.add(c)
student_enrolled_courses = student_enrolled_courses.difference(to_remove)

COURSE_LIST = list(student_enrolled_courses.intersection(exam_courses))
COURSE_LIST.sort()

TOTAL_COURSES = len(COURSE_LIST)


def remove_no_slot(student):
    """
    Input: Individual student regist Ex. [261216,261497]
    Remove course with no exam slot from student
    """
    global COURSE_LIST
    return [slot for slot in student if slot in COURSE_LIST]


def remove_no_exam(students):
    """
    Input: Student regists Ex. [[261216,261497],[],[261498],...]
    Remove student who has no exam -> []
    """
    return [courses for courses in students if courses]


def get_slot(course_list, student):
    """
    Return students who has at least one exam slot
    """
    student_slot = []
    for s in student:  # s = all enroll course Ex. [001101, 001102]
        s_remove_noslot = remove_no_slot(s)
        # Remove student that don't have any exam
        student_slot.append(s_remove_noslot)
    return remove_no_exam(student_slot)


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
    return 1 if abs(s1 // 3 - s2 // 3) > 3 else 0


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
        return 1 if s1 // 3 == s2 // 3 else 0  # Exam 8.00 then 15.30 on the same day
    return 0


def pen_consecutive_d(s1, s2):
    if abs(s1 - s2) == 1:  # Consecutive exam
        return 1 if s1 // 3 != s2 // 3 else 0  # Exam 15.30 then 8.00 on next day
    return 0


def penalty_count(student):
    student.sort()

    pen_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    count = pen_first_slot(student[0])
    pen_count[6] += count

    for i in range(len(student) - 1):
        count = pen_overlap(student[i], student[i + 1])
        pen_count[1] += count
        count = pen_consecutive_a(student[i], student[i + 1])
        pen_count[2] += count
        count = pen_consecutive_b(student[i], student[i + 1])
        pen_count[3] += count
        count = pen_consecutive_c(student[i], student[i + 1])
        pen_count[4] += count
        count = pen_consecutive_d(student[i], student[i + 1])
        pen_count[5] += count
        count = pen_wait3day(student[i], student[i + 1])
        pen_count[6] += count
    return pen_count


def penalty_calc(pen_count):
    pen_value = {1: 10000, 2: 78, 3: 78, 4: 38, 5: 29, 6: 12}
    penalty = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    for i in range(1, 7):
        penalty[i] = pen_value[i] * pen_count[i]
    return penalty


def calc_table(solution):
    table = {}
    for k, v in solution.items():
        if str(v) not in table:
            table[str(v)] = [k]
        else:
            table[str(v)].append(k)
    return table


def linear_pen(x):
    return 10 * x


def expo_pen(x):
    return 1000 + 4 ** (x - 100)


def pen_capacity(solution, max_capacity, course_group, course_total_enroll):
    slot_penalty = {}
    table = calc_table(solution)
    for k, v in table.items():
        curr_capacity = {}
        for c in v:
            group = course_group.get(c, "99")
            if group not in curr_capacity.keys():
                curr_capacity[group] = course_total_enroll[c]
            else:
                curr_capacity[group] += course_total_enroll[c]

        penalty = 0

        # sort by capa -desc
        for group, capa in sorted(curr_capacity.items(), key=lambda item: item[1], reverse=True):
            max_rb_capa = max_capacity['RB']
            rb_capa = 0
            max_capa80 = (max_capacity[group] * 80) // 100
            
            # temporary exclude eng course
            if group == "01" and capa > 5000:
                continue

            # if reach 80% of capacity the rest students will be assign to RB
            if capa > max_capa80:
                split_capa = capa - max_capa80
                # if RB available
                if split_capa <= max_rb_capa - rb_capa:
                    rb_capa += split_capa
                else:
                    capacity_percent = (capa / max_capacity[group]) * 100
                    if capacity_percent > 100:
                        # print("capa%", capacity_percent)
                        # print("capa", capa)
                        # print("max capa", max_capacity[group])
                        # print("faculty", group)
                        # print("------------------------")
                        penalty += expo_pen(capacity_percent)
                    elif capacity_percent >= 80:
                        penalty += linear_pen(capacity_percent)
                
                rb_capacity_percent = (rb_capa / max_rb_capa) * 100

                if rb_capacity_percent > 100:
                    penalty += expo_pen(rb_capacity_percent)
                elif rb_capacity_percent >= 80:
                    penalty += linear_pen(rb_capacity_percent)

        slot_penalty[k] = penalty

    return slot_penalty

def get_reg_exam_solution(course_slot, course_list):
    solution = {}
    for c in course_list:
        solution[c] = course_slot[c]
    return solution

total_penalty = 0
penalties = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
penalties_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

STUDENT_CLEAN = get_slot(COURSE_LIST, STUDENTS)
STUDENT_DUP_COUNT = {str(s): STUDENT_CLEAN.count(s) for s in STUDENT_CLEAN}
# For each student
for s, count in STUDENT_DUP_COUNT.items():
    student_slot = []
    # Convert course-code to exam-slot
    for key in ast.literal_eval(s):
        student_slot.append(course_slot[key])

    pen_count = penalty_count(student_slot)
    # Multiply duplicate student count with pen_count
    pen_count.update((k, v * count) for k, v in pen_count.items())

    pen_calc = penalty_calc(pen_count)

    for i in range(1, 7):
        penalties[i] += pen_calc[i]
        penalties_count[i] += pen_count[i]

reg_exam = get_reg_exam_solution(course_slot,COURSE_LIST)
pencapa = pen_capacity(reg_exam, max_capacity, course_group, course_total_enroll)
exceed_capacity_penalty = sum(pencapa.values())//1

print("Total courses:", TOTAL_COURSES)
print("Total students:", len(STUDENTS))
print("Total students having an exam:", len(STUDENT_CLEAN))
# print("Total students after remove duplicate student:", len(STUDENT_DUP_COUNT))
# print('Each penalty value of solution:\n',penalties)
# print('Each penalty count of solution:\n',penalties_count)
# print("penalties:", penalties)
# print("penalties_count:", penalties_count)
print("Each penalty value of solution:")
for k, v in penalties.items():
    print(str(int(k)-1)+": "+str(v))
print("Each penalty count of solution:")
for k, v in penalties_count.items():
    print(str(int(k)-1)+": "+str(v))
print("Exceed capacity penalty =", exceed_capacity_penalty)
print("Total penalty =", sum(penalties.values()))
print("Total penalty count =", sum(penalties_count.values()))
