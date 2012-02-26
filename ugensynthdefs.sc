SynthDef("builder-clear", {
        |out_bus|
        ReplaceOut.ar(out_bus, 0);
}).store;

SynthDef("Ugen_SinOsc", {
        |out_bus = 0, freq=440, phase=0, mul=1, add=0|
        var out;
        out = SinOsc.ar(freq, phase, mul, add);
        Out.ar(out_bus, out);
}).store;

SynthDef("Ugen_Saw", {
        |out_bus = 0, freq=440, mul=1, add=0|
        var out;
        out = Saw.ar(freq, mul, add);
        Out.ar(out_bus, out);
}).store;

SynthDef("Ugen_LPF", {
        |in_bus, out_bus = 0, freq=1000, mul=1, add=0|
        var out, in;
        in = In.ar(in_bus, 1);
        out = LPF.ar(in, freq, mul, add);
        Out.ar(out_bus, out);
}).store;

SynthDef("Ugen_Add", {
        |in_bus, rhs, out_bus = 0|
        var out, in_a;
        in_a = In.ar(in_bus, 1);
        out = in_a + rhs;
        Out.ar(out_bus, out);
}).store;

SynthDef("Ugen_Mul", {
        |in_bus, rhs, out_bus = 0|
        var out, in_a;
        in_a = In.ar(in_bus, 1);
        out = in_a * rhs;
        Out.ar(out_bus, out);
}).store;


SynthDef("Ugen_Env", {
    |out_bus=0, attack=0.05, decay=0, sustain=1, release=0.2, mul=1, add=0, curve=0, gate=1, doneAction=14|
    var out;
    out = Env.adsr(attackTime:attack, decayTime:decay, sustainLevel:sustain, releaseTime:release, curve:curve);
    out = EnvGen.kr(out, gate:gate, doneAction:doneAction);
    out = out * mul;
    out = out + add;
    Out.kr(out_bus, out);
}).store;

SynthDef("Ugen_EnvPerc", {
    |out_bus=0, attack=0, release=0.5, mul=1, curve=0, gate=1, doneAction=14|
    var out;
    out = Env.perc(attackTime:attack, releaseTime:release, curve:curve);
    out = EnvGen.kr(out, gate:gate, doneAction:doneAction);
    out = out * mul;
    Out.kr(out_bus, out);
}).store;

0.exit;
