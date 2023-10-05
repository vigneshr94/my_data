import requests, paramiko, json, time, re


def get_did(url):
    did = []
    resp = requests.get(f"http://{url}/flask/rover/get")
    for i in json.loads(resp.content)['message']:
        did.append(i['deviceID'])
    return did


def custom_cmd(url, port, host_name, host_password, cmd):
    cmd_to_send = json.loads(cmd)
    data = []
    test_custom_cmd_1(url, cmd)
    time.sleep(5)
    ssh.connect(url, port, host_name, host_password)
    stdin, stdout, stderr = ssh.exec_command("docker exec -t web tail -15 /var/log/voyager/xbee_backend.log")
    time.sleep(20)
    output = stdout.readlines()
    for line in output:
        found1 = re.search("Received:{.+?}", line)
        if found1:
            found2 = re.search("{.+?}", found1.group())
            dic1 = json.loads(found2.group())
            if (dic1['CMD'] == cmd_to_send["CMD"]) and (dic1['DID'] == cmd_to_send["DID"]):
                data.append(dic1)
    return data



def test_custom_cmd_1(url, custom_cmd):
    api_url, data = [f"http://{url}/flask/rover/command", custom_cmd]
    resp = requests.post(api_url, data)
    return resp.status_code, resp.content



url = "192.168.95.7"
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
did = get_did("192.168.95.7")
cmds = ["QSPA", "QSTO", "QBST", "QZBC", 'QHBT', "QANR"]


for i in cmds:
    for k in did:
        print(f"Running {i} on {k}")
        response = custom_cmd(url, 22, "torizon", "sunshine", '{"source":"python_script","CMD":"'+i+'","DID":"'+ k + '"}')
        with open('response.txt', "a") as file:
            file.write(f"\n\ncommand: {i}\nResponse: {response[0]}")