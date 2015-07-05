

db.define_table('page_vists',
	Field('counter', 'integer'),
	Field('last_visited','datetime'),
	Field('args'),
	Field('vars'),
	)