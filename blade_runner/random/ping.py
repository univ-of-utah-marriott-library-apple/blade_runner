import subprocess

cmd = ["ping", "www.apple.com", "-t", "5"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

while proc.poll() is None:
    print(proc.stdout.readline().strip())