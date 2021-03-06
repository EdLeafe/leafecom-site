#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

"""The application's model objects"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql.base import MSTinyInteger, MSEnum
from sqlalchemy import schema, types, orm

from leafecom.model import meta

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    ## Reflected tables must be defined and mapped here
    #global reflected_table
    #reflected_table = sa.Table("Reflected", meta.metadata, autoload=True,
    #                           autoload_with=engine)
    #orm.mapper(Reflected, reflected_table)
    #
    meta.Session.configure(bind=engine)
    meta.engine = engine


## Non-reflected tables may be defined and mapped at module level
#foo_table = sa.Table("Foo", meta.metadata,
#    sa.Column("id", sa.types.Integer, primary_key=True),
#    sa.Column("bar", sa.types.String(255), nullable=False),
#    )
#
#class Foo(object):
#    pass
#
#orm.mapper(Foo, foo_table)


## Classes for reflected tables may be defined here, but the table and
## mapping itself must be done in the init_model function
#reflected_table = None
#
#class Reflected(object):
#    pass


def now():
    return datetime.datetime.now()

archive_table = schema.Table("archive", meta.metadata,
    schema.Column("imsg", types.Integer, schema.Sequence("archive_seq_id", optional=True), primary_key=True),
    schema.Column("clist", types.Unicode(1)),
    schema.Column("csubject", types.Unicode(200)),
    schema.Column("cfrom", types.Unicode(200)),
    schema.Column("tposted", types.DateTime(), default=now),
    schema.Column("cmessageid", types.Unicode(128)),
    schema.Column("creplytoid", types.Unicode(128)),
    schema.Column("mtext", types.UnicodeText(), nullable=False)
)

files_table = schema.Table("files", meta.metadata,
	schema.Column("iid", types.Integer, schema.Sequence("files_seq_id", optional=True), primary_key=True),
    schema.Column("ctype", types.Unicode(1), default=u"v"),
    schema.Column("cfile", types.Unicode(128)),
    schema.Column("ctitle", types.Unicode(60)),
    schema.Column("mdesc", types.UnicodeText(), nullable=False),
    schema.Column("cauthor", types.Unicode(60)),
    schema.Column("cauthoremail", types.Unicode(80)),
	schema.Column("ccosttype", MSEnum("f","s","c","d","g","l","m","o"), default="f"),
	schema.Column("ncost", types.Numeric(precision=4, scale=2, asdecimal=True), default = 0.00),
	schema.Column("csize", types.Unicode(10)),
    schema.Column("dlastupd", types.Date(), nullable=True),
    schema.Column("lpublish", MSTinyInteger, default=0),
    schema.Column("uploaded", MSTinyInteger, default=0)
)

med_table = schema.Table("medical_data", meta.metadata,
	schema.Column("pkid", types.Integer, schema.Sequence("med_seq_id", optional=True), primary_key=True),
	schema.Column("date_taken", types.Date()),
	schema.Column("weight", types.Integer),
	schema.Column("systolic", types.Integer),
	schema.Column("diastolic", types.Integer)
)

feedback_table = schema.Table("feedback", meta.metadata,
	schema.Column("pkid", types.Integer, schema.Sequence("fb_med_seq_id", optional=True), primary_key=True),
	schema.Column("received", types.DateTime(), default=now),
	schema.Column("src", types.Unicode),
	schema.Column("campaign", types.Unicode),
	schema.Column("comment", types.UnicodeText)
)


# Define the classes
class Archive(object):
	pass
class Download(object):
	pass
class MedData(object):
	pass
class Feedback(object):
	pass

# Map the class to the table
orm.mapper(Archive, archive_table)
orm.mapper(Download, files_table)
orm.mapper(MedData, med_table)
orm.mapper(Feedback, feedback_table)
