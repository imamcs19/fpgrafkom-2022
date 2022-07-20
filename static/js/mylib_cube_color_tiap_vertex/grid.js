// grid

function Grid () {
	this.positions = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, this.positions);

	var vertices = [];
	var i;

	for(i = 0; i<nbX; i++)
	{
		pos = 3*(i);
		vertices[pos] = i*0.2;
		vertices[pos+1] = 0.0;
		vertices[pos+2] = 0.0;
	}

	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
	this.positions.itemSize = 3;
	this.positions.numItems = nbX ;

	/* pour chaque sommet on definit une couleur : 
	 * la couleur s'exprime en rouge, vert, bleu et alpha, donc 4 valeurs pour
	 * chaque sommet */
	/* COLOR
	maillageVertexColorBuffer = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, maillageVertexColorBuffer);
	var colors = [];
	for(i = 0; i<nbX; i++)
	{
		for(j = 0; j<nbZ; j++)
		{
			col = 4*(i*nbZ + j);
			colors[col] = 1.0;
			colors[col+1] = 0.0;
			colors[col+2] = 0.0;
			colors[col+3] = 1.0;
		}
	}
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.STATIC_DRAW);
	maillageVertexColorBuffer.itemSize = 4;
	maillageVertexColorBuffer.numItems = nbX * nbZ;
	*/
}


Grid.prototype.draw = function( shaderPgm )
{
	gl.bindBuffer(gl.ARRAY_BUFFER, this.positions);
	gl.vertexAttribPointer(shaderPgm.vertexPositionAttribute, this.positions.itemSize, gl.FLOAT, false, 0, 0);

	/* COLOR 
	gl.bindBuffer(gl.ARRAY_BUFFER, maillageVertexColorBuffer);
	gl.vertexAttribPointer(shaderPgm.vertexColorAttribute, maillageVertexColorBuffer.itemSize, gl.FLOAT, false, 0, 0);
	*/

	//setMatrixUniforms();
	gl.drawArrays(gl.POINTS, 0, this.positions.numItems);

	/* a utiliser pour la partie aretes (et faces)
	gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, maillageVertexIndicesBuffer);
	setMatrixUniforms();
	gl.drawElements(gl.LINES, maillageVertexIndicesBuffer.numItems, gl.UNSIGNED_SHORT, 0);
	*/

}



