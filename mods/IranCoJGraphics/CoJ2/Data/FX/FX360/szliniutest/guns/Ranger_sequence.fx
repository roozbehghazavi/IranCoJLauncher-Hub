SequenceDef()
{
	LifeTime()
	{
		keyf(0, 0.9)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_pistolFlash_emiter.fx", "IRN_Gun_pistolFlash_particle.fx")    // IranCoJ Graphics: the flash
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_pistolEmbers_emiter.fx", "IRN_Gun_pistolEmbers_particle.fx")    // IranCoJ Graphics: embers
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_pistolSmoke_emiter.fx", "IRN_Gun_pistolSmoke_particle.fx")    // IranCoJ Graphics: the black-powder cloud
	}
}
