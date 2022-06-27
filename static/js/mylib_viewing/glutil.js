/*
    This file defines some common functions that are useful for WebGL.
    Also defines the class SimpleView3D, which allows *very* basic 3D,
    and a function for installing a mourse drag feature for use with
    SimpleView3D.  It ensures that requestAnimationFrame() is
    available, and it defines an Animator class to help with animation.
    Finally, it defines a function for loading a file with AJAX.
*/

/**
 * Creates a program for use in the WebGL context gl, and returns the
 * identifier for that program.  If an error occurs while compiling or
 * linking the program, an exception of type String is thrown.  The
 * string contains the compilation or linking error.  If no error occurs,
 * the program identifier is the return value of the function.
 */
function createProgram(gl, vertexShaderSource, fragmentShaderSource) {
   var vsh = gl.createShader( gl.VERTEX_SHADER );
   gl.shaderSource(vsh,vertexShaderSource);
   gl.compileShader(vsh);
   if ( ! gl.getShaderParameter(vsh, gl.COMPILE_STATUS) ) {
      throw "Error in vertex shader:  " + gl.getShaderInfoLog(vsh);
   }
   var fsh = gl.createShader( gl.FRAGMENT_SHADER );
   gl.shaderSource(fsh, fragmentShaderSource);
   gl.compileShader(fsh);
   if ( ! gl.getShaderParameter(fsh, gl.COMPILE_STATUS) ) {
      throw "Error in fragment shader:  " + gl.getShaderInfoLog(fsh);
   }
   var prog = gl.createProgram();
   gl.attachShader(prog,vsh);
   gl.attachShader(prog, fsh);
   gl.linkProgram(prog);
   if ( ! gl.getProgramParameter( prog, gl.LINK_STATUS) ) {
      throw "Link error in program:  " + gl.getProgramInfoLog(prog);
   }
   return prog;
}

/**
 * Get all the text content from an HTML element (including
 * any text in contained elements.)  The text is returned
 * as a string.
 * @param elem either a string giving the id of an element, or
 *    the elemnent node itself.  If neither of these is the
 *    case, an exception of type string is thrown.
 */
function getElementText(elem) {
    if (typeof(elem) == "string")
        elem = document.getElementById(elem);
    if (!elem.firstChild)
        throw "argument to getTextFromElement is not an element or the id of an element";
    var str = "";
    var node = elem.firstChild;
    while (node) {
        if (node.nodeType == 3) // text node
            str += node.nodeValue;
        else if (node.nodeType == 1) // element
            str += getTextFromElement(node);
        node = node.nextSibling;
    }
    return str;
}

/**
 * Create a WebGL drawing context for a canvas element.  The parameter can
 * be either a string that is the id of a canvas element, or it can be the
 * canvas element itself.
 */
function createWebGLContext(canvas) {
   var c;
   if ( ! canvas )
      throw "Canvas required";
   if (typeof canvas == "string")
      c = document.getElementById(canvas);
   else
      c = canvas;
   if ( ! c.getContext )
      throw "No legal canvas provided";
   var gl = c.getContext("webgl");
   if ( ! gl ) {
      gl = c.getContext("experimental-webgl");
   }  
   if ( ! gl )
      throw "Can't create WebGLContext";
   return gl;
}

/**
 * A convenience function, used during debugging, which checks whether a
 * GL error has occured in the drawing context, gl.  The method returns null
 * if no error has occurred, and retuns a string that describes the error if
 * one has occurred.  (The string is a little more useful than the native GL
 * error code.)  Note that once an error occurs, GL retains that error until
 * gl.getError() is called, so you can't assume that the error occurred on
 * the error occurred in the line that precedes the call to this function.
 */
function checkGLError(gl) {
      var e = gl.getError();
      if ( e == gl.NO_ERROR )
         return null;
      else if ( e == gl.INVALID_ENUM )
         return "Invalid constant";
      else if ( e == gl.INVALID_VALUE )
         return "Numeric argument out of range.";
      else if ( e == gl.INVALID_OPERATION )
         return "Invalid operation for current state.";
      else if ( e == gl.OUT_OF_MEMORY )
         return "Out of memory.";
      else
         return "??? Unknown error ???";
}

/**
 * The following statement makes sure that requestAnimationFrame
 * is available as a fuction, using a browser-specific version if 
 * available or falling back to setTimeout if necessary.  Call
 * requestAnimationFrame(callbackFunction) to set up a call to
 * callbackFunction.  callbackFunction is called with a parameter
 * that gives the current time.  
 */
