import sys
import csv
import random
import time
import itertools
import ast
import networkx as nx

START_TIME = time.time()

# Valid slot [0-41]
TOTAL_SLOTS = 42
SLOTS = [slot for slot in range(TOTAL_SLOTS)]

# Read all student enroll courses
with open("regist-mod.in", "r") as regist:
    STUDENTS = list(csv.reader(regist, delimiter=" "))

# Read all courses that students enroll
student_enrolled_courses = set()
with open("data/sched-1-63/courses-mod.in", "r") as courses:
    for row in courses:
        student_enrolled_courses.add(row.split()[0])

# Read exam courses from exam table
exam_courses = set()
with open("exams-timetbl.txt", "r") as read_exam_slot:
    for row in read_exam_slot:
        course = row.split()[0]
        exam_courses.add(course)

to_remove = set()
for c in student_enrolled_courses:
    if c[3]=="7":
        to_remove.add(c)
    elif c[3]=="8":
        to_remove.add(c)
    elif c[3]=="9":
        to_remove.add(c)
student_enrolled_courses = student_enrolled_courses.difference(to_remove)

# TODO COURSE_LIST should contain only courses that required to take an exam
COURSE_LIST = list(student_enrolled_courses.intersection(exam_courses))

COURSE_LIST.append("954491-001")
COURSE_LIST.append("954491-002")
COURSE_LIST.append("954491-003")
COURSE_LIST.append("954491-004")

COURSE_LIST.sort()

TOTAL_COURSES = len(COURSE_LIST)

with open("data/sched-1-63/conflicts-mod-sorted.in", "r") as conflicts:
    CONFLICTS = list(csv.reader(conflicts, delimiter=" "))

G = nx.Graph()
G.add_nodes_from(COURSE_LIST)
gNode = list(G.nodes)

for node in CONFLICTS:
    if node[0] in gNode and node[1] in gNode:
        G.add_edge(node[0], node[1])
SG = [G.subgraph(c).copy() for c in sorted(nx.connected_components(G), key=len, reverse=True)]

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


STUDENT_CLEAN = get_slot(COURSE_LIST, STUDENTS)
STUDENT_DUP_COUNT = {str(s): STUDENT_CLEAN.count(s) for s in STUDENT_CLEAN}


print("Total courses:", TOTAL_COURSES)
print("Total students:", len(STUDENTS))
print("Total students having an exam:", len(STUDENT_CLEAN))

print("--- Read data time %s seconds ---" %
        ((time.time() - START_TIME)))

