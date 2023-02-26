from itertools import groupby
import json
from bs4 import BeautifulSoup
import pandas as pd

#open text file in read mode
text_file = open("./log.html",  encoding="utf8")
 
#read whole file to a string
data = text_file.read()

parsed_html = BeautifulSoup(data)
messages = parsed_html.find_all("div", class_="message")
result = []

roll_results = []
damage_results = []
for message in messages:
    contents = message.contents
    
    # name = None
    roll_result = None
    damage_result = None
    
    for content in contents:
        string_content = str(content)
        parsed_content = BeautifulSoup(string_content)
        by = parsed_content.find_all("span", class_="by")
        inlinerollresult = parsed_content.find_all("span", class_="inlinerollresult") 
        formula_dice = parsed_content.find_all("div", class_="diceroll d20") 
        sheet_damage = parsed_content.find_all("span", class_="sheet-damage") 
        
        if (by):
            name = str(content.contents[0])
            
        if (formula_dice):
            formula_dice_content = formula_dice[0]
            roll_result = BeautifulSoup(str(formula_dice_content.next())).find_all("div", class_="didroll")[0].contents[0]
            
        if (sheet_damage):
            damage_result = 0
            for damage in sheet_damage: 
                damage_contents = damage.contents
                for damage_content in damage_contents:
                    try:
                        damage_result += int(damage_content.text)
                    except:
                        print(f"Error: Damage is not an int: {damage_content.text}")
            
        if (inlinerollresult):
            
            if ("title" in inlinerollresult[0].attrs):
                title = inlinerollresult[0].attrs["title"]
            
            if ("original-title" in inlinerollresult[0].attrs):
                title = inlinerollresult[0].attrs["original-title"]
            
            if (title):
                if ("Rolling 1d20".lower() in str(title).lower()):
                    start = '">'
                    end = "<"
                    roll_result = title[title.find(start)+len(start):title.rfind(end)]
    
    if (name):
        name = name.translate({ord(i):None for i in '()!:{}'})
        name_clean = name.replace("From", "").replace("To", "")
        strip_name = name_clean.strip()
        if(roll_result):
            roll_results.append({
                "name": strip_name,
                "roll_result": roll_result
            })
        
        if (damage_result):
            damage_results.append({
                "name": strip_name,
                "damage_result": damage_result
            })
    
sorted_roll_results = sorted(roll_results, key=lambda roll_result: roll_result["name"])
grouped_roll_results = [list(result) for key, result in groupby(
    sorted_roll_results, key=lambda roll_result: roll_result["name"])]

roll_totals = []
for grouped_roll_result in grouped_roll_results:
    name = grouped_roll_result[0]["name"]
    sum = 0
    total_crit = 0
    total_crit_fails = 0
    for roll_result in grouped_roll_result:
        value = roll_result["roll_result"]
        
        if (value.isdigit()):
            roll_result_int = int(roll_result["roll_result"])
            sum += int(roll_result_int)
            if (roll_result_int is 20):
                total_crit += 1
            elif (roll_result_int is 1):
                total_crit_fails += 1
        else:
            print(f"Not a digit: {value}")
            grouped_roll_result.remove(roll_result)
    average = sum / len(grouped_roll_result)
    roll_totals.append({
        "name": name,
        "totalRolls": len(grouped_roll_result),
        "average": average,
        "total_crit": total_crit,
        "total_crit_fails": total_crit_fails
    })
    
json_object = json.loads(json.dumps(roll_totals))
json_formatted_str = json.dumps(json_object, indent=2)

f = open("results_rolls.json", "w")
f.write(json_formatted_str)
f.close()

with open('results_rolls.json', encoding='utf-8') as inputfile:
    df = pd.read_json(inputfile)

df.to_csv('rolls_csvfile.csv', encoding='utf-8', index=False)

sorted_damage_results = sorted(damage_results, key=lambda damage_result: damage_result["name"])
grouped_damage_results = [list(result) for key, result in groupby(
    sorted_damage_results, key=lambda damage_result: damage_result["name"])]

damage_totals = []
for grouped_damage_result in grouped_damage_results:
    name = grouped_damage_result[0]["name"]
    sum = 0
    for damage_result in grouped_damage_result:
        value = damage_result["damage_result"]
        
        damage_result = int(damage_result["damage_result"])
        sum += int(damage_result)
    damage_totals.append({
        "name": name,
        "sum": sum
    })
    
json_object = json.loads(json.dumps(damage_totals))
json_formatted_str = json.dumps(json_object, indent=2)

f = open("damage_results.json", "w")
f.write(json_formatted_str)
f.close()

with open('damage_results.json', encoding='utf-8') as inputfile:
    df = pd.read_json(inputfile)

df.to_csv('damage_csvfile.csv', encoding='utf-8', index=False)