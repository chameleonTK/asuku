var loaders = [

	{

		width: 100,
		height: 20,

		stepsPerFrame: 1,
		trailLength: 1,
		pointDistance: .25,
		fps: 5,
		padding: 10,
		//step: 'fader',

		fillColor: '#5A5A5A',

		setup: function() {
			this._.lineWidth = 20;
		},

		path: [
			['line', 0, 10, 80, 10]
		]

	}

	

];

function sonicstart(element){
	var d, a, container = element

	console.log(container)
	for (var i = -1, l = loaders.length; ++i < l;) {
		d = document.createElement('div');
		d.className = 'l';
		a = new Sonic(loaders[i]);
		d.appendChild(a.canvas);
		console.log(container);
		container.append(d);
		//a.canvas.style.marginTop = (150 - a.fullHeight) / 2 + 'px';
		//a.canvas.style.marginLeft = (150 - a.fullWidth) / 2 + 'px';
		a.canvas.style.margin = "auto";
		a.play();
	}
}