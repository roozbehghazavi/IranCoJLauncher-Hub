SequenceDef()
{
	LifeTime()
	{
		keyf(0, 2.3)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_sandDust_emiter.fx", "IRN_Impact_sandDust_particle.fx")    // IranCoJ Graphics: dust
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_sandDebris_emiter.fx", "IRN_Impact_sandDebris_particle.fx")    // IranCoJ Graphics: debris
	}
}
