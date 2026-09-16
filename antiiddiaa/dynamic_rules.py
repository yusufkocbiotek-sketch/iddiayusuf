import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Delete get_all_rules again
content = content.split('def get_all_rules():')[0]

dynamic_loader = '''
def get_all_rules():
    import sys
    import inspect
    current_module = sys.modules[__name__]
    
    rules = []
    # Find all classes in this module that inherit from BaseRule (but are not BaseRule itself)
    for name, obj in inspect.getmembers(current_module, inspect.isclass):
        if issubclass(obj, BaseRule) and obj is not BaseRule:
            rules.append(obj)
            
    # Sort them by code or keep as is. In the old logic, they were hardcoded in order.
    # We will sort anomaly rules (digits) descending, and trend rules separately, 
    # to somewhat mimic the old priority order.
    anomaly_rules = []
    trend_rules = []
    
    for r in rules:
        if r.code.isdigit():
            anomaly_rules.append(r)
        else:
            trend_rules.append(r)
            
    # Sort anomaly descending (1556 -> 1460)
    anomaly_rules.sort(key=lambda x: int(x.code), reverse=True)
    # Trend rules sort by code (G1, G11, S1 etc)
    trend_rules.sort(key=lambda x: x.code)
    
    return anomaly_rules + trend_rules
'''

content += dynamic_loader

with open(r'C:\Users\YUSUF\.gemini\antigravity\scratch\rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Implemented dynamic get_all_rules!")
