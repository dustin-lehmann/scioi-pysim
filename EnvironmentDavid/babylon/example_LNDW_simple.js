//import Data from "./data";

var texture_pack = ''
var babylon_objects = {}
// var robots = {}
// var environment_objects= {}
var textures = {}


//===Objects============================================================================================================
// function to create all the different objects in the visualization except for the robot_textures

// class to create all different types of obstalces
class createBoxFromJson {

    constructor(scene, length, width, height, center_x, center_y, center_z, psi, visible, classname) {
        this.object_type = 'obstacle'
        this.scene = scene;
        if (typeof visible == "undefined"){print('dfhjfdskhpfshpffhfphjgfhjpgfhjgfdgfgf')}
        this.visible=visible
        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: height, width: width, depth: length}, scene);
        this.body.rotation.y = psi

        this.body.position = ToBabylon([center_x, center_y, center_z])
        // texture file selected via object type
        let texture_file = textures["materials"][classname]

        // relative texture path
        let texture= "./texture_packs/textures/material_textures/"+texture_file;

        this.material = new BABYLON.StandardMaterial(this.scene);
        this.material.diffuseTexture = new BABYLON.Texture(texture, this.scene)
        this.material.diffuseTexture.uScale = 0.5
        this.material.diffuseTexture.vScale = 0.5
        this.material.specularColor = new BABYLON.Color3(0,0,0)


        this.body.material = this.material

        this.setVisibility(this.visible)

        return this;
    }
    setVisibility(state){
        this.body.visibility = state
    }

    setState(x,y,z,psi) {
    // console.log(psi)
    this.setPosition(x,y,z)
    this.setOrientation(psi)
    }

    setPosition(x, y, z) {
        this.body.position = ToBabylon([x,y,z])


        // this.pivotPointWheels.position.x = y
        // this.pivotPointWheels.position.z = x
    }
    setOrientation(psi){
        this.body.rotation.y = psi
        // this.pivotPointBody.rotation.x = theta
    }
}

// this function transforms input coordinates to babylon coordinates
function ToBabylon(coordinates) {
    return new BABYLON.Vector3(coordinates[0], coordinates[2], -coordinates[1])
}

//===Agents,Robots======================================================================================================

// base class for Agents/Robots
class Robot {
    constructor (scene, id, name, length, width, height, position, psi, shadowGenerator){
        this.object_type = 'agent'
        this.name = name
        this.scene = scene
        this.length = length
        this.width = width
        this.height = height
        this.id = id
        this.position = position
        this.psi = psi

        this.shadowGenerator = shadowGenerator

        this.collision_state = 0
        this.box_visible = 0
        this.model_visible = 1

        this.robot_model = new Robot_Model(this.scene, this.shadowGenerator,{'on_load_callback': this.test(this)})
        this.box_model = new BoxRobot(this.scene, this.length, this.width, this.height, this.position, this.psi)

        var color;
        if (this.id === 1){
            color = [1,0,0]
        } else {
            color = [0,0,1]
        }
        this.indicator = new AgentIndicator(this.scene,this.mesh, {'color': color})

        this.box_model.body.visibility = this.box_visible

    }

    test(){

    }

    setState(x, y, psi){
        this.position = [x,y]
        this.psi = psi
        if (this.robot_model.loaded) {
            this.robot_model.setPosition(x,y)
            this.robot_model.setOrientation(psi)
        }

        this.box_model.setState(x,y,psi)
        this.indicator.setPosition(x,y)
    }

    setCollision(state) {
        this.robot_model.setCollision(state)
    }
}

class BoxRobot {
    constructor(scene, length, width, height, position, psi,type) {
        this.scene = scene;
        this.length = length
        this.width = width
        this.height = height
        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: height, width: length, depth: width}, scene);
        this.material = new BABYLON.StandardMaterial("material", scene);
        this.body.material = this.material

        this.setState(position[0], position[1], psi)

        return this;
    }

    setState(x, y, psi){
        this.body.position = ToBabylon([x,y,this.height/2])
        this.body.rotation.y = psi
    }

    setColour(collision) {
        // This function is used to visualize a collision by changing the colour of a material to a certain colour (green/red)
        if (collision) {
            boxMat.diffuseColor = new BABYLON.Color3(0, 1, 0)

        } else {
            //boxMat.diffuseColor = new BABYLON.Color3(1, 0, 0);
            this.material.diffuseColor = new BABYLON.Color3.Green()
        }
    }
}

