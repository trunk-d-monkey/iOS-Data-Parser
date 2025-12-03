# PYTHON 3
#
# This is a short script written by Aaron Roberts to remove or rename the
# NAME tags in a KML file and allows you to create a text file containing
# names to exclude.  For instance, the Names may be all timestamps in which
# you only want certain ones listed because of the mass amount of points.
# You can list those you want to keep in the input text file and these will
# be skipped over during replacement.  
#
# The intended use if for court preparation when a route needs to be shown
# but the mass amount of names is confusing and only names for specific
# points need to be shown while the others just need to show drop pins.
#
# Use the -h or --help argument to list the help file

import os
import sys
# ~ import geopy
# ~ import gpsdist
import datetime
import struct
import math

# Set global variables
s_file = ''
s_begin = ''
s_end = ''
b_argv = False

# To print the help message from multiple locations
# ld_help is the dictionary of numbers and booleens, lb_prompt is booleen if prompt is shown
def help_message(ld_help, lb_prompt):
	
	ls_help_1 = '''
---------------------------------------------------------------------------
----------------- HELP DOCUMENTATION - ABOUT ------------------------------
---------------------------------------------------------------------------
This program will process a kml file that has the following tags within 
the <Placemark> tags and rename the points if specified and create
path lines from consecutively timestamped points calculating distance
and speed from one point to another.  If precision is specified, it will
calculate a high, point to point, and low speeds in multiple formats.
To use the precision, it must be put into the <name> tage in parantheses
with the unit.  Ex: (13 Meters), (13 M), (13 Feet)

TAGS USED:

    <Placemark>
    <name></name>
    <description></description>
    <TimeStamp><when></when></TimeStamp>
    <Point><altitudeMode></altitudeMode><coordinates></coordinates></Point>
    </Placemark>

iOS Data Parser will put data into this format as will the underlying
query it uses.  
'''

	ls_help_2 = '''
---------------------------------------------------------------------------
-------------- HELP DOCUMENTATION - EXCLUDE LIST --------------------------
---------------------------------------------------------------------------
The exclude list is a simple text file that yout put the ENTIRE contents
of items within the <name> tags that you want to exclude from renaming.
This is useful to keep key points labeled with the Unique timestamp.

This needs to be a basic text file with each name on a separate line

EXAMPLE CONTENTS:

    2022-12-15 14:08:53.809 EST  (9 Meters)
    2022-12-15 14:32:11.816 EST  (9 Meters)
    2022-12-15 14:38:48.817 EST  (10 Meters)
    2022-12-15 16:44:24.813 EST  (3 Meters)
   
If you want to mark key points, you can do so AFTER the process OR you
can change the name IN the input KML BEFORE processing.  However, if
there is a precision, LEAVE the precision there.

EXAMPLE: <name>2022-12-15 14:08:53.809 EST  (9 Meters)</name>
             Becomes: <name>Device at Suspects Home (3 Meters)</name>
'''

	ls_help_3 = '''
---------------------------------------------------------------------------
----------------- HELP DOCUMENTATION FOR ARGUMENTS ------------------------
---------------------------------------------------------------------------

   -h or --help      : Display Help messages
   -i or --input     : Input file (Required)
   -o or --output    : Output file (Defaults to [input file]_output)
   -e or --exclude   : File of names to exclude from replacement (Optional)
   -r or --rename    : What to substitute with (optional, "" for blank)
   -p or --precision : T or True to keep precision in name (Optional)
   -s or --speeed    : Speed caluclation (fps, mps, mph, kmh)
   
   Examples: 
	 kml-refine.py -i input.kml -e exclude.txt -r "" -s mph
	 kml-refine.py -i input.kml -e exclude.txt -p t -s kmh
	 kml-refine.py -i input.kml -o outfile.kml -s mph 
	 
'''

	ls_help_4 = '''
---------------------------------------------------------------------------
----------------- HELP DOCUMENTATION - ACCURACY ---------------------------
---------------------------------------------------------------------------
Accuracy depends on the accuracy of the location.  This means horizontal
precision is key unless you know each point is accurate within a few
meters.  It's suggested that if precision is available, only those points
with high accuracy are used, generally 25 meters or less.  If there are
a high number of points with precision under 15, it's even better to use
only those.  If you get an odd calculations, check if the circles of the
precisions overlap as this causes much of those issues.  
'''
	# Set the order of display for multiple helps
	ll_display_order = [1,4,2,3]
	
	# Populate the dictionary of helps
	ld_help_m = {}
	ld_help_m[1] = ls_help_1
	ld_help_m[2] = ls_help_2
	ld_help_m[3] = ls_help_3
	ld_help_m[4] = ls_help_4
	
	# Release the variables
	ls_help_1 = None
	ls_help_2 = None
	ls_help_3 = None
	ls_help_4 = None
	
	# Cycle through the dictionary by the display order
	for x in ll_display_order:
		# Print ONLY if the dictionary item set to True (from calling this function)
		if ld_help[x] == True: 
			print(ld_help_m.get(x))
			
			if lb_prompt == True: input('Press ENTER to continue')

# Check to make sure input can be translated as an integer to avoid crashes
def check_integer(l_input):
	try: 
		x = int(l_input)
		l_int = True
	except: l_int = False
	return l_int

def check_float(l_input):
	try:
		x = float(l_input)
		l_float = True
	except: l_float = False
	return l_float

