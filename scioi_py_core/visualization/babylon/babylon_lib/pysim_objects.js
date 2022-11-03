function ToBabylon(coordinates) {
    return new BABYLON.Vector3(coordinates[0], coordinates[2], -coordinates[1])
}

// =====================================================================================================================

class WorldObject {
    constructor(scene, object_id, object_type, object_config, visualization_config) {

        this.object_id = object_id
        this.object_type = object_type
        this.object_config = object_config
        this.visualization_config = visualization_config

        this.scene = scene
        this.loaded = false
    }

    // -----------------------------------------------------------------------------------------------------------------
    setState(state){

    }
    // -----------------------------------------------------------------------------------------------------------------
    setPosition(position){

    }
    // -----------------------------------------------------------------------------------------------------------------
    setOrientation(orientation){

    }
    // -----------------------------------------------------------------------------------------------------------------
    highlight(){

    }
    // -----------------------------------------------------------------------------------------------------------------
    setVisibility(){

    }
    // -----------------------------------------------------------------------------------------------------------------
    delete(){

    }
    // -----------------------------------------------------------------------------------------------------------------
    update(sample) {
        if ('configuration' in sample) {
            if ('pos' in sample['configuration']){
                this.setPosition(sample['configuration']['pos'])
            }
            if ('ori' in sample['configuration']){
                this.setOrientation(sample['configuration']['ori'])
            }
        }
    }
    // -----------------------------------------------------------------------------------------------------------------
}


class PysimBox extends WorldObject {
    constructor(scene, object_id, object_type, object_config, visualization_config) {
        super(scene, object_id, object_type, object_config, visualization_config);

        const default_visualization_config = {
            color: [1, 0, 0],
            texture: '',
            texture_uscale: 1,
            texture_vscale: 1,
            visible: true,
            wireframe: false,
            alpha: 1
        }
        this.visualization_config = {...default_visualization_config, ...visualization_config}

        this.size = {
            x: this.object_config['size']['x'],
            y: this.object_config['size']['y'],
            z: this.object_config['size']['z']
        }
        this.position = this.object_config['configuration']['pos']
        this.orientation = this.object_config['configuration']['ori']


        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: this.size.z, width: this.size.x, depth: this.size.y}, scene)
        this.material = new BABYLON.StandardMaterial(this.scene);

        if (this.visualization_config.texture){
            this.material.diffuseTexture = new BABYLON.Texture(this.visualization_config.texture, this.scene)
            this.material.diffuseTexture.uScale = this.visualization_config.texture_uscale
            this.material.diffuseTexture.vScale = this.visualization_config.texture_vscale
            this.material.specularColor = new BABYLON.Color3(0,0,0)
        } else {
            this.material.diffuseColor = new BABYLON.Color3(this.visualization_config.color[0],this.visualization_config.color[1],this.visualization_config.color[2])
        }
        this.body.material = this.material
        this.body.material.alpha = this.visualization_config['alpha']

        if (this.visualization_config['wireframe']){
            this.body.enableEdgesRendering();
            this.body.edgesWidth = 0.75;
            this.body.edgesColor = new BABYLON.Color4(1, 0,0, 1);

        }

        this.setPosition(this.position)
        this.setOrientation(this.orientation)

        this.loaded = true
        return this
    }

    // -----------------------------------------------------------------------------------------------------------------
    setPosition(position) {
        this.position = position
        this.body.position = ToBabylon([position['x'], position['y'], position['z']])
    }

    // -----------------------------------------------------------------------------------------------------------------
    setOrientation(orientation){
        this.orientation = orientation
        const q = Quaternion.fromRotationMatrix(orientation)
        this.body.rotationQuaternion = q.babylon()
    }

    // -----------------------------------------------------------------------------------------------------------------
    setState(state){
        this.setPosition(state['pos'])
        this.setOrientation(state['ori'])
    }
    // -----------------------------------------------------------------------------------------------------------------

}

// =====================================================================================================================
class Tank_Robot extends WorldObject {
     constructor(scene, object_id, object_type, object_config, visualization_config) {
         super(scene, object_id, object_type, object_config, visualization_config);
            console.log("BUILDING A TANK ROBOT")

     }
}
// =====================================================================================================================
class TWIPR_Robot extends WorldObject {
     constructor(scene, object_id, object_type, object_config, visualization_config) {
         super(scene, object_id, object_type, object_config, visualization_config);
            this.loaded = false
            this.model_name = visualization_config['base_model'] + this.object_config['agent_id'] + '.babylon'
            BABYLON.SceneLoader.ImportMesh("", "./", this.model_name, this.scene, this.onLoad.bind(this));
            if (visualization_config['show_collision_frame']) {
                let scaling_factor = 1.01
                this.collision_box = new PysimBox(this.scene, '', '', {'size': {'x': scaling_factor*this.object_config['physics']['size'][0],'y': scaling_factor*this.object_config['physics']['size'][1],'z': scaling_factor*this.object_config['physics']['size'][2]}, 'configuration': this.object_config['configuration']},{'wireframe': true, 'alpha': 0})
            }
            return this

     }

     onLoad(newMeshes, particleSystems, skeletons){

        this.mesh = newMeshes[0]
        this.mesh.scaling.x = 1
        this.mesh.scaling.y = 1
        this.mesh.scaling.z = -1  // Mirror the mesh to fit the SolidWorks Coordinate System

        this.material = new BABYLON.StandardMaterial("material", this.scene);
        this.mesh.material = this.material


        // this.shadowGenerator.addShadowCaster(this.mesh)

        // if (this.options.on_load_callback !== undefined) {
        //     this.options.on_load_callback(this)
        // }

        this.loaded = true
    }
    // -----------------------------------------------------------------------------------------------------------------
    setPosition(position) {
        this.position = position
        this.mesh.position = ToBabylon([position['x'], position['y'], this.object_config['physics']['wheel_diameter']/2])
    }

    // -----------------------------------------------------------------------------------------------------------------
    setOrientation(orientation){
        this.orientation = orientation
        const q = Quaternion.fromRotationMatrix(orientation)
        this.mesh.rotationQuaternion = q.babylon()

        if (this.visualization_config['show_collision_frame']){
            this.collision_box.setOrientation(orientation)
        }
    }

    // -----------------------------------------------------------------------------------------------------------------
    setState(state){
        this.setPosition(state['pos'])
        this.setOrientation(state['ori'])
    }
    update(sample) {
        if ('configuration' in sample) {
            if ('pos' in sample['configuration']){
                this.setPosition(sample['configuration']['pos'])
            }
            if ('ori' in sample['configuration']){
                this.setOrientation(sample['configuration']['ori'])
            }
            if ('collision_box_pos' in sample && this.visualization_config['show_collision_frame']){
                console.log(sample['collision_box_pos'])
                this.collision_box.setPosition(sample['collision_box_pos'])
            }
        }
    }

    // -----------------------------------------------------------------------------------------------------------------
}

