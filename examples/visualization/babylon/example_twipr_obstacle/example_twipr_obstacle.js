class Wall {
    constructor(length,x,z,rotation) {
        this.x = x
        this.length = length
        this.z = z
        this.rotation = rotation
    }
}

class GroundBox {
    constructor(scene, options) {
        this.scene = scene;
        const defaults = {
            testbed_a : 4000,
            testbed_b : 6000,
            texture: "./twipr_models/textures/carpet_markings2.png",
            uscale: 12,
            vscale: 8
        };
        options = {...defaults, ...options};


        this.materialGround = new BABYLON.StandardMaterial(this.scene);
        this.materialGround.diffuseTexture = new BABYLON.Texture(options.texture, this.scene)
        this.materialGround.diffuseTexture.uScale = options.uscale
        this.materialGround.diffuseTexture.vScale = options.vscale
        this.materialGround.specularColor = new BABYLON.Color3(0,0,0)


        // TWIPR body
        this.gb = BABYLON.MeshBuilder.CreateBox('box', {height: 10, width: options.testbed_a, depth: options.testbed_b}, scene);
        this.gb.position.y = -5
        this.gb.material = this.materialGround;

        return this;
    }
}

class Goal {
    constructor(scene, maze, x,z, color, options) {
        this.scene = scene;
        const defaults = {
            a: 100,
            height:20,
        };
        options = {...defaults, ...options};


        this.material = new BABYLON.StandardMaterial(this.scene);
        this.material.diffuseColor = new BABYLON.Color3(color[0],color[1],color[2]);
        this.material.emissiveColor = new BABYLON.Color3(color[0],color[1],color[2]);
        this.material.alpha = 1;

        this.mesh = BABYLON.MeshBuilder.CreateBox('box', {height: options.a, width: options.a, depth: options.a}, scene);
        this.mesh.position.y = options.a/2 + options.height
        this.mesh.position.x = x
        this.mesh.position.z = z
        this.mesh.material = this.material;

        const anim = new BABYLON.Animation("wheelAnimation", "rotation.y", 30, BABYLON.Animation.ANIMATIONTYPE_FLOAT, BABYLON.Animation.ANIMATIONLOOPMODE_CYCLE);


        const keys = [];

        const offset = this.getRandomArbitrary(0,360)
        keys.push({
            frame: 0,
            value: offset
        });

        keys.push({
            frame: 240,
            value: 2 * Math.PI + offset
        });

        anim.setKeys(keys)

        this.mesh.animations = []
        this.mesh.animations.push(anim)
        this.scene.beginAnimation(this.mesh,0,240,true);

        // this.light = new BABYLON.PointLight("", new BABYLON.Vector3(this.mesh.position.x, 0, this.mesh.position.z), this.scene);
        // this.light.intensity = 1
        // this.light.diffuse = this.material.emissiveColor
        //
        // this.shadowGenerator = new BABYLON.ShadowGenerator(512, this.light);
        //
        // for (const m of maze.meshes){
        //      this.shadowGenerator.addShadowCaster(m)
        // }
        // this.shadowGenerator.usePoissonSampling = true;
        return this;
    }

    hide(){
        this.mesh.setEnabled(false)
    }

    show(){
        this.mesh.setEnabled(true)
    }

    getRandomArbitrary(min, max) {
        return Math.random() * (max - min) + min;
    }
}


class Obstacle {
    constructor(scene, x,z,rotation, options) {
        this.scene = scene;
        const defaults = {
            diameter: 20,
            color : [0.8,0.8,0.8],
            height: 120,
            length: 500
        };
        options = {...defaults, ...options};


        this.material = new BABYLON.StandardMaterial(this.scene);
        this.material.diffuseColor = new BABYLON.Color3(options.color[0],options.color[1],options.color[2]);
        this.material.alpha = 1;

        this.mesh = BABYLON.MeshBuilder.CreateCylinder("cone", {diameterTop: options.diameter, tessellation: 0,
        diameter: options.diameter, height: options.length}, this.scene);

        this.mesh.rotation.z = Math.PI/2
        this.mesh.position.x = x
        this.mesh.position.z = z
        this.mesh.position.y = options.diameter/2 + options.height
        this.mesh.rotation.y = rotation
        this.mesh.material = this.material

        return this;
    }

    hide(){
        this.mesh.setEnabled(false)
    }

    show(){
        this.mesh.setEnabled(true)
    }
}

function factorialize(num) {
  if (num < 0)
        return -1;
  else if (num === 0)
      return 1;
  else {
      return (num * factorialize(num - 1));
  }
}

