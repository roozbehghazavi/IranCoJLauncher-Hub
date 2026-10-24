SequenceDef()
{
	LifeTime()
	{
		keyf(0.000000, 2.000000)
	}

	Repeat(1)

	Delay(0.000000)

	Spawn()
	{
		ParticleEmiter("hitflesh3_emiter.fx", "hitflesh3_particle.fx")    //bloodbig
	}

	Delay(0.000000)

	Spawn()
	{
		ParticleEmiter("hitflesh_emiter.fx", "hitflesh_particle.fx")    //bloodcircle
	}

	Delay(0.000000)

	Spawn()
	{
		ParticleEmiter("hitflesh2_emiter.fx", "hitflesh2_particle.fx")    //bloodsmall
	}
	
}

