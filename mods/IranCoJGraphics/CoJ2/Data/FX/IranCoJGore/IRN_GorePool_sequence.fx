SequenceDef()
{
	LifeTime()
	{
		keyf(0, 2.5)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_GorePool_emiter.fx", "IRN_GorePool_particle.fx")    // IranCoJ Gore: a pool spreading under a body
	}
}
