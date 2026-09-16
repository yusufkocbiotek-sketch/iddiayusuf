import codecs
import re

with codecs.open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\story_analyzer.py', 'r', 'utf-8') as f:
    story = f.read()

# Let's extract the whole if..elif chain
match = re.search(r'(    if any\(r\[\'code\'\] ==.*?)\n    #', story, re.DOTALL)
if match:
    chain = match.group(1)
    print(chain[:1000])
    print("...")
    print(chain[-1000:])
else:
    print("Chain not found.")
