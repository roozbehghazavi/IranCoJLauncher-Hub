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
		ParticleEmiter("IRN_Impact_stoneHeavyDust_emiter.fx", "IRN_Impact_stoneHeavyDust_particle.fx")    // IranCoJ Graphics: dust
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_stoneHeavyDebris_emiter.fx", "IRN_Impact_stoneHeavyDebris_particle.fx")    // IranCoJ Graphics: debris
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Impact_stoneHeavySparks_emiter.fx", "IRN_Impact_stoneHeavySparks_particle.fx")    // IranCoJ Graphics: sparks
	}
}
