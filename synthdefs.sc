SynthDef("sine2", {
	|freq = 440, amp = 0.2, pan = 0, out_bus = 0, decay=2, sustain = 0|
	var env, out;
	env = EnvGen.kr(Env.new([0, 1, 1, 0], [0, sustain, decay]), doneAction:2);
	out = Pulse.ar(freq, mul: amp);
	//out = out + SinOsc.ar(SinOsc.kr(LFNoise1.kr(1, add: 5), mul: 10, add: freq * 2 + 5), mul: amp / 4);
	out = out * env;
	out = LPF.ar(out, LFNoise1.kr(1, 1500, 2000));
	out = Pan2.ar(out, pan);
	Out.ar(out_bus, out);
}).store;

SynthDef("SampleHit", {
	|bufnum = 0, channels = 2, out_bus = 0, amp = 1, rate = 1.0, freq=10000|
	var env, out;
	env = EnvGen.kr(Env.perc(0, 1), doneAction:2);
  out = PlayBuf.ar(1, bufnum, BufRateScale.kr(bufnum) * [1, 1.1]);
  out = LPF.ar(out, freq);
  out = out * env * amp;
	Out.ar(out_bus, out);
}).store;

SynthDef("SampleLoop", {
  |bufnum=0, num_channels=2, out_bus=0, amp=1, length=1, start=0|
  var out, env;
  env = EnvGen.kr(Env.linen(0.01, length, 0.01), doneAction:2);
  out = PlayBuf.ar(1, bufnum, BufRateScale.kr(bufnum), startPos:(BufSampleRate.kr(bufnum) * start));
  out = out * amp * env;
  Out.ar(out_bus, out);
}).store;

SynthDef("verb", {
	|in_bus, out_bus = 0, verb_mix = 0.4, verb_room = 0.7, verb_damp = 0.2, amp=1|
	var out;
	out = In.ar(in_bus, 2);
	//FreeVerb.ar(in, mix, room, damp, mul, add)
	//all params 0..1
	out = FreeVerb.ar(out, verb_mix, verb_room, verb_damp);
	out = out * amp;
	Out.ar(out_bus, out);
}).store;

SynthDef("compressor", {
  |in_bus, out_bus=0, thresh=0.5, slope_above=0.5|
  var out;
  
  out = In.ar(in_bus, 2);
	out = Compander.ar(out, out,
		thresh: thresh,
		slopeBelow: 1,
		slopeAbove: slope_above,
		clampTime: 0.01,
		relaxTime: 0.01
	);
	Out.ar(out_bus, out);
}).store;

SynthDef("stutter", {
    |in_bus, out_bus=0, length, switch|
    switch = Impulse.kr(switch);
}).store;

SynthDef("delay", {
  |in_bus, out_bus=0, delay_time=0.5, amp=2, decaytime=1|
  var in, out, delayed;
  out = In.ar(in_bus, 2);
  delayed = AllpassN.ar(out, 5, delaytime:delay_time,
                        decaytime:decaytime, mul:amp);
  out = out + delayed;
  Out.ar(out_bus, out);
}).store;

SynthDef("echo", {
  |in_bus, out_bus=0, delay_time=0.5, amp=2, lp_freq=900|
  var in, out, delayed;
  out = In.ar(in_bus, 2);
  delayed = DelayN.ar(out, 5, delaytime:delay_time, mul:amp);
  delayed = LPF.ar(delayed, lp_freq);
  out = out + delayed;
  Out.ar(out_bus, out);
}).store;

SynthDef("sine3", {
	|freq = 440, amp = 0.1, pan = 0, out_bus = 0, decay=1|
	var env, out;
	env = EnvGen.kr(Env.perc(0, decay), doneAction:2);
	out = SinOsc.ar(freq, mul: amp);
	out = out * env;
	out = Pan2.ar(out, pan);
	Out.ar(out_bus, out);
}).store;

