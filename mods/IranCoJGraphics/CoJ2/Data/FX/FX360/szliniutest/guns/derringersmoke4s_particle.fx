ParticleDef()
{
	LifeTime()
	{
		keyf(0, 2)
	}

	GravityMul()
	{
		keyf(0, -0.06)
	}

	Drag()
	{
		keyf(0, 2)
	}

	WindInfluence()
	{
		keyf(0, 1)
	}

	Color()
	{
		keyv4(0, 0.88, 0.87, 0.85, 0)
		keyv4(0.1, 0.88, 0.87, 0.85, 0.18)
		keyv4(2, 0.88, 0.87, 0.85, 0)
	}

	Size()
	{
		keyf(0, 3)
		keyf(2, 20)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_GunSmoke_particleBLEND.mat", "IRN_GunSmoke_particleBLEND.mat")

	TexMultiRect(4, 4, 16)
	TexPlayMode("forward", 8)
}
