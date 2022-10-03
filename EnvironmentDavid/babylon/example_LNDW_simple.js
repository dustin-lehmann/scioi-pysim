//import Data from "./data";

var robots = {}
var environment_objects= {}

// function to create all the different objects in the visualization except for the robots
class createBoxFromJson {
    constructor(scene, length, width, height, center_x, center_z, psi, visible) {
        this.scene = scene;
        this.visible=visible
        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: height, width: width, depth: length}, scene);
        this.body.rotation.y = psi

        this.body.position = ToBabylon([center_x, center_z, height/2])

        let texture= "./twipr_models/textures/dark.png";
        this.material = new BABYLON.StandardMaterial(this.scene);
        this.material.diffuseTexture = new BABYLON.Texture(texture, this.scene)
        this.material.diffuseTexture.uScale = 0.5
        this.material.diffuseTexture.vScale = 0.5
        this.material.specularColor = new BABYLON.Color3(0,0,0)


        this.body.material = this.material

        this.setVisibility(this.visible)
        console.log('creating box from json')

        return this;
    }
    setVisibility(state){
        this.body.visibility = state
    }
}

class createBoxObject {
    constructor(scene, length, width, height, center_x, center_z, psi,type)
    {
        if(type == "Robot")
            BoxRobot(scene,length,width,height,center_x,center_z,psi,type)
        else
            ObstacleBox(scene,length,width,height,center_x,center_z,psi,type)
    }
}

// this function transforms input coordinates to babylon coordinates
function ToBabylon(coordinates) {
    // return new BABYLON.Vector3(coordinates[0], -coordinates[2], coordinates[1])
    return new BABYLON.Vector3(coordinates[0], coordinates[2], -coordinates[1])
}


class FloorTile {
    constructor(scene, length, width, height, position) {
        this.scene = scene
        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: height, width: width, depth: length}, scene);
        this.body.position = ToBabylon(position)

        this.highlight1 = 0
        this.highlight2 = 0

        let texture= "./twipr_models/textures/ccc.png";

        let uscale = 1;
        let vscale = 1;
        this.material = new BABYLON.StandardMaterial(this.scene);
        this.material.diffuseTexture = new BABYLON.Texture(texture, this.scene)
        this.material.diffuseTexture.uScale = uscale
        this.material.diffuseTexture.vScale = vscale
        this.material.specularColor = new BABYLON.Color3(0,0,0)
        this.body.receiveShadows = true;
        this.body.material = this.material

        this.highlight_body = BABYLON.MeshBuilder.CreateBox('box', {height: 1, width: width*0.95, depth: length*0.95}, scene);
        this.highlight_material = new BABYLON.StandardMaterial("material", scene);
        this.highlight_material.alpha = 0.125
        this.highlight_body.material = this.highlight_material
        this.highlight_body.position = ToBabylon([position[0], position[1], height/2+3])
        this.highlight_body.visibility = 0

    }

    highlight(state, discoverer_id){
        if (state){
            this.highlight_body.visibility = 1
            if (discoverer_id===1 && this.highlight1){
                return
            }
            if (discoverer_id===1 && !this.highlight1){
                if (!this.highlight2){
                    this.highlight_material.diffuseColor = new BABYLON.Color3(1, 0, 0)
                    this.highlight_material.emissiveColor = new BABYLON.Color3(1, 0, 0)
                } else {
                    this.highlight_material.diffuseColor = new BABYLON.Color3(1, 0, 1)
                    this.highlight_material.emissiveColor = new BABYLON.Color3(1, 0, 1)
                }
                this.highlight1 = 1
            }
            if (discoverer_id===2 && !this.highlight2){
                if (!this.highlight1){
                    this.highlight_material.diffuseColor = new BABYLON.Color3(0, 0, 1)
                    this.highlight_material.emissiveColor = new BABYLON.Color3(0, 0, 1)
                } else {
                    this.highlight_material.diffuseColor = new BABYLON.Color3(1, 0, 1)
                    this.highlight_material.emissiveColor = new BABYLON.Color3(1, 0, 1)
                }
                this.highlight2 = 1
            }


             //new BABYLON.Color3.Green(
        } else {
            this.material.diffuseColor = new BABYLON.Color3(1,1,1)
        }
    }
}


