function TrackBall() {
	this.translateMat = mat4.create();
	mat4.identity(this.translateMat);
	mat4.translate(this.translateMat,[0.,0,-10.]);
	this.rotateMat = mat4.create();
	mat4.identity(this.rotateMat);
	this.mouseX;
	this.mouseY;
	this.rotating = 1;
	this.translating = 0;
	this.zooming = 0;
	this.rotationGain=1.0;
	this.translationGain=.01; 
	this.zoomGain=.01; 
}
TrackBall.prototype.setMatrix = function( tbTransform )
{
	mat4.multiply(this.translateMat, this.rotateMat, tbTransform);
}
TrackBall.prototype.setRotating = function () {
	this.rotating = 1;
	this.translating = 0;
	this.zooming = 0;
}
TrackBall.prototype.setTranslating = function () {
	this.rotating = 0;
	this.translating = 1;
	this.zooming = 0;
}
TrackBall.prototype.setZooming = function () {
	this.rotating = 0;
	this.translating = 0;
	this.zooming = 1;
}
TrackBall.prototype.startDragging = function ( mouseX, mouseY ) {
	this.mouseX = mouseX;
	this.mouseY = mouseY;
}
TrackBall.prototype.drag = function ( mouseX, mouseY ) {
	var dx = mouseX - this.mouseX;
	var dy = this.mouseY - mouseY; // mouse Y axis is downward
	this.mouseX = mouseX;
	this.mouseY = mouseY;
	
	if( this.rotating == 1 ){
	var angle = Math.sqrt( dx*dx + dy*dy ); 
	var rotation = mat4.create();
	mat4.identity(rotation);
	mat4.rotate(rotation, degToRad(angle), [-dy,dx,0] );  // [-dy,dx,0] is perpendicular to [dx,dy,0]
	//console.log("dx, dy= ", dx,",",dy, "nrm = ",nrm);
	mat4.multiply( rotation, this.rotateMat, this.rotateMat ); // multiply to the left, since the rotation axis is given in world coordinates !
	}
	else if( this.translating==1 ){
		mat4.translate(this.translateMat, [
			dx * this.translationGain, 
			dy * this.translationGain, 
			0.]);
	}
	else if( this.zooming==1 ){
		mat4.translate(this.translateMat, [
			0., 
			0., 
			dy * this.zoomGain ]);		
		//console.log( mat4.str(this.translateMat));
	}
	
}
