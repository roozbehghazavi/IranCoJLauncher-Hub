SequenceDef()
{
	LifeTime()
	{
		keyf(0, 1.58)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_GoreSpurt_emiter.fx", "IRN_GoreSpurtStreak_particle.fx")    // IranCoJ Gore: a jet with the heartbeat (fresh wound)
	}
}
