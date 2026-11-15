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
		ParticleEmiter("IRN_GoreDripHeavy_emiter.fx", "IRN_GoreDripHeavy_particle.fx")    // IranCoJ Gore: a stream from bad wounds
	}
}
