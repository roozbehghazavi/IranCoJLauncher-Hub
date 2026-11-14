SequenceDef()
{
	LifeTime()
	{
		keyf(0, 1)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_rifleFlash_emiter.fx", "IRN_Gun_rifleFlash_particle.fx")    // IranCoJ Graphics: the flash
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_rifleEmbers_emiter.fx", "IRN_Gun_rifleEmbers_particle.fx")    // IranCoJ Graphics: embers
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_rifleSmoke_emiter.fx", "IRN_Gun_rifleSmoke_particle.fx")    // IranCoJ Graphics: the black-powder cloud
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_rifleWisps_emiter.fx", "IRN_Gun_rifleWisps_particle.fx")    // IranCoJ Graphics: wisps from the muzzle
	}
}
