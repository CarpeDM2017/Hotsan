#! hotsan2.7/bin/python2

"""
See http://www.flowdas.com/blog/%ED%8C%8C%EC%9D%B4%EC%8D%AC-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-%EC%8B%9C%EC%9E%91%ED%95%98%EA%B8%B0-setuptools/ 
"""

from setuptools import setup, find_packages

setup_requires = [
        ]

install_requires = [
        ]

dependency_links = [
        ]

setup(name='Hotsan',
      version='0,0.1',
      description='Hotsan',
      author='CarpeDM',
      author_email=None,
      packages=find_packages(),
      install_requires=install_requires,
      setup_requires=setup_requires,
      dependency_links=dependency_links,
      scripts=[],
      entry_points={
          'console_scripts':[
              'publish = null',
              'scan = null',
              'update = null'
              ]
          }
      )
