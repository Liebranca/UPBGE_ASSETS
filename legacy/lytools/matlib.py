import bpy, os, struct;

from bpy.types import Scene, Material, Image, PropertyGroup, Panel, Operator;
from bpy.utils import register_class, unregister_class;

#   ---     ---     ---     ---     ---

from bpy.props import (

    StringProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    BoolProperty,
    PointerProperty

);

#   ---     ---     ---     ---     ---

IMTYPES={

    "ALBEDO":[0, 1],
    "ORM"   :[2,3],
    "CURV"  :[],
    "NORMAL":[5,6]

};

def MATGNSIS():
    mat=bpy.context.active_object.active_material;
    mat.use_nodes=1; lyt=mat.lytools;

    ntree=mat.node_tree; nodes=ntree.nodes; nodes.clear();
    tc=nodes.new('ShaderNodeTexCoord'); tc.location=[-250,0];
    tc.name=tc.label="TEXCOORD";

    curv_contr0=nodes.new('ShaderNodeVectorMath'); curv_contr0.location=[750,250];
    curv_contr0.name=curv_contr0.label="CURV_CONTR0";

    curv_contr0.operation='MULTIPLY';
    curv_contr0.inputs[1].default_value[:]=[0.4, 0.5, 1.0];

    curv_contr1=nodes.new('ShaderNodeVectorMath'); curv_contr1.location=[935,250];
    curv_contr1.name=curv_contr1.label="CURV_CONTR1";

    curv_contr1.operation='ADD';
    curv_contr1.inputs[1].default_value[:]=[0.2, 0.1, 0.5];

    ntree.links.new(curv_contr0.outputs[0], curv_contr1.inputs[0]);

    vm=nodes.new('ShaderNodeMapping'); vm.location=[0, 0];
    vm.name=vm.label="MAPPING";

    ntree.links.new(tc.outputs[2], vm.inputs[0]);

#   ---     ---     ---     ---     ---

    shd=nodes.new('ShaderNodeGroup');  shd.location=[750, 0];
    shd.node_tree=bpy.data.node_groups["LyShader"];
    shd.name=shd.label="SHADER";

    out=nodes.new('ShaderNodeOutput'); out.location=[1000, 0];
    out.name=out.label="OUT";

#   ---     ---     ---     ---     ---

    matname=lyt.mat_f1.split("\\")[-1]; y=600;
    mth=nodes.new('ShaderNodeMath'); mth.location=[500, -525];
    mth.name=mth.label="FRESNEL"; mth.inputs[0].default_value=1.0;
    mth.operation='SUBTRACT';

    for name in IMTYPES:
        im=nodes.new('ShaderNodeTexImage'); im.location=[500, y];
        im.name=im.label=name; y-=275;

        ntree.links.new(vm.outputs[0], im.inputs[0]);

        for i in range(len(IMTYPES[name])):
            ntree.links.new(im.outputs[i], shd.inputs[IMTYPES[name][i]]);

        imname=matname+name.lower();
        if imname not in bpy.data.images:
            new_img=bpy.data.images.new(imname, width=64, height=64);
            new_img.source='FILE'; new_img.filepath=lyt.mat_f1+name.lower()+'.png'

        im.image=bpy.data.images[imname];
        if name=="NORMAL": im.color_space='NONE';

        if name=="CURV":
            ntree.links.new(im.outputs[0], curv_contr0.inputs[0]);
            ntree.links.new(im.outputs[1], mth.inputs[1]);

    #name=(lyt.mat_f1.split("\\")[-1])[:-1];
    #mat.name=bpy.context.object.name=bpy.context.object.data.name=name;

    ntree.links.new(curv_contr1.outputs[0], shd.inputs [4]);
    ntree.links.new(shd.outputs[0], out.inputs[0]);
    ntree.links.new(shd.outputs[1], out.inputs[1]);

#   ---     ---     ---     ---     ---

NDCHECK=["TEXCOORD", "SHADER", "OUT", "MAPPING", "FRESNEL"] + [key for key in IMTYPES];

def VALIDATE(mat):

    if mat.node_tree:
        for ndname in NDCHECK:
            if ndname not in mat.node_tree.nodes:
                return 0;

        return 1;

    return 0;

#   ---     ---     ---     ---     ---

DROOT="\\".join(__file__.split("\\")[:-2])+'\\data';

#   ---     ---     ---     ---     ---

def GTMAT_F0(self, context):
    w=list(os.walk(DROOT));
    return [tuple([w[0][0]+'\\'+s, s.capitalize(), '']) for s in w[0][1]];

def GTMAT_F1(self, context):
    mat=bpy.context.active_object.active_material;
    w=list(os.walk(mat.lytools.mat_f0));
    w=[pis for pis in w if "textures" in pis[1] or "textures" in pis[0]]; l=[];

    for pis in w:
        for s in pis[1]:
            if s!="textures":
                l.append( tuple( [pis[0]+'\\'+s+'\\'+s+'_', s.capitalize(), '' ]) );

    return l;

