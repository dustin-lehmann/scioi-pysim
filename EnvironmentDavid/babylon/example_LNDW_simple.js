//import Data from "./data";

var texture_pack = ''
var robots = {}
var environment_objects= {}
var textures = {}

// function to create all the different objects in the visualization except for the robot_textures
class createBoxFromJson {
    constructor(scene, length, width, height, center_x, center_z, psi, visible, type) {
        this.scene = scene;
        this.visible=visible
        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: height, width: width, depth: length}, scene);
        this.body.rotation.y = psi

        this.body.position = ToBabylon([center_x, center_z, height/2])
        // let texture= "./twipr_models/textures/dark.png";
        // console.log('hello')
        // console.log(textures["materials"][type])
        // console.log(type)
        // texture file selected via object type
        // console.log(111111111)

        let texture_file = textures["materials"][type]

        // relative texture path
        let texture= "./texture_packs/textures/material_textures/"+texture_file;
        console.log(texture)

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
}

// this function transforms input coordinates to babylon coordinates
function ToBabylon(coordinates) {
    // return new BABYLON.Vector3(coordinates[0], -coordinates[2], coordinates[1])
    return new BABYLON.Vector3(coordinates[0], coordinates[2], -coordinates[1])
}

class Robot {
    constructor (scene, id, name, length, width, height, position, psi, shadowGenerator){
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
        myMaterial.emissiveColor = new BABYLON.Color3(1*options.color[0],1*options.color[1],1*options.color[2]);
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
        console.log(psi)
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

// #####################################################################################################################
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

        // set rotation point for camera -> should be the middle of the testbed
        this.camera = new BABYLON.ArcRotateCamera("Camera", 0, 0, 20, ToBabylon([5.094/2,3.679/2,0]), this.scene);

        // Positions the camera overwriting alpha, beta, radius
        this.camera.setPosition(new BABYLON.Vector3(2.5, 1.5, 7));

        // This attaches the camera to the canvas
        this.camera.attachControl(this.canvas, true);

        //increase angular speed
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

        // Textbox
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
        $.getJSON("objects.json", function(json) {
            texture_pack = json['textures']
            environment_objects = json['environment']
            robots = json['robots']
        });
        //todo: hier val einfügen 
        $.getJSON("../texture_packs/standard_textures.json", function(json) {

            textures = json
        });

        this.drawCoordinateSystem()
        this.buildEnvironment();

        return this.scene;
    }

    buildEnvironment() {
        console.log(Object.entries(environment_objects))
         for (const [key, value] of Object.entries(environment_objects)) {
             // console.log(value['type'])
             // console.log(value['length'])
             value['babylon'] = new createBoxFromJson(this.scene,
                value["length"],
                value["width"],
                value["height"],
                value["center_x"],
                value["center_y"],
                value["psi"],
                value["visible"],
                 value["type"],
            )
             }

        // Robots
        for (const [key, value] of Object.entries(robots)) {
            value['babylon'] = new Robot(this.scene,
                value['id'],
                key,
                value['length'],
                value['width'],
                value['height'],
                value['position'],
                value['psi'],
                this.shadowGenerator)
        }
    }

    drawCoordinateSystem() {
        const points_x = [
            ToBabylon([0,0,0]),
            ToBabylon([0.25,0,0])
        ]
        const points_y = [
            ToBabylon([0,0,0]),
            ToBabylon([0,0.25,0])
        ]
        const points_z = [
            ToBabylon([0,0,0]),
            ToBabylon([0,0,0.25])
        ]
        const options_x = {
            points: points_x,
            color: new BABYLON.Color3(1,0,0),
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

        this.textbox.text = 'Time: ' + sample['t'].toFixed(2) + ' s'
        // Robot

        var robot_data = sample['robots']
        // console.log(this.camera)
        for (const [key, value] of Object.entries(robot_data)) {
            if (key in robots) {
                robots[key]['babylon'].setState(value['position'][0], value['position'][1], value['psi'])
                robots[key]['babylon'].setCollision(value['collision'])
            }
        }
    }
}