import subprocess

with open("/home/torizon/voyager/verdin/vzc/requirements.txt") as r:
    libs = r.readlines()

freeze = subprocess.run('docker exec -t web bash -c "pip freeze > /var/log/voyager/lib.txt"', shell=True)

with open('/home/torizon/log/lib.txt') as l:
    libs_installed = l.readlines()

for i in libs:
    if i in libs_installed:
        continue
    else:
        print("Library " + i.strip() + " is not installed.")



