
from datetime import datetime
import fs.s3fs
myfs = fs.s3fs.S3FS('wantsomedashboards','logfiles',os.environ['AWS_WSDS3_KEY'], os.environ['AWS_WSDS3_SECRET'])


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
	Field('row_text','text'),
	Field('cell_text','text'),
	Field('timestamp_text','text'),
	)


db.define_table('das_config',
	Field('das_id'),
	Field('serial_number'),
	Field('das_location'),
	Field('notes'),
	Field('last_modified','datetime'),
	)

## This info will be stored in dynamo!
## The table will have one key, the serial number. 
# db.define_table('das_attrs',
# 	Field('serial_number','reference das_config.serial_number'),
# 	Field)


db.define_table('device_config',
	Field('device_id'),
	Field('das_id'),
	# Field('serial_number'),
	Field('measuring'),
	Field('device_location'),

	Field('device_field_groups'),

	Field('notes'),
	Field('last_modified', 'datetime'),
	)
db.device_config.das_id.requires=IS_IN_DB(db,'das_config.das_id')
db.device_config.last_modified.default=datetime.now()
db.device_config.device_field_groups.requires=IS_IN_DB(db,'device_field_groups.field_group_name')


db.define_table('log_files',
	Field('device_id'),
	Field('log_filename'),
	Field('log_file', 'upload'),
	Field('date_added','datetime'),
	)
db.log_files.log_file.uploadfs=myfs
db.log_files.device_id.requires=IS_IN_DB(db,'device_config.device_id')


	


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



db.define_table('device_field_groups',
	Field('field_group_name'),
	Field('field_group_type'),
	Field('field_group_columns','list:integer'),
	Field('last_modified','datetime'),
	)

db.device_field_groups.field_group_type.requires=IS_IN_SET(('include','exclude'))


##I don't want to limit this to tenants right now, but I can't think of another name!
db.define_table('arbitrary_field_groups',
	Field('field_group_name'),
	Field('das_id'),
	Field('device_id'),
	Field('field_ids','list:integer'),
	Field('multiplier','double'),
	Field('percentage','double'),
	Field('add_or_subtract'),
	Field('last_modified','datetime'),
	)

## limit to percent
db.arbitrary_field_groups.percentage.requires=IS_FLOAT_IN_RANGE(0,1)
db.arbitrary_field_groups.last_modified.default=datetime.now()
db.arbitrary_field_groups.add_or_subtract.requires=IS_IN_SET(('add','subtract'))

db.arbitrary_field_groups.das_id.requires=IS_IN_DB(db,'das_config.das_id')
db.arbitrary_field_groups.device_id.requires=IS_IN_DB(db,'device_config.device_id')





db.define_table('aws_core_columns',
	Field('table_name'),
	Field('core','boolean'),
	# Field('equipment_type'),
	Field('data'),
	Field('defaultContent'),
	Field('title'),
	Field('column_order','integer'),
	Field('width'),
	)



db.define_table('coned_ra_elec',
	Field('account_number'),
	Field('start_date','datetime'),
	Field('end_date','datetime'),
	Field('electric_usage_kwh'),
	Field('reading_type'),
	Field('kvars'),
	Field('electric_demand_kw'),
	Field('retail_access_amount_usd'),
	)