class Wall {
    constructor(scene, length, width, height, center_x, center_z, psi, visible) {
        this.scene = scene;
        this.visible=visible
        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: height, width: width, depth: length}, scene);
        this.body.rotation.y = psi

        this.body.position = ToBabylon([center_x, center_z, height/2])

        let texture= "./twipr_models/textures/dark.png";
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

class Goal {
    constructor(scene, position, size, visible){

        this.scene = scene

        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: 2, width: size, depth: size}, scene);
        this.body.position = ToBabylon([position[0], position[1], 8])

        this.material = new BABYLON.StandardMaterial("material", scene);
        this.body.material = this.material

        this.material.diffuseColor = new BABYLON.Color3(255/255,215/255,0/255)
        this.setVisibility(visible)
    }
        setVisibility(state){
        this.body.visibility = state
    }
}


class DoorSwitch {
    constructor(scene, position, id) {
        this.scene = scene

        this.height = 20

        this.body = BABYLON.MeshBuilder.CreateCylinder('cylinder', {height:  this.height, diameter: 175})
        this.body.position = ToBabylon([position[0], position[1],  this.height/2])

        this.position = position

        this.material = new BABYLON.StandardMaterial("material", scene);

        this.id = id

        if (id === 1){
            this.material.diffuseColor = new BABYLON.Color3.Red()
        } else if (id === 2){
            this.material.diffuseColor = new BABYLON.Color3.Blue()
        } else if (id === 3){
            this.material.diffuseColor = new BABYLON.Color3.Green()
        } else if (id === 4){
            this.material.diffuseColor = new BABYLON.Color3(242/255,87/255,15/255)
        }

        this.body.material = this.material
        return this
    }

    pressed(state){
        if (state){
            this.body.height = 3
            this.body.position = ToBabylon([this.position[0], this.position[1],  this.body.height/2])
            // this.material.emissiveColor = new BABYLON.Color3.White()
            if (this.id === 1){
                this.material.emissiveColor = new BABYLON.Color3.Red()
            } else if (this.id === 2){
                this.material.emissiveColor = new BABYLON.Color3.Blue()
            } else if (this.id === 3){
                this.material.emissiveColor = new BABYLON.Color3.Green()
            } else if (this.id === 4){
                this.material.emissiveColor = new BABYLON.Color3(242/255,87/255,15/255)
            }
        } else {
            this.body.height = this.height
            this.body.position = ToBabylon([this.position[0], this.position[1],  this.body.height/2])
            this.material.emissiveColor = new BABYLON.Color3.Black()
        }
    }
}


class ObstacleBox {
//todo: add default param for heigth
    constructor(scene, length, width, height, center_x, center_z, psi,type) {
        this.scene = scene;
        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: height, width: width, depth: length}, scene);
        this.body.rotation.y = psi

        this.body.position = ToBabylon([center_x, center_z, height/2])


        // this.collision_box_frame = new CollisionBoxFrame(this.scene)

        let texture= "./twipr_models/textures/walls_japanese.png";
        this.material = new BABYLON.StandardMaterial(this.scene);
        this.material.diffuseTexture = new BABYLON.Texture(texture, this.scene)
        this.material.diffuseTexture.uScale = 0.5
        this.material.diffuseTexture.vScale = 0.5
        this.material.specularColor = new BABYLON.Color3(0,0,0)
        this.body.receiveShadows = true;

        this.body.material = this.material

        return this;
    }

    setVisibility(visibility) {
        this.body.visibility = visibility
    }
}

