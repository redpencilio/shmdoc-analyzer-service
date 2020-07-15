# A file not connected to Flask, in which you can debug
from analyze.analyzer import analyze_file
from pprint import pprint

# result = analyze_file("../hackathon-xml/emplyees.xml", "xml")

result = analyze_file("../hackathon-xml/das6380.xml", "xml")
pprint(result)