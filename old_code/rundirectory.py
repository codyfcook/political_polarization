import subprocess

subprocess.call("python scrape_senate.py", shell=True)
subprocess.call("python scrape_house.py", shell=True)
subprocess.call("python convert_to_csv.py", shell=True)

