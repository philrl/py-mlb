#!/usr/bin/env python
import distutils.core
import py_mlb

distutils.core.setup(
	name='py-mlb',
	version=py_mlb.__version__,
	packages = ['py_mlb'],
	author='Wells Oliver',
	author_email='wells@submute.net',
	url='http://blog.wellsoliver.com/',
	license='http://www.apache.org/licenses/LICENSE-2.0',
	description='Python abstraction layer for MLB.com''s unofficial "API"',
)
