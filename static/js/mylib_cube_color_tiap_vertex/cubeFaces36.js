/// Cube with one color per face

function CubeFaces36 () 
{
	// Vertex positions
	this.vertexBuffer = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, this.vertexBuffer );
	var vertices = [
		// Z-
		-1.0,-1.0,-1.0, // 0
		 1.0, 1.0,-1.0, // 2
		 1.0,-1.0,-1.0, // 1
		-1.0,-1.0,-1.0, // 0
		-1.0, 1.0,-1.0, // 3
		 1.0, 1.0,-1.0, // 2

		// Y-
		-1.0,-1.0,-1.0, // 0
		 1.0,-1.0,-1.0, // 1
		 1.0,-1.0, 1.0, // 5
		-1.0,-1.0,-1.0, // 0
		 1.0,-1.0, 1.0, // 5
		-1.0,-1.0, 1.0, // 4
		
		// X+
		 1.0,-1.0,-1.0, // 1
		 1.0, 1.0,-1.0, // 2
		 1.0, 1.0, 1.0, // 6
		 1.0,-1.0,-1.0, // 1
		 1.0, 1.0, 1.0, // 6
		 1.0,-1.0, 1.0, // 5
		 
		// Y+
		 1.0, 1.0,-1.0, // 2
		-1.0, 1.0, 1.0, // 7
		 1.0, 1.0, 1.0, // 6
		 1.0, 1.0,-1.0, // 2
		-1.0, 1.0,-1.0, // 3
		-1.0, 1.0, 1.0, // 7

		// X-
		-1.0, 1.0,-1.0, // 3
		-1.0,-1.0, 1.0, // 4
		-1.0, 1.0, 1.0, // 7
		-1.0, 1.0,-1.0, // 3
		-1.0,-1.0,-1.0, // 0
		-1.0,-1.0, 1.0, // 4

		// Z+		 
		-1.0,-1.0, 1.0, // 4
		 1.0,-1.0, 1.0, // 5
		 1.0, 1.0, 1.0, // 6
		-1.0,-1.0, 1.0, // 4
		 1.0, 1.0, 1.0, // 6
		-1.0, 1.0, 1.0, // 7
		];
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
	this.vertexBuffer.itemSize = 3;
	this.vertexBuffer.numItems = 36 ;
		
	// Vertex colors
	this.colorBuffer = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, this.colorBuffer );
	var colors = [
		 1.0, 0.0, 0.0, 1.0, // red
		 1.0, 0.0, 0.0, 1.0, // red
		 1.0, 0.0, 0.0, 1.0, // red
		 1.0, 0.0, 0.0, 1.0, // red
		 1.0, 0.0, 0.0, 1.0, // red
		 1.0, 0.0, 0.0, 1.0, // red
		 1.0, 1.0, 0.0, 1.0, // yellow
		 1.0, 1.0, 0.0, 1.0, // yellow
		 1.0, 1.0, 0.0, 1.0, // yellow
		 1.0, 1.0, 0.0, 1.0, // yellow
		 1.0, 1.0, 0.0, 1.0, // yellow
		 1.0, 1.0, 0.0, 1.0, // yellow
		 0.0, 1.0, 0.0, 1.0, // green
		 0.0, 1.0, 0.0, 1.0, // green
		 0.0, 1.0, 0.0, 1.0, // green
		 0.0, 1.0, 0.0, 1.0, // green
		 0.0, 1.0, 0.0, 1.0, // green
		 0.0, 1.0, 0.0, 1.0, // green
		 0.0, 0.0, 1.0, 1.0, // blue
		 0.0, 0.0, 1.0, 1.0, // blue
		 0.0, 0.0, 1.0, 1.0, // blue
		 0.0, 0.0, 1.0, 1.0, // blue
		 0.0, 0.0, 1.0, 1.0, // blue
		 0.0, 0.0, 1.0, 1.0, // blue
		 1.0, 0.0, 1.0, 1.0, // magenta
		 1.0, 0.0, 1.0, 1.0, // magenta
		 1.0, 0.0, 1.0, 1.0, // magenta
		 1.0, 0.0, 1.0, 1.0, // magenta
		 1.0, 0.0, 1.0, 1.0, // magenta
		 1.0, 0.0, 1.0, 1.0, // magenta
		 0.0, 1.0, 1.0, 1.0,  // cyan
		 0.0, 1.0, 1.0, 1.0,  // cyan
		 0.0, 1.0, 1.0, 1.0,  // cyan
		 0.0, 1.0, 1.0, 1.0,  // cyan
		 0.0, 1.0, 1.0, 1.0,  // cyan
		 0.0, 1.0, 1.0, 1.0,  // cyan
	];
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.STATIC_DRAW);
	this.colorBuffer.itemSize = 4;
	this.colorBuffer.numItems = 36 ;
}

CubeFaces36.prototype.draw = function( shaderPgm )
{
	// Vertex positions 
	gl.bindBuffer(gl.ARRAY_BUFFER, this.vertexBuffer);
	gl.vertexAttribPointer(shaderPgm.vertexPositionAttribute, this.vertexBuffer.itemSize, gl.FLOAT, false, 0, 0);

	// Vertex colors
	gl.bindBuffer(gl.ARRAY_BUFFER, this.colorBuffer);
	gl.vertexAttribPointer(shaderPgm.vertexColorAttribute, this.colorBuffer.itemSize, gl.FLOAT, false, 0, 0);

	// Draw triangles
	gl.drawArrays(gl.TRIANGLES, 0, this.vertexBuffer.numItems);
}