# GET ARGUMENTS FUNCTION
def get_arguments():
	
	lb_error = False
	lb_help = False
	l_arguments = []
	d_variables = {}
	
	# Dictionary to hold arguments.  Type and TWO arguments are required. 
	# Modifiy this as needed to hold the arguments needed.  If other things
	# are added to the commmand line by the user or switches without 
	# anything following, they will be ignored. 
	# Any argument following the items in the list will be put into a new
	# dictionary 'd_variables' so that they can be assigned.
	# EX: -d MyFolder will be put into the dictionary as 
	#    {'directory': 'MyFolder'}
	# which can be called by s_directory = d_variables.get('directory')
	
	d_arguments = {
	'help':['-h', '--help'], # Leave the HELP here.  The other items an be changed.
	'input':['-i', '--input'],
	'output':['-o', '--output'],
	'exclude':['-e', '--exclude'],
	'rename':['-r', '--rename'],
	'precision':['-p', '--precision'],
	'speed':['-s','--speed']
	}
	
	i_arg = len(sys.argv) # Get number of arguments
	i_arg_count = 0
	
	# Get a list of arguments
	for x in range(1, i_arg):
		l_arguments.append(sys.argv[x])

	# If an argument is one of the helps, stop and print help documentation.
	for x in l_arguments:
		# Check each argument in the list to see if help is requested. 
		if x.lower() == '-h' or x.lower() == '--help':
			lb_help = True

	if lb_help == False:
		i_index = 0
		for x in l_arguments: # Cycle through list of arguments
			for i in d_arguments.items(): # Cycle through dictionary items (touples)
				if x == i[1][0] or x == i[1][1]:  # Compare if argument matches value
					if (i_index + 2) < i_arg: # Make sure the end is within range to avoid errors
						d_variables[i[0]] = l_arguments[i_index + 1] # If it's within range, assign key/value
			i_index += 1 # Add to the index.
	
	# Variables can now be assigned with the 'd_variables' dictionary.
	ls_input = d_variables.get('input')
	ls_output = d_variables.get('output')
	ls_exclude = d_variables.get('exclude')
	ls_substitute = d_variables.get('rename')
	ls_speed = d_variables.get('speed')
	if ls_speed != None: ls_speed = ls_speed.lower()
	# Get the precision accounting for lower and then assign to booleen.
	ls_precision = d_variables.get('precision')
	if ls_precision != None: ls_precision = ls_precision.lower()
	lb_precision = False # Set this for a default
	if ls_precision == 'true' or ls_precision == 't':
		lb_precision = True
	ls_precision = None
	
	# Allow for default speed measurement if in correct formatting entered
	# and default to mph if none are in the list below
	if ls_speed != None:
		# Format for speed and default if wrong
		ld_speed_formats = {
		'mph':['mph','milesperhour','miles per hour', 'mp hour','miles','mile','mh'],
		'kmh':['kmh','kph','kilometers per hour','kp hour','kilometersperhour','kilometers','kilometer','km'],
		'fps':['fps','feetpersecond','feet per second','feet','foot','ft','fs'],
		'mps':['mps','meters','meter','meters per second','meterspersecond','met','mt','ms']
		}
		
		lb_speed_formatted = False
		for x in ld_speed_formats:
			xl = ld_speed_formats[x]
			if ls_speed in ld_speed_formats[x]: 
				ls_speed = x
				lb_speed_formatted = True
		if lb_speed_formatted == False:
			
			print(f'{ls_speed} is not a known format for mph or kmh')
			print('Defaulting to mph (Miles Per Hour)')
			input('Press ENTER to continue...')
			ls_speed = 'mph'
	
	# Return the arguments
	return ls_input, ls_output, ls_exclude, ls_substitute, lb_precision, ls_speed, lb_help