SynthDef("saw3", {
	|freq = 440, amp = 1, pan = 0, out_bus = 0, decay=1, gate=1, lp_freq=2000|
	var env, out, fenv;
	env = EnvGen.kr(Env.asr(0, 0.8, decay), gate:gate, doneAction:2);
	out = Saw.ar([freq, freq+1], mul: amp);
	out = out + Saw.ar([freq-5, freq+5]/2, mul:amp*0.7);
	out = out + SinOsc.ar(freq*2, mul:amp*0.5);

  fenv = EnvGen.kr(Env.perc(0, 0.2), levelScale:lp_freq, levelBias:500);
	out = LPF.ar(out, fenv);
	out = out * env * 0.1;
	out = Pan2.ar(out, pan);
	Out.ar(out_bus, out);
}).store;

SynthDef("thefriendlypad", {
  |freq=440, amp=1, out_bus=0, gate=1, lp_freq=5000|
  var env, out, width_mod;
  width_mod = SinOsc.kr(LFNoise1.kr([10, 10], mul:1, add:5), mul:0.5, add:0.5);
  out = Pulse.ar(freq, width:width_mod, mul:amp);
  /*env = EnvGen.kr(Env.asr(1, 0.8, 2), gate:gate, doneAction:2);*/
  env = EnvGen.kr(Env.perc(0, 2), gate:gate, doneAction:2);
  out = LPF.ar(out, lp_freq);
  out = out * env;
  Out.ar(out_bus, out);
}).store;

SynthDef("thedemonicpad", {
  |freq=440, amp=0.1, out_bus=0, gate=1, lp_freq=5000|
  var env, out, width_mod, freq_mod;
  width_mod = LFNoise1.kr([2, 2], mul:0.5, add:0.5);
  freq_mod = LFNoise1.kr([0.1, 0.1], mul:1);
  out = Pulse.ar(freq+freq_mod, width:width_mod);
  env = EnvGen.kr(Env.asr(1, 0.8, 2), gate:gate, doneAction:2);
  out = LPF.ar(out, lp_freq);
  out = Pan2.ar(out, LFNoise1.kr(1));
  out = out * env * amp;
  Out.ar(out_bus, out);
}).store;

SynthDef("bass1", {
	|freq = 440, filtermax = 1200, amp = 0.8, pan = 0, out_bus = 0, decay=1|
	var env, out, width_mod, hienv, hi, freqenv;
	env = EnvGen.kr(Env.new([0, 1, 1, 0], [0, 0.25, 0.1]), doneAction:2);
	
	width_mod = LFNoise1.ar([1, 1], mul: 0.5, add:0.5);
	out = Pulse.ar([freq-0.25, freq+0.25], width:width_mod, mul: amp);
	out = out * env;	

	width_mod = LFNoise1.ar(1, mul: 0.5, add:0.5);
	hi = Pulse.ar(freq * 2, width:width_mod, mul: amp/3);
	hienv = EnvGen.kr(Env.perc(0, 0.5));
	hi = hi * hienv;
	out = out + hi;
	out = out + SinOsc.ar(freq * 0.5, mul: amp*1.5);
	
	freqenv = EnvGen.kr(Env.perc(0, 0.5), levelScale:filtermax, levelBias:200);
	out = LPF.ar(out, freqenv);
	out = out * env;
	Out.ar(out_bus, out);
}).store;

SynthDef("basshold", {
	|freq = 440, filtermax = 1200, amp = 0.8, pan = 0, out_bus = 0, decay=1, gate=1|
	var env, out, width_mod, hienv, hi, freqenv;
	
	width_mod = LFNoise1.ar([1, 1], mul: 0.5, add:0.5);
	out = Pulse.ar([freq-0.25, freq+0.25], width:width_mod, mul: amp);
	env = EnvGen.kr(Env.asr(1, 0.8, 1), gate:gate, doneAction:2);

	width_mod = LFNoise1.ar(1, mul: 0.5, add:0.5);
	hi = Pulse.ar(freq * 2, width:width_mod, mul: amp/3);
	hienv = EnvGen.kr(Env.asr(1, 0.9, 1), gate:gate);
	hi = hi * hienv;
	out = out + hi;
	out = out + SinOsc.ar(freq * 0.5, mul: amp*1.5);
	
	freqenv = EnvGen.kr(Env.perc(0, 0.5), levelScale:filtermax, levelBias:200);
	out = LPF.ar(out, freqenv);
	out = out * env;
	Out.ar(out_bus, out);
}).store;



