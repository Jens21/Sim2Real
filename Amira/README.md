**Info**

This directory is for creating the train and test datasets with the amira blender rendering framework.

*Usage*

For usage type something like "sh 'run_script.sh'" or "sbatch 'run_script.sh'".

*Adapt to your needs*

Settings can be changed in the file 'run_script.sh' and the scenario selections can be changed in the file 'scenarios.py'.
If you want more Textures to be available, just add them into the 'Texture' folder.
If you want more distractor objects to be available, just add them into the 'Parts_Distractor' folder.

*It may be necessary to adjust the 'sys.path' in the 'scenarios.py' and 'script.py' files so that the modules can be found during the import. However, this depends on the exact installation of the python modules and is individual.*

**Consider the 'README.md' in 'Addional Files'.**
