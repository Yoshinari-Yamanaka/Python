#-*- encoding:utf-8 -*-
import asyncio
import base64
from concurrent.futures import ThreadPoolExecutor,wait,as_completed,ALL_COMPLETED,FIRST_COMPLETED,FIRST_EXCEPTION
from datetime import datetime,timedelta,timezone
from decimal import Decimal
from functools import partial
import glob
import json
from logging import getLogger, StreamHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL
import math
import os
import pathlib
import re
import sys
import threading
#Third party
import numpy as np
import openpyxl
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyorc

#timezone setting
JST = timezone(timedelta(hours=9),"JST")

#logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LogLevel", DEBUG))
logger.addHandler(handler)
logger.propagate = False

class PyColor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RETURN = '\033[07m'
    ACCENT = '\033[01m'
    FLASH = '\033[05m'
    RED_FLASH = '\033[05;41m'
    END = '\033[0m'

class InvalidFileExtensionError(Exception):
    """
    Invalid File Extension
    capital letters or small letters doesn't matter
    valid ones are just only "xlsx" , "csv" , "json" , "orc" , "pq"
    """
    pass

def json_serialization(obj):
    if isinstance(obj,datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S.%f")
    elif isinstance(obj,Decimal):
        return float(obj)
    raise TypeError(f"Invalid object. cannot serialize obj = {obj} , type = {type(obj)}")


class AutoWriting:
    """
    Automatically, "Write something into a file based on a source file or without it." Class
    """
    @property
    def setting_key(self) -> str:
        return self.__setting_key

    @property
    def source_dir(self) -> str:
        return self.__source_dir
    
    @property
    def target_dir(self) -> str:
        return self.__target_dir

    @property
    def source_file(self) -> str:
        return self.__source_file

    @property
    def target_file(self) -> str:
        return self.__target_file
    
    @property    
    def source_sheet(self) -> str:
        return self.__source_sheet
    
    @property
    def target_sheet(self) -> str:
        return self.__target_sheet

    @setting_key.setter
    def setting_key(self,value: str) -> None:
        self.__setting_key = value
    
    @source_dir.setter
    def source_dir(self,value: str) -> None:
        self.__source_dir = value

    @target_dir.setter
    def target_dir(self,value: str) -> None:
        self.__target_dir = value

    @source_file.setter
    def source_file(self,value: str) -> None:
        self.__source_file = value

    @target_file.setter
    def target_file(self,value: str) -> None:
        self.__target_file = value
    
    @source_sheet.setter
    def source_sheet(self,value: str) -> None:
        self.__source_sheet = value

    @target_sheet.setter
    def target_sheet(self,value: str) -> None:
        self.__target_sheet = value
    

    def csv_to_json(self) -> None:
        """write something into a json file based on a csv file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")
        
        os.makedirs(self.__target_dir,exist_ok = True)

        df = pd.read_csv(f"{self.__source_dir}/{self.__source_file}")
        columns = df.columns
        
        data = {}
        for row in df.itertuples(index= False):
            item = {}
            for i,column in enumerate(row):
                item[columns[i]] = column
            

        for column_name,item in df.iteritems():
            pass
        
        df.to_json(f"{self.__target_dir}/{self.__target_file}", force_ascii = False, indent=4)
        # with open(f"{self.__target_dir}/{self.__target_file}","w") as f:
        #     json.dump(data,f,indent=4,ensure_ascii=False)
    
    def csv_to_orc(self) -> None:
        """write something into a orc file based on a csv file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")
        
        os.makedirs(self.__target_dir,exist_ok = True)

        with open(f"{self.__target_dir}/{self.__target_file}", "wb") as data:

            #Read source data. In this case, We'll convert CSV to ORC
            with open(f"{self.__source_dir}/{self.__source_file}","r") as source:
                #Get rid of \n "return code"
                lines = [i.strip() for i in source.readlines()]
                records= []
                header_name = []
                #rows process
                for line in lines:
                    record = []
                    #colums process
                    for column in line.split(","):
                        #Data process
                        if re.match(r'^".*"$',column):
                            record.append(column.strip('"'))
                            #header process
                            if line == lines[0]:
                                header_name.append("string") 
                        elif re.match(r'^\d+\.\d+$',column):
                            record.append(float(column))
                            #header process
                            if line == lines[0]:
                                header_name.append("double")
                        elif re.match(r'^\d+$',column):
                            record.append(int(column))
                            #header process
                            if line == lines[0]:
                                header_name.append("int")

                    #one record datas is packed as a tuple
                    records.append(tuple(record))

                    #If we are at the first record, we'll give the column names to the ORC table
                    if line == lines[0]:
                        for i in range(len(header_name)):
                            header_name[i] = f"col{i}:{header_name[i]}"
                        header_name = f'struct<{",".join(header_name)}>'

                #Get writer Object. give ORC file object at the position of first augument, 
                #column names at the position of second augument  "Writer" method
                with pyorc.Writer(data, header_name) as writer:
                    for record in records:
                        writer.write(record)

    
    def csv_to_parquet(self) -> None:
        """write something into a parquet file based on a csv file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")
        
        os.makedirs(self.__target_dir,exist_ok = True)

        # CSV -> DataFrame
        df = pd.read_csv(f"{self.__source_dir}/{self.__source_file}")

        # DataFrame -> Arrow Table
        table = pa.Table.from_pandas(df)

        # Arrow Table -> Parquet
        pq.write_table(table, f"{self.__target_dir}/{self.__target_file}")
        

    def excel_to_csv(self) -> None:
        """write something into a csv file based on a excel file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")

        os.makedirs(self.__target_dir,exist_ok = True)

        df = pd.read_excel(f"{self.__source_dir}/{self.__source_file}",sheet_name=self.__source_sheet,
            header=None, index_col=None, usecols=None, skiprows=None).iloc[:,:]
        columns = df.columns

        for row in df.itertuples(index= False):
            item = {}
            for i,column in enumerate(row):
                item[columns[i]] = column
            

        for column_name,item in df.iteritems():
            pass
        
        df.to_csv(f"{self.__target_dir}/{self.__target_file}",index = False, header = None)


    def excel_to_excel(self) -> None:
        """write something into a excel file based on another one"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")

        os.makedirs(self.__target_dir,exist_ok = True)

        df = pd.read_excel(f"{self.__source_dir}/{self.__source_file}",sheet_name=self.__source_sheet,
            header=None, index_col=None, usecols=None, skiprows=None).iloc[:,:]
        columns = df.columns

        for row in df.itertuples(index= False):
            item = {}
            for i,column in enumerate(row):
                item[columns[i]] = column
            

        for column_name,item in df.iteritems():
            pass

        df.to_excel(f"{self.__target_dir}/{self.__target_file}",index = False, header = False)


    def excel_to_json(self) -> None:
        """write something into a json file based on a excel file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")

        os.makedirs(self.__target_dir,exist_ok = True)

        df = pd.read_excel(f"{self.__source_dir}/{self.__source_file}",sheet_name=self.__source_sheet,
            header=None, index_col=None, usecols=None, skiprows=None).iloc[:,:]
        columns = df.columns
        
        data = {}
        for row in df.itertuples(index= False):
            item = {}
            for i,column in enumerate(row):
                item[columns[i]] = column
            

        for column_name,item in df.iteritems():
            pass

        df.to_json(f"{self.__target_dir}/{self.__target_file}", force_ascii = False, indent=4)
        # with open(f"{self.__target_dir}/{self.__target_file}","w") as f:
        #     json.dump(data,f,indent=4,ensure_ascii=False)


    def json_to_csv(self) -> None:
        """write something into a csv file based on a json file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")
        
        os.makedirs(self.__target_dir,exist_ok = True)

        df = ""
        with open(f"{self.__source_dir}/{self.__source_file}","r") as f:
            df = pd.DataFrame(json.load(f))
        columns = df.columns

        for row in df.itertuples(index= False):
            item = {}
            for i,column in enumerate(row):
                item[columns[i]] = column
            

        for column_name,item in df.iteritems():
            pass

        df.to_csv(f"{self.__target_dir}/{self.__target_file}",index = False, header = None)


    def json_to_excel(self) -> None:
        """write something into a excel file based on a json file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")

        os.makedirs(self.__target_dir,exist_ok = True)

        df = ""
        with open(f"{self.__source_dir}/{self.__source_file}","r") as f:
            df = pd.DataFrame(json.load(f))
        columns = df.columns

        for row in df.itertuples(index= False):
            item = {}
            for i,column in enumerate(row):
                item[columns[i]] = column
            

        for column_name,item in df.iteritems():
            pass

        df.to_excel(f"{self.__target_dir}/{self.__target_file}",index = False, header = False)


    def none_to_csv(self) -> None:
        """write something into a csv file without source file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")
        
        os.makedirs(self.__target_dir,exist_ok = True)

        with open(f"{self.__target_dir}/{self.__target_file}","w") as f:
            values = []
            for row in range(1,10):
                body = "1,2,3"
                values.append(body)
            f.write("\n".join(values))


    def none_to_excel(self) -> None:
        """write something into a excel file without source file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")

        os.makedirs(self.__target_dir,exist_ok = True)

        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = self.__target_sheet

        for column in ["A","B","C","D"]:
            for row in range(1,11):
                body = f"Test"
                sheet[column + str(row)] = body
        wb.save(f"{self.__target_dir}/{self.__target_file}")


    def parquet_to_csv(self) -> None:
        """write something into a csv file based on parquet file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")

        os.makedirs(self.__target_dir,exist_ok = True)

        # Parquet -> Arrow Table
        table = pq.read_table(f"{self.__source_dir}/{self.__source_file}")

        # Arrow Table -> DataFrame
        df = table.to_pandas()

        #DataFrame -> CSV
        df.to_csv(f"{self.__target_dir}/{self.__target_file}")
    

    def orc_to_csv(self) -> None:
        """write something into a csv file based on parquet file"""
        logger.info(f"setting key : {self.__setting_key}".ljust(20) + f"{sys._getframe().f_code.co_name}".ljust(16) + f"method has been called. line {sys._getframe().f_lineno}")

        os.makedirs(self.__target_dir,exist_ok = True)

        with open(f"{self.__source_dir}/{self.__source_file}", "rb") as data:
            #Get datas from ORC file without column names
            reader = pyorc.Reader(data)
            #Get just only column names from ORC file
            columns = reader.schema.fields

            #Get each column name
            # for column in columns:
            #     logger.debug(column)
            #     logger.debug(columns[column].kind)

            with open(f"{self.__target_dir}/{self.__target_file}","w") as f:
                #loop row datas
                records = []
                for one_record_data in reader:
                    records.append(','.join(map(str, one_record_data)))
                f.write("\n".join(records))

if __name__ == "__main__":
    try:
        SETTING = {}
        with open("setting.json","r") as f:
            SETTING = json.load(f)
    
    except FileNotFoundError:
        logger.critical(f"{PyColor.RED}There is not 'setting.json' in {os.getcwd()}. First of all, make sure to create it{PyColor.END}")
        raise
    
    else:
        worker_numbers = os.cpu_count()
        if len(sys.argv) == 2:
            try:
                worker_numbers = int(sys.argv[1])
            except ValueError:
                pass

        with ThreadPoolExecutor(max_workers = worker_numbers) as executor:
            futures = {}
            failed_sum = 0

            for key,settings in SETTING.items():
                try:
                    auto_writing = AutoWriting()
                    #key
                    auto_writing.setting_key = key

                    #source
                    auto_writing.source_dir = settings["source"].get("DirectoryName","source")
                    auto_writing.source_file = settings["source"]["FileName"]
                    source_file_extension = auto_writing.source_file.split(".")[-1].lower()

                    #target
                    auto_writing.target_dir = settings["target"].get("DirectoryName","target")
                    auto_writing.target_file = settings["target"]["FileName"]                       
                    target_file_extension = auto_writing.target_file.split(".")[-1].lower()

                    #CSV to JSON
                    if source_file_extension == "csv" and target_file_extension == "json":
                        futures[key] = executor.submit(auto_writing.csv_to_json)
                    
                    #CSV to ORC
                    elif source_file_extension == "csv" and target_file_extension == "orc":
                        futures[key] = executor.submit(auto_writing.csv_to_orc)

                    #CSV to Parquet
                    elif source_file_extension == "csv" and target_file_extension == "pq": 
                        futures[key] = executor.submit(auto_writing.csv_to_parquet)

                    #Excel to CSV
                    elif source_file_extension == "xlsx" and target_file_extension == "csv":
                        if "SourceSheetName" not in settings["source"]:
                            raise KeyError(f"SourceSheetName not in setting key : {key}")

                        auto_writing.source_sheet = settings["source"]["SourceSheetName"]
                        futures[key] = executor.submit(auto_writing.excel_to_csv)
                    
                    #Excel to JSON
                    elif source_file_extension == "xlsx" and target_file_extension == "json":
                        if "SourceSheetName" not in settings["source"]:
                            raise KeyError(f"SourceSheetName not in setting key : {key}")

                        auto_writing.source_sheet = settings["source"]["SourceSheetName"]
                        futures[key] = executor.submit(auto_writing.excel_to_json)

                    #Excel to Excel
                    elif source_file_extension == "xlsx" and target_file_extension == "xlsx":
                        if "SourceSheetName" not in settings["source"]:
                            raise KeyError(f"SourceSheetName not in setting key : {key}")
                        if "TargetSheetName" not in settings["target"]:
                            raise KeyError(f"TargetSheetName not in setting key : {key}")
                        
                        auto_writing.source_sheet = settings["source"]["SourceSheetName"]
                        auto_writing.target_sheet = settings["target"]["TargetSheetName"]
                        futures[key] = executor.submit(auto_writing.excel_to_excel)
                    
                    #JSON to CSV
                    elif source_file_extension == "json" and target_file_extension == "csv":
                        futures[key] = executor.submit(auto_writing.json_to_csv)

                    #JSON to Excel
                    elif source_file_extension == "json" and target_file_extension == "xlsx":
                        futures[key] = executor.submit(auto_writing.json_to_excel)
                    
                    #None Source file to CSV
                    elif source_file_extension == "none" and target_file_extension == "csv":                                
                        futures[key] = executor.submit(auto_writing.none_to_csv)
                    
                    #None Source file to Excel
                    elif source_file_extension == "none" and target_file_extension == "xlsx":
                        if "TargetSheetName" not in settings["target"]:
                            raise KeyError(f"TargetSheetName not in setting key : {key}")
                            
                        auto_writing.target_sheet = settings["target"]["TargetSheetName"]
                        futures[key] = executor.submit(auto_writing.none_to_excel)

                    #Parquet to CSV
                    elif source_file_extension == "pq" and target_file_extension == "csv":
                        futures[key] = executor.submit(auto_writing.parquet_to_csv)
                    
                    #ORC to CSV
                    elif source_file_extension == "orc" and target_file_extension == "csv":
                        futures[key] = executor.submit(auto_writing.orc_to_csv)
                    
                    #Invalid
                    else:
                        message = f'Invalid file extension setting key : {key}\n'
                        message += f'Actual   source file extension : {source_file_extension} , Actual target file extension : {target_file_extension}\n'
                        message += f'Expected source file extension : valid ones are just only "xlsx" , "csv" , "json" , "orc" , "pq" , "none"\n'
                        message += f'Expected target file extension : valid ones are just only "xlsx" , "csv" , "json" , "orc" , "pq"'
                        raise InvalidFileExtensionError(message)
                
                except InvalidFileExtensionError as e:
                    failed_sum += 1
                    logger.error(f"{PyColor.YELLOW}{e}{PyColor.END}")
                
                except KeyError as e:
                    failed_sum += 1
                    logger.error(f"{PyColor.YELLOW}{e}{PyColor.END}")

                except Exception as e:
                    failed_sum += 1
                    logger.warning(f"{PyColor.GREEN}type = {type(e)} , key = {e} , message = {e}{PyColor.END}",exc_info=True)

            #If a Future object finished to returns Exception, get the infos
            future_key = ""
            for future in as_completed(list(futures.values())):
                for key,future_value in futures.items():
                    if future_value == future:
                        future_key = key
                        break
                if future.exception():
                    try:
                        future.result()
                    except Exception as e:
                        message = f"{future_key} failed\n"
                        message += f"type = {type(e)} , message = {e}"
                        logger.warning(f"{PyColor.GREEN}{message}{PyColor.END}",exc_info=True)
                    continue
                futures.pop(future_key)
            
            if not futures and failed_sum == 0:
                logger.debug(f"{PyColor.BLUE}Success{PyColor.END}")