SynthDef("BasicFM", {
    arg freqA = 440, ampA = 1,
    freqB = 0, ampB = 0,
    attackB=0, decayB=0.5,
    freqC = 0, ampC = 0,
    attackC=0, decayC=0.5,
    freqD, ampD, attackD, decayD,
    freqE, ampE, attackE, decayE,
    oscUp=0, oscDown=0,
    oscUpfreqB, oscUpampB,
    lp_freq = 5000, lp_res=0,
    lp_attack=0, lp_decay=0.5, lp_env_amount=0,
    out_bus=0, chain_bus=2,
    chain_wetdry=1,
    attack=0, decay=0.1,
    pan_range = 0;
    
    var env, out, gate, a_noise, osc_up_b, lp_env;
    
    gate = 1;
    
    c = SinOsc.ar(freqC, mul: ampC);
    c = c * EnvGen.kr(Env.perc(attackC, decayC), gate:gate);
    b = SinOsc.ar(freqB + c, mul: ampB);
    b = b * EnvGen.kr(Env.perc(attackB, decayB), gate:gate);
    
    e = SinOsc.ar(freqE, mul: ampE);
    e = e * EnvGen.kr(Env.perc(attackE, decayE), gate:gate);
    d = SinOsc.ar(freqD + e, mul: ampD);
    d = d * EnvGen.kr(Env.perc(attackD, decayD), gate:gate);

    out = SinOsc.ar(freqA + b + d, mul: ampA);

    osc_up_b = SinOsc.ar(oscUpfreqB, mul:oscUpampB);
    out = out + SinOsc.ar(freqA * 2 + 1 + osc_up_b, mul:oscUp);
    out = out * 0.7;

    env = EnvGen.kr(Env.perc(attack, decay), gate:gate, doneAction:2);
    out = out * env;
    out = Pan2.ar(out, LFNoise1.kr(0.01, mul:pan_range));

    lp_env = EnvGen.kr(Env.perc(lp_attack, lp_decay), gate:gate);
    lp_env = lp_env * lp_env_amount;
    out = MoogFF.ar(out, lp_freq + lp_env, lp_res);
    Out.ar(chain_bus, out * chain_wetdry);
    Out.ar(out_bus, out * (1 - chain_wetdry));
}).store;


SynthDef("AdvancedFM", {
    arg freqA = 440, ampA = 1,
    freqB = 0, ampB = 0,
    attackB=0, decayB=0.5,
    freqEnvB, freqAttackB, freqDecayB,
    freqC = 0, ampC = 0,
    freqEnvC, attackC=0, decayC=0.5,
    freqAttackC, freqDecayC,
    freqD, ampD, attackD, decayD, freqEnvD, freqAttackD, freqDecayD,
    freqE, ampE, attackE, decayE, freqEnvE, freqAttackE, freqDecayE,
    oscUp=0, oscDown=0,
    oscUpfreqB, oscUpampB,
    ampModFreq, ampModAmount,
    lp_freq = 5000, lp_res=0,
    lp_attack=0, lp_decay=0.5, lp_env_amount=0,
    out_bus=0, chain_bus=2,
    chain_wetdry=1,
    attack=0, decay=0.1,
    pan_range = 0;
    
    var env, out, gate, a_noise, osc_up_b, lp_env, freq_env, amp_mod;
    
    gate = 1;
    
    freq_env = EnvGen.kr(Env.perc(freqAttackC, freqDecayC), gate:gate, levelScale:freqEnvC, levelBias:(1-freqEnvC));
    c = SinOsc.ar(freqC * freq_env, mul: ampC);
    c = c * EnvGen.kr(Env.perc(attackC, decayC), gate:gate);
    freq_env = EnvGen.kr(Env.perc(freqAttackB, freqDecayB), gate:gate, levelScale:freqEnvB, levelBias:(1-freqEnvB));
    b = SinOsc.ar(freqB + (c * freq_env), mul: ampB);
    b = b * EnvGen.kr(Env.perc(attackB, decayB), gate:gate);
    
    freq_env = EnvGen.kr(Env.perc(freqAttackE, freqDecayE), gate:gate, levelScale:freqEnvE, levelBias:(1-freqEnvE));
    e = SinOsc.ar(freqE * freq_env, mul: ampE);
    e = e * EnvGen.kr(Env.perc(attackE, decayE), gate:gate);
    freq_env = EnvGen.kr(Env.perc(freqAttackD, freqDecayD), gate:gate, levelScale:freqEnvD, levelBias:(1-freqEnvD));
    d = SinOsc.ar(freqD + (e * freq_env), mul: ampD);
    d = d * EnvGen.kr(Env.perc(attackD, decayD), gate:gate);

    out = SinOsc.ar(freqA + b + d);

    osc_up_b = SinOsc.ar(oscUpfreqB, mul:oscUpampB);
    out = out + SinOsc.ar(freqA * 2 + osc_up_b, mul:oscUp);
    out = out * 0.7;

    amp_mod = SinOsc.ar(ampModFreq, mul:ampModAmount/2, add:1-(ampModAmount/2));
    out = out * amp_mod;

    env = EnvGen.kr(Env.perc(attack, decay), gate:gate, doneAction:2);
    out = out * env;
    out = Pan2.ar(out, LFNoise1.kr(0.01, mul:pan_range));

    lp_env = EnvGen.kr(Env.perc(lp_attack, lp_decay), gate:gate);
    lp_env = lp_env * lp_env_amount;
    out = MoogFF.ar(out, lp_freq + lp_env, lp_res);
    out = out * ampA;
    Out.ar(chain_bus, out * chain_wetdry);
    Out.ar(out_bus, out * (1 - chain_wetdry));
}).store;



