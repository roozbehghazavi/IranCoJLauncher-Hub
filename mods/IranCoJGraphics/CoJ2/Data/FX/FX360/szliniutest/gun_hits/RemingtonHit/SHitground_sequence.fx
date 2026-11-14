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
		ParticleEmiter("IRN_Impact_groundHeavyDust_emiter.fx", "IRN_Impact_groundHeavyDust_particle.fx")    // IranCoJ Graphics: dust
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_groundHeavyDebris_emiter.fx", "IRN_Impact_groundHeavyDebris_particle.fx")    // IranCoJ Graphics: debris
	}
}
