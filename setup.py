from cx_Freeze import setup, Executable

""" Это скрипт для сборки дистрибутива. Сборка проекта выполняется утилитой cx_Freeze.
    Команда для сборки:
    python setup.py build
"""
base = "Win32GUI"

addtional_mods = ['numpy.core._methods', 'numpy.lib.format']
setup(name="cluster analysis",
      version="0.1",
      description="distributive",
      options={'build_exe': {'includes': addtional_mods}},
      executables=[Executable(
          script="main.py",
          base=base,
          targetName="ClusterAnalysis2.exe",
          icon="icon\\app_icon.ico"
      )])