window.requestAnimationFrame = 
    window.requestAnimationFrame ||
    window.mozRequestAnimationFrame ||
    window.webkitRequestAnimationFrame ||
    window.msRequestAnimationFrame ||
    function (callback) {
        setTimeout(function() { callback(Date.now()); },  1000/60);
    }

/**
 * This constructor defines the class Animator.  An Animator runs
 * an animation by calling a callback function over and over again.
 * The constructor requires one parameter, which must be a callback
 * function.  Ordinarily, this should be a function with one parameter,
 * which will represent the number of milliseconds for which the
 * animation has beeen running.  If the animation is paused, by
 * calling the stop() method, and then restarted, the the time for
 * which the animation was paused is NOT included in the parameter
 * to callback.  (callback is actually called with two parameters,
 * where the second parameter is the number of millisconds since
 * the animation was started; if the animation was never paused,
 * then the two parameters are the same.)
 *    After creating an Animation, you must call its start() method
 * to start the animation.  Call the stop() method to pause the
 * animation.  As an alternative to start/stop, you can call
 * setAnimating(x) with x = true/false.  The method isAnimating
 * returns true if the animation is running, false if it is paused.
 *    The constructor throws an exception of type string if the
 * first parameter is absent or is not a function.  (Extra 
 * parameters are ignored.)
 *    (The animation uses requestAnimationFrame if available;
 * otherwise, it uses setTimeout.)
 */
function Animator(callback) {
   if ( ! callback || ! (typeof callback == "function") ) {
      throw "Callback function required for Animator";
   }
   var animating = false;
   var animationStartTime;
   var timePaused = 0;
   var pauseStart;
   var reqAnimFrm = window.requestAnimationFrame || 
        window.mozRequestAnimationFrame ||
        window.webkitRequestAnimationFrame ||
        window.msRequestAnimationFrame ||
        function (frame) {
           setTimeout(function() { frame(Date.now()); },  1000/60);
        }
   function doFrm( time ) {
      if (!animating) {
          pauseStart = time;
      }
      else {
          if (!animationStartTime)
             animationStartTime = time;
          if (pauseStart) {
             timePaused += time - pauseStart;
             pauseStart = undefined;
          }
          var wallTime = time - animationStartTime;   // Time since start of animation.
          var animationTime = wallTime - timePaused;  // Time during whigh animation was running (not counting pauses).
          callback(animationTime, wallTime);
          reqAnimFrm(doFrm);
      }
   }
   this.start = function() {
      if (!animating) {
         animating = true;
         reqAnimFrm(doFrm);
      }
   }
   this.stop = function() {
      animating = false;
   }
   this.isAnimating = function() {
      return animating;
   }
   this.setAnimating = function(animate) {
      if (animate)
         this.start();
      else
         this.stop();
   }
}



/**
 * Loads a file from a given url using AJAX.  The AJAX code
 * that is used here should work in any browser that supports
 * WebGL, but not in Internet Explorer [except maybe new versions]
 * The first parameter is the url of the file to be loaded, presumably
 * a relative url.  onSuccess is a function that will be called when
 * the AJAX requests succeeds; the first parameter to onSuccess is
 * the response text from the AJAX call (that is, the content loaded
 * from the url), and the second (optional) paramter is the XMLHttpRequest 
 * object in case you want to get more information from that object.
 * onFailure is a function that will be called if the AJAX request
 * fails; the first parameter is an error message, and the second (optinal)
 * parameter is the XMLHttpRequest object.  If timeLimit is given, 
 * then the request will fail if there is no response within timeLimit
 * milliseconds.  Only the url parameter is required; the others can
 * be missing or null.
 */
function ajaxLoad(url, onSuccess, onFailure, timeLimit) {
   var timeout = null;
   var request = new XMLHttpRequest();  // (doesn't work in IE)
   request.open("GET", url);
   request.onreadystatechange = function () {
      if (request.readyState == 4) {
         if (timeout)
            cancelTimeout(timeout);
         if (request.status == 200) {
            if (onSuccess)
               onSuccess(request.responseText, request);
         }
         else {
            if (onFailure)
               onFailure(request.statusText, request);
         }
      }
   }
   if (timeLimit) {
      setTimeout(function() {
          timeout = null;
          request.abort();
          if (onFailure)
             onFailure("Request timed out", request);
      }, timeLimit);
   } 
   request.send();
}