class AgentIndicator {
    constructor(scene, parent, options) {
        this.scene = scene;
        const defaults = {
            color: [0.8,0,0],
            size: 0.03,
            id: 1,
        };
        options = {...defaults, ...options};

        this.sphere = BABYLON.MeshBuilder.CreateSphere("sphere", {diameter: options.size}, scene);
        this.sphere.position.y = 10


        var myMaterial = new BABYLON.StandardMaterial("myMaterial", this.scene);

        myMaterial.diffuseColor = new BABYLON.Color3(options.color[0],options.color[1],options.color[2]);
        myMaterial.emissiveColor = new BABYLON.Color3(options.color[0],options.color[1],options.color[2]);
        myMaterial.alpha = 0.75;


        this.sphere.material = myMaterial;

        return this;
    }
    setPosition(x, y) {
        this.sphere.position = ToBabylon([x,y,0.2])

    }

}

class Robot_Model {
    constructor(scene, shadowGenerator, options) {
        this.scene = scene;
        this.shadowGenerator = shadowGenerator
        const defaults = {
            id: 1,
            indicator: true,
            on_load_callback: undefined
        };
        options = {...defaults, ...options};
        this.options = options
        this.model = "robot_2.babylon"
        this.color = [46/255, 137/255, 214/255]


        this.loaded = false
        //[108/255, 190/255, 15/255]
        BABYLON.SceneLoader.ImportMesh("", "./", this.model, this.scene, this.onLoad.bind(this));

        return this;
    }

    onLoad(newMeshes, particleSystems, skeletons){
        this.mesh = newMeshes[0]
        this.mesh.scaling.x = 1
        this.mesh.scaling.y = 1
        this.mesh.scaling.z = 1

        this.material = new BABYLON.StandardMaterial("material", this.scene);
        this.mesh.material = this.material


        // this.shadowGenerator.addShadowCaster(this.mesh)

        if (this.options.on_load_callback !== undefined) {

            this.options.on_load_callback(this)
        }


        this.loaded = true
    }

    setState(x,y,psi) {
        // console.log(psi)
        this.setPosition(x,y)
        this.setOrientation(psi)
    }

    setPosition(x, y) {
        this.mesh.position = ToBabylon([x,y,0.004])


        // this.pivotPointWheels.position.x = y
        // this.pivotPointWheels.position.z = x
    }
    setOrientation(psi){
        this.mesh.rotation.y = psi
        // this.pivotPointBody.rotation.x = theta
    }

    setCollision(state){
        // if (state){
        //     // this.material.diffuseColor = new BABYLON.Color3(255/255,51/255,51/255)
        //     this.material.diffuseColor = new BABYLON.Color3.Green()
        // } else {
        //     this.material.diffuseColor = new BABYLON.Color3.White()
        // }
    }
}

// ===Basic Envrionment settings========================================================================================
class LNDW_scene_simple extends Scene {
    constructor(id, options) {
        const defaults = {

        };
        options = {...defaults, ...options};
        super(id);
        this.options = options;
        this.createScene();
    }

