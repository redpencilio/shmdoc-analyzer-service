# A file not connected to Flask, in which you can debug
from analyze.file_analyzer import analyze_file
from pprint import pprint

# result = analyze_file("../../hackathon-xml/emplyees.xml", "xml")

result = analyze_file('event.csv', "csv")
# result = analyze_file('../tests/data/null_vs_empty.json', 'json')
pprint(result)