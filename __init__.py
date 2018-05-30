############################################################################
#  This File is part of Batch Texture and Render Addon                     #
#                                                                          #
############################################################################

if "bpy" in locals():
    import imp
    imp.reload(render_texture_batch)
else:
    from . import render_texture_batch

import bpy
import os, tempfile

bl_info = {
    "name": "Batch Texture and Render",
    "author": "SyncProcess",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "Properties > Render > Batch Texture Render",
    "description": "A tools to help with managing texturing and rendering in batch",
    "category": "Render",
}

def isdirObjFolder(self, context):

    self.isdirObjFolder = False
    if os.path.isdir(self.objFolder):
        self.isdirObjFolder = True


def existsTexture(self, context):

    self.existsTexture = False
    if os.path.exists(self.texture):
        self.existsTexture = True

def isdirRenderFolder(self, context):

    self.isdirRenderFolder = False
    if os.path.isdir(self.renderFolder):
        self.isdirRenderFolder = True

class BatchPropertiesGroup(bpy.types.PropertyGroup):
    progressCollapse = bpy.props.BoolProperty(default=True)
    itemsProcessed = bpy.props.IntProperty(default=0)
    renderingsProcessed = bpy.props.IntProperty(default=0)
    objFolder = bpy.props.StringProperty(description="Folder containing obj's", subtype="FILE_PATH", update=isdirObjFolder)
    isdirObjFolder = bpy.props.BoolProperty(default=False)
    renderFolder = bpy.props.StringProperty(default=tempfile.mkdtemp(prefix='rendertexturebatch'), description="Folder where renders are saved", subtype="FILE_PATH", update=isdirRenderFolder)
    isdirRenderFolder = bpy.props.BoolProperty(default=False)
    texture = bpy.props.StringProperty(description="Texture image", subtype="FILE_PATH", update=existsTexture)
    existsTexture = bpy.props.BoolProperty(default=False)
    batchOptionCollapse = bpy.props.BoolProperty(default=True)
    cameraViews = bpy.props.EnumProperty(
        items=[
            ("1", 'One', 'Front'),
            ("2", 'Two', 'Front and back'),
            ("4", 'Four', 'Front, left, back and right'),
            ("8", 'Eight', 'Eight sides'),
            ("16", 'Sixteen', 'Sixteen sides')
        ],
        name='Camera views',
        description="Camera views",
        default="4"
    )
    renderWidth = bpy.props.IntProperty(name="Render width",
        description="Width of render", default=1800,
        min=1)
    renderHeight = bpy.props.IntProperty(name="Render height",
        description="Height of render", default=1200,
        min=1)
    renderFormat = bpy.props.EnumProperty(
        items=[
            ("JPEG", 'JPEG', 'Jpeg file'),
            ("PNG", 'Png', 'Png file')
        ],
        name='Render format',
        description="Render format can be JPEG or PNG",
        default="JPEG"
    )
    transparent = bpy.props.BoolProperty(name="Alpha mode",
        description="Alpha mode can be transparent or sky",
        default=False)
    singleTexture = bpy.props.BoolProperty(default=True)
    smartUVProject = bpy.props.BoolProperty(default=True)
    orthographicCamera = bpy.props.BoolProperty(default=True)
    cameraAngleStart = bpy.props.IntProperty(name='Camera angle start', description='Camera AngleStart', default=0)
    renderBefore = bpy.props.BoolProperty(default=True)

class BatchTextureRenderPanel(bpy.types.Panel):
    """Creates a Panel in the render properties window"""
    bl_label = "Batch Texture Render"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        batch = bpy.context.scene.render_texture_batch

        layout = self.layout

        batch = context.scene.render_texture_batch

        column = layout.column(align=True)
        box = column.box()

        row = box.row()
        row.prop(batch, "objFolder", text="Objects")

        row = box.row()
        row.prop(batch, "texture", text="Texture")

        row = box.row()
        row.prop(batch, "renderFolder", text="Render")

        expandCollapseIcon = "TRIA_RIGHT"
        if not batch.batchOptionCollapse:
            expandCollapseIcon = "TRIA_DOWN"
        box = box.box()
        row = box.row()
        row.prop(batch, "batchOptionCollapse", text="", emboss=False, icon=expandCollapseIcon)
        row.label("Render Options")

        if not batch.batchOptionCollapse:
            row = box.row()
            row.prop(batch, "cameraViews", text="Cameras", icon = "OUTLINER_OB_CAMERA")
            row = box.row()
            row.prop(batch, "renderWidth", text="Width of render", icon = "ARROW_LEFTRIGHT")
            row = box.row()
            row.prop(batch, "renderHeight", text="Height of render", icon = "FULLSCREEN")
            row = box.row()
            row.prop(batch, "renderFormat", text="Format of render", icon = "RENDER_ANIMATION")
            row = box.row()
            row.prop(batch, "transparent", text="Transparent", icon = "MAT_SPHERE_SKY")
            row = box.row()
            row.prop(batch, "singleTexture", text="Use one texture", icon = "RENDER_ANIMATION")
            row = box.row()
            row.prop(batch, "smartUVProject", text="Smart UV project")
            row = box.row()
            row.prop(batch, "orthographicCamera", text="Orthographic camera")
            row = box.row()
            row.prop(batch, "cameraAngleStart", text="Camera angle start")
            row = box.row()
            row.prop(batch, "renderBefore", text="Render before")

        expandCollapseIcon = "TRIA_RIGHT"
        if not batch.progressCollapse:
            expandCollapseIcon = "TRIA_DOWN"
        box = layout.box()
        row = box.row()
        row.prop(batch, "progressCollapse", text="", emboss=False, icon=expandCollapseIcon)
        row.label(text="Progress")

        if not batch.progressCollapse:
            row = box.row()
            row.label("Articles processed: " + str(batch.itemsProcessed), icon="LINENUMBERS_ON")
            row = box.row()
            row.label("Render count: " + str(batch.renderingsProcessed), icon="IMAGE_DATA")

        row = layout.row()
        row.operator("render_texture_batch.start_batch", icon="RENDER_ANIMATION")
        if (not batch.isdirObjFolder or not batch.existsTexture):

            row = layout.row()
            row.label(text="Please specify object folder, and texture folder or image", icon="INFO")

class RenderTextureBatchOperator(bpy.types.Operator):
    """Start rendering"""
    bl_idname = "render_texture_batch.start_batch"
    bl_label = "Render"

    @classmethod
    def poll(cls, context):
        #There are batches to render
        #There are no batches to render that have invalid paths
        batch = context.scene.render_texture_batch
        return batch.isdirObjFolder and batch.existsTexture

    def execute(self, context):
        batch = context.scene.render_texture_batch
        batch.itemsProcessed = 0
        batch.renderingsProcessed = 0
        render_texture_batch.render_texture_batch(batch)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BatchPropertiesGroup)
    bpy.types.Scene.render_texture_batch = bpy.props.PointerProperty(type=BatchPropertiesGroup)
    bpy.utils.register_module(__name__)

def unregister():

    bpy.utils.unregister_class(BatchPropertiesGroup)
    del bpy.types.Scene.render_texture_batch
    bpy.utils.unregister_module(__name__)