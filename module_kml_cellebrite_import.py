# THIS SCRIPT WILL EXECUTE THE QUEIRIES BELOW TO PARSE OUT DATA FOR THE SELECTED APPLICATION.
# APPLICATION: iOS device locations as of 2023-03-23
# DATABASES REQUIRED: Expored locations from Cellebrite PA saved as a CSV
#
#       \private\var\mobile\Library\Caches\com.apple.routined\
#           Cache.sqlite
#
# Version 1.0
# Date  2023-03-23
# Copyright (C) 2023 - Aaron Dee Roberts
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You can view the GNU General Public License at <http://www.gnu.org/licenses/>

import os
import sys
import sqlite3
from sqlite3 import OperationalError
import module_biome_functions
import module_general_functions
import module_sqlite_table_functions

def import_csv_locations_instructions():
	
	print('================================= INSTRUCTIONS =========================================')
	print('This will import a CSV file exported using Cellebrite\s Physical Analyzer generate KML locations')
	print('which contain the horizontal accuracy and notations indicating if they have been deleted')
	print()
	print('Suggested use is to use PA to export only the DELETED records and add them to the KML file')
	print('generated from the active records in the Cache.sqlite file')
	print()
	print('Times MUST use 4 digit year and SECONDS.  PA takes these from your system settings')
	print('If your display is only minutes and 2 digit year, you can fix this by changing the display')
	print('in your windows settings for the date and time display.')
	print()
	print('The program will see if the time is 24 hour or 12 hour time based on the AM/PM being present')
	print('It will also account for time offsets based on the (UTC) and what comes after.  EX: (UTC-5)')
	print()
	print('First, make sure you\'ve exported the EXCEL file, then opened it and saved it as a CSV')
	print('The CSV file should use commas to separate and be UTF-8 or UTF-16 encoded with are standard')
	print('Next, place the saved file in the "data_to_parse" subfolder or save it to the subfolder.')
	print()
	print('Required fields: TIME, LONGITUDE, LATITUDE. \nOptional fields: PRECISION, END TIME, AGGREGATED LOCATIONS, DELETED')
	print('To avoid errors with some CSV formats, make sure an unused column ')
	print('with a names header such as "UNUSED" is first (all the way LEFT)')
	print()
	input('Press ENTER')
	print()


def is_utf16(ls_filename):
    with open(ls_filename, 'rb') as lf_file:
		# Read the first 2 bytes 
        lrb_start = lf_file.read(2)
        
        # Returns True if first 2 bytes in either of the byte arrays
        # LE or BE depending on system.
        return lrb_start in [b'\xff\xfe', b'\xfe\xff']
        