// #####################################################################################################################
class TWIPR_Scene_Example_Obstacle extends Scene {
    constructor(id, options) {
        const defaults = {

        };
        options = {...defaults, ...options};
        super(id);
        this.options = options;
        this.createScene();
    }

    createScene() {

        // Parameters: alpha, beta, radius, target position, scene
        this.camera = new BABYLON.ArcRotateCamera("Camera", 0, 0, 20, new BABYLON.Vector3(0, 0, 0), this.scene);

        // Positions the camera overwriting alpha, beta, radius
        this.camera.setPosition(new BABYLON.Vector3(-2231, 1025, 37));

        this.camera.setPosition(new BABYLON.Vector3(-3103, 1425, 52));

        this.camera.setPosition(new BABYLON.Vector3(-2473, 1425, 1874));



        // This attaches the camera to the canvas
        this.camera.attachControl(this.canvas, true);

        this.camera.angularSensibilityY = 5000000
        this.camera.angularSensibilityX = 5000

        //This creates a light, aiming 0,1,0 - to the sky (non-mesh)
        this.light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0.5,1,0), this.scene);
        this.light.intensity = 0.5

	    this.light3 = new BABYLON.PointLight("pointLight", new BABYLON.Vector3(-1500, 2000, -1500), this.scene);
	    this.light3.intensity = 0.5;
        this.shadowGenerator = new BABYLON.ShadowGenerator(2048, this.light3);

        this.light4 = new BABYLON.PointLight("pointLight2", new BABYLON.Vector3(1500, 2000, 1500), this.scene);
	    this.light4.intensity = 0.25;

        this.scene.clearColor = new BABYLON.Color3(1,1,1);



        this.ui = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("ui", true, this.scene);

        // Textbox
        this.textbox = new BABYLON.GUI.TextBlock();
        this.textbox.fontSize = 12;
        this.textbox.text = "";
        this.textbox.color = "black";
        this.textbox.paddingTop = 3;
        this.textbox.paddingLeft = 3;
        this.textbox.textVerticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
        this.textbox.textHorizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
        this.ui.addControl(this.textbox);

        this.twipr = []
        this.twipr.push(new TWIPR_Realistic_1(this.scene, this.shadowGenerator, {'id': 1, 'indicator': false}))


        this.groundBox = new GroundBox(this.scene, {'testbed_a': 500, 'testbed_b': 4000, 'texture': "./twipr_models/textures/grunge1_tiles.png", 'uscale': 8, 'vscale': 1})

        this.pole1 = BABYLON.MeshBuilder.CreateBox('box', {height: 140, width: 20, depth: 20}, this.scene);
        this.pole1.position.y = 140/2
        this.pole1.position.x = 240
        this.pole1.position.z = 0

        this.pole2 = BABYLON.MeshBuilder.CreateBox('box', {height: 140, width: 20, depth: 20}, this.scene);
        this.pole2.position.y = 140/2
        this.pole2.position.x = -240
        this.pole2.position.z = 0

        this.material_pole = new BABYLON.StandardMaterial(this.scene);
        this.material_pole.diffuseColor = new BABYLON.Color3(0.5,0.5,0.5);
        this.material_pole.alpha = 1;

        this.pole3 = BABYLON.MeshBuilder.CreateBox('box', {height: 20, width: 500, depth: 20}, this.scene);
        this.pole3.position.y = -10+140
        this.pole3.position.z = 0
        this.pole3.position.x = 0

        this.pole3.material = this.material_pole
        this.pole1.material = this.material_pole
        this.pole2.material = this.material_pole


        this.shadowGenerator.usePoissonSampling = true;

        this.groundBox.gb.receiveShadows = true;

        //
        // if (BABYLON.VideoRecorder.IsSupported(this.engine)) {
        //     var recorder = new BABYLON.VideoRecorder(this.engine);
        //     recorder.startRecording("test.webm", 60);
        // }

        return this.scene;
    }
    onSample(sample) {
        this.textbox.text = 'Time: ' + sample['t'].toFixed(2) + ' s';

        // Robots
        for (let i = 0; i < this.twipr.length; i++) {
            let twipr_signal = sample[i+1]
            this.twipr[i].setPosition(twipr_signal['x'], twipr_signal['y']);
            this.twipr[i].setOrientation(twipr_signal['theta'], twipr_signal['psi']);
        }
    }
}

BABYLON.ArcRotateCamera.prototype.spinTo = function (whichprop, targetval, speed) {
    var ease = new BABYLON.CubicEase();
    ease.setEasingMode(BABYLON.EasingFunction.EASINGMODE_EASEINOUT);
	BABYLON.Animation.CreateAndStartAnimation('at4', this, whichprop, speed, 120, this[whichprop], targetval, 0, ease);
}