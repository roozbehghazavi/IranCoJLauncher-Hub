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
		ParticleEmiter("IRN_Impact_stoneDust_emiter.fx", "IRN_Impact_stoneDust_particle.fx")    // IranCoJ Graphics: dust
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_stoneDebris_emiter.fx", "IRN_Impact_stoneDebris_particle.fx")    // IranCoJ Graphics: debris
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_stoneSparks_emiter.fx", "IRN_Impact_stoneSparks_particle.fx")    // IranCoJ Graphics: sparks
	}
}
