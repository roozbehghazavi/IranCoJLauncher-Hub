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
		ParticleEmiter("IRN_HeadDrops_emiter.fx", "IRN_BurstDrops_particle.fx")    // IranCoJ Gore: a wide throw of drops
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadCluster_emiter.fx", "IRN_BurstCluster2_particle.fx")    // IranCoJ Gore: another big cluster
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadSplash_emiter.fx", "IRN_BurstSplash_particle.fx")    // IranCoJ Gore: two more splashes
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadGobs_emiter.fx", "BulletHitFleshDirt_particle.fx")    // IranCoJ Gore: heavy gobs
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadLines_emiter.fx", "IRN_BurstLines_particle.fx")    // IranCoJ Gore: more streaks
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadPuff_emiter.fx", "IRN_HeadPuff_particle.fx")    // IranCoJ Gore: a short red puff
	}
}
