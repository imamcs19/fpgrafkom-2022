

var getSource = function(url) {
  var req = new XMLHttpRequest();
  req.open("GET", url, false);
  req.send(null);
  return (req.status == 200) ? req.responseText : null;
};


function getShader(gl, id) {
	var shaderScript = document.getElementById(id);
	if (!shaderScript) {
		return null;
	}

	var str = "";
	var k = shaderScript.firstChild;
	while (k) {
		if (k.nodeType == 3) {
			str += k.textContent;
		}
		k = k.nextSibling;
	}

	var shader;
	if (shaderScript.type == "x-shader/x-fragment") {
		shader = gl.createShader(gl.FRAGMENT_SHADER);
	} else if (shaderScript.type == "x-shader/x-vertex") {
		shader = gl.createShader(gl.VERTEX_SHADER);
	} else {
		return null;
	}

	gl.shaderSource(shader, str);
	gl.compileShader(shader);

	if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
		alert(gl.getShaderInfoLog(shader));
		return null;
	}

	return shader;
}



function initShader( vertexShaderName, fragmentShaderName ) {
	var fragmentShader = getShader(gl, fragmentShaderName );
	var vertexShader = getShader(gl, vertexShaderName );

	var shaderPgm = gl.createProgram();
	gl.attachShader(shaderPgm, vertexShader);
	gl.attachShader(shaderPgm, fragmentShader);
	gl.linkProgram(shaderPgm);

	if (!gl.getProgramParameter(shaderPgm, gl.LINK_STATUS)) {
		alert("Could not initialise shaders");
	}


	shaderPgm.vertexPositionAttribute = gl.getAttribLocation(shaderPgm, "aVertexPosition");
	gl.enableVertexAttribArray(shaderPgm.vertexPositionAttribute);

	/* COLOR */
	shaderPgm.vertexColorAttribute = gl.getAttribLocation(shaderPgm, "aVertexColor");
	gl.enableVertexAttribArray(shaderPgm.vertexColorAttribute);
	

	shaderPgm.pMatrixUniform = gl.getUniformLocation(shaderPgm, "uPMatrix");
	shaderPgm.mvMatrixUniform = gl.getUniformLocation(shaderPgm, "uMVMatrix");
	
   return shaderPgm;
}

function initShader2( vertexShaderName, fragmentShaderName ) {
	var fragmentShader = getShader(gl, fragmentShaderName );
	var vertexShader = getShader(gl, vertexShaderName );

	var shaderPgm = gl.createProgram();
	gl.attachShader(shaderPgm, vertexShader);
	gl.attachShader(shaderPgm, fragmentShader);
	gl.linkProgram(shaderPgm);

	if (!gl.getProgramParameter(shaderPgm, gl.LINK_STATUS)) {
		alert("Could not initialise shaders");
	}


	shaderPgm.vertexPositionAttribute = gl.getAttribLocation(shaderPgm, "aVertexPosition");
	gl.enableVertexAttribArray(shaderPgm.vertexPositionAttribute);
	

	shaderPgm.pMatrixUniform = gl.getUniformLocation(shaderPgm, "uPMatrix");
	shaderPgm.mvMatrixUniform = gl.getUniformLocation(shaderPgm, "uMVMatrix");
	
   return shaderPgm;
}




