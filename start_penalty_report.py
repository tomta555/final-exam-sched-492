import os

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

semester = ["161","261","162","262","163","263"]
file_list = os.listdir("data/sched-exam-old/")
round_count = 0
printProgressBar(0, 24, prefix="Progress:", suffix="Complete", length=50)
for i in range(6):
    for j in range(4):
        file = "py penalty_calc.py "+"./data/sched-exam-old/"+file_list[round_count ]+" "+semester[i]
        os.system(file)
        round_count += 1
        printProgressBar(round_count, 24, prefix="Progress:", suffix="Complete", length=50)