# PROCESS FILE FUNCTION
def process_file(ls_input, ls_output, ls_exclude, ls_substitute, lb_precision, ls_speed):
	
	ls_placemark_start = '<Placemark>' # Start of TAG
	ls_placemark_end = '</Placemark>' # End of TAG
	
	ll_exclude = []
	
	# If inputs don't exist, notify and exit
	if os.path.isfile(ls_input) == False: 
		print(f'File {ls_input} does not exist.  Please check spelling')
		return 
	
	# Get list of exclude names and assign blank list if none.
	if ls_exclude != None:
		if os.path.isfile(ls_exclude) == False: 
			print(f'File {ls_exclude} does not exist.  Please check spelling')
			return
		
		# Get list of NAMES to exclude
		l_e = open(ls_exclude, 'r')
		ll_exclude_temp = l_e.readlines()
		# Put the entries into a list while stripping \n
		for l_x in ll_exclude_temp:
			ll_exclude.append(l_x.strip())
		ll_exclude_temp = None
		l_e.close()
	else: ll_exclude = []
	
	# Open the files for input and output
	s_if = open(ls_input, 'r')
	
	# Read the lines from the input file into a list and close the file
	l_if = s_if.read()
	# Close the input file
	s_if.close()
	# Set the variables and build the list for replacement
	ld_entry = {} # For holding individual entries
	ld_entries = {}
	ll_locations = []
	ll_placemarks = []
	li_count = 0
	li_x = 0
	ld_lumber = {} # Will hold the combined points and lines

	while True:
		li_x = l_if.find(ls_placemark_start, li_x + len(ls_placemark_start))
		# In case we reach the end of the file
		if li_x == -1: break
		# Add the location of the START of the tag to the list
		ll_locations.append(li_x)
		# Find the end tag
		li_x = l_if.find(ls_placemark_end, li_x + len(ls_placemark_end))
		# Append the index to the list
		ll_locations.append(li_x)
		# Assign the name as the string between the beginning and ending indexes
		ls_placemark = l_if[ll_locations[0]:ll_locations[1]]
		# Append the name to the list
		ll_placemarks.append(ls_placemark)

		# ~ # Clear the list for the next loop
		ll_locations = []
		
		# Parse the placemark
		ld_entry = get_parts(ls_placemark)
		
		# ld_entry now has placemark parsed.  We need to now add the new name if items are to be renamed

		# If paramater is not None, get the substitution accounting for precision paramater.
		if s_substitute != None:
			# Set the temp name as what to substitute for
			ls_x = s_substitute
			# Account for if precision is True
			if lb_precision == True:
				ls_y = ld_entry.get('precision_label')
				if ls_x != '': ls_x = ls_x + ' '
				ls_x = s_substitute + ls_y
				ls_y = None
			# Get the name to check if in exclude list
			ls_y = ld_entry.get('name')
			# if it's in the list, keep the original name as substitute: ls_y
			if ls_y in ll_exclude: 
				ld_entry['substitute'] = ls_y
			# If NOT, then use the new name: ls_x
			else: 
				ld_entry['substitute'] = ls_x
			ls_x = None
		# If no substitute, then just put original name as substitute for writing later
		else: ld_entry['substitute'] = ld_entry['name']
		
		# Nest the dictionary into the parent dictionary
		ld_entries[ld_entry['timestamp']] = ld_entry
		
		ld_entry = {} # Clear the dictionary for the next parsed single entry
		# Add to the count for the key in the ld_locations
		# ~ li_count += 1

	# Sort the dictionary into a new one to make sure the entries will be in order.
	ld_entries_sorted = dict(sorted(ld_entries.items(), key=lambda item: item[0], reverse=False))
	ld_entries = None # Release the memory and keep the sorted. 

	# WE NOW HAVE A DICTONARY WITH THE PARSED CONTENTS 
	i = 0
	
	# Lets now assign an entry to each in order.  We'll assign it as a 
	# new key to make inserting more straight forward.  
	
	ld_entries = {} # Set up new dictionary, re-using old name
	li_entry = 1 # Set entry to start at 1 for first entry
	for x in ld_entries_sorted.keys():
		ld_entries[li_entry] = ld_entries_sorted[x]
		ld_entries[li_entry]['entry'] = li_entry # Entry matches key
		li_entry += 2 # Increment x2 to allow for line with distance (high and low) and speed (high and low)
	ld_entries_sorted = None # Release the previous dictionary
	
	ld_lines = {} # Will hold the line entries to later join with the point entries. Outside of loop for a reason
	if ls_speed != None and ls_speed != '':
	# Now cycle through the dictionary in order as we parse the distance and speed

		for x in ld_entries.keys():
			
			ll_start = {} # Clear these for each new entry (avoids duplicate at end)
			ll_end = {}
			ld_line = {}
			li_distance = 0
			li_distance_low = 0
			li_distance_high = 0
			li_distance_m = 0
			li_distance_low_m = 0
			li_distance_high_m = 0
			li_seconds = 0
			li_tz = 0
			li_precision_s = 0
			li_precision_e = 0
			li_speed_low_fps = 0
			li_speed_high_fps = 0
			li_speed_low_mph = 0
			li_speed_high_mph = 0
			
			ll_start['entry'] = ld_entries[x]['entry']
			ll_start['lat'] = ld_entries[x]['lat']
			ll_start['lon'] = ld_entries[x]['lon']
			ll_start['elev'] = ld_entries[x]['elev']
			ll_start['precision_integer'] = ld_entries[x]['precision_integer']
			ll_start['timestamp'] = ld_entries[x]['timestamp']
			ll_start['mac_absolute'] = ld_entries[x]['mac_absolute']
			ll_start['tz_offset'] = ld_entries[x]['tz_offset']
			ll_start['precision_integer'] = ld_entries[x]['precision_integer']
			ll_start['precision_type'] = ld_entries[x]['precision_type']

			li_next = ll_start['entry'] + 2

			y = ld_entries.get(li_next)

			if y != None: # Get the following ONLY if there is a record for that entry (accounts for END)
				ll_end['entry'] = y['entry']
				ll_end['lat'] = y['lat']
				ll_end['lon'] = y['lon']
				ll_end['elev'] = y['elev']
				ll_end['precision_integer'] = y['precision_integer']
				ll_end['timestamp'] = y['timestamp']
				ll_end['mac_absolute'] = y['mac_absolute']
				ll_end['tz_offset'] = y['tz_offset']
				ll_end['precision_integer'] = y['precision_integer']
				ll_end['precision_type'] = y['precision_type']
				
				ls_m_unit = 'ft'
				li_distance = haversine_distance(ll_start['lat'], ll_start['lon'], ll_end['lat'], ll_end['lon'], ls_m_unit)
				li_seconds = ll_end['mac_absolute'] - ll_start['mac_absolute']
				
				# 1 foot = 0.3048 meters
				# 1 meter = 3.28048 feet
				# speed(fps) = distance(ft) / time(sec)
				# distance(ft) = speed(fps) * time(sec)
				# time(sec) = distance(ft) / speed(fps)
				# fps = mph * 1.46667
				# mph = fps * 0.681818
				
				# Calculate as MPH then convert
				
				# FT = feet
				# M = meters
				# IN = inches
				# CM = centemeters
				# MM = millimeters
				
				ls_start_ptype = ll_start['precision_type']
				ls_end_ptype = ll_end['precision_type']
				
				# Default to Meters if nothing there
				if ls_start_ptype == None or ls_start_ptype == '': ls_start_ptype = 'M'
				if ls_end_ptype == None or ls_end_ptype == '': ls_end_ptype = 'M'
				
				# Get the integer to use depending on the precision type
				li_precision_s = ll_start.get('precision_integer')
				li_precision_e = ll_end.get('precision_integer')
				
				# Adjust each type to feet for the calculations
				if ls_start_ptype == 'M': li_precision_s = li_precision_s * 3.28084 # Meters to feet
				elif ls_start_ptype == 'IN': li_precision_s = li_precision_s / 12  # Inches to feet
				elif ls_start_ptype == 'CM': li_precision_s = li_precision_s / 30.48 # Centimeters to feet
				elif ls_start_ptype == 'MM': li_precision_s = li_precision_s / 304.8 # Millimeters to feet
				elif ls_start_ptype == 'FT': pass # Already feet
				
				if ls_end_ptype == 'M': li_precision_e = li_precision_e * 3.28084 # Meters to feet
				elif ls_end_ptype == 'IN': li_precision_e = li_precision_e / 12 # Inthces to feet
				elif ls_end_ptype == 'CM': li_precision_e = li_precision_e / 30.48 # Centimeters to feet
				elif ls_end_ptype == 'MM': li_precision_e = li_precision_e / 304.8	# Millimeters to feet
				elif ls_end_ptype == 'FT': pass # Already feet
				
				# CALCULATIONS ALL CONVERTED TO FEET FOR CALCULATIONS BELOW
				# Calculate high and low distances from precision
				li_distance_low = li_distance - (li_precision_s / 2) - (li_precision_e / 2)
				li_distance_high = li_distance + (li_precision_s / 2) + (li_precision_e / 2)
				
				# Get distance in METERS from FEET
				li_distance_low_m = li_distance_low * 0.3048
				li_distance_m = li_distance * 0.3048
				li_distance_high_m = li_distance_high * 0.3048
				
				# Calculate LOW speed (fps, mph)
				# ~ print(f'li_distance_low: {li_distance_low}, li_seconds: {li_seconds}') # TESTING =================
				
				if li_seconds != 0 and li_seconds != 0.0:
					li_speed_low_fps = li_distance_low / li_seconds
				else: li_speed_low_fps = li_distance_low
				li_speed_low_mph = li_speed_low_fps * 0.681818
				
				# Calculate speed point to point (fps, mph)
				if li_seconds != 0 and li_seconds != 0.0:
					li_speed_fps = li_distance / li_seconds
				else: li_speed_fps = li_distance
				li_speed_mph = li_speed_fps * 0.681818
				
				# Calculate HIGH speed (fps, mph)
				if li_seconds != 0 and li_seconds != 0.0:
					li_speed_high_fps = li_distance_high / li_seconds
				else: li_speed_high_fps = li_distance_high
				li_speed_high_mph = li_speed_high_fps * 0.681818
				
				# Convert for kilometers per hour
				li_speed_low_kmh = li_speed_low_mph * 1.60934 # Kilometers per hour
				li_speed_high_kmh = li_speed_high_mph * 1.60934 # Kilometers per hour
				li_speed_kmh = li_speed_mph * 1.60934 # Kilometers per hour point to point
				
				# Convert for meters per second
				li_speed_low_mps = li_speed_low_fps * 0.3048 # Meters per second
				li_speed_high_mps = li_speed_high_fps * 0.3048 # Meters per second
				li_speed_mps = li_speed_fps * 0.3048 # Meters per second point to point
				
				# Decide the name entry (main display)
				if ls_speed == 'mph':
					li_d_speed_low = li_speed_low_mph
					li_d_speed_high = li_speed_high_mph
					li_d_speed = li_speed_mph
				
				if ls_speed == 'fps':
					li_d_speed_low = li_speed_low_fps
					li_d_speed_high = li_speed_high_fps
					li_d_speed = li_speed_fps
				
				if ls_speed == 'kmh':
					li_d_speed_low = li_speed_low_kmh
					li_d_speed_high = li_speed_high_kmh
					li_d_speed = li_speed_kmh
				
				if ls_speed == 'mps':
					li_d_speed_low = li_speed_low_mps
					li_d_speed_high = li_speed_high_mps
					li_d_speed = li_speed_mps
				
				# ONLY show the low and high distances IF one value has horizonal precision > 0
				if li_distance == li_distance_low and li_distance == li_distance_high:
					ls_mph_low = ''
					ls_mph_high = ''
					ls_fps_low = ''
					ls_fps_high = ''
					ls_kmh_low = ''
					ls_kmh_high = ''
					ls_mps_low = ''
					ls_mps_high = ''
					
					ls_distance_low = ''
					ls_distance_low_m = ''
					ls_distance_high = ''
					ls_distance_high_m = ''
					
					ls_speed_name = f'SPEED ({ls_speed}): {li_d_speed:.2f}'
					
				else:
					ls_mph_low = f'\tLow: {li_speed_low_mph:.2f}\n'
					ls_mph_high = f'\n\tHigh: {li_speed_high_mph:.2f}'
					ls_fps_low = f'\tLow: {li_speed_low_fps:.2f}\n'
					ls_fps_high = f'\n\tHigh: {li_speed_high_fps:.2f}'
					ls_kmh_low = f'\tLow: {li_speed_low_kmh:.2f}\n'
					ls_kmh_high = f'\n\tHigh: {li_speed_high_kmh:.2f}'
					ls_mps_low = f'\tLow: {li_speed_low_mps:.2f}\n'
					ls_mps_high = f'\n\tHigh: {li_speed_high_mps:.2f}'
					
					ls_distance_low = f'\tShort: {li_distance_low:.1f}'
					ls_distance_low_m = f', {li_distance_low_m:.1f}\n'
					ls_distance_high = f'\n\tLong: {li_distance_high:.1f}'
					ls_distance_high_m = f', {li_distance_high_m:.1f}'
					
					ls_speed_name = f'SPEED ({ls_speed}): {li_d_speed_low:.2f} - {li_d_speed_high:.2f}'
				
				ls_distance = f"""\tDistance (feet, meters):\n{ls_distance_low}{ls_distance_low_m}\tPoint: {li_distance:.1f}, {li_distance_m:.1f}{ls_distance_high}{ls_distance_high_m}"""
				
				# Speed calculations shown in description
				ls_line_desc = f"""\tMiles Per Hour:      
{ls_mph_low}\tPoint: {li_speed_mph:.2f}{ls_mph_high}
   
\tFeet Per Second:     
{ls_fps_low}\tPoint: {li_speed_fps:.2f}{ls_fps_high}

\tKilometers Per Hour: 
{ls_kmh_low}\tPoint: {li_speed_kmh:.2f}{ls_kmh_high}

\tMeters Per Second:   
{ls_mps_low}\tPoint: {li_speed_mps:.2f}{ls_mps_high}"""

				# Release the variables from the above ls_line_desc
				ls_mph_low = None
				ls_mph_high = None
				ls_fps_low = None
				ls_fps_high = None
				ls_kmh_low = None
				ls_kmh_high = None
				ls_mps_low = None
				ls_mps_high = None
				
				ls_distance_low = None
				ls_distance_low_m = None
				ls_distance_high = None
				ls_distance_high_m = None
				
				# Add the parts to the dictionary
				ld_line['entry'] = ll_start['entry'] + 1
				ld_line['entry_type'] = 'line'
				ld_line['distance'] = ls_distance
				ld_line['timestamp'] = ll_end['timestamp']
				ld_line['name'] = ls_speed_name
				ld_line['coordinates'] = f"{ll_start['lon']},{ll_start['lat']},{ll_start['elev']} {ll_end['lon']},{ll_end['lat']},{ll_end['elev']}"
				ld_line['description'] = ls_line_desc # Add the text for all calculations.
				ld_line['seconds'] = li_seconds
				# Add the dictionary as a nested dictionary into ld_lines
				ld_lines[ld_line['entry']] = ld_line
				
				ls_speed_name = None # Release the variable
				
	# Cycle ld_entries and ld_lines into ld_lumber
	x = len(ld_entries) # Count the records
	y = len(ld_lines) # Count the records
	i_scope = x + y + 1 # Add them and account for the last one
	
	# Need to expand scope IF no speed assigned to allow for ALL entry numbers (since x2 to allow insertion previously)
	# Without this, you'll be missing half the records if you don't include the speed calculation lines
	if ls_speed == None or ls_speed == '': i_scope = i_scope * 2
	
	# Combine the entries into ld_lumber
	for l_entry in range(0, i_scope):
		y = ld_entries.get(l_entry)
		if y != None: ld_lumber[l_entry] = y
		y = ld_lines.get(l_entry)
		if y != None: ld_lumber[l_entry] = y
	
	# Get rid of the other two dictionaries, release memory
	ld_entries = None
	ld_lines = None
	
	# Count the records in the new dictionary
	li_count = len(ld_lumber)
	
	# COMMAND: python kml-refine.py -i input.kml -o output.kml -e exclude.txt -p t -r "" -s mph
	
	# Cycle through the entries and write them to a file.
	ls_result = write_kml(ld_lumber, ls_output)	# Returns nothing for now

	print('\nRESULTS --->>>>>>>>>>>>>>>>>>>>>>>>>>>\n')

	if ls_substitute != None:
		if ls_substitute == '': print('---> Names replaced with BLANKS')
		else: print(f'Names replaced with "{ls_substitute}" in file {ls_output}\n')
	if lb_precision == True: print('---> Precisions included in new names')
	if len(ll_exclude) != 0:
		print('\nEXCLUDED NAMES')
		g_logfile.write('\nEXCLUDED NAMES:\n')
		for l_x in ll_exclude:
			print(l_x)
			g_logfile.write(f'{l_x}\n')
			
			
		
	print(f'\n{li_count} Total records processed\n')
	g_logfile.write(f'\n{li_count} Total records processed\n')