def UPIMPATH(self, context):
    mat=bpy.context.active_object.active_material;
    lyt=mat.lytools;

    for imname in IMTYPES:

        if imname not in mat.node_tree.nodes: continue;

        node=mat.node_tree.nodes[imname];
        node.image.filepath=lyt.mat_f1+imname.lower()+'.png';

    name=(lyt.mat_f1.split("\\")[-1])[:-1];
    #mat.name=bpy.context.object.name=bpy.context.object.data.name=name;
    bpy.ops.file.make_paths_relative();

#   ---     ---     ---     ---     ---

def UPMAT(self, context):
    mat=context.object.active_material;
    lyt=mat.lytools; ntree=mat.node_tree;

    nd=ntree.nodes["SHADER"];
    nd.inputs[7].default_value=lyt.mat_fresnel;

    curv_contr0=ntree.nodes["CURV_CONTR0"];
    curv_contr1=ntree.nodes["CURV_CONTR1"];

    curv_contr0.inputs[1].default_value[0]=lyt.mat_edgedarkm;
    curv_contr1.inputs[1].default_value[0]=lyt.mat_edgedarkb;
    curv_contr0.inputs[1].default_value[1]=lyt.mat_edgebrightm;
    curv_contr1.inputs[1].default_value[1]=lyt.mat_edgebrightb;
    curv_contr0.inputs[1].default_value[2]=lyt.mat_edgeoverm;
    curv_contr1.inputs[1].default_value[2]=lyt.mat_edgeoverb;

def IMFRES(self, context):
    mat=context.object.active_material;
    lyt=mat.lytools; ntree=mat.node_tree;

    if lyt.mat_imfres:
        ntree.links.new(ntree.nodes["FRESNEL"].outputs[0], ntree.nodes["SHADER"].inputs[7]);

    else:
        for link in ntree.links:
            if link.from_node==ntree.nodes["FRESNEL"]:
                ntree.links.remove(link); break;

def UPPROJ(self, context):

    mat=context.object.active_material;
    lyt=mat.lytools; ntree=mat.node_tree;

    im=ntree.nodes["ALBEDO"];
    tc, vm = ntree.nodes["TEXCOORD"], ntree.nodes["MAPPING"];

    if lyt.mat_proj == 'FLAT' and im.projection == 'BOX':
        ntree.links.new(tc.outputs[2], vm.inputs[0]);
    elif lyt.mat_proj == 'BOX' and im.projection == 'FLAT':
        ntree.links.new(tc.outputs[3], vm.inputs[0]);

    for imname in IMTYPES:
        im=ntree.nodes[imname];
        im.projection=lyt.mat_proj;
        im.projection_blend=lyt.mat_blend;

    vm.translation[:]=lyt.mat_loc[:];
    vm.scale[:]=lyt.mat_scale[:];
    vm.rotation[:]=lyt.mat_rot[:];

#   ---     ---     ---     ---     ---

