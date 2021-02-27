import sys
import csv
import random
import time
import itertools
import ast
import networkx as nx
import stscheduler

START_TIME = time.time()

# Valid slot [0-41]
TOTAL_SLOTS = 42
SLOTS = [slot for slot in range(TOTAL_SLOTS)]

# Read all student enroll courses
with open(stscheduler.regist, "r", encoding="utf-8-sig") as regist:
    STUDENTS = list(csv.reader(regist, delimiter=" "))

# Read all courses that students enroll
std_en_courses_set = set()
STD_ENROLL_COURSES = {}
with open(stscheduler.st_courses, "r", encoding="utf-8-sig") as courses:
    for row in courses:
        std_en_courses_set.add(row.split()[0])
        STD_ENROLL_COURSES[row.split()[0]] = int(row.split()[1])

# Read exam courses from exam table
exam_courses = set()
# with open("exams-timetbl-63-2.txt", "r") as read_exam_slot:
#     for row in read_exam_slot:
#         course = row.split()[0]
#         exam_courses.add(course)

# Read exam courses from file (no-section)
with open(stscheduler.all_courses, "r", encoding="utf-8-sig") as courses:
    for c in courses:
        cs = c.rstrip("\n")
        exam_courses.add(cs)

# to_remove = set()
# for c in std_en_courses_set:
#     if c[3]=="7":
#         to_remove.add(c)
#     elif c[3]=="8":
#         to_remove.add(c)
#     elif c[3]=="9":
#         to_remove.add(c)
# std_en_courses_set = std_en_courses_set.difference(to_remove)

# get intersection of courses from regist and from faculty
all_courses = set()
for c in std_en_courses_set:
    x = c
    if len(c) > 6:
        x = c[:-4]
    if x in exam_courses:
        all_courses.add(c)

# TODO COURSE_LIST should contain only courses that required to take an exam
COURSE_LIST = list(all_courses)
COURSE_LIST.sort()

TOTAL_COURSES = len(COURSE_LIST)

with open(stscheduler.conflicts, "r", encoding="utf-8-sig") as conflicts:
    CONFLICTS = list(csv.reader(conflicts, delimiter=" "))

CONFLICT_DICT = {}
for con in CONFLICTS:
    CONFLICT_DICT[con[0] + "_" + con[1]] = int(con[2])

# print("--- Read data time %s seconds ---" %
#         ((time.time() - START_TIME)))

G = nx.Graph()
G.add_nodes_from(COURSE_LIST)
gNode = list(G.nodes)

NODE_SUM_CONFLICTS = {}

for node in CONFLICTS:
    if node[0] not in NODE_SUM_CONFLICTS.keys():
        NODE_SUM_CONFLICTS[node[0]] = int(node[2])
    else:
        NODE_SUM_CONFLICTS[node[0]] += int(node[2])

    if node[1] not in NODE_SUM_CONFLICTS.keys():
        NODE_SUM_CONFLICTS[node[1]] = int(node[2])
    else:
        NODE_SUM_CONFLICTS[node[1]] += int(node[2])

    if node[0] in gNode and node[1] in gNode:
        G.add_edge(node[0], node[1])

SG = [
    G.subgraph(c).copy()
    for c in sorted(nx.connected_components(G), key=len, reverse=True)
]

print("--- Create graph time %s seconds ---" % ((time.time() - START_TIME)))
# print([len(c) for c in SG])
# for s in SG:
#     if len(s) < 5:
#         print(list(s.nodes))
def printProgressBar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    printEnd="\r",
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


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


def calc_each_penalty(pen_count):
    pen_value = {1: 0, 2: 10000, 3: 78, 4: 78, 5: 38, 6: 29, 7: 12}
    penalty = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

    for i in range(1, 8):
        penalty[i] = pen_value[i] * pen_count[i]
    return penalty


def create_table(solution):
    table = {}
    for k, v in solution.items():
        if int(v) not in table:
            table[int(v)] = [k]
        else:
            table[int(v)].append(k)
    return table


