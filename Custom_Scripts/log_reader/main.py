from Zeta2 import main as zeta2_main
from zeta3 import main as zeta3_main

zc_version = int(input("Enter the Zeta version you want to run(2/3): "))
url = input("Enter the URL: ")
if zc_version == 2:
    zeta2_main(url)
elif zc_version == 3:
    zeta3_main(url)


