ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.07)
	}

	GravityMul()
	{
		keyf(0, 0)
	}

	Drag()
	{
		keyf(0, 1)
	}

	WindInfluence()
	{
		keyf(0, 0)
	}

	Color()
	{
		keyv4(0, 1, 1, 1, 1)
		keyv4(0.03, 1, 1, 1, 0.8)
		keyv4(0.07, 1, 1, 1, 0)
	}

	Size()
	{
		keyf(0, 30)
		keyf(0.07, 60)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_MuzzleFlash_particleADD.mat", "IRN_MuzzleFlash_particleADD.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