def count_penalty2(solution, start_slot, end_slot):
    timetable = create_table(solution)
    pen_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    for slot in range(start_slot, end_slot + 1):
        if slot in timetable.keys():
            courses = timetable[slot]
        else:
            continue
        courses_set = set(courses)
        course_to_remove = set()
        for c in courses:
            neighbor_set = set(G.neighbors(c))
            neighbor_in_currslot = neighbor_set.intersection(courses_set)
            neighbor_in_currslot = neighbor_in_currslot.difference(course_to_remove)
            course_to_remove.add(c)
            overlap_count = 0
            for n in neighbor_in_currslot:
                if c + "_" + n != n + "_" + c:
                    overlap_count += CONFLICT_DICT.get(c + "_" + n, 0)
                    overlap_count += CONFLICT_DICT.get(n + "_" + c, 0)
                else:
                    overlap_count += CONFLICT_DICT.get(c + "_" + n, 0)
            pen_count[2] += overlap_count
            if slot % 3 == 0:
                consecutive_a_count = 0
                if slot + 1 in timetable.keys():
                    neighbor_in_nextslot = neighbor_set.intersection(
                        timetable[slot + 1]
                    )
                    for n in neighbor_in_nextslot:
                        consecutive_a_count += CONFLICT_DICT.get(c + "_" + n, 0)
                        consecutive_a_count += CONFLICT_DICT.get(n + "_" + c, 0)
                pen_count[3] += consecutive_a_count

                consecutive_c_count = 0
                if slot + 2 in timetable.keys():
                    neighbor_in_next2slot = neighbor_set.intersection(
                        timetable[slot + 2]
                    )
                    for n in neighbor_in_next2slot:
                        consecutive_c_count += CONFLICT_DICT.get(c + "_" + n, 0)
                        consecutive_c_count += CONFLICT_DICT.get(n + "_" + c, 0)
                pen_count[5] += consecutive_c_count
            elif slot % 3 == 1:
                consecutive_b_count = 0
                if slot + 1 in timetable.keys():
                    neighbor_in_nextslot = neighbor_set.intersection(
                        timetable[slot + 1]
                    )
                    for n in neighbor_in_nextslot:
                        consecutive_b_count += CONFLICT_DICT.get(c + "_" + n, 0)
                        consecutive_b_count += CONFLICT_DICT.get(n + "_" + c, 0)
                pen_count[4] += consecutive_b_count
            elif slot % 3 == 2 and slot != TOTAL_SLOTS - 1:
                consecutive_d_count = 0
                if slot + 1 in timetable.keys():
                    neighbor_in_nextslot = neighbor_set.intersection(
                        timetable[slot + 1]
                    )
                    for n in neighbor_in_nextslot:
                        consecutive_d_count += CONFLICT_DICT.get(c + "_" + n, 0)
                        consecutive_d_count += CONFLICT_DICT.get(n + "_" + c, 0)
                pen_count[6] += consecutive_d_count
    return pen_count


STUDENT_CLEAN = get_slot(COURSE_LIST, STUDENTS)
STUDENT_DUP_COUNT = {str(s): STUDENT_CLEAN.count(s) for s in STUDENT_CLEAN}


print("Total courses:", TOTAL_COURSES)
print("Total students:", len(STUDENTS))
print("Total students having an exam:", len(STUDENT_CLEAN))
print("--- Clean data time %s seconds ---" % ((time.time() - START_TIME)))


