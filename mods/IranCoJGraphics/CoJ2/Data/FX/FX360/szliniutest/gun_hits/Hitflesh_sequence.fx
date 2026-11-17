SequenceDef()
{
	LifeTime()
	{
		keyf(0, 3)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstCluster_emiter.fx", "IRN_BurstCluster_particle.fx")    // IranCoJ Gore: a big cluster of drops flying out
		Probability(0.8)
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstClusterClose_emiter.fx", "IRN_BurstClusterClose_particle.fx")    // IranCoJ Gore: the same, close to the body
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstCluster2_emiter.fx", "IRN_BurstCluster2_particle.fx")    // IranCoJ Gore: a second, narrower cluster
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstSplash_emiter.fx", "IRN_BurstSplash_particle.fx")    // IranCoJ Gore: a splash bursting out (stops in the air)
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstSplashClose_emiter.fx", "IRN_BurstSplashClose_particle.fx")    // IranCoJ Gore: a splash at the wound
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstDrops_emiter.fx", "IRN_BurstDrops_particle.fx")    // IranCoJ Gore: a throw of drops
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstDropsClose_emiter.fx", "IRN_BurstDropsClose_particle.fx")    // IranCoJ Gore: a slower throw of drops
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstLines_emiter.fx", "IRN_BurstLines_particle.fx")    // IranCoJ Gore: streaks thrown wide
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstLinesClose_emiter.fx", "IRN_BurstLinesClose_particle.fx")    // IranCoJ Gore: short streaks
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstPuff_emiter.fx", "IRN_BurstPuff_particle.fx")    // IranCoJ Gore: a puff of spray
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BurstHaze_emiter.fx", "IRN_BurstHaze_particle.fx")    // IranCoJ Gore: a faint red haze
	}
}