# WRITE THE DATA TO THE OUTPUT KML FILE
def write_kml(ld_lumber, ls_output):
	
	ls_line = None # Avooid crashes if something weird happens
	ls_result = ''
	ls_header = """<?xml version="1.0" encoding="utf-8"?><kml xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns="http://www.opengis.net/kml/2.2"><Document>
<Style id="red_measure"><LineStyle><color>ff0000ff</color><width>3</width></LineStyle></Style>\n"""
	ls_footer = """</Document></kml>"""

	l_of = open(s_output, '+w')
	l_of.write(ls_header)
	
	for x in ld_lumber:
		
		ls_entry_type = ld_lumber.get(x).get('entry_type')

		if ls_entry_type == 'line':

			ls_name = ld_lumber.get(x).get('name')
			ls_name = f'<name>{ls_name}</name>'
			
			ls_timestamp = ld_lumber.get(x).get('timestamp')
			ls_timestamp = f'<TimeStamp><when>{ls_timestamp}</when></TimeStamp>'
			ls_style = '<styleUrl>#red_measure</styleUrl>'
			
			# These are all wrapped in <LineString>
			ls_tesselate = '<tessellate>1</tessellate>'
			ls_coordinates = ld_lumber.get(x).get('coordinates')
			ls_coordinates = f'<coordinates>{ls_coordinates}</coordinates>'
			ls_line_string = f'<LineString>{ls_tesselate}{ls_coordinates}</LineString>'
			
			ls_description = ld_lumber.get(x).get('description')
			li_distance = ld_lumber.get(x).get('distance')
			li_seconds = ld_lumber.get(x).get('seconds')
			
			li_minutes_minutes = li_seconds / 60 # Division in minutes
			li_minutes_seconds = li_seconds % 60 # Remainder in seconds
			if li_minutes_minutes > 59: # Accounting for hours (Over 59 minutes)
				li_minutes_hours = li_minutes_minutes / 60
				li_minutes_minutes = li_minutes_minutes % 60
			else: li_minutes_hours = 0
			ls_minutes_hours = str(int(li_minutes_hours)).zfill(2)
			ls_minutes_minutes = str(int(li_minutes_minutes)).zfill(2)
			ls_minutes_seconds = str(int(li_minutes_seconds)).zfill(2)
			
			ls_minutes = f'{ls_minutes_hours}:{ls_minutes_minutes}:{ls_minutes_seconds}'
			
		
			ls_description = f'<description>Duration (sec): {li_seconds}\nHH:MM:SS: {ls_minutes}\n\n{li_distance}\n\n{ls_description}</description>'
			
			ls_line = f'<Placemark>\n\t{ls_timestamp}\n\t{ls_name}\n\t{ls_style}\n\t{ls_line_string}\n\t{ls_description}\n</Placemark>\n'
			
			l_of.write(ls_line)
	
		elif ls_entry_type == 'point':
				
			ls_name = ld_lumber.get(x).get('substitute')
			ls_name = f'<name>{ls_name}</name>'
			
			ls_description = ld_lumber.get(x).get('description')
			ls_description = f'<description>{ls_description}</description>'
			
			ls_timestamp = ld_lumber.get(x).get('timestamp')
			ls_timestamp = f'<TimeStamp><when>{ls_timestamp}</when></TimeStamp>'
			
			# Do altitude mode FIRST since it's part of POINT
			ls_altitude_mode = ld_lumber.get(x).get('altitude_mode')
			ls_altitude_mode = f'<altitudeMode>{ls_altitude_mode}</altitudeMode>'
			
			ls_point = ld_lumber.get(x).get('point')
			ls_point = f'<Point>{ls_altitude_mode}<coordinates>{ls_point}</coordinates></Point>'
			
			ls_precision_label = ld_lumber.get(x).get('precision_label')
			if ls_precision_label != None and ls_precision_label != '': ls_precision_label = f'Horizonal Precision (Radius): {ls_precision_label}'
			else: ls_precision_label =''
			
			ls_description = ld_lumber.get(x).get('description')
			ls_description = f'<description>{ls_description}{ls_precision_label}</description>'
			
			ls_line = f'<Placemark>{ls_name}{ls_description}{ls_timestamp}{ls_point}</Placemark>\n'
			
			l_of.write(ls_line)
			
		else: pass
		
		ls_entry_type = None
	
	l_of.write(ls_footer)
	l_of.close()
	
	return ls_result # Here for future dev if needed

