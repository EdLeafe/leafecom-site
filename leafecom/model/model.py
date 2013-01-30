import datetime
from sqlalchemy import schema, types
from sqlalchemy.dialects.mysql.base import MSTinyInteger, MSEnum
from sqlalchemy import orm

metadata = schema.MetaData()

def now():
    return datetime.datetime.now()

archive_table = schema.Table("archive", metadata,
    schema.Column("imsg", types.Integer, schema.Sequence("archive_seq_id", optional=True), primary_key=True),
    schema.Column("clist", types.Unicode(1)),
    schema.Column("csubject", types.Unicode(200)),
    schema.Column("cfrom", types.Unicode(200)),
    schema.Column("tposted", types.DateTime(), default=now),
    schema.Column("cmessageid", types.Unicode(128)),
    schema.Column("creplytoid", types.Unicode(128)),
    schema.Column("mtext", types.UnicodeText(), nullable=False)
)

files_table = schema.Table("files", metadata,
	schema.Column("iid", types.Integer, schema.Sequence("files_seq_id", optional=True), primary_key=True),
    schema.Column("ctype", types.Unicode(1), default="v"),
    schema.Column("cfile", types.Unicode(128)),
    schema.Column("ctitle", types.Unicode(60)),
    schema.Column("mdesc", types.Text(), nullable=False),
    schema.Column("cauthor", types.Unicode(60)),
    schema.Column("cauthoremail", types.Unicode(80)),
	schema.Column("ccosttype", MSEnum("f","s","c","d","g","l","m","o"), default="f"),
	schema.Column("ncost", types.Numeric(precision=4, scale=2, asdecimal=True), default = 0.00),
	schema.Column("csize", types.Unicode(10)),
    schema.Column("dlastupd", types.Date(), nullable=True),
    schema.Column("lpublish", MSTinyInteger, default=0)
)

med_table = schema.Table("medical_data", metadata,
	schema.Column("pkid", types.Integer, schema.Sequence("med_seq_id", optional=True), primary_key=True),
	schema.Column("date_taken", types.Date()),
	schema.Column("weight", types.Integer),
	schema.Column("systolic", types.Integer),
	schema.Column("diastolic", types.Integer)
)

# Define the classes
class Archive(object):
	pass
class Download(object):
	pass
class MedData(object):
	pass

# Map the class to the table
orm.mapper(Archive, archive_table)
orm.mapper(Download, files_table)
orm.mapper(MedData, med_table)
