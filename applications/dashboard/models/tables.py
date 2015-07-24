
# db.define_table('page_visit_count',
# 	Field('page_name'),
# 	Field('counter', 'integer'),
# 	)

db.define_table('page_visit_data',
	Field('page_name'),
	Field('last_visited','datetime'),
	Field('args', 'text'),
	Field('vars', 'text'),
	Field('filename'),
	Field('log_file','upload'),
	)

db.define_table('debug_tbl',
	Field('error_message','text'),
	Field('other_info'),
	)

db.define_table('das_config',
	Field('das_id'),
	Field('serial_number'),
	Field('das_location'),
	Field('notes'),
	)

## This info will be stored in dynamo!
## The table will have one key, the serial number. 
# db.define_table('das_attrs',
# 	Field('serial_number','reference das_config.serial_number'),
# 	Field)


db.define_table('device_config',
	Field('device_id'),
	Field('serial_number'),
	Field('measuring'),
	Field('device_location'),
	Field('notes'),
	)


db.define_table('log_files',
	Field('device_id'),
	Field('log_filename'),
	Field('log_file', 'upload'),
	Field('date_added','datetime'),
	)


	


## If I store the acquisuite info in dynamo, I don't have to worry about the names of the params,
## I just use the param name and the attribute freely,
## If there is another unit, I just use whatever names and data they store
## That means I only have to keep track of what certain common info names are for each type of unit. 
## If there is a request to view info, I can get the serial- use that to get the acquisuite info from 
## dynamo, use that to get the config for the unit and pull the time series data for that unit.
## I think that is better than marrying the acquisuite names for the fields to the db tables
## I also think it is better than trying to come up with common field names based only on the acquisuite. 

## I still need a DAS config to use as data validation. But I could still actually use dynamo.....
## But then letting other people configure units might be tricky. I'll keep that in the postgre db for now