def import_locations_csv (of_db, of_log, of_folder = './data_output/', if_folder = './data_to_parse/'):

	# DISPLAY THE INSTRUCTIONS
	import_csv_locations_instructions()
	
	#CREATE THE SQLITE TABLE TO HOUSE THE DATA
	module_sqlite_table_functions.create_device_locations_table(of_db, of_log)
	
	err_lock = 1 # STAY IN THE LOOP UNTIL A VALID FILE NAME OR N ENTERED
	
	# ASSIGNES THE FILE TO BE PARSED AS in_file
	while err_lock == 1:
		print('Provide the name of the input CSV file or "N" to exit')
		print()
		in_file = input('INPUT:   ')
		
		if in_file == '' or in_file == None:
			print('Please enter a valid file name')
			print()
			
		elif in_file == 'N' or in_file == 'n':
			err_lock = 0
			return
			
		else:
			# CHECK TO SEE IF THE FILE EXISTS AND ADDING FOLDER NAME TO IT.
			in_file = if_folder + in_file
			print(f'Checking to see if {in_file} exists.')
			if os.path.isfile(in_file) is True:
				print(f'{in_file} does exist so we are proceeding.')
				err_lock = 0
			else:
				print(f'{in_file} does not appear to exist..')
				print('Please provide a file name that exists')
				print()

	# OPEN INFILE AND PARSE EACH LINE
	# Check if file is UTF-16 or not (makes a difference)
	lb_utf16 = is_utf16(in_file)
	
	# Open the file according to encoding
	if lb_utf16 == False: in_file_o = open(in_file,'r')
	if lb_utf16 == True: in_file_o = open(in_file,'r', encoding='utf-16')
	log_file = open(of_log,'a')
	
	
	# SET UP THE SQLITE DATABASE CONNECTION AND CURSOR
	sql_con = sqlite3.connect(of_db)
	sql_con.row_factory = sqlite3.Row
	sql_cur = sql_con.cursor()
	
	# PRE ASSIGN VARIABLES TO AVOID AN ERROR IF THEY ARE NOT THE FIRST LINE.
	# THESE MUST BE ASSIGNED OUTSIDE OF THE LOOP
	 
	i_time = -1
	i_endtime = -1
	i_precision = -1
	i_latitude = -1
	i_longitude = -1
	i_agglocations = -1
	i_deleted = -1
	
	i_lineerror = 0
	i_count = 0
	
	line_skip = 0
	line_count = 0
	
	log_file.write('===============================================================\n')
	log_file.write('====================== IMPORTING CSV DATA =====================\n')
	log_file.write('===============================================================\n\n')
	
	# FIND THE HEADERS AND SET THE VARIABLES FOR THEIR LOCATIONS, LOOP THROUGH THE LINES UNTIL THEY ARE FOUND
	while line_skip < 3:
		
		in_file_l = in_file_o.readline().rstrip() #strip gets rid of \n at end of each line read

		in_file_d = in_file_l.split(',')

		if not in_file_l:
			break
	
		# LOCATE THE FIELDS TO BE USED SO PROPER VALUES CAN BE OBTAINED FOR EACH RECORD
		fieldcount = 0
		
		for field in in_file_d:
			if field.upper() == 'TIME':
				i_time = fieldcount
				line_skip += 1
			if field.upper() == 'END TIME':
				i_endtime = fieldcount
			if field.upper() == 'PRECISION' or field.upper() == 'HORIZONTAL ACCURACY': # Added horizontal accuracy for new Cellebrite update
				i_precision = fieldcount
			if field.upper() == 'LATITUDE':
				i_latitude = fieldcount
				line_skip += 1
			if field.upper() == 'LONGITUDE':
				i_longitude = fieldcount
				line_skip += 1
			if field.upper() == 'AGGREGATED LOCATIONS':
				i_agglocations = fieldcount
			if field.upper() == 'DELETED':
				i_deleted = fieldcount
			
			fieldcount += 1
			
		# COUNT THE LINES READ TO GET THROUGH THE FIELD NAMES
		line_count += 1
		
	# RESET THE LINE SKIP
	line_skip = 0 

	log_file.write('Field location indexes found and assigned\n\n')
	
	# POSSIBLE TO LOOK AT ====== line = linecache.getline(thefilename, 33) READS THAT LINE W/O OPENING THE FILE   STANDARD LIBRARY
	
	# LOOP THROUGH THE REST OF THE RECORDS AND IMPORT THEM IF VALID
	while True:
		
		# TESTING TO MAKE SURE LINES READ
		
		in_file_l = in_file_o.readline().rstrip() #strip gets rid of \n at end of each line read
		in_file_d = in_file_l.split(',')

		if not in_file_l:
			break

		fieldcount = 0
		
		# ~ # PRE ASSIGN THESE TO AVOID POSSIBLE CRASHES
		s_time = ''
		s_endtime = ''
		s_latitude = ''
		s_longitude = ''
		s_time = ''
		s_deleted = ''
		s_precision = ''
		s_endtime = ''
		s_agglocations = ''
		
		# IF THEY ARE ALL ASSIGNED, GET THE DATA FOR EACH FIELD ACCORDINGLY.
		try:
		
			if i_time != -1 and i_latitude != -1 and i_longitude != -1:

				s_time = in_file_d[i_time]
				if i_endtime != -1: s_endtime = in_file_d[i_endtime]
				if i_precision != -1: s_precision = in_file_d[i_precision]
				s_latitude = in_file_d[i_latitude]
				s_longitude = in_file_d[i_longitude]
				if i_agglocations != -1: s_agglocations = in_file_d[i_agglocations]
				if i_deleted != -1: s_deleted = in_file_d[i_deleted]
				# ASSIGN DELETED INSTEAD OF YES FOR LABELING.
				if s_deleted.upper() == "YES":
					s_deleted = "DELETED"	
			
				# GET RID OF THE HORIZONTAL LABEL IN PRECISION
				x = ': ' in s_precision
				if x == True: 
					split_s_precision = s_precision.split(': ')
					s_precision_type = split_s_precision[0]
					s_precision = split_s_precision[1]
				else: s_precision_type = ''
				x = False
				s_precision_units = 'Meters Radius'

				if s_time != None and s_time != '':				
					s_mactime = module_general_functions.datetime_to_epoch(s_time)
					if s_mactime == 'INVALID': s_mactime = 'NULL'
				else: s_mactime = ''
					
				if s_endtime != None and s_endtime != '':
					s_macendtime = module_general_functions.datetime_to_epoch(s_endtime)
					if smacendtime == 'INVALID': s_macendtime = 'NULL'
				else: s_macendtime = ''
				
				# INSERT THE RECORD INTO THE SQLITE DATABASE TABLE _device_locations
				sql_insert = f"""INSERT INTO _device_locations (ZTIMESTAMP, ZENDTIME, ZHORIZONTALACCURACY, ZHACCURACYTYPE, 
				ZHACCURACYUNITS, ZLATITUDE, ZLONGITUDE, AGGREGATEDLOCATIONS, DELETED)
				VALUES ('{s_mactime}','{s_macendtime}','{s_precision}','{s_precision_type}','{s_precision_units}',
				'{s_latitude}','{s_longitude}','{s_agglocations}','{s_deleted}')"""
				
				# Only create the entry if the three requirements are there
				if s_mactime != '' and s_latitude != '' and s_longitude != '':
					sql_cur.execute(sql_insert)
	
				i_count += 1

		# HERE FOR LINES THAT ARE MESSED UP TO AVOID CRASHING	
		except Exception as e:
			i_lineerror += 1
			# ~ print(e)
			print(f'LINE ERROR...(Reporting lines that don\'t fit the header layout){e}')
			print()

	log_file.write(f'Records imported: {i_count} from {in_file}\n')
	log_file.write(f'Line errors from abnormal record lines: {i_lineerror}\n')
	print(f'Records imported: {i_count} from {in_file}')
	print(f'ERRORS in lines: {i_lineerror}')
	
	# PUT OUR TOYS AWAY
	in_file_o.close()
	log_file.close()
	sql_con.commit()
	sql_con.close()


