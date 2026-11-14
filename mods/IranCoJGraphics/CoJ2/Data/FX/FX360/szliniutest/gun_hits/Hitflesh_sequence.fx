SequenceDef()
{
	LifeTime()
	{
		keyf(0, 2.2)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodGush_emiter.fx", "IRN_BloodGush_particle.fx")    // IranCoJ Gore: the stream out of the exit side
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodBurst_emiter.fx", "IRN_BloodBurst_particle.fx")    // IranCoJ Gore: the radial burst
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodCluster_emiter.fx", "IRN_BloodCluster_particle.fx")    // IranCoJ Gore: drop clusters, splatting where they land
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodLine_emiter.fx", "IRN_BloodLine_particle.fx")    // IranCoJ Gore: long streaks
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodPuff_emiter.fx", "IRN_BloodPuff_particle.fx")    // IranCoJ Gore: a quick spray puff
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodHaze_emiter.fx", "IRN_BloodHaze_particle.fx")    // IranCoJ Gore: a big faint haze
	}
}
