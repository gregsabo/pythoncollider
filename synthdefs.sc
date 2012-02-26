SynthDef("example_synth", {
	|freq = 440, amp = 0.2, pan = 0, out_bus = 0, decay=2, sustain = 0|
	var env, out;
	env = EnvGen.kr(Env.new([0, 1, 1, 0], [0, sustain, decay]), doneAction:2);
	out = Pulse.ar(freq, mul: amp);
	out = out * env;
	out = LPF.ar(out, LFNoise1.kr(1, 1500, 2000));
	out = Pan2.ar(out, pan);
	Out.ar(out_bus, out);
}).store;

0.exit;
