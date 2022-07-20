function Frame () 
{
	this.positions = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, this.positions);
	vertices = [
		0.0, 0.0, 0.0,
		1.0, 0.0, 0.0,

		0.0, 0.0, 0.0,
		0.0, 1.0, 0.0,

		0.0, 0.0, 0.0,
		0.0, 0.0, 1.0
			];
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
	this.positions.itemSize = 3;
	this.positions.numItems = 6;

	this.colors = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, this.colors);
	cols = [
		1.0, 0.0, 0.0, 1.0,
		1.0, 0.0, 0.0, 1.0,

		0.0, 1.0, 0.0, 1.0,
		0.0, 1.0, 0.0, 1.0,

		0.0, 0.0, 1.0, 1.0,
		0.0, 0.0, 1.0, 1.0
			];
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(cols), gl.STATIC_DRAW);
	this.colors.itemSize = 4;
	this.colors.numItems = 6;

}
Frame.prototype.draw = function ( shaderPgm, lineWidth )
{
	gl.bindBuffer(gl.ARRAY_BUFFER, this.positions);
	gl.vertexAttribPointer(shaderPgm.vertexPositionAttribute, this.positions.itemSize, gl.FLOAT, false, 0, 0);
	
	gl.bindBuffer(gl.ARRAY_BUFFER, this.colors);
	gl.vertexAttribPointer(shaderPgm.vertexColorAttribute, this.colors.itemSize, gl.FLOAT, false, 0, 0);
	
	gl.lineWidth( lineWidth );
	gl.drawArrays(gl.LINES, 0, this.positions.numItems);
}
