ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1)
	}

	GravityMul()
	{
		keyf(0, -0.1)
	}

	Drag()
	{
		keyf(0, 2.5)
	}

	WindInfluence()
	{
		keyf(0, 1.5)
	}

	Color()
	{
		keyv4(0, 0.86, 0.85, 0.83, 0)
		keyv4(0.04, 0.86, 0.85, 0.83, 0.25)
		keyv4(0.15, 0.86, 0.85, 0.83, 0.16)
		keyv4(0.55, 0.86, 0.85, 0.83, 0.05)
		keyv4(1, 0.86, 0.85, 0.83, 0)
	}

	Size()
	{
		keyf(0, 12)
		keyf(0.3, 34)
		keyf(1, 85)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_GunSmoke_particleBLEND.mat", "IRN_GunSmoke_particleBLEND.mat")

	TexMultiRect(4, 4, 16)
	TexPlayMode("forward", 16)
}
