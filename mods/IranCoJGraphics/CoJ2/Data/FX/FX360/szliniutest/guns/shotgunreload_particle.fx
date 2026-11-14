ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.9)
	}

	GravityMul()
	{
		keyf(0, -0.08)
	}

	Drag()
	{
		keyf(0, 3)
	}

	WindInfluence()
	{
		keyf(0, 1)
	}

	Color()
	{
		keyv4(0, 0.88, 0.87, 0.85, 0)
		keyv4(0.06, 0.88, 0.87, 0.85, 0.16)
		keyv4(0.9, 0.88, 0.87, 0.85, 0)
	}

	Size()
	{
		keyf(0, 6)
		keyf(0.9, 26)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_GunSmoke_particleBLEND.mat", "IRN_GunSmoke_particleBLEND.mat")

	TexMultiRect(4, 4, 16)
	TexPlayMode("forward", 18)
}
