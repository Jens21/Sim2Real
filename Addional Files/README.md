**Instructions**

This directory stores the files of the amira blender rendering framework that have to be added. Simply add the given files and you are ready to use Sim2Real.

| file | location |
| :--: | :------: |
|sim2real_scenarios.py | PATH_TO_AMIRA/amira_blender_rendering/src/amira_blender_rendering/scenes/sim2real_scenarios.py |
| rendermanager.py | PATH_TO_AMIRA/amira_blender_rendering/src/amira_blender_rendering/scenes/rendermanager.py |
|compositor_renderedobjects.py | PATH_TO_AMIRA/amira_blender_rendering/src/amira_blender_rendering/nodes/compositor_renderedobjects.py |
|interfaces.py | PATH_TO_AMIRA/amira_blender_rendering/src/amira_blender_rendering/interfaces.py |
|geometry.py | PATH_TO_AMIRA/amira_blender_rendering/src/amira_blender_rendering/math/geometry.py |

*It may be necessary to adjust the 'sys.path' in the 'scenarios.py' and 'script.py' files so that the modules can be found during the import. However, this depends on the exact installation of the Python modules and is individual.*
