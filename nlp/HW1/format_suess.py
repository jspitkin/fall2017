lines = []
file = open('corpora/suess.txt', 'r')
for line in file:
    line = line.rstrip()
    if len(line) < 1:
        continue
    if line[-1] == '.' or line[-1] == '?' or line[-1] == '!':
        punct = line[-1]
        line = line[:-1] + ' ' +line[-1]
    line = line + '\n'
    lines.append(line)

file = open ('corpora/suess_fixed.txt', 'w')
for line in lines:
    file.write(line)
file.close()