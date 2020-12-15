import sys
import csv
import random 
import time

START_TIME = time.time()

# Number of individuals in each generation
# TODO Adjust population size
POPULATION_SIZE = 100

# Valid genes [0-41]
GENES = [slot for slot in range(42)]

# Read all course from all student
with open('regist.in', 'r') as regis:
    STUDENTS = list(csv.reader(regis, delimiter=' '))

course_set = set()

# Get all course that student enroll
for s in STUDENTS :
    for c in s:
        course_set.add(c)

# Sort course by course-code
# TODO COURSE_LIST should contain only courses that required to take an exam
COURSE_LIST = list(course_set)
COURSE_LIST.sort()

student_slot = []
for s in STUDENTS :
    each_student_slot = []
    for c in s:
        each_student_slot.append(COURSE_LIST.index(c))
    student_slot.append(each_student_slot)

# Replace each student enrolled course with course-index COURSE_LIST
STUDENT_COURSE_INDEX = student_slot.copy()

# Number of Courses
TOTAL_COURSES = len(COURSE_LIST)

print("Finished convert course-code to course-index for every student...")
# def remove_noslot(each_student_slot):
#     ''' 
#     Remove course with no exam slot
#     '''
#     return [slot for slot in each_student_slot if slot != 99]


# def remove_nocourse(student_slot):
#     ''' 
#     Remove student with no exam
#     '''
#     return [slot for slot in student_slot if slot]


# def get_slot(course_slot, student):
#     ''' 
#     Get student with exam slot
#     '''
#     student_slot = []
#     for s in student: # s = all enroll course Ex. [001101, 001102]
#         each_student_slot = []
#         for c in s:  # c = each course from s Ex. 001101

#             # Convert course-code to exam-slot if not found replace with slot 99
#             each_student_slot.append(int(course_slot.get(c, 99)))

#         # Remove slot 99 from student
#         student_slot.append(remove_noslot(each_student_slot))
#     return(remove_nocourse(student_slot))

class Individual(object): 
    ''' 
    Class representing individual in population 
    '''
    def __init__(self, chromosome): 
        self.chromosome = chromosome  
        self.fitness = self.cal_fitness() 
  
    @classmethod
    def mutated_genes(self): 
        ''' 
        Create random genes for mutation 
        '''
        global GENES 
        gene = random.choice(GENES) 
        return gene 
  
    @classmethod
    def create_gnome(self): 
        ''' 
        Create random chromosome
        '''
        # TODO Adjust how to initial polulation
        global TOTAL_COURSES
        gnome_len = TOTAL_COURSES
        return [self.mutated_genes() for _ in range(gnome_len)] 

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

        for i in range(1, len(pen_value)+1):
            penalty[i] = pen_value[i]*pen_count[i]
        return penalty
    
    def mate(self, parent2): 
        ''' 
        Perform mating and produce new offspring 
        '''
        # TODO Adjust mating algorithm
        # chromosome for offspring 
        child_chromosome = []
        for gp1, gp2 in zip(self.chromosome, parent2.chromosome):     
  
            # random probability   
            prob = random.random() 
  
            # if prob is less than 0.45, insert gene 
            # from parent 1  
            if prob < 0.45: 
                child_chromosome.append(gp1) 
  
            # if prob is between 0.45 and 0.90, insert 
            # gene from parent 2 
            elif prob < 0.90: 
                child_chromosome.append(gp2) 
  
            # otherwise insert random gene(mutate),  
            # for maintaining diversity 
            else: 
                child_chromosome.append(self.mutated_genes()) 
  
        # create new Individual(offspring) using  
        # generated chromosome for offspring 
        return Individual(child_chromosome) 
  
    def cal_fitness(self): 
        ''' 
        Calculate fittness score 
        '''

        # TODO Calculate penalty for seat exceeding exam capacity

        global STUDENT_COURSE_INDEX

        total_penalty = 0
        penalties = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        penalties_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

        # for each student
        for s in STUDENT_COURSE_INDEX:

            student_slot = []

            # convert course-index to exam-slot
            for index in s:
                student_slot.append(self.chromosome[index])

            pen_count = self.penalty_count(student_slot)
            pen_calc = self.penalty_calc(pen_count)
            
            for i in range(1, len(pen_calc)+1):
                penalties[i] += pen_calc[i]
                penalties_count[i] += pen_count[i]
        total_penalty = sum(penalties.values())

        return total_penalty 
    


def main(): 
    global POPULATION_SIZE 

    #current generation 
    generation = 1
  
    finish = False
    population = [] 
  
    # create initial population 
    for _ in range(POPULATION_SIZE): 
        gnome = Individual.create_gnome() 
        population.append(Individual(gnome)) 

    print("Finished initialize the first generation of the population...")
        
    while not finish:
        population = sorted(population, key = lambda x:x.fitness) 

        # TODO Adjust how to terminal process
        if population[0].fitness <= 3000000: 
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

        print("Generation: {}\t Total penalty: {}".\
            format(generation, population[0].fitness)) 
  
        generation += 1
    
    print("Generation: {}\t Total penalty: {}".\
        format(generation, population[0].fitness))

    # Write Best
    global TOTAL_COURSES
    with open('Best_chromosome.txt', 'a') as ch:
        for x in range(TOTAL_COURSES):
            ch.write(str(COURSE_LIST[x]) + " " + str(population[0].chromosome[x]) +"\n")
    
    print("Best solution saved to 'Best_chromosome.txt'...")
    
    print("--- Execution time %s minutes ---" % ((time.time() - START_TIME)/60))

if __name__ == '__main__': 
    main()