def get_parts(ls_placemark):
	
	ld_entry = {}
	li_s = 0
	li_e = 0
	li_tzoffset = None
	li_precision = 0
	ls_type_precision = ''

	ld_entry['entry_type'] = 'point' # For diffrentiating points from lines
	
	# Dictionary to locate parts from.  If more than one set, the fist is the outer, 
	# next is inner nested inside, and so on and so on.  Each subsequent set is
	# nested within the previous one.  This drills down and gets the value inside
	# the last set within the others. 
	ld_parts = {
	'name':['<name>','</name>'],
	'description':['<description>','</description>'],
	'timestamp':['<TimeStamp>','</TimeStamp>','<when>','</when>'], 
	'altitude_mode':['<Point>','</Point>','<altitudeMode>', '</altitudeMode>'],
	'point':['<Point>','</Point>','<coordinates>','</coordinates>']
	}
	
	for lx in ld_parts:
		li_len = len(ld_parts.get(lx)) # Get the number of entries in the list
		
		li_count = 0

		while li_count < li_len:

			lts_s = ld_parts.get(lx)[li_count]
			lts_e = ld_parts.get(lx)[li_count + 1]
			lti_s = ls_placemark.find(lts_s) + len(lts_s)
			lti_e = ls_placemark.find(lts_e)
			ll_container = ls_placemark[lti_s:lti_e].strip()
			li_count += 2
		
		ls_k = lx
		
		# If there is a value, put it in the ld_entry dictionary as lx / ls_k
		if ll_container != None and ll_container != '':
			ld_entry[ls_k] = ll_container.strip()
		
	# For assigning TYPE from previous abbrev to use later.  
	ld_type_measure = {
	'FT':'foot',
	'M':'meter',
	'IN':'inch',
	'CM':'centimetre',
	'MM':'millimeter'
	}
	
	# Extract the precision and add it to the dictionary if Precision is selected
	ls_name = ld_entry.get('name')
	# ~ if ls_name != None:
	
	if ls_name == None: ls_name = ''
	ls_precision, li_precision, ls_type_precision = get_precision(ls_name)

	# ~ if ls_precision != '' and ls_precision != None:
		
	# Store the precistion NAME for display
	ld_entry['precision_label'] = ls_precision

	# Store the precision TYPE
	ld_entry['precision_type'] = ls_type_precision
	ls_type_precision = None

	# Store the PRECISION INTEGER
	ld_entry['precision_integer'] = li_precision
	li_precision = None

	# Decode the timestamp and add as Mac Absolute for easier comparison
	# Get the item from the dictionary
	ls_timestamp = ld_entry.get('timestamp')
	
	# Get rid of the T if there is one
	ls_timestamp = ls_timestamp.replace('T', ' ')
	# Clean up the timestamp string and account for time zone assignment
	# NEED to remove letters and extra offset to allow timestamp conversion without crashing. 
	if '  ' in ls_timestamp: ls_timestamp = ls_timestamp.replace('  ', ' ') # Replace double spaces with single
	if 'Z' in ls_timestamp or 'z' in ls_timestamp:
		li_tzoffset = 0
		ls_timestamp = ls_timestamp.replace('Z', '')
		ls_timestamp = ls_timestamp.replace('z', '')
	if len(ls_timestamp) > 19:
		ls_tzoffset = ls_timestamp[19:]
		ls_timestamp = ls_timestamp[:19]
		if ':' in ls_tzoffset: # If it's got a : then only the left will be taken (Hours)
			li_v = ls_tzoffset.find(':')
			ls_tzoffset = ls_tzoffset[:li_v]
		lb_i = check_integer(ls_tzoffset) # Check to make sure it can be an integer
		if lb_i == True: # If true, convert it to an integer and multiply for seconds
			li_tzoffset = int(ls_tzoffset) * 60 * 60

	ld_entry['tz_offset'] = li_tzoffset # Assigin it to the dictionary. 
		
	# Get the string value of the epoch calling the function
	ls_epoch = datetime_to_epoch(ls_timestamp)
	
	# If something is messed up with a timestamp, exit showing the location and specific timestamp
	if ls_epoch == 'INVALID':
		print(f'{ls_timestamp} can\'t be converted to a float (in def get_parts)')
		print(f'Please check the entry for the following, repair, and try again\n\n{ls_placemark}')
		print(f'Specifically: {ls_timestamp} within the entry')
		sys.exit('Error in data input')
	
	# Convert to a float
	lf_epoch = float(ls_epoch)
	ls_epoch = None
	# Add it to the dictionary
	ld_entry['mac_absolute'] = lf_epoch
	lf_epoch = None
	
	# GET the LAT and LON from the point (coordinates)
	ls_coordinates = ld_entry.get('point')
	# Split it into a list
	ll_coordinates = ls_coordinates.split(',')
	ls_lon = ll_coordinates[0]
	ls_lat = ll_coordinates[1]
	# IF elevation is present, readd it
	if len(ll_coordinates) > 2: ls_elev = ll_coordinates[2]
	# If NOT, default to 0
	else: ls_elev = '0'
	# Convert to numbers
	lf_lon = float(ls_lon.strip())
	lf_lat = float(ls_lat.strip())
	lf_elev = int(ls_elev.strip())
	ls_lat = None
	ls_lon = None
	ls_elev = None
	# Put them in the dictionary
	ld_entry['lat'] = lf_lat
	ld_entry['lon'] = lf_lon
	ld_entry['elev'] = lf_elev
	
	return ld_entry

