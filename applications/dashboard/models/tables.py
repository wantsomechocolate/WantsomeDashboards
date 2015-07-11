
db.define_table('page_visit_count',
	Field('page_name'),
	Field('counter', 'integer'),
	)

db.define_table('page_visit_data',
	Field('page_name'),
	Field('last_visited','datetime'),
	Field('args', 'text'),
	Field('vars', 'text'),
	Field('filename'),
	Field('log_file','upload'),
	)

db.define_table('debug_tbl',
	Field('error_message'),
	Field('other_info'),
	)

