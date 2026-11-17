SequenceDef()
{
	LifeTime()
	{
		keyf(0, 2)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstDropsPellet_emiter.fx", "IRN_BurstDrops_particle.fx")    // IranCoJ Gore: a throw of drops
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstSplash_emiter.fx", "IRN_BurstSplash_particle.fx")    // IranCoJ Gore: a splash
		Probability(0.5)
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstLinesPellet_emiter.fx", "IRN_BurstLines_particle.fx")    // IranCoJ Gore: streaks
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstClusterClose_emiter.fx", "IRN_BurstClusterClose_particle.fx")    // IranCoJ Gore: a cluster
		Probability(0.3)
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstPuffPellet_emiter.fx", "IRN_BurstPuff_particle.fx")    // IranCoJ Gore: a light puff
	}
}
