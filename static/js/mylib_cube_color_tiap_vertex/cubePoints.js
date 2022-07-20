// Cube drawn using points

function CubePoints () 
{
	/** Vertex positions */
	this.vertexBuffer = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, this.vertexBuffer );
	var vertices = [
		-1.0,-1.0,-1.0,
		 1.0,-1.0,-1.0,
		 1.0, 1.0,-1.0,
		-1.0, 1.0,-1.0,
		-1.0,-1.0, 1.0,
		 1.0,-1.0, 1.0,
		 1.0, 1.0, 1.0,
		-1.0, 1.0, 1.0
	];
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
	this.vertexBuffer.itemSize = 3;
	this.vertexBuffer.numItems = 8 ;
	
	
	/** Vertex colors */
	this.colorBuffer = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, this.colorBuffer );
	var colors = [
		 0.0, 0.0, 0.0, 1.0,
		 1.0, 0.0, 0.0, 1.0,
		 1.0, 1.0, 0.0, 1.0,
		 0.0, 1.0, 0.0, 1.0,
		 0.0, 0.0, 1.0, 1.0,
		 1.0, 0.0, 1.0, 1.0,
		 1.0, 1.0, 1.0, 1.0,
		 0.0, 1.0, 1.0, 1.0
	];
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.STATIC_DRAW);
	this.colorBuffer.itemSize = 4;
	this.colorBuffer.numItems = 8 ;
}

CubePoints.prototype.draw = function( shaderPgm )
{
	/* Vertex positions */
	gl.bindBuffer(gl.ARRAY_BUFFER, this.vertexBuffer);
	gl.vertexAttribPointer(shaderPgm.vertexPositionAttribute, this.vertexBuffer.itemSize, gl.FLOAT, false, 0, 0);

	/* Vertex colors */
	gl.bindBuffer(gl.ARRAY_BUFFER, this.colorBuffer);
	gl.vertexAttribPointer(shaderPgm.vertexColorAttribute, this.colorBuffer.itemSize, gl.FLOAT, false, 0, 0);

	/* Do the drawing */
	gl.drawArrays(gl.POINTS, 0, this.vertexBuffer.numItems);
}