    createScene() {

        var json_objects = []

        //------------------------------------------------Camera settings-----------------------------------------------

        // set rotation point for camera -> should be the middle of the testbed
        this.camera = new BABYLON.ArcRotateCamera("Camera", 0, 0, 20, ToBabylon([5.094/2,3.679/2,0]), this.scene);

        // Positions the camera overwriting alpha, beta, radius
        this.camera.setPosition(new BABYLON.Vector3(2.5, 1.5, 7));

        // This attaches the camera to the canvas
        this.camera.attachControl(this.canvas, true);

        //---------------------------------------Moving sensibilty settings---------------------------------------------

        this.camera.angularSensibilityY = 25000
        this.camera.angularSensibilityX = 25000
        //increase Zooming speed
        this.camera.wheelPrecision = 10;

        //This creates a light, aiming 0,1,0 - to the sky (non-mesh)
        this.light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0.5,1,0), this.scene);
        this.light.intensity = 0.5

	    this.light3 = new BABYLON.PointLight("pointLight", new BABYLON.Vector3(-1500, 2000, -1500), this.scene);
	    this.light3.intensity = 0.5;
        this.shadowGenerator = new BABYLON.ShadowGenerator(512, this.light3);

        this.light4 = new BABYLON.PointLight("pointLight2", new BABYLON.Vector3(1500, 2000, 1500), this.scene);
	    this.light4.intensity = 0.25;

        this.scene.clearColor = new BABYLON.Color3(0.25,0.25,0.25);
        this.scene.clearColor = new BABYLON.Color3(0,0,0);

        this.ui = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("ui", true, this.scene);

        //------------------------------------------elapsed timeTextbox-------------------------------------------------

        this.textbox = new BABYLON.GUI.TextBlock();
        this.textbox.fontSize = 40;
        this.textbox.text = "Time";
        this.textbox.color = "white";
        this.textbox.paddingTop = 3;
        this.textbox.paddingLeft = 3;
        this.textbox.textVerticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
        this.textbox.textHorizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
        this.ui.addControl(this.textbox);

        this.shadowGenerator.usePoissonSampling = true;

        // var gl = new BABYLON.GlowLayer("glow", this.scene);
        // gl.intensity = 1;

        var gl = new BABYLON.GlowLayer("glow", this.scene, {
            mainTextureFixedSize: 256,
            blurKernelSize: 12,
            intensity: 1.75
        });

        $.ajaxSetup ( {
            async: false
        });

        //----------------------------------------read from JSON--------------------------------------------------------

        // get world objects and the selected texture pack
        $.getJSON("objects.json", function(json) {
            // selection of the used texture pack
            texture_pack = json['textures']
            // all objects displayed in babylon
            babylon_objects = json['objects']
        });
        // get textures from texture pack
        var texture_path = "../texture_packs/"+texture_pack+".json"
        $.getJSON(texture_path, function(json) {

            textures = json
        });

        // draw coordinate system which helps for orientation
        this.drawCoordinateSystem()

        this.buildEnvironment();

        return this.scene;
    }

    buildEnvironment() {
        console.log(babylon_objects)
        for (const [key, value] of Object.entries(babylon_objects)) {
            // console.log(value['type'])
            // console.log(value['length'])
            // object is an obstacle -> create ObstacleBox
            if (value['object_type'] == 'obstacle') {
                console.log(value['visible'])
                value['babylon'] = new createBoxFromJson(this.scene,
                    value["parameters"]['length'],
                    value["parameters"]['width'],
                    value["parameters"]['height'],
                    value["position"]['x'],
                    value["position"]['y'],
                    value['position']['z'],
                    value["psi"],
                    value['parameters']["visible"],
                    value["class"],)
            }

            if (value['object_type'] == 'agent') {

                value['babylon'] = new Robot(this.scene,
                    value['id'],
                    value['name'],
                    value['parameters']['length'],
                    value['parameters']['width'],
                    value['parameters']['height'], // todo-> von class auf Texture schließen!
                    value['position'],
                    value['psi'],
                    this.shadowGenerator)

            }
        }
    }

    drawCoordinateSystem() {
        const points_x = [
            ToBabylon([0, 0, 0]),
            ToBabylon([0.25, 0, 0])
        ]
        const points_y = [
            ToBabylon([0, 0, 0]),
            ToBabylon([0, 0.25, 0])
        ]
        const points_z = [
            ToBabylon([0, 0, 0]),
            ToBabylon([0, 0, 0.25])
        ]
        const options_x = {
            points: points_x,
            color: new BABYLON.Color3(1, 0, 0),
            updatable: false
        }

        var line_x = BABYLON.MeshBuilder.CreateLines("line_x", {points: points_x}, this.scene);
        line_x.color = new BABYLON.Color3(1, 0, 0);

        var line_y = BABYLON.MeshBuilder.CreateLines("line_y", {points: points_y}, this.scene);
        line_y.color = new BABYLON.Color3(0, 1, 0);

        var line_z = BABYLON.MeshBuilder.CreateLines("line_z", {points: points_z}, this.scene);
        line_z.color = new BABYLON.Color3(0, 0, 1);


    }

    onSample(sample) {

        console.log(sample)

        //update all existing world objects
        for (const [key, value] of Object.entries(sample['world'])) {
            // console.log(value)
            babylon_objects[key]['babylon'].setState(value['position']['x'], value['position']['y'], value['position']['z'], value['psi'])

            if (babylon_objects[key].object_type == 'obstacle') {
                // put obstacle specific functions here! -> babylon_objects[key]['babylon'].function_call()
            }

            if (babylon_objects[key].object_type == 'agent') {
                // console.log(value)
                // put agent specific functions here!
            }
        }


        for (const [key, value] of Object.entries(sample['added']))
        {
            //todo:
        }

        for (const [key, value] of Object.entries(sample['deleted']))
        {
            //todo:
        }
    }
}