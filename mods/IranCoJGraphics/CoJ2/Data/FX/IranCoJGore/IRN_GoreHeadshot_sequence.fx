SequenceDef()
{
	LifeTime()
	{
		keyf(0, 1.8)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadGush_emiter.fx", "IRN_BloodGush_particle.fx")    // IranCoJ Gore: two more streams
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadSpray_emiter.fx", "IRN_BloodSpray_particle.fx")    // IranCoJ Gore: a heavy spray of streaks
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadClusters_emiter.fx", "IRN_BloodCluster_particle.fx")    // IranCoJ Gore: a wide throw of drop clusters
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadGobs_emiter.fx", "BulletHitFleshDirt_particle.fx")    // IranCoJ Gore: heavy gobs
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadLines_emiter.fx", "IRN_BloodLine_particle.fx")    // IranCoJ Gore: more streaks
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_HeadPuff_emiter.fx", "IRN_HeadPuff_particle.fx")    // IranCoJ Gore: a short red puff
	}
}
