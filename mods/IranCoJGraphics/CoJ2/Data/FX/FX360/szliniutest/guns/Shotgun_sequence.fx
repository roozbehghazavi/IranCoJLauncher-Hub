SequenceDef()
{
	LifeTime()
	{
		keyf(0, 1.2)
	}

	Repeat(1)

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_shotgunFlash_emiter.fx", "IRN_Gun_shotgunFlash_particle.fx")    // IranCoJ Graphics: the flash
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_shotgunEmbers_emiter.fx", "IRN_Gun_shotgunEmbers_particle.fx")    // IranCoJ Graphics: embers
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_shotgunSmoke_emiter.fx", "IRN_Gun_shotgunSmoke_particle.fx")    // IranCoJ Graphics: the black-powder cloud
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_shotgunWisps_emiter.fx", "IRN_Gun_shotgunWisps_particle.fx")    // IranCoJ Graphics: wisps from the muzzle
	}
}
