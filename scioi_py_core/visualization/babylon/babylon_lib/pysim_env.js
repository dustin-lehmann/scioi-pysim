var world_objects = {}


// =====================================================================================================================
class PysimScene extends Scene {
    constructor(id, config) {

        super(id);
        this.config = config
        console.log("Config")
        console.log(this.config)
        this.createScene();
    }

    createScene() {
        // --- CAMERA ---
        this.camera = new BABYLON.ArcRotateCamera("Camera", 0, 0, 20, new BABYLON.Vector3(0,0,0), this.scene);
        this.camera.setPosition(new BABYLON.Vector3(-0.02, 2.278,2.24));
        this.camera.attachControl(this.canvas, true);
        this.camera.wheelPrecision = 100;
        // --- LIGHTS ---
        this.light1 = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0.5,1,0), this.scene);
        this.light1.intensity = 0.5

        // --- BACKGROUND ---
        this.scene.clearColor = new BABYLON.Color3(0.75,0.75,0.75);

        // --- Textbox ---
        this.ui = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("ui", true, this.scene);
        this.textbox_time = new BABYLON.GUI.TextBlock();
        this.textbox_time.fontSize = 40;
        this.textbox_time.text = "Time";
        this.textbox_time.color = "black";
        this.textbox_time.paddingTop = 40;
        this.textbox_time.paddingLeft = 3;
        this.textbox_time.textVerticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
        this.textbox_time.textHorizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
        this.ui.addControl(this.textbox_time);

        this.textbox_status = new BABYLON.GUI.TextBlock();
        this.textbox_status.fontSize = 40;
        this.textbox_status.text = "STATUS MESSAGES";
        this.textbox_status.color = "black";
        this.textbox_status.paddingTop = 80;
        this.textbox_status.paddingLeft = 3;
        this.textbox_status.textVerticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
        this.textbox_status.textHorizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
        this.ui.addControl(this.textbox_status);


        this.textbox_title = new BABYLON.GUI.TextBlock();
        this.textbox_title.fontSize = 40;
        this.textbox_title.text = "Title";
        this.textbox_title.color = "black";
        this.textbox_title.paddingTop = 3;
        this.textbox_title.paddingLeft = 3;
        this.textbox_title.textVerticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
        this.textbox_title.textHorizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
        this.ui.addControl(this.textbox_title);

        // --- Coordinate System ---
        this.drawCoordinateSystem(0.25)

        // --- GENERATION OF OBJECTS ---
        this.buildWorld()

        var box1 = new PysimBox(this.scene, 0.2,0.1,0.05,[0,0,0],'')
        var box2 = new PysimBox(this.scene, 0.2,0.1,0.05,[1,0,0],'',{color: [0,1,0]})
        var box3 = new PysimBox(this.scene, 0.2,0.1,0.05,[0,1,0],'',{color: [0,0,1]})
        var box4 = new PysimBox(this.scene, 0.2,0.1,0.05,[0,0,1],'',{color: [0,1,1]})


        return this.scene;
    }

    buildWorld() {
        // Check if the config has the appropriate entries:
        if (!("world" in this.config['environment'])){
            console.warn("No world definition in the config")
            return
        }
        if (!('objects' in this.config['environment']['world'])){
            console.warn("No world objects specified in the config")
            return
        }

        // Loop over the config and extract the objects
        for (const [key, value] of Object.entries(this.config['environment']['world']['objects'])){
            console.log(key)
        }
    }

    // -----------------------------------------------------------------------------------------------------------------
    drawCoordinateSystem(length) {
        const points_x = [
            ToBabylon([0, 0, 0]),
            ToBabylon([length, 0, 0])
        ]
        const points_y = [
            ToBabylon([0, 0, 0]),
            ToBabylon([0, length, 0])
        ]
        const points_z = [
            ToBabylon([0, 0, 0]),
            ToBabylon([0, 0, length])
        ]
        new BABYLON.Color3(1, 0, 0);
        var line_x = BABYLON.MeshBuilder.CreateLines("line_x", {points: points_x}, this.scene);
        line_x.color = new BABYLON.Color3(1, 0, 0);

        var line_y = BABYLON.MeshBuilder.CreateLines("line_y", {points: points_y}, this.scene);
        line_y.color = new BABYLON.Color3(0, 1, 0);

        var line_z = BABYLON.MeshBuilder.CreateLines("line_z", {points: points_z}, this.scene);
        line_z.color = new BABYLON.Color3(0, 0, 1);
    }

    // -----------------------------------------------------------------------------------------------------------------
    onSample(sample) {
        // console.log(this.camera.position)
        // console.log(sample)
    }
}