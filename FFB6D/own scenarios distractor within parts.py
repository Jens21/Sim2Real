#!/usr/bin/env python

# Copyright (c) 2020 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# <https://github.com/boschresearch/amira-blender-rendering>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This file implements generation of datasets for workstation scenarios. The file
depends on a suitable workstation scenarion blender file such as
worstationscenarios.blend.
"""

import bpy
import os
import pathlib
from mathutils import Vector
import numpy as np
import random
from math import ceil, log
import sys  #TODO, remove me
from datetime import datetime   #TODO, remove me
import time     #TODO, remove me
import mathutils
from math import radians
from math import degrees

from amira_blender_rendering.utils import camera as camera_utils
from amira_blender_rendering.utils.io import expandpath
from amira_blender_rendering.utils.logging import get_logger, add_file_handler
from amira_blender_rendering.datastructures import Configuration
from amira_blender_rendering.dataset import get_environment_textures, build_directory_info, dump_config
import amira_blender_rendering.scenes as abr_scenes
import amira_blender_rendering.math.geometry as abr_geom
import amira_blender_rendering.utils.blender as blnd
import amira_blender_rendering.interfaces as interfaces
from amira_blender_rendering.abc_importer import ABCImporter
from amira_blender_rendering.utils.annotation import ObjectBookkeeper

_scene_name = 'OwnScenariosDistractorWithinParts'

@abr_scenes.register(name=_scene_name, type='config')
class OwnScenariosDistractorWithinPartsConfiguration(abr_scenes.BaseConfiguration):
    """This class specifies all configuration options for OwnScenariosDistractorWithinParts"""

    def __init__(self):
        super(OwnScenariosDistractorWithinPartsConfiguration, self).__init__()
        np.random.seed(int(112345))
        print("OwnScenariosDistractorWithinPartsConfiguration")

        # specific scene configuration
        self.add_param('scene_setup.blend_file', '$AMIRA_DATA_GFX/modeling/workstation_scenarios.blend',
                       'Path to .blend file with modeled scene')
        self.add_param('scene_setup.environment_textures', '$AMIRA_DATASETS/OpenImagesV4/Images',
                       'Path to background images / environment textures')
        self.add_param('scene_setup.cameras', ['CameraLeft', 'Camera', 'CameraRight'], 'Cameras to render')
        self.add_param('scene_setup.forward_frames', 15, 'Number of frames in physics forward-simulation')

        # specific parts configuration. This is just a dummy entry for purposes
        # of demonstration and help message generation
        # self.add_param(
        #     'parts.example_dummy',
        #     '/path/to/example_dummy.blend',
        #     'Path to additional blender files containing invidual parts. Format: partname = /path/to/blendfile.blend')
        # self.add_param(
        #     'parts.ply.example_dummy',
        #     '/path/to/example_dummy.ply',
        #     'Path to PLY files containing part "example_dummy". Format: ply.partname = /path/to/blendfile.ply')
        # self.add_param(
        #     'parts.ply_scale.example_dummy',
        #     [1.0, 1.0, 1.0],
        #     'Scaling factor in X, Y, Z dimensions of part "example_dummy". Format must be a list of 3 floats.')

        # specific scenario configuration
        self.add_param('scenario_setup.scenario', 0, 'Scenario to render')
        self.add_param('scenario_setup.target_objects', [],
                       'List of objects to drop in the scene for which annotated info are stored')
        self.add_param('scenario_setup.distractor_objects', [],
                       'List of objects to drop in the scene for which info are NOT stored')
        self.add_param('scenario_setup.abc_objects', [], 'List of all ABC-Dataset objects to drop in environment')
        self.add_param('scenario_setup.num_abc_colors', 3, 'Number of random metallic materials to generate')
    
        #additionally added
        #######################################################################################
        self.add_param('scenario_setup.distractor_textures_dir', "", 'Directory of textures for distractor objects')
        #######################################################################################
        
        # multiview configuration (if implemented)
        self.add_param('multiview_setup.mode', '',
                       'Selected mode to generate view points, i.e., random, bezier, viewsphere')
        self.add_param('multiview_setup.mode_config', Configuration(), 'Mode specific configuration')
        self.add_param('multiview_setup.offset', True,
                       'If False, multi views are not offset with initial camera location. Default: True')
        
        # specific debug config
        self.add_param('debug.plot', False, 'If True, in debug mode, enable simple visual debug')
        self.add_param('debug.plot_axis', False, 'If True, in debug-plot mode, plot camera coordinate systems')
        self.add_param('debug.scatter', False, 'If True, in debug mode-plot, enable scatter plot')
        self.add_param('debug.save_to_blend', False, 'If True, in debug mode, log to .blend files')
        # HINT: these object lists above are parsed as strings, later on split with "," separator


@abr_scenes.register(name=_scene_name, type='scene')
class OwnScenariosDistractorWithinParts(interfaces.ABRScene):
    """base class for all workstation scenarios"""
    
    def __init__(self, **kwargs):
        super(OwnScenariosDistractorWithinParts, self).__init__()
        self.logger = get_logger()
        add_file_handler(self.logger)

        print("Begin Own Scenario="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

        # we do composition here, not inheritance anymore because it is too
        # limiting in its capabilities. Using a render manager is a better way
        # to handle compositor nodes
        self.renderman = abr_scenes.RenderManager(used_own_scenarios=True)

        # extract configuration, then build and activate a split config
        self.config = kwargs.get('config', OwnScenariosDistractorWithinPartsConfiguration())
        if self.config.dataset.scene_type.lower() != 'OwnScenariosDistractorWithinParts'.lower():
            raise RuntimeError(
                f"Invalid configuration of scene type {self.config.dataset.scene_type} for class OwnScenariosDistractorWithinParts")
        
        # determine if we are rendering in multiview mode
        self.render_mode = kwargs.get('render_mode', 'default')
        if self.render_mode not in ['default', 'multiview']:
            self.logger.warn(f'render mode "{self.render_mode}" not supported. Falling back to "default"')
            self.render_mode = 'default'
        
        # we might have to post-process the configuration
        self.postprocess_config()        
        print("postprocess_config="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

        # setup directory information for each camera
        self.setup_dirinfo()
        print("setup_dirinfo="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

        # setup the scene, i.e. load it from file
        self.setup_scene()
        print("setup_scene="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

        # setup the renderer. do this _AFTER_ the file was loaded during
        # setup_scene(), because otherwise the information will be taken from
        # the file, and changes made by setup_renderer ignored
        self.renderman.setup_renderer(self.config.render_setup.integrator, self.config.render_setup.denoising,
                                      self.config.render_setup.samples, self.config.render_setup.motion_blur)
        print("setup_renderer="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

        # grab environment textures
        self.setup_environment_textures()
        print("setup_environment_textures="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

        # setup all camera information according to the configuration
        self.setup_cameras()
        print("setup_cameras="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

        # setup global render output configuration
        self.setup_render_output()
        print("setup_render_output="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

        # populate the scene with objects
        self.objs = self.setup_objects(self.config.scenario_setup.target_objects,
                                       bpy_collection='TargetObjects',
                                       abc_objects=self.config.scenario_setup.abc_objects,
                                       abc_bpy_collection='ABCObjects')
        self.distractors = self.setup_objects(self.config.scenario_setup.distractor_objects,
                                              bpy_collection='DistractorObjects')
        print("setup_objects="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
        
        # finally, setup the compositor
        self.setup_compositor()
        print("setup_compositor="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

    def postprocess_config(self):
        # depending on the rendering mode (standard or multiview), determine number of images
        if self.render_mode == 'default':
            # in default mode (i.e., single view), image_count control the number of images (hence scene) to render
            self.config.dataset.view_count = 1
            self.config.dataset.scene_count = self.config.dataset.image_count
        elif self.render_mode == 'multiview':
            # in multiview mode: image_count = scene_count * view_count
            self.config.dataset.scene_count = max(1, self.config.dataset.scene_count)
            self.config.dataset.view_count = max(1, self.config.dataset.view_count)
            self.config.dataset.image_count = self.config.dataset.scene_count * self.config.dataset.view_count
        else:
            self.logger.error(f'render mode {self.render_mode} currently not supported')
            raise ValueError(f'render mode {self.render_mode} currently not supported')

        # convert (PLY and blend) scaling factors from str to list of floats
        def _convert_scaling(key: str, config):
            """
            Convert scaling factors from string to (list of) floats
            
            Args:
                key(str): string to identify prescribed scaling
                config(Configuration): object to modify

            Return:
                none: directly update given "config" object
            """
            if key not in config:
                return

            for part in config[key]:
                vs = config[key][part]
                # split strip and make numeric
                vs = [v.strip() for v in vs.split(',')]
                vs = [float(v) for v in vs]
                # if single value given, apply to all axis
                if len(vs) == 1:
                    vs *= 3
                config[key][part] = vs

        _convert_scaling('ply_scale', self.config.parts)
        _convert_scaling('blend_scale', self.config.parts)

    def setup_dirinfo(self):
        """Setup directory information for all cameras.

        This will be required to setup all path information in compositor nodes
        """
        # compute directory information for each of the cameras
        self.dirinfos = list()
        for cam in self.config.scene_setup.cameras:
            # paths are set up as: base_path + CameraName
            camera_base_path = f"{self.config.dataset.base_path}-{cam}"
            dirinfo = build_directory_info(camera_base_path)
            self.dirinfos.append(dirinfo)

    def setup_scene(self):
        """Set up the entire scene.

        Here, we simply load the main blender file from disk.
        """
        bpy.ops.wm.open_mainfile(filepath=expandpath(self.config.scene_setup.blend_file))
        # we need to hide all dropboxes and dropzones in the viewport, otherwise
        # occlusion testing will not work, because blender's ray_cast method
        # returns hits no empties!
        self.logger.info("Hiding all dropzones from viewport")
        bpy.data.collections['Dropzones'].hide_viewport = True

    def setup_render_output(self):
        """setup render output dimensions. This is not set for a specific camera,
        but in renders render environment.

        Note that this should be called _after_ cameras were set up, because
        their setup might influence these values.
        """

        # first set the resolution if it was specified in the configuration
        if (self.config.camera_info.width > 0) and (self.config.camera_info.height > 0):
            bpy.context.scene.render.resolution_x = self.config.camera_info.width
            bpy.context.scene.render.resolution_y = self.config.camera_info.height

        # Setting the resolution can have an impact on the calibration matrix
        # that was used for rendering. Hence, we will store the effective
        # calibration matrix K alongside. Because we use identical cameras, we
        # can extract this from one of the cameras
        self.get_effective_intrinsics()

    def get_effective_intrinsics(self):
        """Get the effective intrinsics that were used during rendering.

        This function will copy original values for intrinsic, sensor_width, and
        focal_length, and fov, to the configuration an prepend them with 'original_'. This
        way, they are available in the dataset later on
        """

        cam_str = self.config.scene_setup.cameras[0]
        cam_name = self.get_camera_name(cam_str)
        cam = bpy.data.objects[cam_name].data

        # get the effective intrinsics
        effective_intrinsic = camera_utils.get_intrinsics(bpy.context.scene, cam)
        # store in configuration (and backup original values)
        if self.config.camera_info.intrinsic is not None:
            self.config.camera_info.original_intrinsic = self.config.camera_info.intrinsic
        else:
            self.config.camera_info.original_intrinsic = ''
        self.config.camera_info.intrinsic = list(effective_intrinsic)

    def setup_cameras(self):
        """Set up all cameras.

        Note that this does not select a camera for which to render. This will
        be selected elsewhere.
        """
        scene = bpy.context.scene
        for cam in self.config.scene_setup.cameras:
            # first get the camera name. this depends on the scene (blend file)
            # and is of the format CameraName.XXX, where XXX is a number with
            # leading zeros
            cam_name = self.get_camera_name(cam)
            # select the camera. Blender often operates on the active object, to
            # make sure that this happens here, we select it
            blnd.select_object(cam_name)
            # modify camera according to the intrinsics
            blender_camera = bpy.data.objects[cam_name].data
            # set the calibration matrix
            camera_utils.set_camera_info(scene, blender_camera, self.config.camera_info)

    def setup_objects(self, objects: list, bpy_collection: str = 'TargetObjects',
                      abc_objects: list = None, abc_bpy_collection: str = 'ABCObjects'):
        """This method populates the scene with objects.

        Object types and number of objects will be taken from the configuration.
        The format to specify objects is
            ObjectType:Number
        where ObjectType should be the name of an object that exists in the
        blender file, and number indicates how often the object shall be
        duplicated.

        Args:
            objects(list): list of ObjectType:Number to setup
        
        Optional Args:
            bpy_collection(str): Name of bpy collection the given objects are
                linked to in the .blend file. Default: TargetObjects
                If the given objects are non-target (i.e., they populate the scene but
                no information regarding them are stored) use a different collection.
            abc_objects(list): list of ABC objects to add the list of targets
            abc_bpy_collection(str): Name of bpy collection for ABC objects

        Returns:
            objs(list): list of dict to handle desired objects
        """
        rgb_shape = (self.config.camera_info.height, self.config.camera_info.width, 3)
        # let's start with an empty list
        objs = []
        obk = ObjectBookkeeper()

        # extract all objects from the configuration. An object has a certain
        # type, as well as an own id. this information is storeed in the objs
        # list, which contains a dict. The dict contains the following keys:
        #       id_mask             used for mask computation, computed below
        #       object_class_name   type-name of the object
        #       object_class_id     model type ID (simply incremental numbers)
        #       object_id           instance ID of the object
        #       bpy                 blender object reference
        for class_id, obj_spec in enumerate(objects):
            class_name, obj_count = obj_spec.split(':')

            # here we distinguish if we copy a part from the proto objects
            # within a scene, or if we have to load it from file
            is_proto_object = not class_name.startswith('parts.')
            if not is_proto_object:
                # split off the prefix for all files that we load from blender
                class_name = class_name[6:]

            # TODO: file loading happens only very late in this loop. This might
            #       be an issue for large object counts and could be changed to
            #       load-once copy-often.
            for j in range(int(obj_count)):
                # First, deselect everything
                bpy.ops.object.select_all(action='DESELECT')
                if is_proto_object:
                    # duplicate proto-object
                    blnd.select_object(class_name)
                    bpy.ops.object.duplicate()
                    new_obj = bpy.context.object
                else:
                    # we need to load this object from file. This could be
                    # either a blender file, or a PLY file
                    blendfile = expandpath(self.config.parts[class_name], check_file=False)
                    if os.path.exists(blendfile):
                        # this is a blender file, so we should load it
                        # we can now load the object into blender
                        # try-except logic to handle objects from same blend file but different
                        # class names to allow loading same objects with e.g., different scales
                        try:
                            bpy_obj_name = self.config.parts['name'][class_name]
                        except KeyError:
                            bpy_obj_name = class_name
                        blnd.append_object(blendfile, bpy_obj_name)
                        # NOTE: bpy.context.object is **not** the object that we are
                        # interested in here! We need to select it via original name
                        # first, then we rename it to be able to select additional
                        # objects later on
                        new_obj = bpy.data.objects[bpy_obj_name]
                        new_obj.name = f'{class_name}.{j:03d}'
                        # try to rescale object according to its blend_scale if given in the config
                        try:
                            new_obj.scale = Vector(self.config.parts.blend_scale[class_name])
                            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True, properties=False)
                        except KeyError:
                            # log and keep going
                            self.logger.info(f'No blend_scale for obj {class_name} given. Skipping!')
                    else:
                        # no blender file given, so we will load the PLY file
                        # NOTE: no try-except logic for ply since we are not binded to object names as for .blend
                        ply_path = expandpath(self.config.parts.ply[class_name], check_file=True)
                        bpy.ops.import_mesh.ply(filepath=ply_path)
                        # here we can use bpy.context.object!
                        new_obj = bpy.context.object
                        new_obj.name = f'{class_name}.{j:03d}'
                        # try to rescale object according to its ply_scale if given in the config
                        try:
                            new_obj.scale = Vector(self.config.parts.ply_scale[class_name])
                            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True, properties=False)
                        except KeyError:
                            # log and keep going
                            self.logger.info(f'No ply_scale for obj {class_name} given. Skipping!')

                # move object to collection: in case of debugging
                try:
                    collection = bpy.data.collections[bpy_collection]
                except KeyError:
                    collection = bpy.data.collections.new(bpy_collection)
                    bpy.context.scene.collection.children.link(collection)

                if new_obj.name not in collection.objects:
                    collection.objects.link(new_obj)

                # bookkeep instance
                obk.add(class_name)

                # append all information
                objs.append({
                    'id_mask': '',
                    'object_class_name': class_name,
                    'object_class_id': class_id,
                    'object_id': j,
                    'bpy': new_obj,
                    'visible': None,
                    'dimensions': rgb_shape  # TODO: this is not implemented yet
                })

        # Adding ABC objects
        if abc_objects is None or not len(abc_objects):
            self.logger.info("Config file does NOT include ABC-Dataset objects")
        else:
            n_materials = int(self.config.scenario_setup.num_abc_colors)
            self.logger.info(f"making {n_materials} random metallic materials")
            abc_importer = ABCImporter(n_materials=n_materials)

            for class_id, obj_spec in enumerate(abc_objects):
                _class_name, obj_count = obj_spec.split(':')

                for j in range(int(obj_count)):
                    bpy.ops.object.select_all(action='DESELECT')

                    obj_handle, class_name = abc_importer.import_object(_class_name)

                    if obj_handle is None:
                        continue

                    # move object to collection: in case of debugging
                    try:
                        collection = bpy.data.collections[abc_bpy_collection]
                    except KeyError:
                        collection = bpy.data.collections.new(abc_bpy_collection)
                        bpy.context.scene.collection.children.link(collection)

                    if obj_handle.name not in collection.objects:
                        collection.objects.link(obj_handle)

                    # bookkeep instance
                    obk.add(class_name)

                    # append to list of objects
                    objs.append({
                        'id_mask': '',
                        'object_class_name': class_name,
                        'object_class_id': obk[class_name]["id"],
                        'object_id': obk[class_name]["instances"] - 1,
                        'bpy': obj_handle,
                        'visible': None,
                        'dimensions': rgb_shape  # TODO: not implemented yet
                    })

        # build masks id for compositor of the format _N_M, where N is the model
        # id, and M is the object id
        w_class = ceil(log(len(obk), 10)) if len(obk) else 0  # format width for number of model types
        
        # additionally added
        ###################################################################################
        """
        added_layers=[]
        added_collections=[]
        """
        ###################################################################################
        
        for i, obj in enumerate(objs):
            w_obj = ceil(log(obk[obj['object_class_name']]['instances'], 10))  # format width for same model
            id_mask = f"_{obj['object_class_id']:0{w_class}}_{obj['object_id']:0{w_obj}}"
            obj['id_mask'] = id_mask
            
        # additionally added
        ###################################################################################
        """
            if bpy_collection=='TargetObjects':
                layer_per_object=bpy.context.scene.view_layers.new(name='layer_'+obj['bpy'].name)
                added_layers.append(layer_per_object)
                layer_per_object.use_pass_object_index=True
                collection_per_layer=bpy.data.collections.new(name='collection_'+obj['bpy'].name)
                added_collections.append(collection_per_layer)
                collection_per_layer.objects.link(bpy.data.objects[obj['bpy'].name])
                bpy.context.scene.collection.children.link(collection_per_layer)
                bpy.context.layer_collection.children['collection_'+obj['bpy'].name].exclude = True
            bpy.context.collection.objects.unlink(bpy.data.objects[obj['bpy'].name])
            
         
        for j, layer in enumerate(added_layers):
            layer.layer_collection.children['TargetObjects'].exclude=True
            layer.layer_collection.children['Dropzones'].exclude=True
            
            for i, collec in enumerate(added_collections):
                if(layer.name.replace('layer_','')!=collec.name.replace('collection_','')):
                    layer.layer_collection.children[collec.name].exclude=True
                    
        if bpy.context.layer_collection.children.get('DistractorObjects'):
            for i, layer in enumerate(bpy.context.scene.view_layers):
                if layer.name !='View Layer':
                    layer.layer_collection.children['DistractorObjects'].exclude=True
        """
        ###################################################################################
    
        return objs

    def setup_compositor(self):
        self.renderman.setup_compositor(self.objs, color_depth=self.config.render_setup.color_depth)

    def setup_environment_textures(self):
        # get list of environment textures
        self.environment_textures = get_environment_textures(self.config.scene_setup.environment_textures)

    # additionally added
    ###################################################################################
    #def randomize_object_transforms(self, objs: list):
    def randomize_object_transforms(self, objs : list, distractors : list):
    ###################################################################################
        """move all objects to random locations within their scenario dropzone,
        and rotate them.
        
        Args:
            objs(list): list of objects whose pose is randomized
            
        NOTE: the list must be mutable since we directly modify the objects w/o returning them
        """
        # we need #objects * (3 + 3)  many random numbers, so let's just grab them all
        # at once
        
        # additionally added
        ###################################################################################
        #rnd = np.random.uniform(size=(len(objs), 3))
        #rnd_rot = np.random.rand(len(objs), 3)))
        rnd_rot = np.random.rand(len(objs)+len(distractors), 3)
        ###################################################################################

        # now, move each object to a random location (uniformly distributed) in
        # the scenario-dropzone. The location of a drop box is its centroid (as
        # long as this was not modified within blender). The scale is the scale
        # along the axis in one direction, i.e. the full extend along this
        # direction is 2 * scale.
        
        dropbox = f"Dropbox.{self.config.scenario_setup.scenario:03}"
        drop_location = bpy.data.objects[dropbox].location
        drop_scale = bpy.data.objects[dropbox].scale
        
        # additionally added
        ###################################################################################
        if len(distractors) !=0:
            dropbox_distractor = f"DropboxDistractor.{self.config.scenario_setup.scenario:03}"
            drop_distrac_location = bpy.data.objects[dropbox_distractor].location
            drop_distrac_scale = bpy.data.objects[dropbox_distractor].scale
        ###################################################################################

        # additionally added
        ###################################################################################
        #for i, obj in enumerate(objs):
        M=np.random.uniform(size=2)  
        E=[0]*len(M)
        p=[0]*len(M)
        q=[0]*len(M)
        rnd=[0]*len(M)  
        
        for i in range(len(M)):
            if M[i]>0.5:
                E[i]=M[i]-0.3*np.random.uniform(0,max(0.5,M[i])-min(0.5,M[i]))
            else:
                E[i]=M[i]+0.3*np.random.uniform(0,max(0.5,M[i])-min(0.5,M[i]))
                
            
            p[i]=E[i]*(1-2*M[i])/(E[i]-M[i])    
            q[i]=p[i]/E[i]-p[i]
        
        x=np.random.randint(2)
        height_map_size=100
        height_map=np.zeros(shape=(height_map_size,height_map_size))
        
        for a, obj in enumerate(objs+distractors):
        ###################################################################################
            if obj['bpy'] is None:
                continue

            # additionally added
            ###################################################################################
            obj['bpy'].rigid_body.linear_damping=0.04
            obj['bpy'].rigid_body.angular_damping=0.1
            
            for i in range(0, bpy.context.scene.frame_end, 40):
                obj['bpy'].rigid_body.enabled=False
                obj['bpy'].keyframe_insert(data_path="rigid_body.enabled", frame=i)
                
                obj['bpy'].rigid_body.enabled=True
                obj['bpy'].keyframe_insert(data_path="rigid_body.enabled", frame=i+1)
            #obj['bpy'].location.x = drop_location.x + (rnd[i, 0] - .5) * 2.0 * drop_scale[0]
            #obj['bpy'].location.y = drop_location.y + (rnd[i, 1] - .5) * 2.0 * drop_scale[1]
            #obj['bpy'].location.z = drop_location.z + (rnd[i, 2] - .5) * 2.0 * drop_scale[2]
            if x==1 and False: 
                if obj in objs: #eig ist keine Unterscheidung nötig, da die Dropzone für Distractor und target objekte dieselbe ist
                    for i in range(len(M)):
                        value=np.random.uniform(1,5)
                        rnd[i] = np.random.beta(a=value,b=value)
                        #rnd[i] = np.random.beta(a=p[i],b=q[i])
                        
                    rnd[0]=rnd[0]*2.0-1.0
                    rnd[1]=rnd[1]*2.0-1.0
                    #rnd[2]=rnd[2]*2.0-1.0
                                 
                    obj['bpy'].location.x=(0.32-obj['bpy'].dimensions.x/2)*rnd[0]+0 #that the object don't interfere with the collision boxes on the side
                    obj['bpy'].location.y=(0.24-obj['bpy'].dimensions.y/2)*rnd[1]+0
                    obj['bpy'].location.z=0.3+float(a)*0.25
                else:
                    for i in range(len(M)):
                        rnd[i] = np.random.beta(a=p[i],b=q[i])
                        
                    rnd[0]=rnd[0]*2.0-1.0
                    rnd[1]=rnd[1]*2.0-1.0
                    #rnd[2]=rnd[2]*2.0-1.0
                                 
                    obj['bpy'].location.x=(0.32-obj['bpy'].dimensions.x/2)*rnd[0]+0
                    obj['bpy'].location.y=(0.24-obj['bpy'].dimensions.y/2)*rnd[1]+0
                    obj['bpy'].location.z=0.3+float(a)*0.25
                ###################################################################################
                #obj['bpy'].rotation_euler = Vector((rnd_rot[a, :] * np.pi))
                obj['bpy'].rotation_euler[2] = np.random.uniform()* np.pi
                if np.random.uniform()>0.8:
                    obj['bpy'].rotation_euler[0] = np.random.uniform()* np.pi
                    obj['bpy'].rotation_euler[1] = np.random.uniform()* np.pi
            
            else:
                size_x=0.36*0.6
                size_y=0.27*0.6
                
                obj['bpy'].rotation_euler[2] = np.random.uniform()* 2*np.pi
                
                obj['bpy'].location.x=(np.random.uniform()*2-1)*size_x
                obj['bpy'].location.y=(np.random.uniform()*2-1)*size_y
                
                vert=obj['bpy'].data.vertices
                loc=obj['bpy'].location
                coords=[(obj['bpy'].matrix_world.to_3x3() @ v.co) for v in vert]
                
                min_coords=np.zeros(3)
                max_coords=np.zeros(3)
                for coord in coords:
                    min_coords=np.minimum(min_coords,coord)
                    max_coords=np.maximum(max_coords,coord)
                
                from_x=max(0,int(np.floor((obj['bpy'].location.x-0.001+min_coords[0]+size_x)/(2*size_x)*height_map_size)))
                to_x=min(99,int(np.ceil((obj['bpy'].location.x+0.001+max_coords[0]+size_x)/(2*size_x)*height_map_size)))
                
                from_y=max(0,int(np.floor((obj['bpy'].location.y-0.001+min_coords[1]+size_y)/(2*size_y)*height_map_size)))
                to_y=min(99,int(np.ceil((obj['bpy'].location.y+0.001+max_coords[1]+size_y)/(2*size_y)*height_map_size)))
                
                min_height=0
                for x in range(from_x,to_x+1):
                    for y in range(from_y,to_y+1):
                        min_height=max(min_height,height_map[x,y])
                
                obj['bpy'].location.z=min_height+0.001-min_coords[2]

                for x in range(from_x,to_x+1):
                    for y in range(from_y,to_y+1):
                        height_map[x,y]=obj['bpy'].location.z+max_coords[2]

            self.logger.info(f"Object {obj['object_class_name']}: {obj['bpy'].location}, {obj['bpy'].rotation_euler}")

        # update the scene. unfortunately it doesn't always work to just set
        # the location of the object without recomputing the dependency
        # graph
        
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()

    def randomize_environment_texture(self):
        # set some environment texture, randomize, and render
        env_txt_filepath = expandpath(random.choice(self.environment_textures))
        self.renderman.set_environment_texture(env_txt_filepath)

    def forward_simulate(self):
        self.logger.info(f"forward simulation of {self.config.scene_setup.forward_frames} frames")
        scene = bpy.context.scene
        print("self.config.scene_setup.forward_frames="+str(self.config.scene_setup.forward_frames),flush=True,file=sys.stderr)
        for i in range(self.config.scene_setup.forward_frames):
            scene.frame_set(i + 1)

    def activate_camera(self, cam_name: str):
        """Activate selected camera:
        
        Args:
            cam_name(str): actual name of selected bpy camera object
        """
        bpy.context.scene.camera = bpy.context.scene.objects[cam_name]

    def set_camera_location(self, cam_name: str, location):
        """
        Set location of selected camera
        
        Args:
            cam_name(str): actual name of selected bpy camera object
            location(array): camera location
        """
        # select the camera. Blender often operates on the active object, to
        # make sure that this happens here, we select it
        blnd.select_object(cam_name)
        # set camera location
        bpy.data.objects[cam_name].location = location

    def get_camera_name(self, cam_str):
        """Get camera name from suffix string and scenario number. This depends on the loaded blend file"""
        return f"{cam_str}.{self.config.scenario_setup.scenario:03}"

    def test_visibility(self, camera_name: str, locations: np.array):
        """Test whether given camera sees all target objects
        and store visibility level/label for each target object
        
        Args:
            camera(str): name of bpy selected camera object
            locations(list): list of locations to check. If None, check current camera location
        """
        # # convert to list
        # cameras = cameras if isinstance(cameras, list) else [cameras]

        camera = bpy.context.scene.objects[camera_name]

        # make sure to work with multi-dim array
        if locations.shape == (3,):
            locations = np.reshape(locations, (1, 3))
        
        # loop over locations
        for location in locations:
            #camera.location = location #additionally added
            
            any_not_visible_or_occluded = False
            for obj in self.objs:
                not_visible_or_occluded,n_pix_not_visible, n_pix_occluded, n_pix_not_visible_and_occluded, n_pix = abr_geom.test_occlusion_own(
                    bpy.context.scene,
                    bpy.context.scene.view_layers['View Layer'],
                    camera,
                    obj['bpy'],
                    bpy.context.scene.render.resolution_x,
                    bpy.context.scene.render.resolution_y,
                    require_all=False,
                    origin_offset=0.01)
                # store object visitibility info
                obj['visible'] = not not_visible_or_occluded
                #additionally added
                obj['n_pix_not_visible']=n_pix_not_visible
                obj['n_pix_occluded']=n_pix_occluded
                obj['n_pix_not_visible_and_occluded']=n_pix_not_visible_and_occluded
                obj['n_pix']=n_pix
                #additionally added
                if not_visible_or_occluded:
                    self.logger.warn(f"object {obj} not visible or occluded")
                
                any_not_visible_or_occluded = any_not_visible_or_occluded or not_visible_or_occluded
                    
            # if any_not_visibile_or_occluded --> at least one object is not visible from one locaiton: return False
            if any_not_visible_or_occluded:
                return False

        # --> all objects are visible (from all locations): return True
        return True
    
    #additionally added
    #################################################################################
    def randomize_obj_texture(self, objs):
        if os.path.isdir(self.config.scenario_setup.distractor_textures_dir):
            i=0
            for obj in objs:
                file_texture=self.config.scenario_setup.distractor_textures_dir+str(np.random.choice(os.listdir(self.config.scenario_setup.distractor_textures_dir)))
            
                mat = bpy.data.materials.new(name="New_Mat"+str(i))
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes["Principled BSDF"]
                texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
                texImage.image = bpy.data.images.load(file_texture)
                mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

                ob = obj['bpy']

                # Assign it to object
                if ob.data.materials:
                    ob.data.materials[0] = mat
                else:
                    ob.data.materials.append(mat)
                        
                bpy.context.view_layer.objects.active = ob=obj['bpy']
                bpy.ops.object.editmode_toggle()
                #bpy.ops.uv.smart_project()
                bpy.ops.uv.cube_project(cube_size=1)
                bpy.ops.object.editmode_toggle()
                
                i+=1
    #################################################################################
    
    def squared_solver(self, a, b, c):
        sq=np.sqrt(b**2-4*a*c)
        x1=(-b+sq)/(2*a)
        x2=(-b-sq)/(2*a)
        
        return (x1,x2)
    
    def change_camera_location_randomly(self, dist, alpha_rad):
        #getting the closest point with a fake point
        point_to_test=np.array([0,-np.cos(alpha_rad)*10,np.sin(alpha_rad)*10])  
        closest_location=self.objs[0]['bpy'].matrix_world.to_translation()
        closest_dist=np.linalg.norm(point_to_test-closest_location)
        max_location=self.objs[0]['bpy'].matrix_world.to_translation()
        min_location=self.objs[0]['bpy'].matrix_world.to_translation()
        for i in range(1,len(self.objs)):
            loc=self.objs[i]['bpy'].matrix_world.to_translation()
            max_location=np.maximum(max_location,loc)
            min_location=np.minimum(min_location,loc)
            d=np.linalg.norm(point_to_test-loc)
            if d<closest_dist:
                closest_dist=d
                closest_location=loc
        
        mid_location=(max_location+min_location)/2
        
        m=point_to_test[2]/point_to_test[1]
        
        a=1+m**2
        b=-2*(closest_location[1]+m*closest_location[2])
        c=-dist**2+closest_location[1]**2+closest_location[2]**2
        (x1,x2)=self.squared_solver(a,b,c)
        
        y=min(x1,x2)
        z=m*y
        
        cam=bpy.data.objects[self.get_camera_name(self.config.scene_setup.cameras[0])]
        cam.matrix_world.translation=(0,y,z)
        
        bpy.context.view_layer.update()
                
        self.change_where_camera_is_looking(mid_location)
        
        self.change_cameras_location_within_bounds()
       
    def change_cameras_location_within_bounds(self):
        
        def ebene_gerade_coords(a,b,c,point,cam_loc):
            
            solution=np.linalg.solve(np.transpose(np.array([b-a,c-a,cam_loc-point])),np.array(cam_loc-a))
            
            return solution
            
        def get_lambda(a,b,c,points, cam_loc):
            min_dist=np.linalg.norm(cam_loc-points[0])
            point=points[0]
            for i in range(1,len(points)):                
                dist=np.linalg.norm(cam_loc-points[i])
                if dist<min_dist:
                    point=points[i]
                    min_dist=dist

            solutions=ebene_gerade_coords(a,b,c,point,cam_loc)
            intersection= cam_loc+(point-cam_loc)*solutions[2]
            dist_intersection=np.linalg.norm(cam_loc-intersection)
            
            return min_dist/dist_intersection
            
        def ebene(a,b,c,x):
            return a+(b-a)*x[0]+(c-a)*x[1]
    
        def mini(points):
            p=points[0]
            for i in range(1,len(points)):
                p=np.minimum(points[i],p)
                
            return p
    
        def maxi(points):
            p=points[0]
            for i in range(1,len(points)):
                p=np.maximum(points[i],p)
                
            return p
    
        cam=bpy.context.scene.camera
        cam_loc=np.array(cam.matrix_world.to_translation())
        
        #frame = cam.data.view_frame(scene=bpy.context.scene)
        frame = cam.data.view_frame(scene=bpy.context.scene)
        # move from object-space into world-space 
        frame = [(cam.matrix_world @ Vector([v[0],v[1],v[2],1])).xyz for v in frame]  
        
        top_right_point=np.array(frame[0])
        bottom_right_point=np.array(frame[1])
        bottom_left_point= np.array(frame[2])
        top_left_point= np.array(frame[3])
           
        obj_points=[np.array(x['bpy'].matrix_world.to_translation()) for x in self.objs]
        lamb=get_lambda(top_left_point,top_right_point,bottom_left_point, obj_points, cam_loc)
        
        top_right_point=(top_right_point-cam_loc)*lamb+cam_loc
        bottom_left_point=(bottom_left_point-cam_loc)*lamb+cam_loc
        top_left_point=(top_left_point-cam_loc)*lamb+cam_loc
        bottom_right_point=(bottom_right_point-cam_loc)*lamb+cam_loc
        
        solutions=[np.linalg.solve(np.transpose(np.array([top_right_point-top_left_point,bottom_left_point-top_left_point,cam_loc-point])),np.array(cam_loc-top_left_point)) for point in obj_points]
        coords_2d=[sol[0:2] for sol in solutions]
                
        min_coords=mini(coords_2d)
        min_coords=np.maximum([0,0],min_coords)
        
        max_coords=maxi(coords_2d)
        max_coords=np.minimum([1,1], max_coords)
        
        top_left_sub_point=ebene(top_left_point,top_right_point,bottom_left_point,min_coords)
        bottom_right_sub_point=ebene(top_left_point,top_right_point,bottom_left_point,max_coords)
                
        rnd_right_left=np.random.uniform(-1+0.1+max_coords[0],min_coords[0]-0.1)
        rnd_up_down=np.random.uniform(-1+0.1+max_coords[1],min_coords[1]-0.1)
        
        length_vert=np.linalg.norm(top_right_point-top_left_point)  #y-Achse
        length_hor=np.linalg.norm(top_left_point-bottom_left_point) #x-Achse
        
        rnd_up_down*=length_hor
        rnd_right_left*=length_vert
        
        cam.matrix_world.translation+=(cam.matrix_world @ (Vector([rnd_right_left,0,0,0])+Vector([0,rnd_up_down,0,0]))).xyz
        
        bpy.context.view_layer.update()
               
    def change_where_camera_is_looking(self, look_at_point):   
        cam=bpy.data.objects[self.get_camera_name(self.config.scene_setup.cameras[0])]
        loc_camera = cam.matrix_world.to_translation()

        direction = look_at_point - loc_camera
           
        #z=np.arctan(-direction[0]/direction[1])
        x=np.arctan(np.sqrt(direction[0]**2+direction[1]**2)/-direction[2])-2*np.pi
            
        while x<0:
            x+=2*np.pi
            
        bpy.data.objects[self.get_camera_name(self.config.scene_setup.cameras[0])].rotation_euler[0]=x
        bpy.data.objects[self.get_camera_name(self.config.scene_setup.cameras[0])].rotation_euler[1]=0
        bpy.data.objects[self.get_camera_name(self.config.scene_setup.cameras[0])].rotation_euler[2]=0
        
        bpy.context.view_layer.update()
        
    def to_radian(self,x,y,z):
        def to_rad(d):
            return d/180.0*np.pi
            
        return (to_rad(x),to_rad(y),to_rad(z))
    
    def generate_dataset(self):
        """This will generate a multiview dataset according to the configuration that
        was passed in the constructor.
        """
        # The number of images in the dataset is controlled differently in case of default (singleview) vs multiview
        # rendering mode.
        # In default mode
        #   dataset.image_count controls the number of images
        #
        # In multiview mode
        #   dataset.image_count = dataset.scene_count * dataset.view_count
        #
        # In addition the [multiview] config section defines specific configuration such as
        #
        #   [multiview_setup]
        #   mode(str): how to generate camera locations for multiview. E.g., viewsphere, bezier, random
        #   mode_cfg(dict-like/config): additional mode specific configs
        print("begin generate dataset="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
        
        # filename setup
        if self.config.dataset.image_count <= 0:
            return False
        scn_format_width = int(ceil(log(self.config.dataset.scene_count, 10)))
        
        # extract actual bpy object camera names and generate locations
        camera_names = [self.get_camera_name(cam_str) for cam_str in self.config.scene_setup.cameras]
        if self.render_mode == 'default':
            cameras_locations = camera_utils.get_current_cameras_locations(camera_names)
            for cam_name, cam_location in cameras_locations.items():
                cameras_locations[cam_name] = np.reshape(cam_location, (1, 3))
        
        elif self.render_mode == 'multiview':
            cameras_locations, _ = camera_utils.generate_multiview_cameras_locations(
                num_locations=self.config.dataset.view_count,
                mode=self.config.multiview_setup.mode,
                camera_names=camera_names,
                config=self.config.multiview_setup.mode_config,
                offset=self.config.multiview_setup.offset)
        
        else:
            raise ValueError(f'Selected render mode {self.render_mode} not currently supported')
        
        # some debug options
        # NOTE: at this point the object of interest have been loaded in the blender
        # file but their positions have not yet been randomized..so they should all be located
        # at the origin
        if self.config.debug.enabled:
            # simple plot of generated camera locations
            if self.config.debug.plot:
                from amira_blender_rendering.math.curves import plot_points

                for cam_name in camera_names:
                    plot_points(np.array(cameras_locations[cam_name]),
                                bpy.context.scene.objects[cam_name],
                                plot_axis=self.config.debug.plot_axis,
                                scatter=self.config.debug.scatter)

            # save all generated camera locations to .blend for later debug
            if self.config.debug.save_to_blend:
                for i_cam, cam_name in enumerate(camera_names):
                    self.save_to_blend(
                        self.dirinfos[i_cam],
                        camera_name=cam_name,
                        camera_locations=cameras_locations[cam_name],
                        basefilename='workstationscenario_camera_locations')

        # control loop for the number of static scenes to render
        scn_counter = 0
        print("begin while scn_counter="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
        while scn_counter < self.config.dataset.scene_count:

            # randomize scene: move objects at random locations, and forward simulate physics
            self.randomize_environment_texture()
            # additionally added
            ###################################################################################
            #self.randomize_object_transforms(self.objs + self.distractors)
            self.randomize_object_transforms(self.objs, self.distractors)
            self.randomize_obj_texture(self.distractors)
            #bpy.types.RigidBodyWorld.substeps_per_frame=40            
            bpy.context.preferences.system.memory_cache_limit=16384
            ###################################################################################
            
            self.forward_simulate() 
                
#change_objects_loc_rot_here
                 
            print("forward_simulate="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
                        
            # check visibility
            repeat_frame = False
            if not self.config.render_setup.allow_occlusions:
                for cam_name, cam_locations in cameras_locations.items():
                    repeat_frame = not self.test_visibility(cam_name, cam_locations)

            # if we need to repeat (change static scene) we skip one iteration
            # without increasing the counter
            if repeat_frame:
                self.logger.warn(f'Something wrong. '
                                 f'Re-randomizing scene {scn_counter + 1}/{self.config.dataset.scene_count}')
                continue
            
            # loop over cameras
            for i_cam, cam_str in enumerate(self.config.scene_setup.cameras):
                # get bpy object camera name
                cam_name = self.get_camera_name(cam_str)
                
                # check whether we broke the for-loop responsible for image generation for
                # multiple camera views and repeat the frame by re-generating the static scene
                if repeat_frame:
                    break
                
                # extract camera locations
                cam_locations = cameras_locations[cam_name]
                print("cameras_locations="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
                
                # compute format width
                view_format_width = int(ceil(log(len(cam_locations), 10)))
                
                # activate camera
                self.activate_camera(cam_name)
                print("activate_camera="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

                # loop over locations
                for view_counter, cam_loc in enumerate(cam_locations):

                    self.logger.info(
                        f"Generating image for camera {cam_str}="
                        f"scene {scn_counter + 1}/{self.config.dataset.scene_count}, "
                        f"view {view_counter + 1}/{self.config.dataset.view_count}")

                    # filename
                    base_filename = f"s{scn_counter:0{scn_format_width}}_v{view_counter:0{view_format_width}}"

                    # set camera location
                    #self.set_camera_location(cam_name, cam_loc)
                    print("set_camera_location="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

                    #additionally added
                    ################################################################################################
                    #Min:  0.617447154743158    Max:  1.0502419872856639
                    #0 / 10:  0.617447154743158
                    #1 / 10:  0.7079019273762083
                    #2 / 10:  0.7332982118619715
                    #3 / 10:  0.7544499287640324
                    #4 / 10:  0.7760178179015551
                    #5 / 10:  0.798877044890526
                    #6 / 10:  0.8346648848975794
                    #7 / 10:  0.859757597176487
                    #8 / 10:  0.8934435629251612
                    #9 / 10:  0.934346685094234
                    #10 / 10:  1.0502419872856639  
                    zahl=np.random.uniform()
                    if zahl<0.1:
                        dist=np.random.uniform(0.617447, 0.707901)
                    elif zahl<0.9:
                        dist=np.random.uniform(0.707901, 0.934346)
                    else:
                        dist=np.random.uniform(0.934346,1.050241)
                    dist-=0.1   #TODO, maybe remove me
                    #Min: 53.63628763550403    Max: 65.20794319211619
                    #0 - 10:  53.63628763550403
                    #1 - 10:  55.80951607172378
                    #2 - 10:  56.55942323136876
                    #3 - 10:  57.068274767004304
                    #4 - 10:  57.56385299517175
                    #5 - 10:  58.160399734534906
                    #6 - 10:  58.75736203823386
                    #7 - 10:  59.56064041522681
                    #8 - 10:  60.52886473626949
                    #9 - 10:  61.52943303098482
                    #10 - 10:  65.20794319211619
                    
                    zahl=np.random.uniform()
                    if zahl<0.1:
                        alpha=np.random.uniform(53.636287,55.809516)
                    elif zahl<0.9:
                        alpha=np.random.uniform(55.809516,61.529433)
                    else:
                        alpha=np.random.uniform(61.529433,65.207943)
                    
                    alpha=90-alpha
                    #alpha=50*np.random.uniform()+20
                    alpha=alpha*np.pi/180.0
                    self.change_camera_location_randomly(dist, alpha)
                    
                    bpy.data.objects[cam_name].data.lens=2.16
                    ################################################################################################

                    # at this point all the locations have already been tested for visibility
                    # according to allow_occlusions config.
                    # Here, we re-run visibility to set object visibility level as well as to update
                    # the depsgraph needed to update translation and rotation info
                    all_visible = self.test_visibility(cam_name, cam_loc)
                    print("test_visibility="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
                    
                    # update path information in compositor
                    self.renderman.setup_pathspec(self.dirinfos[i_cam], base_filename, self.objs)
                    print("setup_pathspec="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
                    
                    if not all_visible:
                        # if debug is enabled save to blender for debugging
                        if self.config.debug.enabled and self.config.debug.save_to_blend:
                            self.save_to_blend(
                                self.dirinfos[i_cam],
                                scene_index=scn_counter,
                                view_index=view_counter,
                                basefilename='workstationscenario_visibility')
                    
                    #additionally added
                    ################################################################################################     
                    self.change_camera_location_randomly(dist, alpha)
                    ################################################################################################
                    
                    # finally, render
                    self.renderman.render()
                    print("renderman.render="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

                    # postprocess. this will take care of creating additional
                    # information, as well as fix filenames
                    try:
                        self.renderman.postprocess(
                            self.dirinfos[i_cam],
                            base_filename,
                            bpy.context.scene.camera,
                            self.objs,
                            self.config.camera_info.zeroing,
                            postprocess_config=self.config.postprocess)

                        if self.config.debug.enabled and self.config.debug.save_to_blend:
                            # reset frame to 0 and save
                            bpy.context.scene.frame_set(0)
                            self.save_to_blend(
                                self.dirinfos[i_cam],
                                scene_index=scn_counter,
                                view_index=view_counter,
                                basefilename='workstationscenario')

                    except ValueError:
                        self.logger.error(
                            f"\033[1;31mValueError during post-processing. "
                            f"Re-generating image {scn_counter + 1}/{self.config.dataset.scene_count}\033[0;37m")
                        repeat_frame = True

                        print("Except ValueError",flush=True, file=sys.stderr)

                        # if requested save to blend files for debugging
                        if self.config.debug.enabled and self.config.debug.save_to_blend:
                            self.logger.error('There might be a discrepancy between generated mask and '
                                              'object visibility data. Saving debug info to .blend')
                            self.save_to_blend(
                                self.dirinfos[i_cam],
                                scene_index=scn_counter,
                                view_index=view_counter,
                                on_error=True,
                                basefilename='workstationscenario')

                        break
                    print("image rendered="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

            # update scene counter
            if not repeat_frame:
                scn_counter = scn_counter + 1
        print("end generate_dataset="+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me

        return True

    def dump_config(self):
        """Dump configuration to a file in the output folder(s)."""
        # dump config to each of the dir-info base locations, i.e. for each
        # camera that was rendered we store the configuration
        for dirinfo in self.dirinfos:
            output_path = dirinfo.base_path
            pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)
            dump_config(self.config, output_path)

    def teardown(self):
        """Tear down the scene"""
        # nothing to do
        pass
