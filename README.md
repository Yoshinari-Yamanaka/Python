# AutoWriting Process with Python

Write something into a Excel, JSON, CSV, ORC or Parquet file with Python

"create_file.py" do that based on "setting.json" made by "create_setting.py" or manually.

### 1. Install Python Libraries

```
~$ pip install pandas openpyxl xlrd xlwt
#If you write or read "ORC" file   ex) *.orc
~$ pip install pyorc
#If you write or read "Parquet" file   ex) *.pq
~$ pip install pyarrow
```

### 2. About setting.json

1. 

Required

```
1. "source"
  1-1. "FileName"  or when you create without a based file, write "none"
       Valid FileExtensions ... .xlsx     .json    .csv   none  .orc  .pq
       Invalid FileExtensions ... .xls (Microsoft Office Excel 1997 ~ 2003), .pdf etc.
  1-2. "SourceSheetName" just only refer to Excel file.
2. "target"
  2-1. "FileName"
       Valid FileExtensions ... .xlsx     .json    .csv   none  .orc  .pq
       Invalid FileExtensions ... .xls (Microsoft Office Excel 1997 ~ 2003), .pdf etc.
  1-2. "TargetSheetName" just only write something into a Excel file
```

Optional
```
. "DirectoryName" "source" and "target"
```

ex)

```json
{
    "1": {
        "source": {
            "DirectoryName" : "source",
            "FileName": "source.xlsx",
            "SourceSheetName": "Sheet1"
        },
        "target": {
            "DirectoryName" : "target",
            "FileName": "target.xlsx",
            "TargetSheetName": "Sheet1"
        }
    }
}
```

### 3. Execute

```
#Just only create setting.json programmably
python create_setting.py

python create_file.py
```

### 4. create_file.py Output

**When you Success All Tasks**

Success


**Invalid File Extensions**

```
Invalid file extension setting key : 2
Actual   source file extension : xls , Actual target file extension : xlsx
Expected source file extension : valid ones are just only "xlsx" , "csv" , "json" , "none"
Expected target file extension : valid ones are just only "xlsx" , "csv" , "json"
```

**When you create Excel File and you forgot define "SheetName", you got folllowing error**

```
TargetSheetName not in setting key : 1
```

**setting.json file not found**

```
There is not 'setting.json' in /Your/file/path/to/. First of all, make sure to create it
```
