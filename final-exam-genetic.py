import sys
import csv
import random
import time
import itertools
import ast

START_TIME = time.time()

# Number of individuals in each generation
# TODO Adjust population size
POPULATION_SIZE = 100

# Valid genes [0-41]
GENES = [slot for slot in range(42)]

# Read all student enroll courses
with open('regist.in', 'r') as regist:
    STUDENTS = list(csv.reader(regist, delimiter=' '))

# Get all courses that students enroll
student_enrolled_courses = set()
with open('data/sched-1-63/courses.in', 'r') as courses:
    for row in courses:
        student_enrolled_courses.add(row.split()[0])

# Read exam courses from exam table
exam_courses = set()
with open('exams-timetbl.txt', 'r') as read_exam_slot:
    for row in read_exam_slot:
        course = row.split()[0]
        exam_courses.add(course)

# Sort course by course-code
# TODO COURSE_LIST should contain only courses that required to take an exam
COURSE_LIST = list(student_enrolled_courses.intersection(exam_courses))
COURSE_LIST.sort()

# Number of courses
TOTAL_COURSES = len(COURSE_LIST)


def remove_no_slot(student):
    ''' 
    Remove course with no exam slot
    '''
    global COURSE_LIST
    return [slot for slot in student if slot in COURSE_LIST]


def remove_no_exam(student):
    ''' 
    Remove student with no exam
    '''
    return [slot for slot in student if slot]


def get_slot(course_list, student):
    ''' 
    Get student with exam slot
    '''
    student_slot = []
    for s in student:  # s = all enroll course Ex. [001101, 001102]
        s_remove_noslot = remove_no_slot(s)
        # Remove student that don't have any exam
        student_slot.append(s_remove_noslot)
    return (remove_no_exam(student_slot))


STUDENT_CLEAN = get_slot(COURSE_LIST, STUDENTS)
STUDENT_DUP_COUNT = {str(s): STUDENT_CLEAN.count(s) for s in STUDENT_CLEAN}


print("Total courses:", TOTAL_COURSES)
print("Total students:", len(STUDENTS))
print("Total students cleaned:", len(STUDENT_CLEAN))
print("Total students remove dupl:", len(STUDENT_DUP_COUNT))
print("Finished cleaned student regist data...")


