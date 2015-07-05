


db.define_table('page_visit_count',
	Field('page_name'),
	Field('counter', 'integer'),
	)

db.define_table('page_visit_data',
	Field('last_visited','datetime'),
	Field('args'),
	Field('vars'),
	)