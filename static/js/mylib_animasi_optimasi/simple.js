(function () {
	'use strict';

	var canvas, con2d;
	var optimizer = new pso.Optimizer();
	var iteration = 0, iterationNMax = 20;
	var delay = 50;
	var domain = null;
	var objectiveFunction;
	var samples = [];
	var utk_zoom_in = 15;

	function degrees_to_radians(degrees) {
        return degrees * (Math.PI / 180);
    }

    function radians_to_degrees(radians) {
        return radians/(Math.PI / 180);
    }

	var fundom = [{
	    // menambahkan var utk_zoom_in 15 kali lipat agar view-nya nampak jelas
	    		fun: function (x) { return utk_zoom_in * (Math.abs(Math.sin(x[0] * 2)) + 2 * Math.exp(-Math.pow(x[0], 10)) * Math.cos(x[0] * 2)); },
		domain: [new pso.Interval(-4.00, 4.00)]
	}, {
	    //
	    // optional:
		fun: function (x) { return 3*Math.pow((1-x[0]),2)*Math.exp(-Math.pow(x[0],2) - Math.pow(x[1]+1,2) -
		10*(x[0]/5 - Math.pow(x[0],3) - Math.pow(x[1],5)) * Math.exp(-Math.pow(x[0],2) - Math.pow(x[1],2)) -
		(1/3)*Math.exp(-Math.pow(x[0]+1,2) -Math.pow(x[1],2))); },
		domain: [new pso.Interval(-5.0, 5.12)]

		//alternatif solusi:
		//1. membuat gridmap (x,y)
		//2. masukkan gridmap ke dalam f(x,y)
		//3. buffer nilai x,y,z
		// *lakukan langkah 1-3 dgn python / js
		//4. hasil dari langkah ke-3, dikirimkan ke webGL
		//5. set setiap vertex atau kumpulkannya dgn GL_POINTS atau lainnya
		//
		//6. PSO, cukup generate bbrp vertex yaitu sebanyak populasi yg diinginkan
		//7. lalu titik partikel PSO trsbt buat misal dgn GL_POINTS
		//8. animasikan titik partikel tersebut
		//9. selesai

	}, {
		fun: function (x) { return Math.cos(Math.PI * 2 * x[0]) * 5 - Math.pow(x[0], 2); },
		domain: [new pso.Interval(-5.12, 5.12)]
	}, {
		fun: function (x) { return -Math.cos(x[0]) * Math.exp(-Math.pow(x - Math.PI, 2)); },
		domain: [new pso.Interval(-30, 30)]
	}, {
		fun: function (x) { return Math.exp(-Math.pow(x[0] - 5, 2)) * 20 + Math.cos(x[0] * 10); },
		domain: [new pso.Interval(-10, 10)]
	}, {
		fun: function (x) { return -Math.pow(x[0], 2); },
		domain: [new pso.Interval(-5, 5)]
	}];

	var initialPopulationSize;
	var timeoutId = null;
	var running = false;

	function precomputeSamples() {
		var nSamples = 250;
		var ax = (domain[0].end - domain[0].start) / nSamples;
		for (var i = 0, x = domain[0].start; i <= nSamples; i++, x += ax) {
			samples[i] = objectiveFunction([x]);
		}
	}

	function init()	{
		optimizer.init(initialPopulationSize, domain);
	}

	function step()	{
		optimizer.step();
		drawFunction();
		drawPopulation();
		drawBest();
	}

	function drawLine(x1, y1, x2, y2) {
		con2d.moveTo(x1, y1);
		con2d.lineTo(x2, y2);
	}

	function drawPopulation() {
		var particles = optimizer.getParticles();

		var rap = canvas.width / (domain[0].end - domain[0].start);
		con2d.lineWidth = 1;
		con2d.strokeStyle = '#F04';

		con2d.beginPath();
		particles.forEach(function(particle) {
			drawLine(
				(particle.position[0] - domain[0].start) * rap, 0,
				(particle.position[0] - domain[0].start) * rap, canvas.height
			);
		});
		con2d.stroke();

		con2d.lineWidth = 1.2;
		con2d.strokeStyle = '#1FA';

		con2d.beginPath();
		particles.forEach(function(particle) {
			drawLine(
				(particle.bestPosition[0] - domain[0].start) * rap, 0,
				(particle.bestPosition[0] - domain[0].start) * rap, canvas.height
			);
		});
		con2d.stroke();
	}

	function drawBest() {
		var rap = canvas.width / (domain[0].end - domain[0].start);
		con2d.lineWidth = 1.5;
		con2d.strokeStyle = '#05F';

		con2d.beginPath();
		var best = optimizer.getBestPosition();
		drawLine(
			(best - domain[0].start) * rap, 0,
			(best - domain[0].start) * rap, canvas.height
		);
		con2d.stroke();
	}

	function drawFunction() {
		var cy = canvas.height / 2;
		var ax = canvas.width / (samples.length - 1);

		con2d.fillStyle = '#FFF';
		con2d.fillRect(0, 0, canvas.width, canvas.height);

		con2d.strokeStyle = '#555';
		con2d.lineWidth = 1.5;

		con2d.beginPath();
		for(var i = 1, x = ax; i < samples.length; i++, x += ax) {
			drawLine(
				x - ax, cy - samples[i - 1] * ax,
				x, cy - samples[i] * ax
			);
		}
		con2d.stroke();
	}

	function loop() {
		if (running) {
			step();
			document.getElementById('out_best').value = 'f(' + optimizer.getBestPosition() + ') = ' + optimizer.getBestFitness();
			iteration++;
			if (iteration < iterationNMax) {
				timeoutId = setTimeout(loop, delay);
			} else {
				running = false;
			}
		}
	}

	function start() {
		if (!running) {
			running = true;
			updateParameters();
			iteration = 0;
			init();
			loop();
		}
	}

	function stop() {
		if (timeoutId !== null) {
			clearTimeout(timeoutId);
			timeoutId = null;
		}
		running = false;
	}

	function updateFunction() {
		stop();

		var index = document.getElementById('lst_func').selectedIndex;
		optimizer.setObjectiveFunction(fundom[index].fun);
		domain = fundom[index].domain;
		objectiveFunction = fundom[index].fun;
		precomputeSamples();
		drawFunction();
	}

	function updateParameters() {
		iterationNMax = parseInt(document.getElementById('inp_niter').value);

		initialPopulationSize = parseInt(document.getElementById('inp_popinit').value);
		var inertiaWeight = parseFloat(document.getElementById('inp_inertia').value);
		var social = parseFloat(document.getElementById('inp_social').value);
		var personal = parseFloat(document.getElementById('inp_personal').value);

		optimizer.setOptions({
			inertiaWeight: inertiaWeight,
			social: social,
			personal: personal
		});
	}

	function setup() {
		canvas = document.getElementById('canvaspso');
		con2d = canvas.getContext('2d');

		function createSliderPair(sliderId, inputId) {
			associateSlider(
				document.getElementById(sliderId),
				document.getElementById(inputId)
			);
		}

		[
			['slider_niter', 'inp_niter'],
			['slider_popinit', 'inp_popinit'],
			['slider_inertia', 'inp_inertia'],
			['slider_social', 'inp_social'],
			['slider_personal', 'inp_personal']
		].forEach(function (pair) {
			createSliderPair.apply(null, pair);
		});

		document.getElementById('but_start').addEventListener('click', start);
		document.getElementById('but_stop').addEventListener('click', stop);
		document.getElementById('lst_func').addEventListener('change', updateFunction);

		updateFunction();
	}

	setup();
})();
