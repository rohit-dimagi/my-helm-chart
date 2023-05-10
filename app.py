import sys
import yaml
import os
import json
charts = []
chart_details = {}
for arg in sys.argv[1:]:
    folder = arg.split('/')[1]
    charts.append(folder)

charts=(list(set(charts)))

for chart in charts:
    file=os.path.join("charts/", chart, "Chart.yaml")
    with open(file, 'r') as yaml_files:
        data = yaml.safe_load(yaml_files)
        version = data["version"]
        chart_details[chart]= version

output= {"directories": charts, "versions": chart_details}

print(f"charts={json.dumps(output)}")