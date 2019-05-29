import subprocess
import time

proc = subprocess.Popen(['java', '-jar', '.\\minie-0.0.1-SNAPSHOT.jar'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
text =["Mr. Ollivander had come so close that he and Harry were almost nose to nose.",
"\"And that's where...\"",
"Mr. Ollivander touched the lightning scar on Harry's forehead with a long, white finger.",
"said Mr. Ollivander, suddenly stern.",
"said Mr. Ollivander sharply.",
"No two Ollivander wands are the same, just as no two unicorns, dragons, or phoenixes are quite the same.",
"Mr. Ollivander was flitting around the shelves, taking down boxes.",
"Harry took the wand and (feeling foolish) waved it around a bit, but Mr. Ollivander snatched it out of his hand almost at once.",
"Try --\"",
"Harry tried -- but he had hardly raised the wand when it, too, was snatched back by Mr. Ollivander.",
"He had no idea what Mr. Ollivander was waiting for.",
"The pile of tried wands was mounting higher and higher on the spindly chair, but the more wands Mr. Ollivander pulled from the shelves, the happier he seemed to become.",
"Hagrid whooped and clapped and Mr. Ollivander cried, \"Oh, bravo!",
"He paid seven gold Galleons for his wand, and Mr. Ollivander bowed them from his shop."]

relations=[]
for x in text:
    proc.stdin.write((x+'\n').encode())
    proc.stdin.flush()
    line=proc.stdout.readline()
    while not line.decode().startswith('('):
        line=proc.stdout.readline()
        if(line.decode().startswith('No')):
            break
    while line.decode() != '\n':
        if(line.decode().startswith('No')):
            break
        result = line.decode()
        split= result.split(';')
        split[0].replace('(', '')
        if len(split) == 3:
            second_split = split[2].split(')')
            second_split[0].replace(')', '')
            entry = [split[0], split[1], second_split[0]]
        else:
            second_split = split[1].split(')')
            second_split[0].replace(')','')
            entry = [split[0], second_split[0]]
        relations.append(entry)
        line = proc.stdout.readline()

print(relations)
'''
print('writing')
proc.stdin.write(b'Harry is stupid\n')
proc.stdin.flush()
print('waiting')
print(proc.stdout.readline())
print(proc.stdout.readline())
print(proc.stdout.readline())
print(proc.stdout.readline())
print('writing')
proc.stdin.write(b'Harry is stupid\n')
proc.stdin.flush()
print('waiting')
print(proc.stdout.readline())
print(proc.stdout.readline())
print(proc.stdout.readline())
print(proc.stdout.readline())
'''