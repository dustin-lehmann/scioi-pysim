function ToBabylon(coordinates) {
    return new BABYLON.Vector3(coordinates[0], coordinates[2], -coordinates[1])
}
// =====================================================================================================================

class WorldObject {
    constructor(scene, object_id, object_type, world_config) {

        this.object_id = object_id
        this.object_type = object_type
        this.world_config = world_config


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

    }
    // -----------------------------------------------------------------------------------------------------------------
}


class PysimBox extends WorldObject {
    constructor(scene, object_id, object_type, world_config) {
        super(scene,object_id ,object_type ,world_config);

        const default_config = {
            color: [1, 0, 0],
            texture: '',
            texture_uscale: 0.5,
            texture_vscale: 0.5,
            visible: true
        }
        this.config = {...default_config, ...options}

        this.size = {
            x: this.world_config['size_x'],
            y: this.world_config['size_y'],
            z: this.world_config['size_z']
        }
        this.position = this.world_config['configuration']['pos']
        this.orientation = this.world_config['configuration']['ori']

        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: this.size.z, width: this.size.x, depth: this.size.y}, scene)
        this.material = new BABYLON.StandardMaterial(this.scene);

        if (this.config.texture){
            this.material.diffuseTexture = new BABYLON.Texture(this.config.texture, this.scene)
            this.material.diffuseTexture.uScale = this.config.texture_uscale
            this.material.diffuseTexture.vScale = this.config.texture_vscale
            this.material.specularColor = new BABYLON.Color3(0,0,0)
        } else {
            this.material.diffuseColor = new BABYLON.Color3(this.config.color[0],this.config.color[1],this.config.color[2])
        }
        this.body.material = this.material

        this.setPosition(this.position)
        this.setOrientation(this.orientation)

        return this
    }

    // -----------------------------------------------------------------------------------------------------------------
    setPosition(position) {
        this.position = position
        this.body.position = ToBabylon([position[0], position[1], position[2]])
    }

    // -----------------------------------------------------------------------------------------------------------------
    setOrientation(orientation){
        this.orientation = orientation
    }

    // -----------------------------------------------------------------------------------------------------------------
    setState(state){
        this.setPosition(state['pos'])
        this.setOrientation(state['ori'])
    }
    // -----------------------------------------------------------------------------------------------------------------

}

// =====================================================================================================================
class TWIPR {
}