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

        console.log("BUILDING A BOX")
        const default_visualization_config = {
            color: [1, 0, 0],
            texture: '',
            texture_uscale: 1,
            texture_vscale: 1,
            visible: true
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

        this.setPosition(this.position)
        this.setOrientation(this.orientation)

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
            console.log("BUILDING A TWIPR ROBOT")

     }
}