class Individual(object):
    ''' 
    Class representing individual in population 
    '''

    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.pen_calc, self.pen_count = self.cal_penalty()
        self.fitness = self.cal_fitness(self.pen_calc)

    @classmethod
    def mutated_genes(self):
        ''' 
        Create random genes for mutation 
        '''

        global GENES
        gene = random.choice(GENES)
        return gene

    @classmethod
    def create_genome(self):
        ''' 
        Create random chromosome
        '''

        # TODO Adjust how to initial polulation
        global COURSE_LIST

        genome = {}
        for key in COURSE_LIST:
            genome[key] = self.mutated_genes()
        return genome

    # TODO Add fuction descriptions

    def pen_first_slot(self, first_slot):
        return 1 if first_slot > 9 else 0  # No exam more than 3 days

    def pen_wait3day(self, s1, s2):  # No exam more than 3 days
        return 1 if abs(s1//3 - s2//3) > 3 else 0

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
            return 1 if s1//3 == s2//3 else 0  # Exam 8.00 then 15.30 on the same day
        return 0

    def pen_consecutive_d(self, s1, s2):
        if abs(s1 - s2) == 1:  # Consecutive exam
            return 1 if s1//3 != s2//3 else 0  # Exam 15.30 then 8.00 on next day
        return 0

    def penalty_count(self, student_slot):

        student_slot.sort()

        pen_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

        count = self.pen_first_slot(student_slot[0])
        pen_count[7] += count

        for i in range(len(student_slot)-1):
            count = self.pen_overlap(student_slot[i], student_slot[i+1])
            pen_count[2] += count
            count = self.pen_consecutive_a(student_slot[i], student_slot[i+1])
            pen_count[3] += count
            count = self.pen_consecutive_b(student_slot[i], student_slot[i+1])
            pen_count[4] += count
            count = self.pen_consecutive_c(student_slot[i], student_slot[i+1])
            pen_count[5] += count
            count = self.pen_consecutive_d(student_slot[i], student_slot[i+1])
            pen_count[6] += count
            count = self.pen_wait3day(student_slot[i], student_slot[i+1])
            pen_count[7] += count
        return pen_count

    def penalty_calc(self, pen_count):
        pen_value = {1: 250, 2: 200, 3: 50, 4: 40, 5: 30, 6: 20, 7: 10}
        penalty = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

        for i in range(1, len(pen_value) + 1):
            penalty[i] = pen_value[i] * pen_count[i]
        return penalty

    def mate(self, parent2):
        ''' 
        Perform mating and produce new offspring 
        '''
        
        # TODO Adjust mating algorithm

        global COURSE_LIST

        # chromosome for offspring
        child_chromosome = {}
        for c in COURSE_LIST:

            # random probability
            prob = random.random()

            # if prob is less than 0.45, insert gene
            # from parent 1
            if prob < 0.45:
                child_chromosome[c] = (self.chromosome[c])

            # if prob is between 0.45 and 0.90, insert
            # gene from parent 2
            elif prob < 0.90:
                child_chromosome[c] = (parent2.chromosome[c])

            # otherwise insert random gene(mutate),
            # for maintaining diversity
            else:
                child_chromosome[c] = self.mutated_genes()

        # create new Individual(offspring) using
        # generated chromosome for offspring
        return Individual(child_chromosome)

    def cal_penalty(self):
        ''' 
        Calculate penalty
        '''

        # TODO Calculate penalty for seat exceeding exam capacity

        global STUDENT_DUP_COUNT

        penalties = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        penalties_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

        # For each student
        for s, count in STUDENT_DUP_COUNT.items():

            student_slot = []

            # Convert course-code to exam-slot
            for key in ast.literal_eval(s):
                student_slot.append(self.chromosome[key])

            pen_count = self.penalty_count(student_slot)
            # Multiply duplicate student count with pen_count
            pen_count.update((k, v*count) for k, v in pen_count.items())

            pen_calc = self.penalty_calc(pen_count)

            for i in range(1, len(pen_calc)+1):
                penalties[i] += pen_calc[i]
                penalties_count[i] += pen_count[i]

        return penalties, penalties_count

    def cal_fitness(self, pen_calc):
        ''' 
        Calculate fittness score 
        '''
        
        total_penalty = sum(pen_calc.values())

        return total_penalty


def main():
    global POPULATION_SIZE
    global TOTAL_COURSES

    # current generation
    generation = 1

    finish = False
    population = []

    # create initial population
    for _ in range(POPULATION_SIZE):
        genome = Individual.create_genome()
        population.append(Individual(genome))

    print("Finished initialize the first generation of the population...")

    while not finish:
        population = sorted(population, key=lambda x: x.fitness)

        # TODO Adjust how to terminal process
        if population[0].fitness <= 2000000:
            finish = True
            break

        # Otherwise generate new offsprings for new generation
        new_generation = []

        # Perform Elitism, that mean 10% of fittest population
        # goes to the next generation
        s = int((10*POPULATION_SIZE)/100)
        new_generation.extend(population[:s])

        # From 50% of fittest population, Individuals
        # will mate to produce offspring
        s = int((90*POPULATION_SIZE)/100)
        for _ in range(s):
            parent1 = random.choice(population[:50])
            parent2 = random.choice(population[:50])
            child = parent1.mate(parent2)
            new_generation.append(child)

        population = new_generation

        print("Generation: {}\t Total penalty of fittest: {}".
              format(generation, population[0].fitness))
        print(population[0].pen_calc)
        print(population[0].pen_count)

        generation += 1
        # Write Best
        with open('Best_chromosome.txt', 'w') as ch:
            for k in sorted(population[0].chromosome.keys()):
                ch.write(str(k) + " " +
                         str(population[0].chromosome[k]) + "\n")

    print("Generation: {}\t Total penalty of fittest: {}".
          format(generation, population[0].fitness))
    print(population[0].pen_calc)
    print(population[0].pen_count)

    with open('Best_chromosome.txt', 'a') as ch:
        for k in sorted(population[0].chromosome.keys()):
            ch.write(str(k) + " " + str(population[0].chromosome[k]) + "\n")

    print("Best solution saved to 'Best_chromosome.txt'...")

    print("--- Execution time %s minutes ---" %
          ((time.time() - START_TIME)/60))


if __name__ == '__main__':
    main()
