#-*- encoding:utf-8 -*-
import json

if __name__ == "__main__":
    with open("setting.json","w") as f:
        event = {}
        
        for i in range(100):
            event[str(i)] = {
                "source" : {
                    "FileName" : "none",
                    "SourceSheetName" : "Sheet1"
                },
                "target" : {
                    "FileName" : f"target{i}.csv",
                    "TargetSheetName" : "Sheet1"
                }
            }
        json.dump(
            event,
            f,
            indent=4
        )