class Door {
    constructor(scene, position, psi, length, id, visible) {
        this.position = position
        this.length = length
        this.psi = psi
        this.id = id

        this.height = 200

        this.scene = scene;
        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: this.height, width: length, depth: 10}, scene);
        this.body.rotation.y = psi

        this.body.position = ToBabylon([position[0], position[1], this.height/2])


         this.id = id
        this.material = new BABYLON.StandardMaterial("material", scene);
        this.body.material = this.material

        if (id === 1){
            this.material.diffuseColor = new BABYLON.Color3.Red()
        } else if (id === 2){
            this.material.diffuseColor = new BABYLON.Color3.Blue()
        } else if (id === 3){
            this.material.diffuseColor = new BABYLON.Color3.Green()
        } else if (id === 4){
            this.material.diffuseColor = new BABYLON.Color3(242/255,87/255,15/255)
        }

        this.setVisibility(visible)

        // let texture= "./twipr_models/textures/dark.png";
        // this.material = new BABYLON.StandardMaterial(this.scene);
        // this.material.diffuseTexture = new BABYLON.Texture(texture, this.scene)
        // this.material.diffuseTexture.uScale = 0.5
        // this.material.diffuseTexture.vScale = 0.5
        // this.material.specularColor = new BABYLON.Color3(0,0,0)
        //
        //
        // this.body.material = this.material

        // this.setVisibility(this.visible)
        return this
    }
    setVisibility(state) {
        if (state === 0){
            this.hide()
        } else {
            this.body.visibility = state
        }

    }

    hide(){
        this.body.visibility = 0
    }

    open(state){
        if (state) {
            this.body.scaling.y = 0
            this.body.position = ToBabylon([this.position[0], this.position[1], -this.height])
        } else {
            this.body.scaling.y = 1
            this.body.height = this.height
            this.body.position = ToBabylon([this.position[0], this.position[1], this.body.height/2])
        }

    }
}

class CollisionBoxFrame {
    constructor(scene, options) {
        this.scene = scene;
        const defaults = {
            length: 700,
            width: 700,
            height: 1,
        };
        options = {...defaults, ...options};

        this.options = options

        this.body = BABYLON.MeshBuilder.CreateBox('box', {height: options.height, width: options.length, depth: options.width}, scene);
        this.material = new BABYLON.StandardMaterial("material", scene);
        this.material.alpha = 0
        this.body.material = this.material
        this.body.enableEdgesRendering();
        this.body.edgesColor.copyFromFloats(1, 0, 1, 0.5);
        this.body.edgesWidth = 1000;
        this.body.edgesShareWithInstances = true;
        this.body.position.y = this.options.height/2

        this.old_width = this.options.width
        this.old_length = this.options.length

        return this;
    }