class Schedule(object):
    """
    Class representing Schedule
    """

    def __init__(self, solution):
        self.solution = solution
        self.penalty_value, self.penalty_count = self.calc_penalty()
        self.total_penalty = self.calc_total_penalty(self.penalty_value)

    @classmethod
    def create_schedule(self):
        """
        Find schedule by graph coloring
        """
        global SG, SLOTS, TOTAL_SLOTS
        solution = {}
        for g in SG:
            sorted_degree = sorted(g.degree, key=lambda x: x[1], reverse=True)
            sorted_degree_dict = dict(sorted_degree)
            root = max(g.degree, key=lambda x: x[1])[0]
            edges = nx.bfs_edges(
                g,
                root,
                sort_neighbors=lambda z: sorted(
                    z, key=lambda x: sorted_degree_dict[x], reverse=True
                ),
            )
            nodes = [root] + [v for u, v in edges]
            for n in nodes:
                slots = set([slot for slot in range(TOTAL_SLOTS)])
                color = set([solution[c] for c in set(g.neighbors(n)) if c in solution.keys()])
                slots = slots.difference(color)
                if slots:
                    solution[n] = random.choice(list(slots))
                else:
                    solution[n] = random.choice(SLOTS)

        return solution

    # TODO Add fuction descriptions

    def pen_first_slot(self, first_slot):
        return 1 if first_slot > 9 else 0  # No exam more than 3 days

    def pen_wait3day(self, s1, s2):  # No exam more than 3 days
        return 1 if abs(s1 // 3 - s2 // 3) > 3 else 0

    def pen_overlap(self, s1, s2):  # 2 exams in 1 slot
        return 1 if abs(s1 - s2) == 0 else 0

    def pen_consecutive_a(self, s1, s2):
        if abs(s1 - s2) == 1:  # Consecutive exam
            return 1 if s1 % 3 == 0 else 0  # Exam 8.00 then 12.00 on the same day
        return 0

    def pen_consecutive_b(self, s1, s2):
        if abs(s1 - s2) == 1:  # Consecutive exam
            return 1 if s1 % 3 == 1 else 0  # Exam 12.00 then 15.30 on the same day
        return 0

    def pen_consecutive_c(self, s1, s2):
        if abs(s1 - s2) == 2:  # Consecutive exam
            return (
                1 if s1 // 3 == s2 // 3 else 0
            )  # Exam 8.00 then 15.30 on the same day
        return 0

    def pen_consecutive_d(self, s1, s2):
        if abs(s1 - s2) == 1:  # Consecutive exam
            return 1 if s1 // 3 != s2 // 3 else 0  # Exam 15.30 then 8.00 on next day
        return 0

    def count_penalty(self, student_slot):

        student_slot.sort()

        pen_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

        count = self.pen_first_slot(student_slot[0])
        pen_count[6] += count

        for i in range(len(student_slot) - 1):
            count = self.pen_overlap(student_slot[i], student_slot[i + 1])
            pen_count[1] += count
            count = self.pen_consecutive_a(student_slot[i], student_slot[i + 1])
            pen_count[2] += count
            count = self.pen_consecutive_b(student_slot[i], student_slot[i + 1])
            pen_count[3] += count
            count = self.pen_consecutive_c(student_slot[i], student_slot[i + 1])
            pen_count[4] += count
            count = self.pen_consecutive_d(student_slot[i], student_slot[i + 1])
            pen_count[5] += count
            count = self.pen_wait3day(student_slot[i], student_slot[i + 1])
            pen_count[6] += count
        return pen_count

    def calc_each_penalty(self, pen_count):
        pen_value = {1: 10000, 2: 78, 3: 78, 4: 38, 5: 29, 6: 12}
        penalty = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

        for i in range(1, 7):
            penalty[i] = pen_value[i] * pen_count[i]
        return penalty

    def calc_penalty(self):
        """
        Calculate penalty
        """

        global STUDENT_DUP_COUNT

        penalties = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        penalties_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

        # For each student
        for s, count in STUDENT_DUP_COUNT.items():

            student_slot = []

            # Convert course-code to exam-slot
            for key in ast.literal_eval(s):
                student_slot.append(self.solution[key])

            pen_count = self.count_penalty(student_slot)
            # Multiply duplicate student count with pen_count
            pen_count.update((k, v * count) for k, v in pen_count.items())

            pen_calc = self.calc_each_penalty(pen_count)

            for i in range(1, 7):
                penalties[i] += pen_calc[i]
                penalties_count[i] += pen_count[i]

        return penalties, penalties_count

    def calc_total_penalty(self, pen_calc):
        """
        Calculate fittness score
        """

        total_penalty = sum(pen_calc.values())

        return total_penalty


def main():
    schedule = []
    for _ in range(1000):
        sol = Schedule.create_schedule()
        schedule.append(Schedule(sol))
    # schedule = Schedule(Schedule.create_schedule())
    schedule = sorted(schedule, key=lambda x: x.total_penalty)

    print("Total penalty of solution:", schedule[0].total_penalty)
    print("Each penalty value of solution:")
    for k, v in schedule[0].penalty_value.items():
        print(str(int(k)-1)+": "+str(v))
    print("Each penalty count of solution:")
    for k, v in schedule[0].penalty_count.items():
        print(str(int(k)-1)+": "+str(v))

    with open("graph-coloring-solution.txt", "a") as ch:
        for k in sorted(schedule[0].solution.keys()):
            ch.write(str(k) + " " + str(schedule[0].solution[k]) + "\n")

    print("Solution saved to 'graph-coloring-solution.txt'...")
    print("--- Execution time %s seconds ---" %
          ((time.time() - START_TIME)))

if __name__ == "__main__":
    main()
