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
		ParticleEmiter("IRN_Impact_groundDust_emiter.fx", "IRN_Impact_groundDust_particle.fx")    // IranCoJ Graphics: dust
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_groundDebris_emiter.fx", "IRN_Impact_groundDebris_particle.fx")    // IranCoJ Graphics: debris
	}
}
