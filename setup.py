from setuptools import setup

setup(name='tkterminal',
      version='0.1',
      description='Terminal',
      url='http://github.com/valkoapina/TkTerminal',
      author='valkoapina',
      author_email='valkoapina@gmail.com',
      license='MIT',
      packages=['tkterminal'],
      zip_safe=False,
      entry_points={
          'gui_scripts': [
              'tkterminal = tkterminal.__main__:main'
          ]
      },
      install_requires=[
          'pyserial',
      ]
      )