# Get the precision if in () with Meters "Meters)"
def get_precision(l_s_name):
	# Measurements dictionary.  Checks and if any values are in name, uses key as abbreviation
	ld_measurements = {
	'FT':['feet','f','ft','foot'],
	'M':['m','meters','meter'],
	'IN':['i','in','inch','inches'],
	'CM':['cm','c','centimetre','centimetres'],
	'MM':['mm','millimeter','millimeters']
	}
	
	ls_abb = '' # Set this to avoid errors (shouldn't happen though)
	li_x = -1 # Here just in case it's not assigned for some crazy reason.
	ls_precision = ''# Here to assign as a string if nothing else is added
	li_precision = 0

	ls_c_name = l_s_name.lower() # Set it to lower case for proper comparison

	for l_k in ld_measurements.keys():
		for l_v in ld_measurements.get(l_k):
			ls_find = f' {l_v})'

			if ls_find in ls_c_name: 
				li_x = ls_c_name.rfind(ls_find) # check to see if it's there (find the measurement name)
				ls_abb = l_k # Assign the variable for the abbreviation
				
	if li_x != -1: # Don't continue if first search term not found. 
		li_s = l_s_name.rfind('(',0 , li_x) + 1
		ls_p_name = l_s_name[li_s:li_x]
		
		# Account for precisions in both integer and float
		lb_precision_i = check_integer(ls_p_name)
		lb_precision_f = check_float(ls_p_name)
		
		# Convert string to integer or float...whatever fits
		if lb_precision_i == True: li_precision = int(ls_p_name)
		if lb_precision_f == True: li_precision = (float(ls_p_name))
		
		ls_precision = f'({li_precision} {ls_abb})'
		
	# li_precision is integer of precision
	# ls_precision is the NAME including (), integer, and abbreviation 
	# ls_abb is the measurement abbreviation (FT, M, IN, CM, MM) 
	
	return ls_precision, li_precision, ls_abb