    set_size_position(max_x, min_x, max_y, min_y ){
        this.body.position.x = min_x + (max_x-min_x)/2
        this.body.position.z = -(min_y + (max_y-min_y)/2)
        var scaling_x = (max_x-min_x)/this.old_length
        var scaling_z = (max_y-min_y)/this.old_width
        this.body.scaling = new BABYLON.Vector3(scaling_x, 1, scaling_z);
    }
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
        this.body.position = ToBabylon([x*1000,y*1000,this.height/2])
        this.body.rotation.y = psi
    }

    setColour(collision) {
        // This fucntion is used to visualize a collision by changing the colour of a material to a certain colour (green/red)
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
            size: 30,
            id: 1,
        };
        options = {...defaults, ...options};

        this.sphere = BABYLON.MeshBuilder.CreateSphere("sphere", {diameter: options.size}, scene);
        this.sphere.position.y = 100


        var myMaterial = new BABYLON.StandardMaterial("myMaterial", this.scene);

        myMaterial.diffuseColor = new BABYLON.Color3(options.color[0],options.color[1],options.color[2]);
        myMaterial.emissiveColor = new BABYLON.Color3(1*options.color[0],1*options.color[1],1*options.color[2]);
        myMaterial.alpha = 0.75;


        this.sphere.material = myMaterial;

        return this;
    }
    setPosition(x, y) {
        this.sphere.position = ToBabylon([x,y,175])

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
        this.mesh.scaling.x = 1000
        this.mesh.scaling.y = 1000
        this.mesh.scaling.z = 1000

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
        this.mesh.position = ToBabylon([x*1000,y*1000,4])


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

        // this.canvas.width = window.innerWidth
        // this.canvas.height = window.innerHeight

        var json_objects = []

        // const localAxes = new BABYLON.AxesViewer(this.scene, 100);

        // Parameters: alpha, beta, radius, target position, scene
        // this.camera = new BABYLON.ArcRotateCamera("Camera", 0, 0, 20, new BABYLON.Vector3(0, 0, 0), this.scene);

        this.camera = new BABYLON.ArcRotateCamera("Camera", 0, 0, 20, ToBabylon([5094/2,3679/2,0]), this.scene);

        // Positions the camera overwriting alpha, beta, radius
        this.camera.setPosition(new BABYLON.Vector3(2506, 2818, 1987));
        // This attaches the camera to the canvas
        this.camera.attachControl(this.canvas, true);

        //increase angular speed
        this.camera.angularSensibilityY = 2500
        this.camera.angularSensibilityX = 2500
        //increase Zooming speed
        this.camera.wheelPrecision = 0.2;

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
        this.textbox.text = "fdsfd";
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

        $.getJSON("objects.json", function(json) {
            environment_objects = json['environment']
            robots = json['robots']
        });

        this.drawCoordinateSystem()
        this.buildEnvironment();

        return this.scene;
    }

    buildEnvironment() {
        // console.log(environment_objects)
        console.log(environment_objects)
         for (const [key, value] of Object.entries(environment_objects)) {
            console.log('creating object')
             value['babylon'] = new createBoxFromJson(this.scene,
                value["length"]*1000,
                value["width"]*1000,
                value["height"]*1000,
                value["center_x"]*1000,
                value["center_y"]*1000,
                value["psi"],
                // value["visible"]
                1
            )
             // console.log(value['type'])
             }

        // Robots
        for (const [key, value] of Object.entries(robots)) {
            value['babylon'] = new Robot(this.scene,
                value['id'],
                key,
                value['length']*1000,
                value['width']*1000,
                value['height'],
                value['position']*1000,
                value['psi'],
                this.shadowGenerator)
        }

    }

    drawCoordinateSystem() {
        const points_x = [
            ToBabylon([0,0,0]),
            ToBabylon([1000,0,0])
        ]
        const points_y = [
            ToBabylon([0,0,0]),
            ToBabylon([0,1000,0])
        ]
        const points_z = [
            ToBabylon([0,0,0]),
            ToBabylon([0,0,1000])
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

    //     this.textbox.text = 'Time: ' + sample['t'].toFixed(2) + ' s'
        // Robot
        var robot_data = sample['robots']
        for (const [key, value] of Object.entries(robot_data)) {
            if (key in robots) {
                console.log(robots[key])
                robots[key]['babylon'].setState(value['position'][0], value['position'][1], value['psi'])
                robots[key]['babylon'].setCollision(value['collision'])
            }
        }
    //
    //     var floor_data = sample['floor']
    //     for (const [key, value] of Object.entries(floor_data)) {
    //         if (key in floor_tiles) {
    //             floor_tiles[key]['babylon'].highlight(value['highlight'], value['discoverer'])
    //         }
    //     }
    //
    //     var wall_data = sample['walls']
    //     for (const [key, value] of Object.entries(wall_data)) {
    //         if (key in walls) {
    //             walls[key]['babylon'].setVisibility(value['visible'])
    //         }
    //     }
    //     var switch_data = sample['switches']
    //     for (const [key, value] of Object.entries(switch_data)) {
    //         if (key in switches) {
    //             switches[key]['babylon'].pressed(value['state'])
    //         }
    //     }
    //     var door_data = sample['doors']
    //     for (const [key, value] of Object.entries(door_data)) {
    //         if (key in doors) {
    //             doors[key]['babylon'].open(value['state'])
    //             doors[key]['babylon'].setVisibility(value['visible'])
    //         }
    //     }
    //     var goal_data = sample['goals']
    //     for (const [key, value] of Object.entries(goal_data)) {
    //         if (key in goals) {
    //             goals[key]['babylon'].setVisibility(value['visible'])
    //         }
    //     }
    }
}