class LYT_MaterialSettings(PropertyGroup):

    mat_f0=EnumProperty (

        items       = GTMAT_F0,
        update      = UPIMPATH,

        name        = "Cathegory",
        description = "Root folder to pick from"

    );

    mat_f1=EnumProperty (

        items       = GTMAT_F1,
        update      = UPIMPATH,

        name        = "Material",
        description = "Material folder to work with"

    );

    mat_proj=EnumProperty (

        items       = [('FLAT', 'UV',        'Use UV coordinates for texture mapping'),
                       ('BOX',  'Generated', 'Map textures through box projection'   )],

        update      = UPPROJ,
        name        = "Mapping",
        description = "Sets texture mapping mode"

    );

    mat_scale=FloatVectorProperty (

        name        = "Scaling",
        description = "Scales UV/generated texture coordinates",
        subtype     = 'NONE',

        size        = 3,
        default     = [1.0,1.0,1.0],
        update      = UPPROJ

    );

    mat_loc=FloatVectorProperty (

        name        = "Location",
        description = "Offsets UV/generated texture coordinates",
        subtype     = 'TRANSLATION',

        size        = 3,
        default     = [0.0,0.0,0.0],
        update      = UPPROJ

    );

    mat_rot=FloatVectorProperty (

        name        = "Rotation",
        description = "Rotates UV/generated texture coordinates",
        subtype     = 'EULER',

        size        = 3,
        default     = [0.0,0.0,0.0],
        update      = UPPROJ

    );

    mat_blend=FloatProperty (

        name        = "Blend",
        description = "Blurs texture at the seams",

        default     = 0.05,
        min         = 0.0,
        max         = 1.0,

        update      = UPPROJ

    );

    mat_fresnel=FloatProperty (

        name        = "Fresnel",
        description = "Brightens material at the edges",

        default     = 0.075,
        min         = 0.0,
        max         = 1.0,

        update      = UPMAT

    );

    mat_imfres=BoolProperty (

        name        = "From curv",
        description = "Use curvmap's alpha channel as fresnel value",

        default     = 0,
        update      = IMFRES

    );

    mat_edgedarkm=FloatProperty (

        name        = "Darkness mult",
        description = "Boosts the darknening of edges and self-occlussion",

        default     = 0.2,
        min         = 0.0,
        max         = 1.0,

        update      = UPMAT

    );

    mat_edgedarkb=FloatProperty (

        name        = "Darkness base",
        description = "Boosts the darknening of crevices and self-occlussion",

        default     = 0.4,
        min         = 0.0,
        max         = 1.0,

        update      = UPMAT

    );

    mat_edgebrightm=FloatProperty (

        name        = "Brightness mult",
        description = "Boosts brightness at edges",

        default     = 0.5,
        min         = 0.0,
        max         = 1.0,

        update      = UPMAT

    );

    mat_edgebrightb=FloatProperty (

        name        = "Brightness base",
        description = "Boosts brightness at edges",

        default     = 0.1,
        min         = 0.0,
        max         = 1.0,

        update      = UPMAT

    );

    mat_edgeoverm=FloatProperty (

        name        = "Lightness mult",
        description = "Affects light ambient factor",

        default     = 1.0,
        min         = 0.0,
        max         = 1.0,

        update      = UPMAT

    );

    mat_edgeoverb=FloatProperty (

        name        = "Lightness base",
        description = "Affects light ambient factor",

        default     = 0.5,
        min         = 0.0,
        max         = 1.0,

        update      = UPMAT

    );

#   ---     ---     ---     ---     ---

class LYT_INITMAT(Operator):

    bl_idname      = "lytmat.initmat";
    bl_label       = "Initialize material template";

    bl_description = "Clears current nodetree and sets up default material template";

#   ---     ---     ---     ---     ---

    def execute(self, context):
        MATGNSIS(); return {'FINISHED'};

#   ---     ---     ---     ---     ---

class LYT_materialPanel(Panel):

    bl_label       = 'LYT MATE';
    bl_idname      = 'LYT_materialPanel';
    bl_space_type  = 'PROPERTIES';
    bl_region_type = 'WINDOW';
    bl_context     = 'material';
    bl_category    = 'LYT';

#   ---     ---     ---     ---     ---
    
    @classmethod
    def poll(cls, context):
        ob=context.object;
        if ob:
            if isinstance(ob, bpy.types.Object):
                return ob.active_material!=None;

        return 0;

    def draw(self, context):

        layout = self.layout;

        scene  = context.scene;
        mat    = context.active_object.active_material;
        lyt    = context.active_object.active_material.lytools;

        row=layout.row(); row.prop(lyt, "mat_f0");

        if lyt.mat_f0:
            row=layout.row(); row.prop(lyt, "mat_f1");

            if not VALIDATE(mat):
                row=layout.row(); row.operator("lytmat.initmat", text="INIT", icon="SMOOTH");

            else:

                layout.separator();

                row=layout.row(); row.prop(lyt, "mat_proj");
                if lyt.mat_proj == 'BOX':
                    row=layout.row(); row.prop(lyt, "mat_blend");

                row=layout.row(); row.prop(lyt, "mat_scale");
                row=layout.row(); row.prop(lyt, "mat_loc");
                row=layout.row(); row.prop(lyt, "mat_rot");

                layout.separator();

                row=layout.row(); row.prop(lyt, "mat_imfres");
                if not lyt.mat_imfres: row.prop(lyt, "mat_fresnel");

                layout.separator();
                row=layout.row(); row.label("Edges:");

                row=layout.row(); row.prop(lyt, "mat_edgedarkm");
                row=layout.row(); row.prop(lyt, "mat_edgedarkb");
                row=layout.row(); row.prop(lyt, "mat_edgebrightm");
                row=layout.row(); row.prop(lyt, "mat_edgebrightb");
                row=layout.row(); row.prop(lyt, "mat_edgeoverm");
                row=layout.row(); row.prop(lyt, "mat_edgeoverb");


#   ---     ---     ---     ---     ---

def register():
    register_class(LYT_MaterialSettings);
    register_class(LYT_INITMAT);
    register_class(LYT_materialPanel);
    Material.lytools=PointerProperty(type=LYT_MaterialSettings);

def unregister():
    del Material.lytools;
    unregister_class(LYT_materialPanel);
    unregister_class(LYT_INITMAT);
    unregister_class(LYT_MaterialSettings);

#   ---     ---     ---     ---     ---