# FOR CONVERTING A CONVENTIONAL DATE/TIME WITH SECONDS TO MAC ABSOLUTE TIME (SECONDS SINCE 2000-01-01 00:00:00)
def datetime_to_epoch(timestamp, epoch = 'mac_absolute'):
	# times: mac_absolute, unix, unix_millisecond, unix_microsecond
	# Requires import datetime, import time
	# Needs time accurate to seconds and 4 digit year (EX: 2023-04-20 12:02:15)
	# Very flexible and does not matter if year or month are first OR if "-" or "/" is used.  
	# One or two spaces need to be between the date and time.  
	# AM and PM can be used along with the UTC amount (EX: UTC-5).  The code will adjust it all accordingly. 
	# Returns "INVALID" if the format is incorrect.
	
	date_time = timestamp
	
	# SETTING CERTAIN VARIABLES TO MAKE SURE THEY HAVE DEFAULTS
	is_pm = False
	is_tz = False
	t_offset = '0'
	
	# GET RID OF THE ( AND ) THAT MAY BE AROUND THE UTC
	x = '(' in date_time
	if x == True:
		y = date_time.replace('(', '')
		date_time = y
	y = None
	x = None

	x = ')' in date_time
	if x == True:
		y = date_time.replace(')', '')
		date_time = y
	y = None
	x = None

	# CHECK FOR DOUBLE SPACES AND REMOVE TO SINGLE SPACE
	x = '  ' in date_time
	if x == True:
		y = date_time.replace('  ', ' ')
		date_time = y
	x = None
	y = None
	
	# CHECK FOR PM AND SET THE VARIABLE
	x = "PM" in date_time.upper()
	if x == True:
		is_pm = True
		y = date_time.replace('PM', '')
		date_time = y
	x = None
	
	# REMOVE THE AM TO AVOID ISSUES LATER
	x1 = 'AM' in date_time.upper()
	if x1 == True:
		y1 = date_time.replace('AM', '')
		date_time = y1
	x1 = None
	y1 = None
	
	# CHECK FOR THE UTC, GET ANY OFFSET, AND REMOVE 
	x = 'UTC' in date_time.upper()
	if x == True:
		is_tz = True
		tz_i = date_time.upper().index('UTC')
		z = date_time.upper()[tz_i:]
		t_offset = z[3:]
		y = date_time[0:tz_i]
		date_time = y
	x = None
	y = None
	tz_i = None
	
	# THIS IS TO TAKE SPACES OFF OF THE END OF THE UTC AND ASSIGN 0 AS AN OFFSET...AVOID ERROR LATER
	x = " " in t_offset
	if x == True:
		t_offset.replace(' ', '')
	if t_offset == "":
		t_offset = '0'
	x = None
	
	# SETTING THE EPOCH
	if epoch == 'mac_absolute':
		epoch_start = datetime.datetime(2001, 1, 1, 0, 0, 0) # SET THE EPOCH FOR MAC ABSOLUTE
	if epoch == 'unix' or epoch == 'unix_millisecond' or epoch == 'unix_microsecond':
		epoch_start = datetime.datetime(1970, 1, 1, 0, 0, 0) # SET FOR UNIX EPOCH

	try:
		x = " " in date_time
		if x == True:
			split_date_time = date_time.split(" ")

		x = False
		
		# ACCOUNT FOR MULTIPLE SPACES BEETWEEN DATE AND TIME
		x_ct = 0
		
		split_time = split_date_time[1].split(":")
		
		# USING THIS TO ACCOUNT FOR "/" USED IN DATES INSTEAD OF "-"
		x = "-" in split_date_time[0]
		if x == True:
			split_date = split_date_time[0].split("-")
			
		x = "/" in split_date_time[0]
		if x == True:
			split_date = split_date_time[0].split("/")
		
		date_time_comb = split_date + split_time
		date_time = ""

		# ACCONTING FOR YEAR FIRST
		if len(split_date[0]) == 4:
			intYear = int(date_time_comb[0])
			intMonth = int(date_time_comb[1])
			intDay = int(date_time_comb[2])
		
		# ACCOUNTING FOR MONTH FIRST
		if len(split_date[0]) == 2 or len(split_date[0]) == 1:
			intYear = int(date_time_comb[2])
			intMonth = int(date_time_comb[0])
			intDay = int(date_time_comb[1])
		
		# ASSIGN HOUR, MINUTE, SECOND
		intHour = int(date_time_comb[3])
		# ADD 12 HOURS IF THE PM IS PRESENT
		if is_pm == True:
			intHour += 12
		intMinute = int(date_time_comb[4])
		intSecond = int(date_time_comb[5])
		
		# assigned regular string date
		date_time = datetime.datetime(intYear, intMonth, intDay, intHour, intMinute, intSecond)
		time_diff = (date_time - epoch_start)
		time_return_utc = time_diff.total_seconds()
		
		# ADJUST THE OFFSET TO SECONDS, MILLISECONDS, MICROSECONDS
		if epoch == 'mac_absolute' or epoch == 'unix':
			t_offset_sec = int(t_offset) * 60 * 60
		
		if epoch == 'unix_millisecond':
			t_offset_sec = int(t_offset) * 60 * 60 * 1000
			time_return_utc = time_return_utc * 1000

		if epoch == 'unix_microsecond':
			t_offset_sec = int(t_offset) * 60 * 60 * 1000000
			time_return_utc = time_return_utc * 1000000
		
		# REVERSE THE OFFSET SO IT ADJUSTS BACK TO UTC
		tod = 0 - t_offset_sec
		t_offset_sec = 0 + tod
		time_return_utc = time_return_utc + (t_offset_sec)

		return str(time_return_utc)
		
	except:
		 print(f'Invalid format entered. {date_time} is not the proper format for the date time and will cause an error.')
		 return 'INVALID'

