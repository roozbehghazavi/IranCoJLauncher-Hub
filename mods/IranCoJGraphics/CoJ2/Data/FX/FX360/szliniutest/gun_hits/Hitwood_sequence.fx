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
		ParticleEmiter("IRN_Impact_woodDust_emiter.fx", "IRN_Impact_woodDust_particle.fx")    // IranCoJ Graphics: dust
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_woodDebris_emiter.fx", "IRN_Impact_woodDebris_particle.fx")    // IranCoJ Graphics: debris
	}
}