class Schedule(object):
    """
    Class representing Schedule
    """

    def __init__(self, solution):
        self.solution = solution
        # self.wait_count = self.count_wait_penalty()
        self.penalty_count = count_penalty2(self.solution, 0, 41)
        self.wait_count = self.count_all_wait_penalty()
        self.penalty_count[7] = self.wait_count
        self.penalty_value = calc_each_penalty(self.penalty_count)
        self.total_penalty = self.calc_total_penalty(self.penalty_value)

    @classmethod
    def create_sorted_node(self, g):
        """
        Return tuple of nodes sort by degree -> number of student enrolled -> number of conflicts
        """
        global STD_ENROLL_COURSES, NODE_SUM_CONFLICTS
        g_tuple = []

        for i in list(g.degree):
            g_tuple.append(
                (i[1], STD_ENROLL_COURSES[i[0]], NODE_SUM_CONFLICTS.get(i[0], 0), i[0])
            )

        return sorted(g_tuple, reverse=True)

    @classmethod
    def create_schedule(self):
        """
        Find schedule by graph coloring
        """
        global SG, SLOTS, TOTAL_SLOTS
        solution = {}

        for g in SG:
            # tuple (degree, enrolled_amount, sum_conflict)
            sorted_nodes = self.create_sorted_node(g)
            degree_dict = dict(g.degree)
            root = sorted_nodes[0][3]
            edges = nx.bfs_edges(
                g,
                root,
                sort_neighbors=lambda nodes: sorted(
                    nodes, key=lambda x: degree_dict[x], reverse=True
                ),
            )
            nodes_seq = [root] + [v for u, v in edges]
            for n in nodes_seq:
                slots = set([slot for slot in range(TOTAL_SLOTS)])
                color = set(
                    [solution[c] for c in set(g.neighbors(n)) if c in solution.keys()]
                )
                slots = slots.difference(color)

                slot_penalty = {}
                for s in SLOTS:
                    solution[n] = s
                    if s % 3 == 0 and s != 0:
                        penalty_count = count_penalty2(solution, s - 1, s + 2)
                    elif s % 3 == 1:
                        penalty_count = count_penalty2(solution, s - 1, s + 1)
                    elif s % 3 == 2 and s != 41:
                        penalty_count = count_penalty2(solution, s - 2, s + 1)
                    elif s == 0:
                        penalty_count = count_penalty2(solution, s, s + 2)
                    elif s == 41:
                        penalty_count = count_penalty2(solution, s - 2, s)
                    penalty_value = sum(calc_each_penalty(penalty_count).values())
                    slot_penalty[s] = penalty_value

                # calc penalty then random with weight
                if slots:

                    # select slot
                    # find list of all slot that this new slot associated with
                    # calculate penalty from all slot in above list
                    # if slot % 3 == 0:
                    #   -1 0 +1 +2
                    # elif slot % 3 == 1:
                    #   -1 0 +1
                    # elif slot % 3 == 2:
                    #   -2 -1 0 +1
                    to_remove_slot = set(SLOTS).difference(slots)
                    for k in to_remove_slot:
                        slot_penalty.pop(k, None)

                lowest_pen_tuple = min(slot_penalty.items(), key=lambda x: x[1])
                lowest_pen = lowest_pen_tuple[1]
                lowest_pen_slot = [
                    k for k, v in slot_penalty.items() if v == lowest_pen
                ]

                solution[n] = random.choice(lowest_pen_slot)

                # solution[n] = lowest_pen_tuple[0]

                # if all(pen == 0 for pen in slot_penalty.values()):
                #     solution[n] = random.choice(list(slots))
                # else:
                #     sum_penalty = sum(slot_penalty.values())
                #     slot_list = []
                #     prob_list = []
                #     for k, v in slot_penalty.items():
                #         slot_list.append(k)
                #         prob_list.append(sum_penalty-v)
                #     solution[n] = random.choices(slot_list, weights=prob_list, k=1)[0]

                # solution[n] = random.choice(list(slots))

        return solution

    # TODO Add fuction descriptions

    def pen_first_slot(self, first_slot):
        return 1 if first_slot > 9 else 0  # No exam more than 3 days

    def pen_wait3day(self, s1, s2):  # No exam more than 3 days
        return 1 if abs(s1 // 3 - s2 // 3) > 3 else 0

    def count_wait_penalty(self, student_slot):

        student_slot.sort()
        wait_count = 0

        count = self.pen_first_slot(student_slot[0])
        wait_count += count

        for i in range(len(student_slot) - 1):
            count = self.pen_wait3day(student_slot[i], student_slot[i + 1])
            wait_count += count

        return wait_count

    def count_all_wait_penalty(self):

        global STUDENT_DUP_COUNT

        # penalties = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        total_wait_count = 0

        # For each student
        for s, st_count in STUDENT_DUP_COUNT.items():

            student_slot = []

            # Convert course-code to exam-slot
            for key in ast.literal_eval(s):
                student_slot.append(self.solution[key])

            wait_count = self.count_wait_penalty(student_slot)
            # Multiply duplicate student count with pen_count
            wait_count *= st_count
            total_wait_count += wait_count
        return total_wait_count

    def calc_total_penalty(self, pen_calc):
        """
        Calculate fittness score
        """

        total_penalty = sum(pen_calc.values())

        return total_penalty


def main():
    total_sol = 10
    schedule = []
    printProgressBar(0, total_sol, prefix="Progress:", suffix="Complete", length=50)
    for i in range(total_sol):
        sol = Schedule.create_schedule()
        schedule.append(Schedule(sol))
        printProgressBar(i + 1, total_sol, prefix="Progress:", suffix="Complete", length=50)
    schedule = sorted(schedule, key=lambda x: x.penalty_count[3])
    # schedule = sorted(schedule, key=lambda x: x.total_penalty)

    print("Total penalty of solution:", schedule[0].total_penalty)
    print("Each penalty value of solution:")
    for k, v in schedule[0].penalty_value.items():
        print(str(int(k)) + ": " + str(v))
    print("Each penalty count of solution:")
    for k, v in schedule[0].penalty_count.items():
        print(str(int(k)) + ": " + str(v))
    print(schedule[0].penalty_count)

    with open(stscheduler.out_folder+"graph-coloring-solution-63-2.txt",
        "a",
        encoding="utf-8-sig",
    ) as ch:
        for k in sorted(schedule[0].solution.keys()):
            ch.write(str(k) + " " + str(schedule[0].solution[k]) + "\n")

    # print("Solution saved to 'graph-coloring-solution.txt'...")
    print("--- Execution time %s seconds ---" % ((time.time() - START_TIME)))


if __name__ == "__main__":
    main()