// SOS Drums by Renick Bell, renick_at_gmail.com
// recipes from Gordon Reid in his Sound on Sound articles


// SOSdrums


// SOSkick -------
// http://www.soundonsound.com/sos/jan02/articles/synthsecrets0102.asp
// increase mod_freq and mod_index for interesting electronic percussion

SynthDef(\SOSKick,
	{ arg out = 0, freq = 50, mod_freq = 5, mod_index = 5, sustain = 0.4, amp = 0.8, beater_noise_level = 0.025;
	var pitch_contour, drum_osc, drum_lpf, drum_env;
	var beater_source, beater_hpf, beater_lpf, lpf_cutoff_contour, beater_env;
	var kick_mix;
	pitch_contour = Line.kr(freq*2, freq, 0.02);
	drum_osc = PMOsc.ar(	pitch_contour,
				mod_freq,
				mod_index/1.3,
				mul: 1,
				add: 0);
	drum_lpf = LPF.ar(in: drum_osc, freq: 1000, mul: 1, add: 0);
	drum_env = drum_lpf * EnvGen.ar(Env.perc(0.005, sustain), 1.0, doneAction: 2);
	beater_source = WhiteNoise.ar(beater_noise_level);
	beater_hpf = HPF.ar(in: beater_source, freq: 500, mul: 1, add: 0);
	lpf_cutoff_contour = Line.kr(6000, 500, 0.03);
	beater_lpf = LPF.ar(in: beater_hpf, freq: lpf_cutoff_contour, mul: 1, add: 0);
	beater_env = beater_lpf * EnvGen.ar(Env.perc, 1.0, doneAction: 2);
	kick_mix = Mix.new([drum_env, beater_env]) * 2 * amp;
	Out.ar(out, [kick_mix, kick_mix])
	}
	).store;



// SOSsnare -------
// http://www.soundonsound.com/sos/Mar02/articles/synthsecrets0302.asp

