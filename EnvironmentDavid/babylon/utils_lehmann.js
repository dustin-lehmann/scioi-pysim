class TiledGround{
    constructor(scene,a,b,color1,color2){
        var grid = {
            'h' : 16,
            'w' : 16
        };

        this.tiledGround = new BABYLON.MeshBuilder.CreateTiledGround("Tiled Ground", {xmin: -a/2, zmin: -b/2, xmax: a/2, zmax: b/2, subdivisions: grid}, scene);

    //Create the multi material
    // Create differents material_textures
    this.whiteMaterial = new BABYLON.StandardMaterial("White", scene);
    this.whiteMaterial.diffuseColor = new BABYLON.Color3(color1[0],color1[1],color1[2]);
    this.whiteMaterial.specularColor = new BABYLON.Color3(0, 0, 0);

    this.blackMaterial = new BABYLON.StandardMaterial("White", scene);
    this.blackMaterial.diffuseColor = new BABYLON.Color3(color2[0],color2[1],color2[2]);
    this.blackMaterial.specularColor = new BABYLON.Color3(0, 0, 0);

    // Create Multi Material
    this.multimat = new BABYLON.MultiMaterial("multi", scene);
    this.multimat.subMaterials.push(this.whiteMaterial);
    this.multimat.subMaterials.push(this.blackMaterial);


    // Apply the multi material
    // Define multimat as material of the tiled ground
    this.tiledGround.material = this.multimat;

    // Needed variables to set subMeshes
    this.verticesCount = this.tiledGround.getTotalVertices();
    this.tileIndicesLength = this.tiledGround.getIndices().length / (grid.w * grid.h);

    // Set subMeshes of the tiled ground
    this.tiledGround.subMeshes = [];
    var base = 0;
    for (var row = 0; row < grid.h; row++) {
        for (var col = 0; col < grid.w; col++) {
            this.tiledGround.subMeshes.push(new BABYLON.SubMesh(row%2 ^ col%2, 0, this.verticesCount, base , this.tileIndicesLength, this.tiledGround));
            base += this.tileIndicesLength;
        }
    }
}
}