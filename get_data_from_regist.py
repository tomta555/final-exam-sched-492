import csv

with open("regist-mod.in", "r") as regist:
    STUDENTS = list(csv.reader(regist, delimiter=" "))

conflicts = {}
courses = {}
for s in STUDENTS:
    for i in range(len(s)):
        if (s[i]) not in courses.keys():
            courses[s[i]] = 1
        else:
            courses[s[i]] += 1
        for j in range(i+1,len(s)):
            if (s[i]+" "+s[j]) not in conflicts.keys():
                conflicts[s[i]+" "+s[j]] = 1
            else:
                conflicts[s[i]+" "+s[j]] += 1

with open("conflicts-mod-sorted.in", "a") as conf:
    for k, v in sorted(conflicts.items(),key=lambda item: item[1], reverse=True):
        conf.write(k + " " + str(v) + "\n")
        
with open("courses-mod.in", "a") as cour:
    for k, v in sorted(courses.items(),key=lambda item: item[0]):
        cour.write(k + " " + str(v) + "\n")