SynthDef(\SOSSnare,
	{arg out = 0, sustain = 0.1, drum_mode_level = 0.25,
	snare_level = 40, snare_tightness = 1000,
	freq = 405, amp = 0.8;
	var drum_mode_sin_1, drum_mode_sin_2, drum_mode_pmosc, drum_mode_mix, drum_mode_env;
	var snare_noise, snare_brf_1, snare_brf_2, snare_brf_3, snare_brf_4, snare_reson;
	var snare_env;
	var snare_drum_mix;

	drum_mode_env = EnvGen.ar(Env.perc(0.005, sustain), 1.0, doneAction: 2);
	drum_mode_sin_1 = SinOsc.ar(freq*0.53, 0, drum_mode_env * 0.5);
	drum_mode_sin_2 = SinOsc.ar(freq, 0, drum_mode_env * 0.5);
	drum_mode_pmosc = PMOsc.ar(	Saw.ar(freq*0.85),
					184,
					0.5/1.3,
					mul: drum_mode_env*5,
					add: 0);
	drum_mode_mix = Mix.new([drum_mode_sin_1, drum_mode_sin_2, drum_mode_pmosc]) * drum_mode_level;

// choose either noise source below
//	snare_noise = Crackle.ar(2.01, 1);
	snare_noise = LFNoise0.ar(20000, 0.1);
	snare_env = EnvGen.ar(Env.perc(0.005, sustain), 1.0, doneAction: 2);
	snare_brf_1 = BRF.ar(in: snare_noise, freq: 8000, mul: 0.5, rq: 0.1);
	snare_brf_2 = BRF.ar(in: snare_brf_1, freq: 5000, mul: 0.5, rq: 0.1);
	snare_brf_3 = BRF.ar(in: snare_brf_2, freq: 3600, mul: 0.5, rq: 0.1);
	snare_brf_4 = BRF.ar(in: snare_brf_3, freq: 2000, mul: snare_env, rq: 0.0001);
	snare_reson = Resonz.ar(snare_brf_4, snare_tightness, mul: snare_level) ;
	snare_drum_mix = Mix.new([drum_mode_mix, snare_reson]) * 5 * amp;
	Out.ar(out, [snare_drum_mix, snare_drum_mix])
	}
).store;



// SOShats -------
// http://www.soundonsound.com/sos/Jun02/articles/synthsecrets0602.asp


SynthDef(\SOSHats,
	{arg out = 0, freq = 6000, sustain = 0.1, amp = 0.8;
	var root_cymbal, root_cymbal_square, root_cymbal_pmosc;
	var initial_bpf_contour, initial_bpf, initial_env;
	var body_hpf, body_env;
	var cymbal_mix;
	
	root_cymbal_square = Pulse.ar(freq, 0.5, mul: 1);
	root_cymbal_pmosc = PMOsc.ar(root_cymbal_square,
					[freq*1.34, freq*2.405, freq*3.09, freq*1.309],
					[310/1.3, 26/0.5, 11/3.4, 0.72772],
					mul: 1,
					add: 0);
	root_cymbal = Mix.new(root_cymbal_pmosc);
	initial_bpf_contour = Line.kr(15000, 9000, 0.1);
	initial_env = EnvGen.ar(Env.perc(0.005, 0.1), 1.0);
	initial_bpf = BPF.ar(root_cymbal, initial_bpf_contour, mul:initial_env);
	body_env = EnvGen.ar(Env.perc(0.005, sustain, 1, -2), 1.0, doneAction: 2);
	body_hpf = HPF.ar(in: root_cymbal, freq: Line.kr(9000, 12000, sustain),mul: body_env, add: 0);
	cymbal_mix = Mix.new([initial_bpf, body_hpf]) * amp;
	Out.ar(out, [cymbal_mix, cymbal_mix])
	}).store;



// SOStom -------
// http://www.soundonsound.com/sos/Mar02/articles/synthsecrets0302.asp

SynthDef(\SOSTom,
	{arg out = 0, sustain = 0.4, drum_mode_level = 0.25,
	freq = 90, drum_timbre = 1.0, amp = 0.8;
	var drum_mode_sin_1, drum_mode_sin_2, drum_mode_pmosc, drum_mode_mix, drum_mode_env;
	var stick_noise, stick_env;
	var drum_reson, tom_mix;

	drum_mode_env = EnvGen.ar(Env.perc(0.005, sustain), 1.0, doneAction: 2);
	drum_mode_sin_1 = SinOsc.ar(freq*0.8, 0, drum_mode_env * 0.5);
	drum_mode_sin_2 = SinOsc.ar(freq, 0, drum_mode_env * 0.5);
	drum_mode_pmosc = PMOsc.ar(	Saw.ar(freq*0.9),
								freq*0.85,
								drum_timbre/1.3,
								mul: drum_mode_env*5,
								add: 0);
	drum_mode_mix = Mix.new([drum_mode_sin_1, drum_mode_sin_2, drum_mode_pmosc]) * drum_mode_level;
	stick_noise = Crackle.ar(2.01, 1);
	stick_env = EnvGen.ar(Env.perc(0.005, 0.01), 1.0) * 3;
	tom_mix = Mix.new([drum_mode_mix, stick_env]) * 2 * amp;
	Out.ar(out, [tom_mix, tom_mix])
	}
).store;


0.exit;
