SequenceDef()
{
	LifeTime()
	{
		keyf(0, 0.8)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_gatlingFlash_emiter.fx", "IRN_Gun_gatlingFlash_particle.fx")    // IranCoJ Graphics: the flash
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_gatlingEmbers_emiter.fx", "IRN_Gun_gatlingEmbers_particle.fx")    // IranCoJ Graphics: embers
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_gatlingSmoke_emiter.fx", "IRN_Gun_gatlingSmoke_particle.fx")    // IranCoJ Graphics: the black-powder cloud
	}
}
