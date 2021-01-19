//Covid-19 Pandemic Reader
//sonification by Daniel Maszkowicz
//
//https://github.com/maszkowicz/CovidPandemic_Reader
//http://ooo.szkmd.ooo

s.boot;
s.quit;

//Open the receiver port
thisProcess.openUDPPort(9002);
thisProcess.openPorts; //check open ports

(
SynthDef(
	\covid_sound,
	{
		arg out=0, amp=0.0, freq=131.6, pulse=8.0, pan = 0;
		var sound = SinOsc.ar(freq: freq, phase: 0, mul: 0.4*LFPulse.kr(freq: pulse, iphase: 0.0, width: 0.1, mul: 1.0, add: 0.0).lag(0.1));
		//var pan = LFNoise1.ar(16,1).lag(0.01);
		var level = Clip.kr(amp,0,0.75);//amp*(0.6+LFNoise1.ar(16,0.4).lag(0.01));
		Out.ar(out, Pan2.ar(sound, pan, level))
	}
).add;

SynthDef(\sinegrain, {
	|out = 0, attack = 0.01, decay = 0.01, freq=0.0, pan = 0, amp = 0.5|
	var sound, env;
	// an amplitude envelope with fixed duration
	env = EnvGen.ar(Env.perc(attack, decay), doneAction: 2);
	// the underlying sound
	sound = FSinOsc.ar(freq);
	// use the envelope to control sound amplitude:
	sound = sound*(env*amp);
	// add stereo panning
	sound = Pan2.ar(sound, pan);
	// write to output bus
	Out.ar(out, sound)
}).add;

SynthDef(\sinebass, {
	|out = 0, freq=0.0, amp = 0.5|
	var mul, width, pan;
	width = 0.5;
	mul = 0.2*LFPulse.kr(freq: 2*7.83, width: width).lag(0.1);
	pan = SinOsc.kr(freq: 7.83);
	Out.ar(out, Pan2.ar(SinOsc.ar(freq: freq, mul: mul),pan,amp))
}
).add;

SynthDef(\fmbass, { arg out=0, amp=0.1, attack=0.1, sustain = 3, decay=2, gate=1, pan=0, freq=200;
	var sig, amp2;
	var sig1, sig2, sig3, sig4, sig5, sig6, sig7, sig8;
	var env1, env2, env3, env4, env5, env6, env7, env8;
	amp2 = EnvGen.ar(Env.linen(attack, sustain, decay), doneAction: 2);
	freq = freq / 4;
	freq = freq * ((0..1)/1 - 0.5 * 0.0007 + 1);
	env1 = EnvGen.kr(Env([0,1,0.051,0],[0.001,0.01,0.8], [4,-8]), 1);
	env2 = EnvGen.kr(Env([0,1,0.051,0],[0.005,0.5,1.5], [0,-8], releaseNode:2), 1);
	env3 = EnvGen.kr(Env([0,1,1,0],[0.01,0.01,0.2], [0,0,-4], releaseNode:2), gate);
	env4 = EnvGen.kr(Env([0,1,0],[0.002,2.8], [0,-4]), 1);
	env5 = EnvGen.kr(Env([0,1,1,0],[0.001,0.1,0.8], [4,0,-4], releaseNode:2), gate);
	env6 = EnvGen.kr(Env([0,1,0],[0.001,3.0], [0,-4]), 1);
	//freq = freq * EnvGen.kr(Env([1,1.002,0.998,1],[0.1,0.8]), 1);
	sig1 = SinOsc.ar(freq * 11 + 0) * env1;
	sig2 = SinOsc.ar(freq * 6 * ( sig1 * 2.5 + 1 )) * env2;
	sig3 = SinOsc.ar(freq * 2 * 1 + 0) * env3;
	sig4 = SinOsc.ar(freq * 1 * ( sig3 * 2.5 + 1 ) + 0) * env4;
	sig5 = SinOsc.ar(freq * 1 * ( sig2 * 2.5 + 1 ) * (sig4 * 2.5 + 1)) * env5;
	sig6 = SinOsc.ar(freq * 2) * env6;
	//sig = sig2 + sig3 + sig4 + sig5 + sig6;
	sig = [sig1, sig2, sig3, sig4, sig5, sig6] * DC.ar([0.0, 0.0, 0.0,  0.0, 0.5, 0.5]);
	sig.debug("sig");
	sig = sig /2;
	sig = sig.flop.sum;
	sig = sig * EnvGen.ar(\adsr.kr( Env.adsr(0.001,0,1,0.01, 1,-1) ),gate,doneAction:2);
	sig = sig * AmpComp.kr(freq);
	sig.debug("sigx");
	sig = Pan2.ar(sig, pan + [ 0, 0, 0, 0, 0, 0], amp*amp2).sum;
	Out.ar(out, sig);
}).add;
)

//create receivers
(
~covid = Synth(\covid_sound,[\amp,0]);
~covid_bass = Synth(\sinebass,[\amp,0]);

~cases = OSCFunc(
	{
		arg msg,time,address,receivedPort;
		var freq, pulse;
		freq=((msg.at(1).log)*200);
		pulse=((msg.at(1).log10+2)*2);
		~covid.set(\freq,freq);
		~covid.set(\pulse,pulse);
		msg.postln
	},'/pandemic/cases',nil);

~curve = OSCFunc(
	{
		arg msg,time,address,receivedPort;
		var amp;
		amp = (10000000**(msg.at(1)))/1000;
		~covid.set(\amp,amp);
		amp = 0.2*(2-msg.at(2));
		~covid.set(\pan,msg.at(2)*0.7);
		~covid_bass.set(\amp,amp);
		msg.postln
	},'/pandemic/curve',nil);

~start = OSCFunc(
	{
		arg msg,time,address,receivedPort;
		msg.postln;
		s.record(path: "~/Documents/Sonification/Codiv_sonification/Results/pandemic.wav".standardizePath)
	},'/pandemic/startrecord',nil);

~stop = OSCFunc(
	{
		arg msg,time,address,receivedPort;
		msg.postln;
		s.stopRecording;
		~covid_bass.set(\amp,0)
	},'/pandemic/stoprecord',nil);

~country = OSCFunc(
	{
		arg msg,time,address,receivedPort;
		var freq;
		var beat;
		freq = (222-(msg.at(1)*900));
		beat = 1+msg.at(1)*3;
		Synth(\sinegrain,[\out,0,\freq,freq,\attack,0.01,\decay,4,\amp,0.1]);
		Synth(\sinegrain,[\out,0,\freq,freq+beat,\attack,1,\decay,2,\amp,0.05]);
		Synth(\fmbass,[\out,0,\freq,2*freq,\amp,0.1,\attack,0.03,\sustain,5,\decay,3]);
		~covid_bass.set(\freq,2*freq);
		msg.postln
	},'/pandemic/country',nil);

~mute = OSCFunc(
	{
		arg msg,time,address,receivedPort;
		~covid.set(\amp,0)
	},'/pandemic/mute',nil);
)

(
~cases.free;
~curve.free;
~country.free;
~start.free;
~stop.free;
~covid.free;
~covid_bass.free;
)

