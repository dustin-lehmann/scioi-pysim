var world_objects = {}


// =====================================================================================================================
class PysimScene extends Scene {
    constructor(id, config) {

        super(id);
        this.config = config
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
        this.light1.intensity = 1

        // --- BACKGROUND ---
        this.scene.clearColor = new BABYLON.Color3(0.75,0.75,0.75);

        // --- Textbox ---
        this.ui = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("ui", true, this.scene);
        this.textbox_time = new BABYLON.GUI.TextBlock();
        this.textbox_time.fontSize = 40;
        this.textbox_time.text = "";
        this.textbox_time.color = "black";
        this.textbox_time.paddingTop = 3;
        this.textbox_time.paddingLeft = 3;
        this.textbox_time.textVerticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
        this.textbox_time.textHorizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
        this.ui.addControl(this.textbox_time);

        this.textbox_status = new BABYLON.GUI.TextBlock();
        this.textbox_status.fontSize = 40;
        this.textbox_status.text = "";
        this.textbox_status.color = "black";
        this.textbox_status.paddingTop = 3;
        this.textbox_status.paddingRight = 30;
        this.textbox_status.textVerticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
        this.textbox_status.textHorizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_RIGHT
        this.ui.addControl(this.textbox_status);


        this.textbox_title = new BABYLON.GUI.TextBlock();
        this.textbox_title.fontSize = 40;
        this.textbox_title.text = "";
        this.textbox_title.color = "black";
        this.textbox_title.paddingTop = 3;
        this.textbox_title.paddingLeft = 3;
        this.textbox_title.textVerticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
        this.textbox_title.textHorizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_CENTER;
        this.ui.addControl(this.textbox_title);

        // --- Coordinate System ---
        this.drawCoordinateSystem(0.25)

        // --- GENERATION OF OBJECTS ---
        this.buildWorld()



        // --- WEBAPP CONFIG ---
        if ('webapp_config' in this.config){
            if ('title' in this.config['webapp_config']){
                this.textbox_title.text = this.config['webapp_config']['title']
            }
        }

        return this.scene;
    }

    buildWorld() {
        // Check if the config has the appropriate entries:
        if (!("world" in this.config)){
            console.warn("No world definition in the config")
            return
        }
        if (!('objects' in this.config['world'])){
            console.warn("No world objects specified in the config")
            return
        }

        // Loop over the config and extract the objects
        for (const [key, value] of Object.entries(this.config['world']['objects'])){
            // Check if the object type is in the object config
            let babylon_object_name
            if (value.object_type in this.config['object_config']){
                babylon_object_name = this.config['object_config'][value.object_type]['BabylonObject']
                let objectPtr = eval(babylon_object_name)
                world_objects[key] = new objectPtr(this.scene, key, value.object_type, value, this.config['object_config'][value.object_type]['config'])
            } else {
                console.warn("Cannot find the object type in the object definition")
            }
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
        if ('world' in sample){
            for (const [key, value] of Object.entries(sample['world']['objects'])){
                if (key in world_objects){
                    world_objects[key].update(value)
                }
            }
        } else {
            console.warn("No world data in current sample")
        }
        if ('time' in sample){
            this.textbox_time.text = 'Time: ' + sample['time'] + ' s'
        } else {
            console.warn("No time data in current sample")
        }

        if ('status' in sample){
            this.textbox_status.text = sample['status']
        }
    }
}