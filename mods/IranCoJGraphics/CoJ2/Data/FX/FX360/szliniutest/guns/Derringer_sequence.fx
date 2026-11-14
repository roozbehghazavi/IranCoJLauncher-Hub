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
		ParticleEmiter("IRN_Gun_derringerFlash_emiter.fx", "IRN_Gun_derringerFlash_particle.fx")    // IranCoJ Graphics: the flash
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_derringerEmbers_emiter.fx", "IRN_Gun_derringerEmbers_particle.fx")    // IranCoJ Graphics: embers
	}

	Delay(0)

	Spawn()
	{
		ParticleEmiter("IRN_Gun_derringerSmoke_emiter.fx", "IRN_Gun_derringerSmoke_particle.fx")    // IranCoJ Graphics: the black-powder cloud
	}
}
