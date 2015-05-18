__author__ = 'snownettle'
import cProfile
import re
cProfile.run('re.compile("foo|bar")')
