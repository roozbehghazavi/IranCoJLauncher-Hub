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
		ParticleEmiter("IRN_Impact_woodHeavyDust_emiter.fx", "IRN_Impact_woodHeavyDust_particle.fx")    // IranCoJ Graphics: dust
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_woodHeavyDebris_emiter.fx", "IRN_Impact_woodHeavyDebris_particle.fx")    // IranCoJ Graphics: debris
	}
}