def haversine_distance(lat1, lon1, lat2, lon2, m_unit):
    # NEED import math
    
    ld_unit = {
    'km':6371.0, # Earth radius in kilometers
    'mt':6378137.0, # Earth radius in meters
    'mi':3958.0, # Earth radius in miles
    'ft':20926000.0 # Earth radius in feet (sphereoid model used by GPS)
    }
    
    l_r = ld_unit.get(m_unit)
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = l_r * c
    return distance


# BEGIN ====================== BEGIN ===================== BEGIN =======
# Get the arguments to pass onto the processing function
s_input, s_output, s_exclude, s_substitute, b_precision, s_speed, b_help = get_arguments()

if b_help == True:
	help_message({1:True,2:True,3:True,4:True}, True)

# Check to make sure it's all there to avoid crashes
if (s_input != None and s_input != ''):

	# Variables for s_message
	if s_substitute != None and s_substitute != '': sm_substitute = f'\n    Rename: {s_substitute}'
	else: sm_substitute = ''
	if b_precision != None and b_precision != False: sm_precision = f'\n    Show Precision: {b_precision}'
	else: sm_precision = ''
	if s_exclude !=None and s_exclude != '': sm_exclude = f'\n    Exclude Files List: {s_exclude}'
	else: sm_exclude = ''
	if s_speed != None and s_speed != '': sm_speed = f'\n    Speed Calculations: {s_speed}'
	else: sm_speed = ''

	if s_output == None or s_output == '': s_output = f'{s_input}_output.kml'

	s_message = f"""
=======================================
======== KML SPEED CALCULATOR =========
=======================================
    Processing: {s_input}
    Output: {s_output}{sm_precision}{sm_substitute}{sm_speed}{sm_exclude}
---------------------------------------"""
	print(s_message)

	# Start the log file globally to allow logging from any function
	g_logfile = open(f'{s_output}_log.txt', '+w')
	g_logfile.write(f'LOGGING OF KML REFINE FUNCTIONS:\n\nOutput File: {s_output}\n')
	g_logfile.write(f'Input File: {s_input}\n')
	
	s_calculations = """
CALCULATIONS USED IN PROCESSING ENTRIES:

    feet = meters * = 0.3048
    feet = meters / 3.28048 
    meters = feet * 3.28048
	feet = Centemeters / 30.48
    feet = Millimeters / 304.8
    speed(fps) = distance(ft) / time(sec)
    speed(mps) = fps * 0.3048
    speed(kmh) = mph * 1.60934
    distance(ft) = speed(fps) * time(sec)
    time(sec) = distance(ft) / speed(fps)
    fps = mph * 1.46667
    mph = fps * 0.681818
    
    Precision low + high calculated by converting to feet, dividing
    each in half then subtracking both for low and adding both for
    high.  These were then calculated for high + low speeds. 

    Speeds and distance rounded to the hundredth (0.00) decimal (:.2f)
    
	"""
	g_logfile.write(s_calculations)
	s_calculations = None
	
	
	# If they are all present, process the file. 
	process_file(s_input, s_output, s_exclude, s_substitute, b_precision, s_speed)
	
	# Close the log file at the end
	g_logfile.close()
	
else: 
	if b_help == False:
		# Call help message {dictionary shows what to display}, booleen says if promps are displayed.
		help_message({1:False,2:False,3:True, 4:False}, False)
		print('------->>> You need to at least specify the input\n')
		



