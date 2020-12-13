from setuptools import setup, find_packages
setup(
	name='artcli',
	version='1.0.0',
	description='JFrog Artifactory CLI',
	author='Amit Michaely',
	author_email='amitm@jfrog.com',
	install_requiers=[''],
	packages=find_packages('src'),
	package_dir={'':'src'},
	entry_points={
		'console_scripts':[
			'artcli=cli:main',
		]
	}
)