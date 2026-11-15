SequenceDef()
{
	LifeTime()
	{
		keyf(0, 2.2)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodGushHeavy_emiter.fx", "IRN_BloodGush_particle.fx")    // IranCoJ Gore: two streams
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodSprayHeavy_emiter.fx", "IRN_BloodSpray_particle.fx")    // IranCoJ Gore: a wider spray of streaks
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodClusterHeavy_emiter.fx", "IRN_BloodCluster_particle.fx")    // IranCoJ Gore: drop clusters, a wider throw
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodLineHeavy_emiter.fx", "IRN_BloodLine_particle.fx")    // IranCoJ Gore: more streaks
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_BloodPuffHeavy_emiter.fx", "IRN_BloodPuff_particle.fx")    // IranCoJ Gore: a lighter puff
	}
}
