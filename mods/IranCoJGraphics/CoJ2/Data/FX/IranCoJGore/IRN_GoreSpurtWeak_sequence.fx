SequenceDef()
{
	LifeTime()
	{
		keyf(0, 1.54)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_GoreSpurtWeak_emiter.fx", "IRN_GoreSpurtStreak_particle.fx")    // IranCoJ Gore: a weaker jet (the pressure dropping)
	}
}
