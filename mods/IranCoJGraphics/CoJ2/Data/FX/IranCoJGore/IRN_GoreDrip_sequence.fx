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
		ParticleEmiter("IRN_GoreDrip_emiter.fx", "IRN_GoreDrip_particle.fx")    // IranCoJ Gore: a trickle from a wound
	}
}
