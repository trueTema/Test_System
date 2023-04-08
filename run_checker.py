import subprocess

cmd = ["python3", "check.py"]
process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

with open('1.txt', 'r') as f:
    line = f.readline()
    while line != '':
        process.stdin.write(line.encode())
        line = f.readline()

output, error = process.communicate()
print('checker returned:', int(output.decode()), 'points')
process.stdin.close()
process.stdout.close()