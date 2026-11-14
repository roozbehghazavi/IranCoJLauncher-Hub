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
		ParticleEmiter("IRN_Impact_metalHeavyDust_emiter.fx", "IRN_Impact_metalHeavyDust_particle.fx")    // IranCoJ Graphics: dust
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_metalHeavySparks_emiter.fx", "IRN_Impact_metalHeavySparks_particle.fx")    // IranCoJ Graphics: sparks
	}
}
